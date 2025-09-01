import os
import logging
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, UserProfile, Transaction, Goal, ChatMessage
from gemini_service import GeminiService
from utils import calculate_budget_breakdown, calculate_asset_allocation, calculate_goal_savings

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")

# Configure PostgreSQL database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize Gemini service
gemini_service = GeminiService()

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def dashboard():
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    # Get current month transactions
    current_month = datetime.now().replace(day=1).date()
    next_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).date()
    
    month_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= current_month,
        Transaction.date < next_month
    ).all()
    
    # Calculate budget summary
    total_income = sum(t.amount for t in month_transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in month_transactions if t.type == 'expense')
    
    # Get active goals
    active_goals = Goal.query.filter_by(user_id=current_user.id, status='active').all()
    
    # Calculate portfolio summary if profile exists
    portfolio_summary = None
    if profile:
        portfolio_summary = calculate_asset_allocation(profile.__dict__)
    
    # Get AI tip of the day
    ai_tip = None
    if profile:
        try:
            ai_tip = gemini_service.get_daily_tip(profile.__dict__, {
                'income': total_income,
                'expenses': total_expenses,
                'goals': active_goals
            })
        except Exception as ai_error:
            logging.warning(f"AI tip generation failed: {ai_error}")
            ai_tip = "Welcome to your financial dashboard! Track your expenses and reach your goals."
    
    return render_template('dashboard.html', 
                         user=current_user,
                         profile=profile,
                         total_income=total_income,
                         total_expenses=total_expenses,
                         active_goals=active_goals,
                         portfolio_summary=portfolio_summary,
                         ai_tip=ai_tip)

@app.route('/budgeting', methods=['GET', 'POST'])
@login_required
def budgeting():
    if request.method == 'POST':
        try:
            transaction = Transaction(
                user_id=current_user.id,
                type=request.form['type'],
                category=request.form['category'],
                amount=float(request.form['amount']),
                description=request.form['description'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            )
            db.session.add(transaction)
            db.session.commit()
            flash('Transaction added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding transaction: {str(e)}', 'error')
        return redirect(url_for('budgeting'))
    
    # Get current month transactions
    current_month = datetime.now().replace(day=1).date()
    next_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).date()
    
    month_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= current_month,
        Transaction.date < next_month
    ).order_by(Transaction.date.desc()).all()
    
    # Calculate budget breakdown
    transactions_data = [{
        'amount': t.amount,
        'type': t.type,
        'category': t.category
    } for t in month_transactions]
    budget_breakdown = calculate_budget_breakdown(transactions_data)
    
    # Get category-wise expenses
    expense_categories = {}
    for transaction in month_transactions:
        if transaction.type == 'expense':
            category = transaction.category
            expense_categories[category] = expense_categories.get(category, 0) + transaction.amount
    
    return render_template('budgeting.html', 
                         transactions=month_transactions,
                         budget_breakdown=budget_breakdown,
                         expense_categories=expense_categories)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            existing_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
            
            if existing_profile:
                existing_profile.job_title = request.form['job_title']
                existing_profile.monthly_salary = float(request.form['monthly_salary'])
                existing_profile.age = int(request.form['age'])
                existing_profile.dependents = int(request.form['dependents'])
                existing_profile.location = request.form['location']
                existing_profile.risk_tolerance = request.form['risk_tolerance']
                existing_profile.financial_goals = request.form['financial_goals']
                existing_profile.monthly_expenses = float(request.form['monthly_expenses'])
                existing_profile.existing_investments = float(request.form['existing_investments'])
                existing_profile.debt_amount = float(request.form['debt_amount'])
                existing_profile.emergency_fund = float(request.form.get('emergency_fund', 0))
                existing_profile.updated_at = datetime.utcnow()
            else:
                existing_profile = UserProfile(
                    user_id=current_user.id,
                    job_title=request.form['job_title'],
                    monthly_salary=float(request.form['monthly_salary']),
                    age=int(request.form['age']),
                    dependents=int(request.form['dependents']),
                    location=request.form['location'],
                    risk_tolerance=request.form['risk_tolerance'],
                    financial_goals=request.form['financial_goals'],
                    monthly_expenses=float(request.form['monthly_expenses']),
                    existing_investments=float(request.form['existing_investments']),
                    debt_amount=float(request.form['debt_amount']),
                    emergency_fund=float(request.form.get('emergency_fund', 0))
                )
                db.session.add(existing_profile)
            
            db.session.commit()
            
            # Generate AI advisory with timeout
            advisory = None
            try:
                advisory = gemini_service.generate_financial_advisory(existing_profile.__dict__)
            except Exception as ai_error:
                logging.warning(f"AI advisory failed: {ai_error}")
                advisory = "AI advisory temporarily unavailable. Your profile has been saved successfully."
            
            flash('Profile updated successfully!', 'success')
            return render_template('profile.html', 
                                 profile=existing_profile, 
                                 advisory=advisory)
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
            return redirect(url_for('profile'))
    
    # Get existing profile
    existing_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    advisory = None
    
    if existing_profile:
        try:
            advisory = gemini_service.generate_financial_advisory(existing_profile.__dict__)
        except Exception as ai_error:
            logging.warning(f"AI advisory failed: {ai_error}")
            advisory = "Complete your profile to get personalized AI financial advisory."
    
    return render_template('profile.html', 
                         profile=existing_profile,
                         advisory=advisory)

@app.route('/portfolio')
@login_required
def portfolio():
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    if not profile:
        flash('Please complete your profile first to see portfolio recommendations.', 'warning')
        return redirect(url_for('profile'))
    
    # Calculate asset allocation
    allocation = calculate_asset_allocation(profile.__dict__)
    
    # Get AI explanation
    explanation = gemini_service.explain_portfolio_allocation(profile.__dict__, allocation)
    
    # Real-world investment examples
    investment_examples = {
        "equity": [
            {"name": "HDFC Equity Fund", "type": "Mutual Fund", "risk": "High", "returns": "12-15%"},
            {"name": "Mirae Asset Large Cap Fund", "type": "Mutual Fund", "risk": "Medium", "returns": "10-13%"},
            {"name": "ICICI Prudential Technology Fund", "type": "Sector Fund", "risk": "Very High", "returns": "15-20%"}
        ],
        "debt": [
            {"name": "PPF", "type": "Government Scheme", "risk": "Very Low", "returns": "7-8%"},
            {"name": "HDFC Corporate Bond Fund", "type": "Debt Fund", "risk": "Low", "returns": "6-8%"},
            {"name": "SBI Fixed Deposit", "type": "Bank FD", "risk": "Very Low", "returns": "5-7%"}
        ],
        "gold": [
            {"name": "HDFC Gold ETF", "type": "ETF", "risk": "Medium", "returns": "8-12%"},
            {"name": "Digital Gold", "type": "Digital Investment", "risk": "Medium", "returns": "Variable"},
            {"name": "Gold Mutual Funds", "type": "Mutual Fund", "risk": "Medium", "returns": "8-10%"}
        ]
    }
    
    return render_template('portfolio.html', 
                         profile=profile,
                         allocation=allocation,
                         explanation=explanation,
                         investment_examples=investment_examples)

@app.route('/coach', methods=['GET', 'POST'])
@login_required
def coach():
    if request.method == 'POST':
        user_message = request.form['message']
        
        # Get user context
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(10).all()
        user_goals = Goal.query.filter_by(user_id=current_user.id).all()
        
        # Convert to dict format for AI service
        profile_dict = profile.__dict__ if profile else {}
        transactions_data = [t.__dict__ for t in recent_transactions]
        goals_data = [g.__dict__ for g in user_goals]
        
        # Get AI response
        ai_response = gemini_service.chat_with_coach(user_message, profile_dict, transactions_data, goals_data)
        
        # Save chat history
        chat_entry = ChatMessage(
            user_id=current_user.id,
            user_message=user_message,
            ai_response=ai_response
        )
        db.session.add(chat_entry)
        db.session.commit()
        
        flash('Message sent!', 'success')
    
    # Get chat history
    chat_messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp.desc()).limit(20).all()
    chat_messages.reverse()  # Show oldest first
    
    return render_template('coach.html', chat_messages=chat_messages)

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals_page():
    if request.method == 'POST':
        try:
            goal_data = {
                'target_amount': float(request.form['target_amount']),
                'current_amount': float(request.form.get('current_amount', 0)),
                'target_date': datetime.strptime(request.form['target_date'], '%Y-%m-%d').date()
            }
            
            # Calculate monthly savings needed
            monthly_savings = calculate_goal_savings(goal_data)
            
            goal = Goal(
                user_id=current_user.id,
                title=request.form['title'],
                target_amount=goal_data['target_amount'],
                target_date=goal_data['target_date'],
                current_amount=goal_data['current_amount'],
                category=request.form['category'],
                status='active',
                monthly_savings_needed=monthly_savings
            )
            
            db.session.add(goal)
            db.session.commit()
            flash('Goal created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating goal: {str(e)}', 'error')
        return redirect(url_for('goals_page'))
    
    # Get user goals
    user_goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).all()
    
    # Get AI suggestions for each goal
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if profile:
        for goal in user_goals:
            goal.ai_suggestion = gemini_service.suggest_goal_optimization(goal.__dict__, profile.__dict__)
    
    return render_template('goals.html', goals=user_goals)

@app.route('/update_goal', methods=['POST'])
@login_required
def update_goal():
    goal_id = int(request.form['goal_id'])
    current_amount = float(request.form['current_amount'])
    
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if goal:
        goal.current_amount = current_amount
        goal.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Goal updated successfully!', 'success')
    
    return redirect(url_for('goals_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        session['username'] = username
        
        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/delete_transaction/<int:transaction_id>')
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('budgeting'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
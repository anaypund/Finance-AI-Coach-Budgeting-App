import os
import logging
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_moment import Moment
from werkzeug.security import generate_password_hash, check_password_hash
from models import (
    users_col, profiles_col, transactions_col, goals_col, chat_col,
    create_user, check_user_password, create_profile, add_transaction,
    add_goal, save_chat_message
)
from gemini_service import GeminiService
from utils import calculate_budget_breakdown, calculate_asset_allocation, calculate_goal_savings
from bson import ObjectId
from config import Config


logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Add global functions to Jinja templates
app.jinja_env.globals.update(min=min, max=max)

# Initialize Flask extensions
login_manager = LoginManager()
moment = Moment(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

class MongoUser:
    def __init__(self, user_dict):
        self.user_dict = user_dict

    def get_id(self):
        return str(self.user_dict["_id"])

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    user = users_col.find_one({"_id": ObjectId(user_id)})
    return MongoUser(user) if user else None


# Initialize Gemini service
gemini_service = GeminiService()

@app.route('/')
@login_required
def dashboard():
    profile = profiles_col.find_one({"user_id": ObjectId(current_user.get_id())})
    
    # Get current month transactions
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    month_transactions = list(transactions_col.find({
        "user_id": ObjectId(current_user.get_id()),
        "date": {"$gte": current_month, "$lt": next_month}
    }))
    
    # Calculate budget summary
    total_income = sum(t["amount"] for t in month_transactions if t["type"] == 'income')
    total_expenses = sum(t["amount"] for t in month_transactions if t["type"] == 'expense')

    # Get active goals
    active_goals = list(goals_col.find({"user_id": ObjectId(current_user.get_id()), "status": "active"}))

    # Calculate portfolio summary if profile exists
    portfolio_summary = None
    if profile:
        portfolio_summary = calculate_asset_allocation(profile)
    
    # Get AI tip of the day
    ai_tip = None
    if profile:
        try:
            ai_tip = gemini_service.get_daily_tip(profile, {
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
            transaction_data = {
                "type": request.form['type'],
                "category": request.form['category'],
                "amount": float(request.form['amount']),
                "description": request.form['description'],
                "date": datetime.strptime(request.form['date'], '%Y-%m-%d')
            }
            add_transaction(current_user.get_id(), transaction_data)
            flash('Transaction added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding transaction: {str(e)}', 'error')
        return redirect(url_for('budgeting'))
    
    # Get current month transactions
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    month_transactions = list(transactions_col.find({
        "user_id": ObjectId(current_user.get_id()),
        "date": {"$gte": current_month, "$lt": next_month}
    }).sort("date", -1))
    
    # Calculate budget breakdown
    transactions_data = [{
        'amount': t['amount'],
        'type': t['type'],
        'category': t['category']
    } for t in month_transactions]
    budget_breakdown = calculate_budget_breakdown(transactions_data)
    
    # Get category-wise expenses
    expense_categories = {}
    for transaction in month_transactions:
        if transaction['type'] == 'expense':
            category = transaction['category']
            expense_categories[category] = expense_categories.get(category, 0) + transaction['amount']
    
    return render_template('budgeting.html', 
                         transactions=month_transactions,
                         budget_breakdown=budget_breakdown,
                         expense_categories=expense_categories)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            existing_profile = profiles_col.find_one({"user_id": ObjectId(current_user.get_id())})
            
            profile_data = {
                "job_title": request.form['job_title'],
                "monthly_salary": float(request.form['monthly_salary']),
                "age": int(request.form['age']),
                "dependents": int(request.form['dependents']),
                "location": request.form['location'],
                "risk_tolerance": request.form['risk_tolerance'],
                "financial_goals": request.form['financial_goals'],
                "monthly_expenses": float(request.form['monthly_expenses']),
                "existing_investments": float(request.form['existing_investments']),
                "debt_amount": float(request.form['debt_amount']),
                "emergency_fund": float(request.form.get('emergency_fund', 0)),
                "updated_at": datetime.utcnow()
            }
            
            if existing_profile:
                profiles_col.update_one(
                    {"user_id": ObjectId(current_user.get_id())},
                    {"$set": profile_data}
                )
            else:
                create_profile(current_user.get_id(), profile_data)
            
            # Get the updated profile data
            updated_profile = profiles_col.find_one({"user_id": ObjectId(current_user.get_id())})
            
            # Generate AI advisory with timeout
            advisory = None
            try:
                advisory = gemini_service.generate_financial_advisory(updated_profile)
            except Exception as ai_error:
                logging.warning(f"AI advisory failed: {ai_error}")
                advisory = "AI advisory temporarily unavailable. Your profile has been saved successfully."
            
            flash('Profile updated successfully!', 'success')
            return render_template('profile.html', 
                                 profile=existing_profile, 
                                 advisory=advisory)
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
            return redirect(url_for('profile'))
    
    # Get existing profile
    existing_profile = profiles_col.find_one({"user_id": ObjectId(current_user.get_id())})
    advisory = None
    
    if existing_profile:
        try:
            advisory = gemini_service.generate_financial_advisory(existing_profile)
        except Exception as ai_error:
            logging.warning(f"AI advisory failed: {ai_error}")
            advisory = "Complete your profile to get personalized AI financial advisory."
    
    return render_template('profile.html', 
                         profile=existing_profile,
                         advisory=advisory)

@app.route('/portfolio')
@login_required
def portfolio():
    profile = profiles_col.find_one({"user_id": ObjectId(current_user.get_id())})
    
    if not profile:
        flash('Please complete your profile first to see portfolio recommendations.', 'warning')
        return redirect(url_for('profile'))
    
    # Calculate asset allocation
    allocation = calculate_asset_allocation(profile)
    
    # Get AI explanation
    explanation = gemini_service.explain_portfolio_allocation(profile, allocation)
    
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
        profile = profiles_col.find_one({"user_id": ObjectId(current_user.get_id())})
        recent_transactions = list(transactions_col.find({
            "user_id": ObjectId(current_user.get_id())
        }).sort("date", -1).limit(10))
        user_goals = list(goals_col.find({
            "user_id": ObjectId(current_user.get_id())
        }))
        
        # Get AI response
        ai_response = gemini_service.chat_with_coach(user_message, profile, recent_transactions, user_goals)
        
        # Save chat history
        save_chat_message(current_user.get_id(), user_message, ai_response)
        
        flash('Message sent!', 'success')
    
    # Get chat history
    chat_messages = list(chat_col.find({
        "user_id": ObjectId(current_user.get_id())
    }).sort("timestamp", 1).limit(20))
    
    return render_template('coach.html', chat_messages=chat_messages)

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals_page():
    if request.method == 'POST':
        try:
            goal_data = {
                'target_amount': float(request.form['target_amount']),
                'current_amount': float(request.form.get('current_amount', 0)),
                'target_date': datetime.strptime(request.form['target_date'], '%Y-%m-%d')
            }
            
            # Calculate monthly savings needed
            monthly_savings = calculate_goal_savings(goal_data)
            
            goal_data.update({
                "title": request.form['title'],
                "category": request.form['category'],
                "status": 'active',
                "monthly_savings_needed": monthly_savings,
                "created_at": datetime.utcnow()
            })
            
            add_goal(current_user.get_id(), goal_data)
            flash('Goal created successfully!', 'success')
        except Exception as e:
            flash(f'Error creating goal: {str(e)}', 'error')
        return redirect(url_for('goals_page'))
    
    # Get user goals
    user_goals = list(goals_col.find({
        "user_id": ObjectId(current_user.get_id())
    }).sort("created_at", -1))
    
    # Get AI suggestions for each goal
    profile = profiles_col.find_one({"user_id": ObjectId(current_user.get_id())})
    if profile:
        for goal in user_goals:
            goal['ai_suggestion'] = gemini_service.suggest_goal_optimization(goal, profile)
    
    current_time = datetime.utcnow()
    return render_template('goals.html', goals=user_goals, current_time=current_time)

@app.route('/update_goal', methods=['POST'])
@login_required
def update_goal():
    goal_id = request.form['goal_id']
    current_amount = float(request.form['current_amount'])
    
    result = goals_col.update_one(
        {
            "_id": ObjectId(goal_id),
            "user_id": ObjectId(current_user.get_id())
        },
        {
            "$set": {
                "current_amount": current_amount,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count:
        flash('Goal updated successfully!', 'success')
    
    return redirect(url_for('goals_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_id = check_user_password(email, password)
        if user_id:
            user = users_col.find_one({"_id": ObjectId(user_id)})
            login_user(MongoUser(user))
            session['username'] = user["username"]
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

        if users_col.find_one({"email": email}):
            flash('Email already registered!', 'error')
            return render_template('register.html')

        user_id = create_user(username, email, password)
        user = users_col.find_one({"_id": ObjectId(user_id)})
        login_user(MongoUser(user))
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

@app.route('/delete_transaction/<transaction_id>')
@login_required
def delete_transaction(transaction_id):
    transactions_col.delete_one({
        "_id": ObjectId(transaction_id),
        "user_id": ObjectId(current_user.get_id())
    })
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('budgeting'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
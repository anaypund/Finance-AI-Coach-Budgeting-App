from datetime import datetime, timedelta
import calendar

def calculate_budget_breakdown(transactions):
    """Calculate 50/30/20 budget breakdown from transactions"""
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    
    # Categorize expenses into needs, wants, and savings
    needs_categories = ['groceries', 'rent', 'utilities', 'transportation', 'insurance', 'healthcare']
    wants_categories = ['entertainment', 'dining', 'shopping', 'hobbies', 'travel']
    
    needs_total = 0
    wants_total = 0
    
    for transaction in transactions:
        if transaction['type'] == 'expense':
            category = transaction['category'].lower()
            if any(need in category for need in needs_categories):
                needs_total += transaction['amount']
            elif any(want in category for want in wants_categories):
                wants_total += transaction['amount']
    
    # Calculate savings (income - total expenses)
    savings_total = total_income - total_expenses
    
    # Calculate percentages
    needs_percentage = (needs_total / total_income * 100) if total_income > 0 else 0
    wants_percentage = (wants_total / total_income * 100) if total_income > 0 else 0
    savings_percentage = (savings_total / total_income * 100) if total_income > 0 else 0
    
    # Recommended percentages (50/30/20 rule)
    recommended_needs = total_income * 0.50
    recommended_wants = total_income * 0.30
    recommended_savings = total_income * 0.20
    
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'needs': {
            'amount': needs_total,
            'percentage': needs_percentage,
            'recommended': recommended_needs,
            'status': 'good' if needs_total <= recommended_needs else 'over'
        },
        'wants': {
            'amount': wants_total,
            'percentage': wants_percentage,
            'recommended': recommended_wants,
            'status': 'good' if wants_total <= recommended_wants else 'over'
        },
        'savings': {
            'amount': savings_total,
            'percentage': savings_percentage,
            'recommended': recommended_savings,
            'status': 'good' if savings_total >= recommended_savings else 'under'
        }
    }

def calculate_asset_allocation(profile):
    """Calculate recommended asset allocation based on user profile"""
    age = profile.get('age', 30)
    risk_tolerance = profile.get('risk_tolerance', 'moderate')
    monthly_salary = profile.get('monthly_salary', 0)
    
    # Base allocation by age (100 - age rule for equity)
    base_equity = max(100 - age, 20)  # Minimum 20% equity
    
    # Adjust based on risk tolerance
    if risk_tolerance == 'conservative':
        equity_allocation = max(base_equity - 20, 20)
    elif risk_tolerance == 'aggressive':
        equity_allocation = min(base_equity + 20, 80)
    else:  # moderate
        equity_allocation = base_equity
    
    # Remaining allocation
    remaining = 100 - equity_allocation
    
    # Debt allocation (bonds, FDs, etc.)
    debt_allocation = remaining * 0.7
    
    # Gold allocation
    gold_allocation = remaining * 0.2
    
    # Emergency fund (separate from investment)
    emergency_fund_months = 6
    emergency_fund_amount = monthly_salary * emergency_fund_months
    
    return {
        'equity': round(equity_allocation),
        'debt': round(debt_allocation),
        'gold': round(gold_allocation),
        'emergency_fund_amount': emergency_fund_amount,
        'emergency_fund_months': emergency_fund_months
    }

def calculate_goal_savings(goal_data):
    """Calculate monthly savings needed to achieve a goal"""
    target_amount = goal_data['target_amount']
    current_amount = goal_data.get('current_amount', 0)
    target_date = goal_data['target_date']
    
    # Calculate months remaining
    today = datetime.now()
    months_remaining = (target_date.year - today.year) * 12 + (target_date.month - today.month)
    
    if months_remaining <= 0:
        return target_amount - current_amount  # Need to save it all now
    
    # Amount still needed
    amount_needed = target_amount - current_amount
    
    # Monthly savings required
    monthly_savings = amount_needed / months_remaining
    
    return max(monthly_savings, 0)

def get_expense_categories():
    """Get predefined expense categories"""
    return [
        'groceries', 'rent', 'utilities', 'transportation', 'insurance',
        'healthcare', 'entertainment', 'dining', 'shopping', 'hobbies',
        'travel', 'education', 'charity', 'subscriptions', 'other'
    ]

def get_income_categories():
    """Get predefined income categories"""
    return [
        'salary', 'freelance', 'business', 'investment_returns',
        'rental_income', 'bonus', 'gift', 'other'
    ]

def get_goal_categories():
    """Get predefined goal categories"""
    return [
        'emergency_fund', 'vacation', 'house_down_payment', 'car',
        'wedding', 'education', 'retirement', 'business', 'other'
    ]

def calculate_financial_health_score(profile, transactions, goals):
    """Calculate a financial health score (0-100)"""
    score = 0
    
    # Emergency fund check (25 points)
    monthly_expenses = profile.get('monthly_expenses', 0)
    existing_investments = profile.get('existing_investments', 0)
    
    emergency_fund_months = existing_investments / monthly_expenses if monthly_expenses > 0 else 0
    if emergency_fund_months >= 6:
        score += 25
    elif emergency_fund_months >= 3:
        score += 15
    elif emergency_fund_months >= 1:
        score += 8
    
    # Debt-to-income ratio (25 points)
    monthly_salary = profile.get('monthly_salary', 0)
    debt_amount = profile.get('debt_amount', 0)
    
    if monthly_salary > 0:
        debt_to_income = debt_amount / (monthly_salary * 12)
        if debt_to_income < 0.2:
            score += 25
        elif debt_to_income < 0.4:
            score += 15
        elif debt_to_income < 0.6:
            score += 8
    
    # Savings rate (25 points)
    if transactions:
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        
        if total_income > 0:
            savings_rate = (total_income - total_expenses) / total_income
            if savings_rate >= 0.3:
                score += 25
            elif savings_rate >= 0.2:
                score += 20
            elif savings_rate >= 0.1:
                score += 15
            elif savings_rate >= 0.05:
                score += 10
    
    # Goal progress (25 points)
    if goals:
        goal_progress_total = 0
        for goal in goals:
            if goal['target_amount'] > 0:
                progress = goal['current_amount'] / goal['target_amount']
                goal_progress_total += min(progress, 1.0)
        
        avg_progress = goal_progress_total / len(goals)
        score += avg_progress * 25
    
    return min(round(score), 100)

def format_currency(amount):
    """Format amount as Indian currency"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.1f}Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.1f}L"
    elif amount >= 1000:  # 1 thousand
        return f"₹{amount/1000:.1f}K"
    else:
        return f"₹{amount:,.0f}"

def get_month_year_options():
    """Get list of month-year options for filtering"""
    options = []
    current_date = datetime.now()
    
    for i in range(12):  # Last 12 months
        date = current_date - timedelta(days=i*30)
        month_name = calendar.month_name[date.month]
        options.append({
            'value': f"{date.year}-{date.month:02d}",
            'label': f"{month_name} {date.year}"
        })
    
    return options

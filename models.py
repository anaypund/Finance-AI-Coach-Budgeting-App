from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

# MongoDB Connection
client = MongoClient(Config.MONGODB_URI)
db = client[Config.DB_NAME]

# Collections
users_col = db["users"]
profiles_col = db["user_profiles"]
transactions_col = db["transactions"]
goals_col = db["goals"]
chat_col = db["chat_messages"]

# ----------------------------
# User model helpers
# ----------------------------
def create_user(username, email, password):
    password_hash = generate_password_hash(password)
    user = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    }
    result = users_col.insert_one(user)
    return str(result.inserted_id)

def check_user_password(email, password):
    user = users_col.find_one({"email": email})
    if user and check_password_hash(user["password_hash"], password):
        return str(user["_id"])
    return None

# ----------------------------
# Profile helpers
# ----------------------------
def create_profile(user_id, data):
    profile = {
        "user_id": ObjectId(user_id),
        "job_title": data.get("job_title"),
        "monthly_salary": float(data.get("monthly_salary")),
        "age": int(data.get("age")),
        "dependents": int(data.get("dependents", 0)),
        "location": data.get("location"),
        "risk_tolerance": data.get("risk_tolerance", "moderate"),
        "financial_goals": data.get("financial_goals", ""),
        "monthly_expenses": float(data.get("monthly_expenses", 0)),
        "existing_investments": float(data.get("existing_investments", 0)),
        "debt_amount": float(data.get("debt_amount", 0)),
        "emergency_fund": float(data.get("emergency_fund", 0)),
        "updated_at": datetime.utcnow()
    }
    profiles_col.insert_one(profile)

# ----------------------------
# Transactions helpers
# ----------------------------
def add_transaction(user_id, data):
    txn = {
        "user_id": ObjectId(user_id),
        "type": data["type"],
        "category": data["category"],
        "amount": float(data["amount"]),
        "description": data.get("description", ""),
        "date": data["date"],
        "created_at": datetime.utcnow()
    }
    transactions_col.insert_one(txn)

# ----------------------------
# Goals helpers
# ----------------------------
def add_goal(user_id, data):
    goal = {
        "user_id": ObjectId(user_id),
        "title": data["title"],
        "target_amount": float(data["target_amount"]),
        "current_amount": float(data.get("current_amount", 0)),
        "target_date": data["target_date"],
        "category": data["category"],
        "status": data.get("status", "active"),
        "monthly_savings_needed": float(data.get("monthly_savings_needed", 0)),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    goals_col.insert_one(goal)

# ----------------------------
# Chat messages helpers
# ----------------------------
def save_chat_message(user_id, user_message, ai_response):
    chat = {
        "user_id": ObjectId(user_id),
        "user_message": user_message,
        "ai_response": ai_response,
        "timestamp": datetime.utcnow()
    }
    chat_col.insert_one(chat)

# ----------------------------
# Validation functions (unchanged)
# ----------------------------
def validate_user_data(data):
    required_fields = ['username', 'email', 'password']
    return all(field in data and data[field] for field in required_fields)

def validate_profile_data(data):
    required_fields = ['job_title', 'monthly_salary', 'age', 'location']
    return all(field in data and data[field] for field in required_fields)

def validate_transaction_data(data):
    required_fields = ['type', 'category', 'amount', 'description', 'date']
    return all(field in data and data[field] for field in required_fields)

def validate_goal_data(data):
    required_fields = ['title', 'target_amount', 'target_date', 'category']
    return all(field in data and data[field] for field in required_fields)

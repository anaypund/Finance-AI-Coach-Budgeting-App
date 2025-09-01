from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    monthly_salary = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    dependents = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100), nullable=False)
    risk_tolerance = db.Column(db.String(20), nullable=False, default='moderate')  # conservative, moderate, aggressive
    financial_goals = db.Column(db.Text)
    monthly_expenses = db.Column(db.Float, nullable=False)
    existing_investments = db.Column(db.Float, default=0)
    debt_amount = db.Column(db.Float, default=0)
    emergency_fund = db.Column(db.Float, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.id}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # income, expense
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.type}: {self.amount}>'

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    target_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    monthly_savings_needed = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Goal {self.title}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>'

# Validation functions
def validate_user_data(data):
    """Validate user registration data"""
    required_fields = ['username', 'email', 'password']
    return all(field in data and data[field] for field in required_fields)

def validate_profile_data(data):
    """Validate user profile data"""
    required_fields = ['job_title', 'monthly_salary', 'age', 'location']
    return all(field in data and data[field] for field in required_fields)

def validate_transaction_data(data):
    """Validate transaction data"""
    required_fields = ['type', 'category', 'amount', 'description', 'date']
    return all(field in data and data[field] for field in required_fields)

def validate_goal_data(data):
    """Validate goal data"""
    required_fields = ['title', 'target_amount', 'target_date', 'category']
    return all(field in data and data[field] for field in required_fields)
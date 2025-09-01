import os
import logging
from google import genai
from google.genai import types
import json
from datetime import datetime

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = "gemini-2.5-flash"
    
    def generate_financial_advisory(self, profile):
        """Generate personalized financial advisory based on user profile"""
        try:
            prompt = f"""
            As a professional financial advisor, provide personalized financial advice for the following user profile:
            
            Job Title: {profile.get('job_title', 'N/A')}
            Monthly Salary: ₹{profile.get('monthly_salary', 0):,.2f}
            Age: {profile.get('age', 'N/A')}
            Dependents: {profile.get('dependents', 0)}
            Location: {profile.get('location', 'N/A')}
            Risk Tolerance: {profile.get('risk_tolerance', 'moderate')}
            Monthly Expenses: ₹{profile.get('monthly_expenses', 0):,.2f}
            Existing Investments: ₹{profile.get('existing_investments', 0):,.2f}
            Current Debt: ₹{profile.get('debt_amount', 0):,.2f}
            Financial Goals: {profile.get('financial_goals', 'N/A')}
            
            Please provide:
            1. Financial health assessment
            2. Savings recommendations
            3. Debt management advice (if applicable)
            4. Investment strategy suggestions
            5. Emergency fund recommendations
            6. Tax planning tips
            
            Keep the advice practical, actionable, and specific to the Indian financial context.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else "Unable to generate advisory at this time."
            
        except Exception as e:
            logging.error(f"Error generating financial advisory: {e}")
            return "Sorry, I'm unable to provide advisory at this moment. Please try again later."
    
    def get_daily_tip(self, profile, financial_data):
        """Generate daily financial tip based on user profile and recent data"""
        try:
            prompt = f"""
            Based on the user's financial profile and current month's data, provide a short, actionable financial tip for today:
            
            Monthly Income: ₹{financial_data.get('income', 0):,.2f}
            Monthly Expenses: ₹{financial_data.get('expenses', 0):,.2f}
            Risk Tolerance: {profile.get('risk_tolerance', 'moderate')}
            Age: {profile.get('age', 'N/A')}
            Active Goals: {len(financial_data.get('goals', []))}
            
            Provide a single, practical tip that the user can implement today. Keep it under 100 words.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else "Track your expenses daily to stay on budget!"
            
        except Exception as e:
            logging.error(f"Error generating daily tip: {e}")
            return "Review your spending categories to identify potential savings."
    
    def chat_with_coach(self, user_message, profile, recent_transactions, goals):
        """Handle chat conversation with financial coach"""
        try:
            # Prepare context
            context = ""
            if profile:
                context += f"User Profile: {profile.get('job_title', 'N/A')}, Age: {profile.get('age', 'N/A')}, "
                context += f"Monthly Salary: ₹{profile.get('monthly_salary', 0):,.2f}, "
                context += f"Risk Tolerance: {profile.get('risk_tolerance', 'moderate')}\n"
            
            if recent_transactions:
                context += f"Recent Transactions: {len(recent_transactions)} transactions in the last period\n"
            
            if goals:
                context += f"Active Goals: {len(goals)} financial goals\n"
            
            prompt = f"""
            You are an AI financial coach helping users with their personal finance questions. 
            
            User Context:
            {context}
            
            User Question: {user_message}
            
            Provide a helpful, personalized response that:
            1. Directly addresses their question
            2. Considers their financial profile
            3. Offers actionable advice
            4. Is encouraging and supportive
            5. Uses Indian financial context (₹, Indian investment options, etc.)
            
            Keep the response conversational and under 200 words.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else "I'm here to help with your financial questions. Could you please rephrase your question?"
            
        except Exception as e:
            logging.error(f"Error in chat with coach: {e}")
            return "I'm experiencing some technical difficulties. Please try asking your question again."
    
    def explain_portfolio_allocation(self, profile, allocation):
        """Explain portfolio allocation strategy"""
        try:
            prompt = f"""
            Explain the following portfolio allocation strategy in simple terms for a user with this profile:
            
            Age: {profile.get('age', 'N/A')}
            Risk Tolerance: {profile.get('risk_tolerance', 'moderate')}
            Monthly Salary: ₹{profile.get('monthly_salary', 0):,.2f}
            
            Recommended Allocation:
            Equity: {allocation.get('equity', 0)}%
            Debt: {allocation.get('debt', 0)}%
            Gold: {allocation.get('gold', 0)}%
            Emergency Fund: {allocation.get('emergency', 0)}%
            
            Explain:
            1. Why this allocation suits their profile
            2. How each asset class benefits them
            3. Risk and return expectations
            4. When to review and rebalance
            
            Use simple language and Indian investment context.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else "This allocation balances growth and safety based on your profile."
            
        except Exception as e:
            logging.error(f"Error explaining portfolio: {e}")
            return "This allocation is designed to match your risk tolerance and financial goals."
    
    def suggest_goal_optimization(self, goal, profile):
        """Suggest ways to optimize goal achievement"""
        try:
            days_to_goal = (goal['target_date'] - datetime.now()).days
            progress_percentage = (goal['current_amount'] / goal['target_amount']) * 100
            
            prompt = f"""
            Provide optimization suggestions for this financial goal:
            
            Goal: {goal['title']}
            Target Amount: ₹{goal['target_amount']:,.2f}
            Current Amount: ₹{goal['current_amount']:,.2f}
            Days Remaining: {days_to_goal}
            Progress: {progress_percentage:.1f}%
            Monthly Savings Needed: ₹{goal.get('monthly_savings_needed', 0):,.2f}
            
            User Monthly Salary: ₹{profile.get('monthly_salary', 0):,.2f}
            
            Provide 2-3 specific, actionable suggestions to help achieve this goal faster or more efficiently.
            Keep suggestions under 100 words total.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else "Consider increasing your monthly savings or exploring higher-yield investment options."
            
        except Exception as e:
            logging.error(f"Error suggesting goal optimization: {e}")
            return "Stay consistent with your savings plan and review progress monthly."

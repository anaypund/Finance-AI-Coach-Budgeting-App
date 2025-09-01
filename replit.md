# FinanceAI - Smart Personal Finance Management

## Overview

FinanceAI is a comprehensive personal finance management web application that provides users with intelligent financial tracking, budgeting tools, goal management, and AI-powered financial coaching. The application helps users manage their income and expenses, set and track financial goals, receive personalized investment advice, and interact with an AI financial coach for instant guidance.

The application is built around a user-centric design that emphasizes actionable financial insights through data visualization, automated budget analysis using the 50/30/20 rule, and personalized recommendations based on user profiles and financial behavior patterns.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask-based Python web application with a modular structure
- **Authentication**: Session-based authentication using Flask sessions with password hashing via Werkzeug security utilities
- **API Structure**: RESTful endpoints for financial data management, user profiles, and AI chat functionality
- **Business Logic**: Separated utility functions for financial calculations (budget breakdowns, asset allocation, goal savings calculations)

### Frontend Architecture  
- **Template Engine**: Jinja2 templating with a base template inheritance pattern
- **UI Framework**: Bootstrap with dark theme for responsive design
- **Visualization**: Chart.js for financial data visualization (budget charts, portfolio allocation)
- **Progressive Enhancement**: JavaScript for interactive features, form validation, and dynamic content updates

### Data Storage Solution
- **Primary Database**: MongoDB with PyMongo driver for document-based data storage
- **Collections Structure**: 
  - Users collection for authentication data
  - User profiles for financial information and preferences
  - Transactions for income/expense tracking
  - Goals for financial goal management
  - Chat history for AI conversation persistence
- **Data Modeling**: Schema-less approach with documented data structures in models.py for reference

### AI Integration Architecture
- **AI Service**: Dedicated GeminiService class using Google's Gemini API for financial advisory generation
- **Personalization Engine**: Profile-based advice generation considering user demographics, risk tolerance, and financial situation
- **Context Awareness**: Integration of user financial data with AI responses for relevant recommendations

### Financial Calculation Engine
- **Budget Analysis**: Automated 50/30/20 rule implementation for needs/wants/savings categorization
- **Asset Allocation**: Risk-based portfolio recommendations using user profile data
- **Goal Tracking**: Progress calculation and timeline projection for financial goals
- **Real-time Calculations**: Dynamic financial metrics updating based on transaction data

## External Dependencies

### Third-Party Services
- **Google Gemini API**: AI-powered financial advisory and chat functionality requiring GEMINI_API_KEY environment variable
- **MongoDB Atlas**: Cloud database service (configurable via MONGO_URI environment variable, defaults to local instance)

### Frontend Libraries
- **Bootstrap**: UI framework with custom dark theme from Replit CDN
- **Chart.js**: JavaScript charting library for financial data visualization  
- **Font Awesome**: Icon library for consistent UI iconography

### Python Dependencies
- **Flask**: Web framework for application structure and routing
- **PyMongo**: MongoDB driver for database operations
- **Google GenAI**: Official Google client library for Gemini API integration
- **Werkzeug**: Security utilities for password hashing and authentication
- **BSON**: MongoDB object ID handling and data type conversion

### Environment Configuration
- **SESSION_SECRET**: Flask session encryption key
- **MONGO_URI**: MongoDB connection string (production/local)
- **GEMINI_API_KEY**: Google Gemini API authentication token

### Development Dependencies
- **Logging**: Built-in Python logging for debugging and monitoring
- **DateTime**: Python datetime utilities for financial data time-based operations
- **JSON**: Data serialization for API responses and AI service communication
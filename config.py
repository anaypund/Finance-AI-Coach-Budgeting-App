import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configuration class
class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY not found in environment variables")
        raise ValueError("GEMINI_API_KEY not set")

    # Flask Configuration
    SECRET_KEY = os.environ.get("SESSION_SECRET", "your-secret-key-here")

    # MongoDB Configuration
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
    DB_NAME = os.environ.get("DB_NAME", "Test")

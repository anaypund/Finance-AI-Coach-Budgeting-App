# Gemini + MongoDB Chatbot

This project is a simple chatbot built using **Google’s Gemini API** and **MongoDB**.
It allows you to send prompts to a Gemini model, store conversations in MongoDB, and retrieve them later.

---

## 🚀 Features

* Connects to **Gemini AI** for prompt-based responses.
* Stores user queries and responses in **MongoDB Atlas / local MongoDB**.
* Retrieve and log previous conversations.
* Simple environment-based configuration.

---

## 📂 Project Structure

```
.
├── main.py          # Entry point of the chatbot
├── db.py            # MongoDB connection and helpers
├── gemini_client.py # Gemini API client setup
├── requirements.txt # Python dependencies
└── README.md        # Project documentation
```

---

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/anaypund/Finance-AI-Coach-Budgeting-App.git
cd Finance-AI-Coach-Budgeting-App
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the project root and add:

```env
GEMINI_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017
```

---

## ▶️ Running the Project

```bash
python main.py
```

---

## 🛠️ Example Usage

```python
from gemini_client import GeminiClient
from db import ConversationDB

gemini = GeminiClient()
db = ConversationDB()

# Ask a question
response = gemini.ask("Hello, how are you?")
print("Gemini:", response)

# Save to DB
db.save_conversation("Hello, how are you?", response)
```

---

## 📌 Notes

* Make sure MongoDB is running locally (`mongod`) or update `MONGO_URI` for Atlas.
* Free Gemini models (like `gemini-1.5-flash`) are used to avoid quota issues.

---


# FinBot – AI-Powered Personal Finance Chatbot

## Project Overview

FinBot is a personal finance chatbot designed to help users track their income and expenses, manage monthly budgets, and monitor their spending.

It provides a simple chat-based interface where users can enter their financial transactions in natural language. FinBot identifies transaction details, suggests expense categories, and asks for confirmation before saving transactions.

## Features

- **Chatbot Interface:** Interact with FinBot using simple messages.
- **Expense Tracking:** Record and manage daily expenses.
- **Income Tracking:** Record salary and other income.
- **Smart Category Suggestions:** Suggest categories based on merchant names and keywords.
- **UPI Simulator:** Simulate UPI payments and record them.
- **Transaction History:** View saved income and expense records.
- **Dashboard:** View total income, expenses, balance, and expense charts.
- **Budget Management:** Create and monitor monthly category budgets.
- **Budget Alerts:** Receive warnings when spending reaches 80% or exceeds the budget.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Chart.js

## Project Structure

    FinBot/
    |
    |-- app.py
    |-- database/
    |   |-- db.py
    |   |-- finbot.db
    |
    |-- templates/
    |   |-- index.html
    |   |-- dashboard.html
    |   |-- transactions.html
    |   |-- budgets.html
    |   |-- upi_simulator.html
    |
    |-- static/
    |   |-- style.css
    |
    |-- README.md

## Installation and Execution

### 1. Clone the repository

    git clone YOUR_GITHUB_REPOSITORY_URL

### 2. Open the project folder

    cd FinBot

### 3. Create a virtual environment

    python -m venv venv

### 4. Activate the virtual environment

    .\venv\Scripts\activate

### 5. Install Flask

    pip install flask

### 6. Run the application

    python app.py

### 7. Open in your browser

    http://127.0.0.1:5000/

## How It Works

1. The user enters an income or expense through the chatbot.
2. FinBot identifies the transaction amount and type.
3. It suggests an expense category using keyword matching.
4. The user confirms or cancels the transaction.
5. Confirmed transactions are stored in SQLite.
6. The dashboard and budget pages display updated financial information.
7. Budget alerts notify users when spending reaches important limits.

## Future Enhancements

- Integration with authorized banking and payment services.
- Advanced AI-based expense classification.
- Monthly financial reports.
- Spending predictions and personalized saving suggestions.
- Secure user authentication and multiple user accounts.

## Important Note

The current UPI feature is a simulator for educational purposes. It does not connect to a real bank account or transfer actual money.

## Project Purpose

This project demonstrates the use of Python, Flask, database management, web development, and basic intelligent text processing to develop a personal finance management application.

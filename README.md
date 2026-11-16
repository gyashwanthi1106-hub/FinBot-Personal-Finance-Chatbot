# FinBot – Personal Finance Chatbot

FinBot is a Flask-based personal finance chatbot that helps users track income and expenses, manage monthly budgets, view transaction history, and monitor spending through an interactive dashboard.

## Features

- Chatbot-based expense and income tracking
- Automatic expense category suggestions
- Transaction history management
- Interactive dashboard with charts
- Monthly budget management
- Budget alerts when spending reaches or exceeds the limit
- UPI payment simulator

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Chart.js

## Project Structure

```text
FinBot/
├── app.py
├── database/
│   └── db.py
├── templates/
├── static/
├── requirements.txt
├── README.md
└── .gitignore
```

## How to Run

1. Clone the repository.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app.py
```

4. Open `http://127.0.0.1:5000` in your browser.

## Note

The UPI feature is a simulator. It does not connect to real bank accounts or process actual UPI payments. Expense categories are suggested using keyword-based matching.

## Future Enhancements

- Secure financial account integration
- Advanced AI-based financial suggestions
- Mobile application support

from flask import Flask, render_template, request, jsonify, session, redirect
from database.db import (
    create_tables,
    add_transaction,
    get_transactions,
    get_dashboard_summary,
    add_budget,
    get_budgets
)
import re

app = Flask(__name__)
app.secret_key = "finbot_secret_key"

create_tables()


# Category suggestions
CATEGORY_KEYWORDS = {
    "Food": ["food", "restaurant", "hotel", "pani puri", "pizza",
             "burger", "lunch", "dinner", "breakfast", "cafe"],
    "Travel": ["travel", "bus", "train", "auto", "cab", "taxi", "petrol"],
    "Shopping": ["shopping", "clothes", "dress", "costume", "shoes"],
    "Medical": ["medical", "medicine", "hospital", "doctor"],
    "Education": ["education", "books", "college", "course", "fees"],
    "Entertainment": ["movie", "cinema", "game", "concert"],
    "Rent": ["rent", "house rent"]
}


# Detect expense category
def find_category(message):
    message = message.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if re.search(r"\b" + re.escape(keyword) + r"\b", message):
                return category

    return None


# Detect income or expense
def find_transaction_type(message):
    message = message.lower()

    income_keywords = [
        "salary", "income", "received", "earned",
        "credited", "freelance", "freelancing",
        "got paid"
    ]

    for keyword in income_keywords:
        if re.search(r"\b" + re.escape(keyword) + r"\b", message):
            return "Income"

    return "Expense"


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()

    # Check whether user is answering a category question
    pending = session.get("pending_transaction")

    if pending and pending.get("needs_category"):
        category = find_category(message)

        if not category:
            return jsonify({
                "reply": "I couldn't identify that category. Please enter Food, Travel, Shopping or another supported category."
            })

        pending["category"] = category
        pending["needs_category"] = False
        session["pending_transaction"] = pending

        return jsonify({
            "reply": f"Please confirm: ₹{pending['amount']:.2f} for {pending['description']} belongs to {category}. Should I save it?",
            "needs_confirmation": True
        })

    # Read transaction amount
    amount_match = re.search(r'\d+(?:\.\d{1,2})?', message)

    if not amount_match:
        return jsonify({
            "reply": "Please tell me the transaction amount and what it was for."
        })

    amount = float(amount_match.group())

    if amount <= 0:
        return jsonify({
            "reply": "Please enter an amount greater than zero."
        })

    # Detect transaction type
    transaction_type = find_transaction_type(message)

    # Income does not need an expense category
    if transaction_type == "Income":
        category = "Income"

        pending = {
            "amount": amount,
            "description": message,
            "category": category,
            "transaction_type": "Income",
            "needs_category": False
        }

        session["pending_transaction"] = pending

        return jsonify({
            "reply": f"I detected an income of ₹{amount:.2f}. Should I save it?",
            "needs_confirmation": True
        })

    # Expense category detection
    category = find_category(message)

    pending = {
        "amount": amount,
        "description": message,
        "category": category,
        "transaction_type": "Expense",
        "needs_category": category is None
    }

    session["pending_transaction"] = pending

    if category is None:
        return jsonify({
            "reply": f"I found an expense of ₹{amount:.2f}, but I'm not sure which category it belongs to. Please tell me the category."
        })

    return jsonify({
        "reply": f"You spent ₹{amount:.2f} on {message}. I suggest the category {category}. Should I save this transaction?",
        "needs_confirmation": True
    })


# Confirm or cancel transaction

@app.route("/confirm", methods=["POST"])
def confirm():
    data = request.get_json()
    confirmed = data.get("confirmed", False)

    pending = session.get("pending_transaction")

    if not pending:
        return jsonify({
            "reply": "There is no pending transaction to confirm."
        })

    if confirmed:
        transaction_type = pending.get("transaction_type", "Expense")

        add_transaction(
            transaction_type,
            pending["amount"],
            pending["category"],
            pending["description"]
        )

        reply = "Your transaction has been confirmed and saved successfully!"

        # Check budget only for expenses
        if transaction_type == "Expense":
            budget_list = get_budgets()

            for budget in budget_list:
                if budget["category"].lower() == pending["category"].lower():

                    percentage = budget["percentage"]

                    if percentage >= 100:
                        reply += (
                            f" Budget exceeded! You have spent "
                            f"₹{budget['spent']:.2f} out of "
                            f"₹{budget['amount']:.2f} "
                            f"for {budget['category']}."
                        )

                    elif percentage >= 80:
                        reply += (
                            f" Budget alert! You have used "
                            f"{percentage:.0f}% of your "
                            f"{budget['category']} budget."
                        )

                    break

        session.pop("pending_transaction", None)

        return jsonify({
            "reply": reply
        })

    session.pop("pending_transaction", None)

    return jsonify({
        "reply": "Transaction cancelled. Nothing was saved."
    })


# UPI Simulator page
@app.route("/upi-simulator")
def upi_simulator():
    return render_template("upi_simulator.html")


# Simulated UPI payment
@app.route("/simulate_upi", methods=["POST"])
def simulate_upi():
    data = request.get_json()

    receiver = data.get("receiver", "").strip()

    try:
        amount = float(data.get("amount", 0))
    except (ValueError, TypeError):
        amount = 0

    transaction_id = data.get("transaction_id", "").strip()

    if not receiver or not transaction_id or amount <= 0:
        return jsonify({
            "reply": "Please enter valid payment details."
        }), 400

    category = find_category(receiver)

    pending = {
        "amount": amount,
        "description": f"UPI payment to {receiver} (ID: {transaction_id})",
        "category": category,
        "transaction_type": "Expense",
        "needs_category": category is None
    }

    session["pending_transaction"] = pending

    if category is None:
        return jsonify({
            "reply": f"Payment of ₹{amount:.2f} to {receiver} detected. Which category does it belong to?",
            "needs_category": True
        })

    return jsonify({
        "reply": f"Payment of ₹{amount:.2f} to {receiver} detected. Suggested category: {category}. Should I save this transaction?",
        "needs_confirmation": True
    })


# Accept category for unknown UPI receiver
@app.route("/upi-category", methods=["POST"])
def upi_category():
    data = request.get_json()
    category = data.get("category", "").strip()

    pending = session.get("pending_transaction")

    if not pending or not pending.get("needs_category"):
        return jsonify({
            "reply": "No pending UPI transaction found."
        })

    if not category:
        return jsonify({
            "reply": "Please enter a category."
        })

    pending["category"] = category.title()
    pending["needs_category"] = False

    session["pending_transaction"] = pending

    return jsonify({
        "reply": f"You selected {category.title()} for {pending['description']}. Should I save this transaction?",
        "needs_confirmation": True
    })


# Transactions page
@app.route("/transactions")
def transactions():
    records = get_transactions()
    return render_template("transactions.html", transactions=records)


# Dashboard page
@app.route("/dashboard")
def dashboard():
    total_expenses, total_income, balance, category_data = get_dashboard_summary()

    return render_template(
        "dashboard.html",
        total_expenses=total_expenses,
        total_income=total_income,
        balance=balance,
        category_data=category_data
    )


# Budget Management page
@app.route("/budgets")
def budgets():
    budget_list = get_budgets()

    return render_template(
        "budgets.html",
        budgets=budget_list
    )


# Save a new budget
@app.route("/add-budget", methods=["POST"])
def save_budget():
    category = request.form.get("category", "").strip()

    try:
        amount = float(request.form.get("amount", 0))
    except (ValueError, TypeError):
        amount = 0

    if not category or amount <= 0:
        return "Please enter a valid category and budget amount.", 400

    add_budget(category, amount)

    return redirect("/budgets")


if __name__ == "__main__":
    app.run(debug=True)

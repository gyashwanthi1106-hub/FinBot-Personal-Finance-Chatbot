
import sqlite3

# Connect to database
def connect_db():
    conn = sqlite3.connect("database/finbot.db")
    return conn


# Create database tables
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ChatHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()



# Add a transaction
def add_transaction(transaction_type, amount, category, description, transaction_date=None):
    conn = connect_db()
    cursor = conn.cursor()

    if transaction_date:
        cursor.execute("""
            INSERT INTO Transactions
            (transaction_type, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?)
        """, (transaction_type, amount, category, description, transaction_date))
    else:
        cursor.execute("""
            INSERT INTO Transactions
            (transaction_type, amount, category, description)
            VALUES (?, ?, ?, ?)
        """, (transaction_type, amount, category, description))

    conn.commit()
    conn.close()

    print("Transaction saved successfully!")

# View all saved transactions
def view_transactions():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Transactions")
    transactions = cursor.fetchall()

    for transaction in transactions:
        print(transaction)

    conn.close()


# Get transactions for the website
def get_transactions():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, transaction_type, amount, category, description, date
        FROM Transactions
        ORDER BY id DESC
    """)

    transactions = cursor.fetchall()
    conn.close()

    return transactions


# Get dashboard financial summary
def get_dashboard_summary():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUM(CASE WHEN transaction_type = 'Expense'
                THEN amount ELSE 0 END),
            SUM(CASE WHEN transaction_type = 'Income'
                THEN amount ELSE 0 END)
        FROM Transactions
    """)

    result = cursor.fetchone()

    total_expenses = result[0] or 0
    total_income = result[1] or 0
    balance = total_income - total_expenses

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM Transactions
        WHERE transaction_type = 'Expense'
        GROUP BY category
    """)

    category_data = cursor.fetchall()

    conn.close()

    return total_expenses, total_income, balance, category_data


# Add or update a budget
def add_budget(category, amount):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM Budgets
        WHERE category = ?
    """, (category,))

    existing_budget = cursor.fetchone()

    if existing_budget:
        cursor.execute("""
            UPDATE Budgets
            SET amount = ?
            WHERE category = ?
        """, (amount, category))
    else:
        cursor.execute("""
            INSERT INTO Budgets (category, amount)
            VALUES (?, ?)
        """, (category, amount))

    conn.commit()
    conn.close()


# Get budgets and calculate monthly spending
def get_budgets():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            Budgets.category,
            Budgets.amount,
            COALESCE(SUM(Transactions.amount), 0)
        FROM Budgets
        LEFT JOIN Transactions
            ON Budgets.category = Transactions.category
            AND Transactions.transaction_type = 'Expense'
            AND date(Transactions.date) >= date('now', 'start of month')
        GROUP BY Budgets.id
    """)

    rows = cursor.fetchall()
    conn.close()

    budgets = []

    for row in rows:
        category = row[0]
        amount = row[1]
        spent = row[2]

        remaining = amount - spent

        percentage = min((spent / amount) * 100, 100) if amount > 0 else 0

        budgets.append({
            "category": category,
            "amount": amount,
            "spent": spent,
            "remaining": remaining,
            "percentage": percentage
        })

    return budgets


# Check whether a transaction already exists
def transaction_exists(transaction_type, amount, description, transaction_date):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM Transactions
        WHERE transaction_type = ?
        AND amount = ?
        AND description = ?
        AND date(date) = date(?)
        LIMIT 1
    """, (transaction_type, amount, description, transaction_date))

    result = cursor.fetchone()
    conn.close()

    return result is not None

# Run database setup
if __name__ == "__main__":
    create_tables()
    print("FinBot database and tables created successfully!")

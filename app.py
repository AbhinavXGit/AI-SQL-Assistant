"""
AI SQL Assistant
A beginner-friendly natural-language interface for querying a sales database.

Run:
    python app.py

Example questions:
    Show total sales
    What are the top 5 products?
    Show the top 5 customers
    How many orders are there?
    Show sales by month
"""

import sqlite3
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

DB_PATH = Path(__file__).parent / "sales.db"

# Small training set for the intent classifier.
TRAINING_DATA = [
    ("show total sales", "total_sales"),
    ("what is the total revenue", "total_sales"),
    ("how much money did we make", "total_sales"),
    ("give me total sales", "total_sales"),

    ("show top products", "top_products"),
    ("what are the best selling products", "top_products"),
    ("which products sold the most", "top_products"),
    ("top 5 products", "top_products"),

    ("show top customers", "top_customers"),
    ("who are the biggest customers", "top_customers"),
    ("which customers spent the most", "top_customers"),
    ("top 5 customers", "top_customers"),

    ("how many orders are there", "order_count"),
    ("count all orders", "order_count"),
    ("number of orders", "order_count"),

    ("show sales by month", "monthly_sales"),
    ("monthly revenue", "monthly_sales"),
    ("sales for each month", "monthly_sales"),
    ("show monthly sales", "monthly_sales"),
]

SQL_TEMPLATES = {
    "total_sales": """
        SELECT ROUND(SUM(total_amount), 2) AS total_sales
        FROM orders;
    """,
    "top_products": """
        SELECT p.product_name,
               SUM(oi.quantity) AS units_sold,
               ROUND(SUM(oi.quantity * oi.unit_price), 2) AS sales
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY sales DESC
        LIMIT 5;
    """,
    "top_customers": """
        SELECT c.customer_name,
               ROUND(SUM(o.total_amount), 2) AS total_spent
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.customer_name
        ORDER BY total_spent DESC
        LIMIT 5;
    """,
    "order_count": """
        SELECT COUNT(*) AS order_count
        FROM orders;
    """,
    "monthly_sales": """
        SELECT strftime('%Y-%m', order_date) AS month,
               ROUND(SUM(total_amount), 2) AS sales
        FROM orders
        GROUP BY month
        ORDER BY month;
    """
}

def build_model():
    questions, intents = zip(*TRAINING_DATA)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
    X = vectorizer.fit_transform(questions)
    model = LogisticRegression(max_iter=1000)
    model.fit(X, intents)
    return vectorizer, model

def setup_database():
    if DB_PATH.exists():
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT,
        total_amount REAL,
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY(order_id) REFERENCES orders(order_id),
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    );
    """)

    customers = [
        (1, "Rahul Sharma"), (2, "Priya Singh"), (3, "Aman Verma"),
        (4, "Neha Das"), (5, "Rohan Gupta"), (6, "Sneha Roy")
    ]
    products = [
        (1, "Laptop"), (2, "Wireless Mouse"), (3, "Keyboard"),
        (4, "Headphones"), (5, "Monitor")
    ]
    orders = [
        (101, 1, "2026-01-05", 82000), (102, 2, "2026-01-12", 3500),
        (103, 3, "2026-02-02", 12500), (104, 1, "2026-02-18", 7800),
        (105, 4, "2026-03-03", 15000), (106, 5, "2026-03-17", 42000),
        (107, 2, "2026-04-07", 6800), (108, 6, "2026-04-19", 9200),
        (109, 3, "2026-05-11", 56000), (110, 5, "2026-05-23", 11000),
    ]
    items = [
        (1,101,1,1,80000), (2,101,2,1,2000),
        (3,102,4,1,3500), (4,103,3,2,2500), (5,103,2,1,7500),
        (6,104,2,2,2000), (7,104,3,1,3800),
        (8,105,5,1,15000), (9,106,1,1,42000),
        (10,107,4,2,3400), (11,108,2,2,1800), (12,108,3,1,5600),
        (13,109,1,1,56000), (14,110,5,1,11000)
    ]

    cur.executemany("INSERT INTO customers VALUES (?,?)", customers)
    cur.executemany("INSERT INTO products VALUES (?,?)", products)
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", items)

    conn.commit()
    conn.close()

def answer_question(question, vectorizer, model):
    X = vectorizer.transform([question])
    intent = model.predict(X)[0]
    confidence = max(model.predict_proba(X)[0])

    # Avoid confidently answering completely unrelated questions.
    if confidence < 0.30:
        return intent, confidence, None

    return intent, confidence, SQL_TEMPLATES[intent]

def print_results(cursor, rows):
    if not rows:
        print("No results found.")
        return

    columns = [d[0] for d in cursor.description]
    print("\n" + " | ".join(columns))
    print("-" * 60)
    for row in rows:
        print(" | ".join(str(value) for value in row))

def main():
    setup_database()
    vectorizer, model = build_model()

    print("=" * 60)
    print("AI SQL ASSISTANT")
    print("=" * 60)
    print("Ask questions about the sample sales database.")
    print("Type 'help' for examples or 'exit' to quit.")

    conn = sqlite3.connect(DB_PATH)

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            break

        if question.lower() == "help":
            print("\nExamples:")
            print("- Show total sales")
            print("- What are the top 5 products?")
            print("- Which customers spent the most?")
            print("- How many orders are there?")
            print("- Show sales by month")
            continue

        if not question:
            continue

        intent, confidence, sql = answer_question(question, vectorizer, model)

        print(f"\nDetected intent: {intent}")
        print(f"Confidence: {confidence:.2f}")

        if sql is None:
            print("Sorry, I don't understand that question yet.")
            continue

        print("\nGenerated SQL:")
        print(sql.strip())

        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            print("\nResult:")
            print_results(cursor, rows)
        except sqlite3.Error as error:
            print("Database error:", error)

    conn.close()
    print("Goodbye!")

if __name__ == "__main__":
    main()

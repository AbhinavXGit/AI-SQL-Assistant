# AI SQL Assistant

A beginner-friendly Python project that lets users ask simple questions about a sales database in natural language. A small TF-IDF + Logistic Regression model identifies the user's intent, selects a safe SQL template, executes the SQL query, and displays the result.

## Features

- Natural-language questions
- Simple ML-based intent classification
- Automatic SQL query selection
- SQLite sales database
- Query execution and result display
- Confidence score
- Basic error handling
- Sample sales data included

## Example questions

- Show total sales
- What are the top 5 products?
- Which customers spent the most?
- How many orders are there?
- Show sales by month

## Project workflow

```text
User Question
      ↓
Text Processing
      ↓
TF-IDF Vectorization
      ↓
Intent Classification
      ↓
SQL Template Selection
      ↓
Database Query
      ↓
Result
```

## Technologies

- Python
- SQL
- SQLite
- Scikit-learn
- TF-IDF
- Logistic Regression

## How to run

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd AI-SQL-Assistant
```

### 2. Create a virtual environment (optional)

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python app.py
```

The first run automatically creates `sales.db` with sample customers, products and orders.

## What I learned

- Connecting Python with a relational database
- Writing SQL queries for business questions
- Basic NLP text representation using TF-IDF
- Training a simple classification model
- Mapping user intent to SQL operations
- Handling database results and errors

## Future improvements

- Connect to MySQL
- Add more natural-language questions
- Add a web interface
- Use an LLM for more flexible SQL generation
- Add SQL validation and query safety checks

import os
import sqlite3
import pandas as pd

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "books.db")

SQL_QUERIES = {
    "Query 1 (SELECT, WHERE, ORDER BY, LIMIT) - Top 5 Most Expensive In-Stock Books": """
        SELECT title, price_gbp, price_inr, rating 
        FROM books 
        WHERE in_stock = 1 
        ORDER BY price_gbp DESC 
        LIMIT 5;
    """,
    
    "Query 2 (DISTINCT) - Distinct Star Ratings Present": """
        SELECT DISTINCT rating 
        FROM books 
        ORDER BY rating ASC;
    """,
    
    "Query 3 (BETWEEN, WHERE, ORDER BY) - Books Priced Between £20 and £40 with Rating >= 4": """
        SELECT title, price_gbp, rating 
        FROM books 
        WHERE price_gbp BETWEEN 20.00 AND 40.00 AND rating >= 4 
        ORDER BY rating DESC, price_gbp ASC 
        LIMIT 5;
    """,
    
    "Query 4 (IN, WHERE, ORDER BY) - Top Rated Books in Specific Categories": """
        SELECT title, rating, price_inr 
        FROM books 
        WHERE rating IN (4, 5) AND category_id IN (1, 2) 
        ORDER BY price_inr DESC 
        LIMIT 5;
    """,
    
    "Query 5 (JOIN) - Complete Relational Books and Category Information": """
        SELECT b.book_id, b.title, c.category_name, b.price_gbp, b.price_inr, b.rating, b.in_stock
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        ORDER BY b.book_id ASC;
    """
}


def get_connection(db_path=DEFAULT_DB_PATH):
    """
    Establishes and returns a SQLite database connection with foreign keys enabled.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn):
    """
    Creates the normalized relational tables (categories and books) if they do not exist.
    """
    cursor = conn.cursor()
    
    # 1. Categories Parent Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    );
    """)
    
    # 2. Books Child Table with Foreign Key
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price_gbp REAL NOT NULL,
        price_inr REAL NOT NULL,
        rating INTEGER NOT NULL,
        in_stock INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );
    """)
    
    conn.commit()


def save_to_database(df_clean, db_path=DEFAULT_DB_PATH):
    """
    Inserts clean DataFrame rows into the normalized categories and books tables.
    """
    conn = get_connection(db_path)
    init_db(conn)
    cursor = conn.cursor()
    
    # 1. Insert unique categories
    unique_categories = df_clean["category"].unique()
    for cat in unique_categories:
        cursor.execute("INSERT OR IGNORE INTO categories (category_name) VALUES (?)", (cat,))
    conn.commit()
    
    # 2. Map category_name -> category_id
    cursor.execute("SELECT category_name, category_id FROM categories")
    category_id_map = dict(cursor.fetchall())
    
    # 3. Clear existing books and batch insert new records
    cursor.execute("DELETE FROM books")
    
    books_to_insert = [
        (
            row["title"],
            row["price_gbp"],
            row["price_inr"],
            row["rating"],
            1 if row["in_stock"] else 0,
            category_id_map[row["category"]]
        )
        for _, row in df_clean.iterrows()
    ]
    
    cursor.executemany("""
        INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, books_to_insert)
    
    conn.commit()
    conn.close()
    print(f"[OK] Stored {len(books_to_insert)} books and {len(unique_categories)} categories in SQLite DB ('{db_path}').")


def verify_pandas_merge_equivalence(conn):
    """
    Demonstrates that the SQL JOIN and pure pandas pd.merge() produce identical results.
    """
    # 1. SQL JOIN
    df_sql = pd.read_sql(SQL_QUERIES["Query 5 (JOIN) - Complete Relational Books and Category Information"], conn)
    
    # 2. pd.merge()
    df_books = pd.read_sql("SELECT * FROM books", conn)
    df_categories = pd.read_sql("SELECT * FROM categories", conn)
    
    df_pandas = pd.merge(df_books, df_categories, on="category_id", how="inner")
    df_pandas = df_pandas[[
        "book_id", "title", "category_name", "price_gbp", "price_inr", "rating", "in_stock"
    ]].sort_values(by="book_id").reset_index(drop=True)
    
    is_equivalent = df_sql.equals(df_pandas)
    return is_equivalent, df_sql, df_pandas

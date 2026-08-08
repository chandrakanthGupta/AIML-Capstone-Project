import os
import sys

# Ensure the project src directory is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from scraper import scrape_all_target_categories
from cleaner import clean_books_dataframe
from database import (
    DEFAULT_DB_PATH,
    SQL_QUERIES,
    get_connection,
    save_to_database,
    verify_pandas_merge_equivalence,
)

TARGET_CATEGORIES = ["Mystery", "Historical Fiction", "Sequential Art"]


def export_sql_artifacts(conn, base_dir):
    """
    Exports SQL query definitions and execution outputs to their designated artifact files.
    """
    sql_dir = os.path.join(base_dir, "sql")
    outputs_dir = os.path.join(base_dir, "outputs")
    os.makedirs(sql_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    
    sql_file = os.path.join(sql_dir, "queries.sql")
    results_file = os.path.join(outputs_dir, "query_results.txt")
    
    # 1. Export queries.sql
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write("-- ==================================================\n")
        f.write("-- Zepto Data & AI Platform - Data Pipeline Queries\n")
        f.write("-- Normalized SQLite Database: books.db\n")
        f.write("-- ==================================================\n\n")
        for name, sql in SQL_QUERIES.items():
            f.write(f"-- {name}\n")
            f.write(sql.strip() + "\n\n")
    print(f"[+] Saved SQL queries to: {sql_file}")
    
    # 2. Export query_results.txt
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM books")
    book_count = cursor.fetchone()[0]
    
    is_equivalent, _, _ = verify_pandas_merge_equivalence(conn)
    
    with open(results_file, "w", encoding="utf-8") as f:
        f.write("====================================================\n")
        f.write("ZEPTO DATA & AI PLATFORM - SQL QUERY RESULTS OUTPUT\n")
        f.write(f"Total Categories: {cat_count} | Total Books: {book_count}\n")
        f.write("====================================================\n\n")
        
        for name, sql in SQL_QUERIES.items():
            f.write(f"----------------------------------------------------\n")
            f.write(f"Query: {name}\n")
            f.write(f"----------------------------------------------------\n")
            f.write(f"SQL Query:\n{sql.strip()}\n\nResults:\n")
            cursor.execute(sql)
            results = cursor.fetchall()
            for r in results:
                f.write(f"{r}\n")
            f.write(f"\n[Total Rows: {len(results)}]\n\n")
            
        f.write("====================================================\n")
        f.write(f"Pandas vs SQL Equivalence Verification: {is_equivalent}\n")
        f.write("====================================================\n")
        
    print(f"[+] Saved query results output to: {results_file}")


def run_pipeline():
    """
    Executes the full end-to-end data pipeline:
    Scrape -> Clean -> Load Database -> Execute & Export Queries -> Verify Equivalence
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    print("==========================================================")
    print("STARTING ZEPTO DATA PIPELINE (END-TO-END EXECUTION)")
    print("==========================================================")
    
    # Step 1: Web Scraping
    print("\n[STEP 1/4] Web Scraping from books.toscrape.com...")
    raw_books = scrape_all_target_categories(TARGET_CATEGORIES)
    print(f"[OK] Scraping completed. Total raw records scraped: {len(raw_books)}")
    
    # Step 2: Data Cleaning & Transformation
    print("\n[STEP 2/4] Cleaning Data & Performing Currency Conversion (1 GBP = 105.50 INR)...")
    df_clean = clean_books_dataframe(raw_books)
    print(f"[OK] Cleaning completed. Cleaned DataFrame shape: {df_clean.shape}")
    
    # Step 3: Database Loading
    print("\n[STEP 3/4] Initializing Normalized Database & Inserting Records...")
    db_path = os.path.join(base_dir, "data", "books.db")
    save_to_database(df_clean, db_path)
    
    # Step 4: SQL Execution & Pandas Verification
    print("\n[STEP 4/4] Executing SQL Queries and Verifying Pandas Equivalence...")
    conn = get_connection(db_path)
    is_equivalent, _, _ = verify_pandas_merge_equivalence(conn)
    print(f"[OK] Equivalence check (SQL JOIN == pd.merge()): {is_equivalent}")
    
    # Export artifacts
    export_sql_artifacts(conn, base_dir)
    conn.close()
    
    print("\n==========================================================")
    print("DATA PIPELINE EXECUTED SUCCESSFULLY END-TO-END!")
    print("==========================================================")


if __name__ == "__main__":
    run_pipeline()

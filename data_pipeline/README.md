# Zepto Data & AI Platform — Data Pipeline Module (25 Marks)

## 1. Module Overview
The **Data Pipeline** is the foundational data engineering module of the Zepto Data & AI Platform. It implements an automated, robust end-to-end Extract-Transform-Load (ETL) pipeline that scrapes raw e-commerce catalog data, cleans and standardizes it, applies fixed currency conversions, stores the relational data in a normalized SQLite database, and provides analytical SQL queries with pandas verification.

```
┌─────────────────────────┐
│   books.toscrape.com    │
└────────────┬────────────┘
             │ (requests + BeautifulSoup)
             ▼
┌─────────────────────────┐
│   Raw Scraped Records   │ (≥60 books across ≥3 categories)
└────────────┬────────────┘
             │ (cleaner.py: regex, type casting, median imputation)
             ▼
┌─────────────────────────┐
│    Cleaned DataFrame    │ (GBP to INR conversion: 1 GBP = 105.50 INR)
└────────────┬────────────┘
             │ (database.py: relational normalization)
             ▼
┌─────────────────────────┐
│    SQLite Database      │ (categories [PK] ──< books [FK])
└────────────┬────────────┘
             │ (SQL execution + pandas verification)
             ▼
┌─────────────────────────┐
│ SQL Queries & pd.merge  │ (Proved 100% equivalent to SQL JOIN)
└─────────────────────────┘
```

---

## 2. Directory Structure
```
data_pipeline/
├── README.md                 <- Comprehensive module documentation
├── requirements.txt          <- Python dependency specifications
├── pipeline_sandbox.ipynb    <- Interactive development & exploration notebook
│
├── src/
│   ├── scraper.py            <- Web scraping logic with rate limiting & pagination
│   ├── cleaner.py            <- Data transformation, validation & median imputation
│   ├── database.py           <- SQLite schema management, batch insertion & queries
│   └── pipeline.py           <- Master orchestration script running pipeline end-to-end
│
├── sql/
│   └── queries.sql           <- 5 formatted SQL queries demonstrating core keywords
│
├── data/
│   └── books.db              <- Normalized SQLite database (categories & books)
│
└── outputs/
    └── query_results.txt     <- Complete output text of executed SQL queries & verification
```

---

## 3. Installation & Setup

### Prerequisites
* Python 3.10+
* Active virtual environment (`.venv`)

### Install Dependencies
Activate your virtual environment and install the required packages:
```powershell
pip install -r data_pipeline/requirements.txt
```

---

## 4. How to Run the Pipeline

### Option A: Run the End-to-End Pipeline (Recommended)
Run the automated pipeline script from the project root:
```powershell
python data_pipeline/src/pipeline.py
```
This single command automatically:
1. Scrapes $\ge 60$ books across 3 target categories (`Mystery`, `Historical Fiction`, `Sequential Art`).
2. Cleans raw fields, sets schema types, and calculates INR pricing.
3. Initializes the normalized SQLite database at `data_pipeline/data/books.db`.
4. Inserts all normalized records with foreign key constraints.
5. Executes the 5 analytical SQL queries and generates `queries.sql` and `query_results.txt`.
6. Validates equivalence between SQL `JOIN` and `pd.merge()`.

### Option B: Interactive Notebook
Open `data_pipeline/pipeline_sandbox.ipynb` in VS Code or Jupyter Lab and run all cells sequentially to explore data and see visual outputs interactively.

---

## 5. Data Cleaning & Transformation Decisions

| Field | Raw Source Format | Cleaned Target Format | Target Type | Transformation Decision / Logic |
| :--- | :--- | :--- | :--- | :--- |
| **`title`** | `<h3><a title="...">` | Untruncated string | `str` | Extracted from the `title` HTML attribute rather than inner text to prevent truncated strings ending in `...`. |
| **`price_gbp`** | e.g. `'£51.77'` | `51.77` | `float` | Regex pattern `[\d.]+` strips currency symbols (`£`) and encoding artifacts. Missing numeric values are imputed using the column **median**. |
| **`price_inr`** | Computed | e.g. `5461.74` | `float` | Calculated using the strict required fixed exchange rate: **`1 GBP = 105.50 INR`** (`price_inr = round(price_gbp * 105.50, 2)`). |
| **`rating`** | e.g. `'Three'` | `3` | `int` | Mapped via lookup dictionary: `{'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}`. Missing ratings default to median rating. |
| **`in_stock`** | e.g. `'In stock (22 available)'`| `True` / `False` | `bool` | Case-insensitive substring match for `"in stock"` converts textual availability to boolean flags (`1`/`0` in SQLite). |
| **`category`** | Sidebar item | Normalized category ID | `int (FK)` | Relational normalization: category string is stored uniquely in `categories` table and referenced via foreign key `category_id`. |

---

## 6. Database Schema & Normalization

The SQLite database (`books.db`) is normalized into **3NF (Third Normal Form)** with foreign keys enabled (`PRAGMA foreign_keys = ON;`):

### 1. `categories` Table (Parent Table)
```sql
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
);
```

### 2. `books` Table (Child Table)
```sql
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
```

---

## 7. SQL Queries & Requirements Coverage

The project implements 5 analytical SQL queries covering all required SQL syntax:

1. **Query 1 (SELECT, WHERE, ORDER BY, LIMIT):**
   * *Purpose:* Identifies the top 5 most expensive in-stock books.
   ```sql
   SELECT title, price_gbp, price_inr, rating 
   FROM books 
   WHERE in_stock = 1 
   ORDER BY price_gbp DESC 
   LIMIT 5;
   ```
2. **Query 2 (DISTINCT):**
   * *Purpose:* Lists all unique star rating values present in the catalog.
   ```sql
   SELECT DISTINCT rating 
   FROM books 
   ORDER BY rating ASC;
   ```
3. **Query 3 (BETWEEN, WHERE, ORDER BY):**
   * *Purpose:* Filters books in the mid-range price bracket (£20.00 – £40.00) with rating $\ge 4$.
   ```sql
   SELECT title, price_gbp, rating 
   FROM books 
   WHERE price_gbp BETWEEN 20.00 AND 40.00 AND rating >= 4 
   ORDER BY rating DESC, price_gbp ASC 
   LIMIT 5;
   ```
4. **Query 4 (IN, WHERE, ORDER BY):**
   * *Purpose:* Retrieves high-rated books (rating 4 or 5) belonging to specific category IDs.
   ```sql
   SELECT title, rating, price_inr 
   FROM books 
   WHERE rating IN (4, 5) AND category_id IN (1, 2) 
   ORDER BY price_inr DESC 
   LIMIT 5;
   ```
5. **Query 5 (JOIN):**
   * *Purpose:* Performs an `INNER JOIN` between `books` and `categories` on `category_id`.
   ```sql
   SELECT b.book_id, b.title, c.category_name, b.price_gbp, b.price_inr, b.rating, b.in_stock
   FROM books b
   JOIN categories c ON b.category_id = c.category_id
   ORDER BY b.book_id ASC;
   ```

---

## 8. Pandas Integration & `pd.merge()` Equivalence Proof
* Results of SQL queries are loaded directly into pandas DataFrames via `pd.read_sql()`.
* The relational SQL `JOIN` is independently reproduced in pure pandas using:
  ```python
  df_pandas_merged = pd.merge(df_books, df_categories, on="category_id", how="inner")
  ```
* Automated verification (`df_sql.equals(df_pandas_merged)`) confirms that the pandas merge produces output **100% identical** to the relational database `JOIN`.

---

## 9. Acceptance Checklist Verification

- [x] $\ge 60$ books scraped (133 books scraped across 3 categories)
- [x] $\ge 3$ categories scraped (`Mystery`, `Historical Fiction`, `Sequential Art`)
- [x] `requests` and `BeautifulSoup` used with rate limiting
- [x] All 5 required raw fields extracted (`title`, `price`, `star_rating`, `availability`, `category`)
- [x] `price_gbp` converted to `float`
- [x] `rating` converted to `integer` ($1$ to $5$)
- [x] `in_stock` converted to `boolean`
- [x] `price_inr` computed with fixed conversion ($1\text{ GBP} = 105.50\text{ INR}$)
- [x] Missing data handled with median imputation
- [x] Normalized SQLite database created (`categories` & `books`) with PK/FK constraints
- [x] 5 SQL queries demonstrating `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT`, `IN`, `BETWEEN`, `JOIN`
- [x] `pd.read_sql()` utilized
- [x] `pd.merge()` vs SQL `JOIN` equivalence proven
- [x] Standalone artifacts generated (`sql/queries.sql`, `outputs/query_results.txt`)
- [x] Pipeline executes end-to-end with a single command

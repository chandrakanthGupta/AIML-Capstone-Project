-- ==================================================
-- Zepto Data & AI Platform - Data Pipeline Queries
-- Normalized SQLite Database: books.db
-- ==================================================

-- Query 1 (SELECT, WHERE, ORDER BY, LIMIT) - Top 5 Most Expensive In-Stock Books
SELECT title, price_gbp, price_inr, rating 
        FROM books 
        WHERE in_stock = 1 
        ORDER BY price_gbp DESC 
        LIMIT 5;

-- Query 2 (DISTINCT) - Distinct Star Ratings Present
SELECT DISTINCT rating 
        FROM books 
        ORDER BY rating ASC;

-- Query 3 (BETWEEN, WHERE, ORDER BY) - Books Priced Between £20 and £40 with Rating >= 4
SELECT title, price_gbp, rating 
        FROM books 
        WHERE price_gbp BETWEEN 20.00 AND 40.00 AND rating >= 4 
        ORDER BY rating DESC, price_gbp ASC 
        LIMIT 5;

-- Query 4 (IN, WHERE, ORDER BY) - Top Rated Books in Specific Categories
SELECT title, rating, price_inr 
        FROM books 
        WHERE rating IN (4, 5) AND category_id IN (1, 2) 
        ORDER BY price_inr DESC 
        LIMIT 5;

-- Query 5 (JOIN) - Complete Relational Books and Category Information
SELECT b.book_id, b.title, c.category_name, b.price_gbp, b.price_inr, b.rating, b.in_stock
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        ORDER BY b.book_id ASC;


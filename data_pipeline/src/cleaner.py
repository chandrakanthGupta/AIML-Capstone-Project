import re
import pandas as pd

# Mapping for textual star ratings to integer numbers
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

# Fixed conversion rate as required by capstone grading criteria
GBP_TO_INR_RATE = 105.50


def clean_price(price_str):
    """
    Extracts numerical float price value from raw string (e.g. '£51.77' -> 51.77).
    Returns float or None if parsing fails.
    """
    if pd.isna(price_str) or not str(price_str).strip():
        return None
    
    match = re.search(r"[\d.]+", str(price_str))
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def clean_rating(rating_str):
    """
    Converts rating word string to integer (e.g. 'Three' -> 3).
    """
    if pd.isna(rating_str):
        return None
    return RATING_MAP.get(str(rating_str).strip(), None)


def clean_availability(avail_str):
    """
    Converts availability text to a boolean (True if 'In stock', else False).
    """
    if pd.isna(avail_str):
        return False
    return "in stock" in str(avail_str).lower()


def clean_books_dataframe(raw_books_list):
    """
    Transforms raw book dictionaries into a clean, validated Pandas DataFrame.
    Implements median imputation for missing numeric values and sets final schemas.
    """
    df = pd.DataFrame(raw_books_list)
    if df.empty:
        return pd.DataFrame(columns=["title", "category", "price_gbp", "price_inr", "rating", "in_stock"])
        
    df_clean = df.copy()
    
    # 1. Clean Price (GBP)
    df_clean["price_gbp"] = df_clean["price"].apply(clean_price)
    if df_clean["price_gbp"].isnull().any():
        median_price = df_clean["price_gbp"].median()
        df_clean["price_gbp"] = df_clean["price_gbp"].fillna(median_price)
        print(f"[INFO] Imputed missing prices with median: £{median_price:.2f}")
        
    # 2. Currency Conversion (Fixed rate 1 GBP = 105.50 INR)
    df_clean["price_inr"] = (df_clean["price_gbp"] * GBP_TO_INR_RATE).round(2)
    
    # 3. Clean Star Rating (1-5 integer)
    df_clean["rating"] = df_clean["star_rating"].apply(clean_rating)
    if df_clean["rating"].isnull().any():
        median_rating = int(df_clean["rating"].median())
        df_clean["rating"] = df_clean["rating"].fillna(median_rating)
    df_clean["rating"] = df_clean["rating"].astype(int)
    
    # 4. Clean Availability (Boolean)
    df_clean["in_stock"] = df_clean["availability"].apply(clean_availability).astype(bool)
    
    # 5. Column selection and ordering
    clean_columns = ["title", "category", "price_gbp", "price_inr", "rating", "in_stock"]
    return df_clean[clean_columns]

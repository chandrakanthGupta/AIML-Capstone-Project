# ==============================================================================
# Zepto Data & AI Platform - Analytics Module
# Part A: Exploratory Data Analysis (EDA) Script
# ==============================================================================

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# ------------------------------------------------------------------------------
# 1. Data Ingestion & Offline Fallback Setup
# ------------------------------------------------------------------------------
CSV_PATH = "titanic.csv"

# Load from Seaborn or use the local offline fallback if it exists
if not os.path.exists(CSV_PATH):
    print("🌐 Fetching Titanic dataset from Seaborn network cache...")
    df_raw = sns.load_dataset('titanic')
    df_raw.to_csv(CSV_PATH, index=False)
    print(f"✅ Raw dataset saved locally: {CSV_PATH}")
else:
    print(f"📁 Loading dataset directly from local CSV: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)
print(f"Dataset Shape: {df.shape}\n")


# ------------------------------------------------------------------------------
# 2. Profiling & Missing Values Analysis
# ------------------------------------------------------------------------------
print("📝 Dataset Info:")
df.info()

print("\n📈 Dataset Summary Statistics:")
print(df.describe(include='all'))

print("\n⚠️ Missing Values percentages:")
missing_percentages = (df.isnull().sum() / len(df)) * 100
missing_cols = missing_percentages[missing_percentages > 0].sort_values(ascending=False)
for col, pct in missing_cols.items():
    print(f" - '{col}': {pct:.2f}% missing")


# ------------------------------------------------------------------------------
# 3. Missing Value Cleaning (Applying Threshold Rules)
# ------------------------------------------------------------------------------
# - embarked & embark_town: 0.22% missing (under 5% -> drop rows)
df.dropna(subset=['embarked', 'embark_town'], inplace=True)

# - age: 19.87% missing (5% to 30% -> impute with median)
median_age = df['age'].median()
df['age'] = df['age'].fillna(median_age)

# - deck: 77.22% missing (above 30% -> drop column entirely)
df.drop(columns=['deck'], inplace=True)

print("\n✅ Cleaned Missing Values.")
print(f"New Dataset Shape: {df.shape}")


# ------------------------------------------------------------------------------
# 4. Univariate Analysis (Outliers & Skewness)
# ------------------------------------------------------------------------------
def compute_iqr_outliers(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    return len(outliers), lower_bound, upper_bound

age_outliers, age_low, age_high = compute_iqr_outliers(df['age'])
fare_outliers, fare_low, fare_high = compute_iqr_outliers(df['fare'])

print(f"\n📌 Outlier Counts (IQR Rule):")
print(f" - 'age': {age_outliers} outliers")
print(f" - 'fare': {fare_outliers} outliers")

print(f"\n📌 Fare Central Tendency:")
print(f" - Mean:   {df['fare'].mean():.4f}")
print(f" - Median: {df['fare'].median():.4f}")
print(f" - Mode:   {df['fare'].mode()[0]:.4f}")


# ------------------------------------------------------------------------------
# 5. Bivariate Analysis (Survival rates & Correlation)
# ------------------------------------------------------------------------------
print("\n📌 Survival Rate by Sex:")
print(df.groupby('sex')['survived'].mean())

print("\n📌 Survival Rate by Passenger Class (Pclass):")
print(df.groupby('pclass')['survived'].mean())

print("\n📌 Survival Rate by Sex & Class (Boolean Masking):")
for sex in ['female', 'male']:
    for pclass in [1, 2, 3]:
        mask = (df['sex'] == sex) & (df['pclass'] == pclass)
        rate = df[mask]['survived'].mean()
        print(f" - {sex.title()}, Class {pclass}: {rate:.4f}")

# 6x6 Correlation Matrix (Numeric Columns only)
corr_cols = ['survived', 'pclass', 'age', 'sibsp', 'parch', 'fare']
corr_matrix = df[corr_cols].corr()
print("\n📌 6x6 Correlation Matrix:")
print(corr_matrix)


# ------------------------------------------------------------------------------
# 6. Exploratory Standardization check (Z-Score)
# ------------------------------------------------------------------------------
scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[['age', 'fare']] = scaler.fit_transform(df[['age', 'fare']])

print("\n📊 Standardization Statistics Check:")
print("Original Stats:")
print(df[['age', 'fare']].describe().loc[['mean', 'std']])
print("\nStandardized Stats (Z-Score):")
print(df_scaled[['age', 'fare']].describe().loc[['mean', 'std']])

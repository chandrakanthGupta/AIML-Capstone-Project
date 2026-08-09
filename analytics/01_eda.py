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
print("==================================================")
print(f"📊 DATASET SHAPE: {df.shape}")
print("==================================================\n")

print("📝 DATASET INFO:")
df.info()

print("\n==================================================")
print("📈 DATASET STATISTICAL SUMMARY:")
print("==================================================")
print(df.describe(include='all'))

print("\n==================================================")
print("⚠️ MISSING VALUES (Percentage per column):")
print("==================================================")
missing_percentages = (df.isnull().sum() / len(df)) * 100
missing_cols = missing_percentages[missing_percentages > 0].sort_values(ascending=False)
for col, pct in missing_cols.items():
    print(f" - '{col}': {pct:.2f}% missing")


# ------------------------------------------------------------------------------
# 3. Missing Value Cleaning (Applying Threshold Rules)
# ------------------------------------------------------------------------------
# Justification:
# - embarked & embark_town: 0.22% missing (under 5% -> drop rows)
# - age: 19.87% missing (5% to 30% -> impute with median)
# - deck: 77.22% missing (above 30% -> drop column entirely)

df.dropna(subset=['embarked', 'embark_town'], inplace=True)
median_age = df['age'].median()
df['age'] = df['age'].fillna(median_age)
df.drop(columns=['deck'], inplace=True)

print("\n✅ Missing values successfully handled!")
print(f"📊 Cleaned Dataset Shape: {df.shape}")
print(f"⚠️ Remaining missing values: {df.isnull().sum().sum()}")


# ------------------------------------------------------------------------------
# 4. Univariate Analysis (Outliers & Skewness)
# ------------------------------------------------------------------------------
# A. Visual Distributions Plotting
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Age Distributions
sns.histplot(df['age'], kde=True, ax=axes[0, 0], color='skyblue')
axes[0, 0].set_title('Age Distribution (Histogram)')
sns.boxplot(x=df['age'], ax=axes[0, 1], color='lightgreen')
axes[0, 1].set_title('Age Box Plot (Outliers)')

# Fare Distributions
sns.histplot(df['fare'], kde=True, ax=axes[1, 0], color='salmon')
axes[1, 0].set_title('Fare Distribution (Histogram)')
sns.boxplot(x=df['fare'], ax=axes[1, 1], color='gold')
axes[1, 1].set_title('Fare Box Plot (Outliers)')

plt.tight_layout()
plt.show()

# B. Outlier Calculation Functions & Metrics
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

print("\n==================================================")
print("📌 OUTLIER REPORT (IQR Rule)")
print("==================================================")
print(f" - 'age': {age_outliers} outliers (outside [{age_low:.2f}, {age_high:.2f}])")
print(f" - 'fare': {fare_outliers} outliers (outside [{fare_low:.2f}, {fare_high:.2f}])")

print("\n==================================================")
print("📌 FARE CENTRAL TENDENCY")
print("==================================================")
print(f" - Mean:   {df['fare'].mean():.4f}")
print(f" - Median: {df['fare'].median():.4f}")
print(f" - Mode:   {df['fare'].mode()[0]:.4f}")


# ------------------------------------------------------------------------------
# 5. Bivariate Analysis (Survival rates & Correlation Heatmap)
# ------------------------------------------------------------------------------
print("\n==================================================")
print("📌 SURVIVAL RATE BY SEX")
print("==================================================")
print(df.groupby('sex')['survived'].mean())

print("\n==================================================")
print("📌 SURVIVAL RATE BY PCLASS")
print("==================================================")
print(df.groupby('pclass')['survived'].mean())

print("\n==================================================")
print("📌 SURVIVAL RATE BY SEX & PCLASS (BOOLEAN MASKING)")
print("==================================================")
for sex in ['female', 'male']:
    for pclass in [1, 2, 3]:
        mask = (df['sex'] == sex) & (df['pclass'] == pclass)
        subset = df[mask]
        rate = subset['survived'].mean()
        print(f" - {sex.title()}, Pclass {pclass}: {rate:.4f} (Total: {len(subset)})")

# 6x6 Correlation Matrix Plotting (Numeric Columns only)
corr_cols = ['survived', 'pclass', 'age', 'sibsp', 'parch', 'fare']
corr_matrix = df[corr_cols].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".4f", vmin=-1, vmax=1, square=True)
plt.title('6x6 Correlation Heatmap')
plt.show()


# ------------------------------------------------------------------------------
# 6. Multivariate Data Story (4 Survival Charts)
# ------------------------------------------------------------------------------
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Chart 1: Survival Rate by Passenger Class & Sex
sns.barplot(x="pclass", y="survived", hue="sex", data=df, ax=axes[0, 0], errorbar=None, palette="muted")
axes[0, 0].set_title("1. Survival Rate by Passenger Class & Sex")
axes[0, 0].set_ylabel("Survival Rate")
axes[0, 0].set_xlabel("Passenger Class")

# Chart 2: Age Distribution of Survivors vs Non-Survivors by Sex
sns.violinplot(x="survived", y="age", hue="sex", data=df, split=True, ax=axes[0, 1], palette="pastel")
axes[0, 1].set_title("2. Age Distribution by Survival Status & Sex")
axes[0, 1].set_xticklabels(["Died", "Survived"])
axes[0, 1].set_ylabel("Age")

# Chart 3: Fare Distribution by Survival Status
sns.boxplot(x="survived", y="fare", data=df, ax=axes[1, 0], palette="coolwarm", showfliers=False)
axes[1, 0].set_title("3. Fare Distribution of Survivors vs Non-Survivors")
axes[1, 0].set_xticklabels(["Died", "Survived"])
axes[1, 0].set_ylabel("Fare")

# Chart 4: Survival Rate by Family Size
df_temp = df.copy()
df_temp['family_size'] = df_temp['sibsp'] + df_temp['parch'] + 1
sns.barplot(x="family_size", y="survived", data=df_temp, ax=axes[1, 1], errorbar=None, color="salmon")
axes[1, 1].set_title("4. Survival Rate by Family Size")
axes[1, 1].set_xlabel("Family Size (SibSp + Parch + 1)")
axes[1, 1].set_ylabel("Survival Rate")

plt.tight_layout()
plt.show()


# ------------------------------------------------------------------------------
# 7. Exploratory Standardization Check (Z-Score Before/After)
# ------------------------------------------------------------------------------
scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[['age', 'fare']] = scaler.fit_transform(df[['age', 'fare']])

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Age Distributions Before vs After
sns.histplot(df['age'], kde=True, color='skyblue', ax=axes[0, 0])
axes[0, 0].set_title("Age Distribution (Before Standardization)")
axes[0, 0].set_xlabel("Original Age")

sns.histplot(df_scaled['age'], kde=True, color='blue', ax=axes[0, 1])
axes[0, 1].set_title("Age Distribution (After Standardization)")
axes[0, 1].set_xlabel("Z-Score")

# Fare Distributions Before vs After
sns.histplot(df['fare'], kde=True, color='salmon', ax=axes[1, 0])
axes[1, 0].set_title("Fare Distribution (Before Standardization)")
axes[1, 0].set_xlabel("Original Fare")

sns.histplot(df_scaled['fare'], kde=True, color='red', ax=axes[1, 1])
axes[1, 1].set_title("Fare Distribution (After Standardization)")
axes[1, 1].set_xlabel("Z-Score")

plt.tight_layout()
plt.show()

print("==================================================")
print("📊 NUMERICAL VERIFICATION (Mean & Std)")
print("==================================================")
print("BEFORE:")
print(df[['age', 'fare']].describe().loc[['mean', 'std']])
print("\nAFTER:")
print(df_scaled[['age', 'fare']].describe().loc[['mean', 'std']])

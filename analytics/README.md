# Zepto Data & AI Platform — Analytics Module

## 1. Data Profiling & Cleaning Decisions

### Missing Value Analysis & Strategies
* **`embarked` & `embark_town`** (0.22% missing): Dropped the rows containing missing values as the missingness is well under the 5% threshold.
* **`age`** (19.87% missing): Imputed missing values using the median age of the passengers, as the missingness is between 5% and 30%.
* **`deck`** (77.22% missing): Dropped the column entirely because a missing rate of over 70% makes imputation highly unreliable.

---

## 2. Univariate Analysis

### Outliers (IQR Rule)
* **`age`**: 66 outliers detected (passengers outside the range of 2.5 to 54.5 years).
* **`fare`**: 114 outliers detected (passengers paying higher than 65.63).

### Skewness of Fare
* **Metrics**: Mean (32.09) > Median (14.45) > Mode (8.05)
* **Conclusion**: The `fare` distribution is **right-skewed** (positively skewed) because the mean is heavily pulled upward by a few high-paying outliers, creating a long tail to the right.

---

## 3. Bivariate Analysis

### Survival Rate Breakdowns
* **By Sex**: Female passengers had a **74.04%** survival rate, compared to only **18.89%** for male passengers.
* **By Passenger Class**: Class 1 passengers had a **62.62%** survival rate, Class 2 had **47.28%**, and Class 3 had **24.24%**.
* **Combined (Sex & Pclass)**:
  * Female, Class 1: **96.77%**
  * Female, Class 2: **92.11%**
  * Female, Class 3: **50.00%**
  * Male, Class 1: **36.89%**
  * Male, Class 2: **15.74%**
  * Male, Class 3: **13.54%**

### Heatmap Correlation Interpretations
From the 6x6 correlation matrix, the two strongest off-diagonal correlations (by absolute value) are:
1. **`pclass` & `fare` (r = -0.5495)**: A strong negative correlation. This reflects that 1st class tickets (low class number) were significantly more expensive than 3rd class tickets (high class number).
2. **`sibsp` & `parch` (r = 0.4145)**: A moderate positive correlation. This indicates that passengers travelling with siblings/spouses were also highly likely to travel with parents/children, representing family units travelling together.

---

## 4. Multivariate Data Story (Survival Arguments)

### Chart 1: Survival Rate by Passenger Class & Sex
* **Interpretation**: This chart reveals that female passengers had a significantly higher survival rate across all classes compared to males. However, passenger class acted as a strong secondary predictor: 1st class females survived at nearly 97%, while 3rd class females dropped to 50%. Males in 1st class also survived at a much higher rate (37%) than males in 2nd and 3rd class (13-16%).

### Chart 2: Age Distribution by Survival Status & Sex
* **Interpretation**: The violin plot shows that young boys (under 10 years old) survived at a noticeably higher rate than adult males, which directly supports the historical "women and children first" evacuation protocol. For females, survival rates remained consistently high across almost all age brackets, whereas adult males faced extremely low survival rates regardless of age.

### Chart 3: Fare Distribution of Survivors vs Non-Survivors
* **Interpretation**: Passengers who survived generally paid significantly higher fares than those who perished, as shown by the shifted median and quartiles in the box plot. This confirms that socio-economic status was a major factor in evacuation priority, as higher-paying passengers had better access to lifeboats.

### Chart 4: Survival Rate by Family Size
* **Interpretation**: Passengers travelling alone (family size = 1) or in large families (family size $\ge$ 5) had low survival rates (under 30%). In contrast, passengers travelling in small family units of 2 to 4 people experienced the highest survival rates (between 50% and 70%), suggesting that small groups were more agile and successful during the evacuation.

---

## 5. Exploratory Standardization Check (Sanity Check)
Standardization using the z-score formula $z = \frac{x - \mu}{\sigma}$ was performed on the full dataset for `age` and `fare`:
* **Before**: 
  * `age`: Mean = 29.36, Std = 13.02
  * `fare`: Mean = 32.10, Std = 49.70
* **After**:
  * `age`: Mean $\approx$ 0.00, Std $\approx$ 1.00
  * `fare`: Mean $\approx$ 0.00, Std $\approx$ 1.00
* **Conclusion**: The transformation successfully center-scaled both numeric distributions.


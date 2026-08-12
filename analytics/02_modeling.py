# ==============================================================================
# Zepto Data & AI Platform - Analytics Module
# Part B: Predictive Modeling Script
# ==============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# ML Preprocessing & Pipeline imports
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Model imports
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression

# Evaluation Metric imports
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score
)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImblearnPipeline

# ------------------------------------------------------------------------------
# 1. Ingest Data from Cleaned CSV
# ------------------------------------------------------------------------------
CSV_PATH = "titanic.csv"
df = pd.read_csv(CSV_PATH)
print(f"✅ Cleaned dataset loaded. Shape: {df.shape}")


# ------------------------------------------------------------------------------
# 2. Stratified Train/Test Split
# ------------------------------------------------------------------------------
X = df.drop(columns=['survived', 'alive', 'embark_town'])
y = df['survived']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    stratify=y, 
    random_state=42
)
print("📌 Train/Test Stratified Split Done.")


# ------------------------------------------------------------------------------
# 3. Preprocessing ColumnTransformer
# ------------------------------------------------------------------------------
numeric_features = ['age', 'sibsp', 'parch', 'fare']
categorical_features = ['sex', 'embarked', 'pclass']

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', drop='first'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)
print("📌 ColumnTransformer Constructed.")


# ------------------------------------------------------------------------------
# 4. Train Classifiers
# ------------------------------------------------------------------------------
log_reg = LogisticRegression(random_state=42, max_iter=1000)
dec_tree = DecisionTreeClassifier(max_depth=3, random_state=42)
rand_forest = RandomForestClassifier(random_state=42, oob_score=True)

pipeline_lr = Pipeline(steps=[('preprocessor', preprocessor), ('estimator', log_reg)])
pipeline_dt = Pipeline(steps=[('preprocessor', preprocessor), ('estimator', dec_tree)])
pipeline_rf = Pipeline(steps=[('preprocessor', preprocessor), ('estimator', rand_forest)])

pipeline_lr.fit(X_train, y_train)
pipeline_dt.fit(X_train, y_train)
pipeline_rf.fit(X_train, y_train)
print("📌 Base Classifiers Trained.")


# ------------------------------------------------------------------------------
# 5. Evaluate Classifiers
# ------------------------------------------------------------------------------
def evaluate_model(pipeline, X_test, y_test):
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    return [acc, prec, rec, f1, auc]

lr_results = evaluate_model(pipeline_lr, X_test, y_test)
dt_results = evaluate_model(pipeline_dt, X_test, y_test)
rf_results = evaluate_model(pipeline_rf, X_test, y_test)

print("\nModel Comparison Matrix:")
print(f"Logistic Regression: {lr_results}")
print(f"Decision Tree:       {dt_results}")
print(f"Random Forest:       {rf_results}")


# ------------------------------------------------------------------------------
# 6. Imbalance Handling Comparison
# ------------------------------------------------------------------------------
pipeline_balanced = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('estimator', RandomForestClassifier(random_state=42, class_weight='balanced'))
])

pipeline_smote = ImblearnPipeline(steps=[
    ('preprocessor', preprocessor),
    ('smote', SMOTE(random_state=42)),
    ('estimator', RandomForestClassifier(random_state=42))
])

pipeline_balanced.fit(X_train, y_train)
pipeline_smote.fit(X_train, y_train)
print("📌 Imbalance Models Trained.")


# ------------------------------------------------------------------------------
# 7. GridSearchCV Hyperparameter Tuning (Random Forest)
# ------------------------------------------------------------------------------
param_grid = {
    'estimator__n_estimators': [50, 100, 150],
    'estimator__max_depth': [4, 6, 8],
    'estimator__max_features': ['sqrt', 'log2']
}

grid_search = GridSearchCV(
    estimator=pipeline_rf,
    param_grid=param_grid,
    cv=5,
    scoring='f1',
    n_jobs=-1
)
grid_search.fit(X_train, y_train)

best_pipeline = grid_search.best_estimator_
best_rf = best_pipeline.named_steps['estimator']
print(f"📌 Tuned RF Best Params: {grid_search.best_params_}")
print(f"📌 Tuned RF OOB Score:   {best_rf.oob_score_:.4f}")


# ------------------------------------------------------------------------------
# 8. Regression Side-Task (Fare Prediction)
# ------------------------------------------------------------------------------
y_train_reg = X_train['fare']
X_train_reg = X_train.drop(columns=['fare']).copy()
X_train_reg['survived'] = y_train

y_test_reg = X_test['fare']
X_test_reg = X_test.drop(columns=['fare']).copy()
X_test_reg['survived'] = y_test

numeric_features_reg = ['age', 'sibsp', 'parch']
categorical_features_reg = ['sex', 'embarked', 'pclass', 'survived']

preprocessor_reg = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features_reg),
        ('cat', categorical_transformer, categorical_features_reg)
    ]
)

pipeline_reg = Pipeline(steps=[
    ('preprocessor', preprocessor_reg),
    ('estimator', LinearRegression())
])
pipeline_reg.fit(X_train_reg, y_train_reg)

y_pred_reg = pipeline_reg.predict(X_test_reg)
mae = mean_absolute_error(y_test_reg, y_pred_reg)
r2 = r2_score(y_test_reg, y_pred_reg)
print(f"📌 Regression: MAE = {mae:.4f}, R2 = {r2:.4f}")


# ------------------------------------------------------------------------------
# 9. Model Serialization & Test Load
# ------------------------------------------------------------------------------
pipeline_filename = "best_pipeline.joblib"
joblib.dump(best_pipeline, pipeline_filename)
print("📌 Model Pipeline Serialized.")

loaded_pipeline = joblib.load(pipeline_filename)
print("📌 Model Pipeline Reloaded Successfully.")

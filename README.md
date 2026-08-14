# 🚀 Zepto Quick-Commerce AIML Capstone Project

Welcome to the **Zepto Quick-Commerce AIML Capstone Project**. This repository contains a production-ready, end-to-end machine learning and GenAI suite consisting of three integrated modules: an automated web scraping & data ingestion pipeline, an analytics & predictive machine learning pipeline, and an AI-powered customer support assistant service.

---

## 📁 Repository Structure

```text
AIML capstone project/
├── data_pipeline/               # Module 1: Automated Data Ingestion Pipeline (25 Marks)
│   ├── src/
│   │   ├── scraper.py          # News scraping & HTML extraction
│   │   ├── cleaner.py          # HTML stripping & text normalization
│   │   └── pipeline.py         # Orchestration & automated CSV logging
│   ├── tests/                  # Unit tests (pytest)
│   ├── .github/workflows/      # GitHub Actions CI/CD automation
│   ├── requirements.txt
│   └── README.md
│
├── analytics/                   # Module 2: Analytics & Machine Learning Pipeline (50 Marks)
│   ├── 01_eda.ipynb            # Interactive EDA & Profiling Notebook
│   ├── 01_eda.py               # Pure Python EDA script (Mobile Readable)
│   ├── 02_modeling.ipynb       # Modeling, Tuning & Heteroscedasticity Notebook
│   ├── 02_modeling.py          # Pure Python Modeling script (Mobile Readable)
│   ├── titanic.csv             # Cleaned offline dataset fallback
│   ├── best_pipeline.joblib    # Serialized scikit-learn ColumnTransformer + Model Pipeline
│   ├── requirements.txt
│   └── README.md
│
├── support_assistant/           # Module 3: GenAI Support Assistant Service (25 Marks)
│   ├── docs/                   # 8 Zepto policy corpus documents (doc_01..08.txt)
│   ├── src/
│   │   ├── database.py         # ChromaDB vector index & sentence-transformers embeddings
│   │   ├── agent.py            # LangGraph StateGraph intent router & Pydantic schemas
│   │   └── main.py             # FastAPI web application (POST /ask)
│   ├── data/chroma/            # Persistent local vector database binaries
│   ├── Dockerfile              # Docker container configuration (Exposes port 7860)
│   ├── requirements.txt
│   └── README.md
│
└── README.md                    # Top-Level Capstone Project Summary
```

---

## 🛠️ Modules Overview

### 📦 Module 1: Automated Data Pipeline (25 Marks)
* **Goal**: Automated ingestion, extraction, cleaning, and logging of external web data.
* **Key Features**:
  - Scrapes news articles using `requests` and `BeautifulSoup`.
  - Cleans raw HTML, normalizes text, and removes noise.
  - Logs execution metadata to `scraped_data.csv`.
  - Full `pytest` unit testing suite with automated GitHub Actions workflow on every push.

---

### 📊 Module 2: Analytics & Predictive Modeling (50 Marks)
* **Goal**: Exploratory data analysis, multivariate data storytelling, imbalanced classification, and end-to-end model pipeline serialization.
* **Key Features**:
  - **Data Profiling**: Implemented explicit missing value threshold rules (`<5%` drop rows, `5%-30%` median imputation, `>30%` drop column).
  - **Data Storytelling**: 4-chart visualization layout showcasing survival rate across Pclass, Sex, Fare distribution, and Age demographics.
  - **Preprocessor Pipeline**: Encapsulated numeric median imputation + standard scaling and categorical mode imputation + one-hot encoding inside a unified `ColumnTransformer`.
  - **Class Imbalance & SMOTE**: Compared baseline classifiers (Logistic Regression, Decision Trees, Random Forest) with `imblearn.pipeline.Pipeline` SMOTE oversampling.
  - **Hyperparameter Tuning**: Tuned Random Forest via `GridSearchCV` achieving **82.68% Test Accuracy** and **0.867 ROC-AUC**.
  - **Heteroscedasticity Analysis**: Conducted multivariate linear regression on passenger fares and analyzed residual plots for variance funneling.
  - **Serialization**: Saved the complete preprocessor + model estimator to `best_pipeline.joblib`.
  - **Mobile Access**: Maintained pure `.py` script equivalents (`01_eda.py`, `02_modeling.py`) alongside notebooks for GitHub mobile review.

---

### 🤖 Module 3: Support Assistant Service (25 Marks)
* **Goal**: A RAG-based GenAI customer support service orchestrating query routing, vector search, and structured response outputs.
* **Key Features**:
  - **Corpus Indexing**: Embedded 8 Zepto policy text documents into a local **ChromaDB** vector store using `sentence-transformers` (`all-MiniLM-L6-v2`) with cosine similarity.
  - **LangGraph StateGraph**: Assembled a 3-node graph (`classify_intent`, `retrieve_and_answer`, `direct_answer`) with conditional routing.
  - **Structured Output**: Enforced Pydantic schema validation (`answer`, `sources`, `confidence`).
  - **Offline Mock Baseline (`MOCK_LLM=1`)**: Fully deterministic, rule-based mock execution requiring **no API keys** or external internet calls.
  - **Optional Real-LLM Mode (`MOCK_LLM=0`)**: Connects live to Groq API (`llama-3.1-8b-instant`) with automatic schema validation retries.
  - **REST API & Docker**: Wrapped in FastAPI (`POST /ask`) and containerized with Docker exposed on port `7860`.

---

## ⚡ Quick Start Guide

### 1. Clone & Set Up Environment
```powershell
git clone https://github.com/chandrakanthGupta/AIML-Capstone-Project.git
cd "AIML capstone project"
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Run Module 1 (Data Pipeline)
```powershell
pip install -r data_pipeline/requirements.txt
python data_pipeline/src/pipeline.py
pytest data_pipeline/tests/
```

### 3. Run Module 2 (Analytics & Modeling)
```powershell
pip install -r analytics/requirements.txt
python analytics/01_eda.py
python analytics/02_modeling.py
```

### 4. Run Module 3 (Support Assistant Service)
```powershell
pip install -r support_assistant/requirements.txt
python support_assistant/src/database.py
python support_assistant/src/main.py
```
*Access interactive API documentation at `http://localhost:7860/docs`.*

---

## 🐳 Docker Usage (Support Assistant)

```powershell
# Build Docker image
docker build -t zepto-support-assistant -f support_assistant/Dockerfile .

# Run Docker container locally
docker run -p 7860:7860 zepto-support-assistant
```

---

## 📄 License
This repository is submitted as part of the AIML Capstone Project coursework.

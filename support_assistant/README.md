# Module 3: Support Assistant Service (Zepto RAG)

A complete, production-grade GenAI Customer Support service built for Zepto. The application embeds and indexes a Zepto policy document corpus in ChromaDB, orchestrates intent routing and context retrieval via a LangGraph `StateGraph`, guarantees structured Pydantic output, and exposes a RESTful API wrapped in FastAPI and containerized with Docker.

---

## 🏗️ RAG Pipeline Architecture

The pipeline processes user queries through four sequential stages:

```
[ Ingestion ] ➡️ [ Local Embedding ] ➡️ [ Retrieval (ChromaDB) ] ➡️ [ Generation (LangGraph) ]
  (doc_01..08)      (MiniLM-L6-v2)        (Cosine Similarity)      (Mock / Groq LLM)
```

### Stage-by-Stage Breakdown:

1. **Ingestion (`docs/`)**:
   - **Corpus**: 8 text files (`doc_01.txt` through `doc_08.txt`) covering Zepto's delivery, returns & refunds, membership tiers, order tracking, order cancellation, damaged/missing items, gift cards, and support hours policies.
   - **Chunking**: Each file represents a focused policy document chunk.

2. **Embedding (`support_assistant/src/database.py`)**:
   - **Model**: `all-MiniLM-L6-v2` loaded locally via `sentence-transformers`.
   - **Vector Store**: Embeddings are stored persistently in ChromaDB at `support_assistant/data/chroma` using cosine distance space (`hnsw:space: cosine`).
   - **Execution**: Runs 100% locally on CPU without requiring internet access or API tokens.

3. **Retrieval (`support_assistant/src/database.py`)**:
   - Query text is embedded into a 384-dimensional vector.
   - ChromaDB queries the collection for the top-3 most similar document chunks using cosine similarity.
   - Converts vector distance to cosine similarity score (`1 - distance`).

4. **Generation & Orchestration (`support_assistant/src/agent.py`)**:
   - Orchestrated via a 3-node LangGraph `StateGraph`:
     - **`classify_intent`**: Classifies query as `policy_question` or `general_question`.
     - **`retrieve_and_answer`**: Runs vector search over ChromaDB and generates grounded policy answers.
     - **`direct_answer`**: Returns a direct response for general queries without retrieval.
   - **Structured Output**: Output is validated against the `SupportResponse` Pydantic model (`answer`, `sources`, `confidence`).

---

## 🔀 The `MOCK_LLM` Toggle

Every LLM generation step is gated behind the `MOCK_LLM` environment variable:

* **`MOCK_LLM=1` (Default - Graded Baseline)**:
  - **Offline & Deterministic**: No API calls or network access required.
  - **`classify_intent`**: Uses keyword matching (`delivery`, `return`, `refund`, `membership`, `tracking`, `cancel`, `gift card`, `support hours`).
  - **`retrieve_and_answer`**: Vector search executes for real in ChromaDB. Generates canned response: `Based on the retrieved context: {top_chunk_snippet}`.
  - **`direct_answer`**: Returns fixed canned text: `"I can only answer questions about Zepto policies right now."`.

* **`MOCK_LLM=0` (Optional Real-LLM Extension)**:
  - Calls Groq API (`llama3-8b-8192`) or standard OpenAI endpoint.
  - **`classify_intent`**: Prompts LLM to classify query intent.
  - **`retrieve_and_answer`**: Prompts LLM with retrieved context using role-context-task-format structured template with negative constraints and few-shot examples.
  - **Validation & Retry**: Validates output against Pydantic schema; automatically retries up to 2 times with corrective prompts on JSON parse errors.

---

## 🚀 Running the Service Locally

### 1. Install Dependencies
```powershell
pip install -r support_assistant/requirements.txt
```

### 2. Populate Vector Database
```powershell
python support_assistant/src/database.py
```

### 3. Start FastAPI Server
```powershell
python support_assistant/src/main.py
```
*Server runs locally at `http://localhost:7860` with interactive API docs at `http://localhost:7860/docs`.*

---

## 🐳 Docker Deployment

### 1. Build Docker Image
```powershell
docker build -t zepto-support-assistant -f support_assistant/Dockerfile .
```

### 2. Run Docker Container
```powershell
docker run -p 7860:7860 zepto-support-assistant
```
The POST `/ask` endpoint will be live at `http://localhost:7860/ask`.

---

## 📊 Recorded JSON Response Transcripts (Graded Baseline: `MOCK_LLM=1`)

### Test Call 1: Policy Question (Triggers Retrieval)
**Request**: `POST /ask`
```json
{
  "query": "What is the delivery fee for orders below INR 149?"
}
```

**Response**: `200 OK`
```json
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del",
  "sources": [
    "doc_01"
  ],
  "confidence": 1.0
}
```

---

### Test Call 2: General Question (Direct Answer)
**Request**: `POST /ask`
```json
{
  "query": "What is the capital of France?"
}
```

**Response**: `200 OK`
```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

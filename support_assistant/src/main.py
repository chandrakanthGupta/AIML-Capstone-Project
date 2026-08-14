import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Import compiled LangGraph graph and response schema
from support_assistant.src.agent import graph, SupportResponse
from support_assistant.src.database import populate_database, get_chroma_client, COLLECTION_NAME

# ------------------------------------------------------------------------------
# 1. Request Schema
# ------------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str = Field(..., example="What is the delivery fee for orders below 149?")


# ------------------------------------------------------------------------------
# 2. FastAPI Application Setup
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Zepto Customer Support Assistant",
    description="A GenAI service orchestrating RAG search over Zepto policies using LangGraph, ChromaDB, and FastAPI.",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    """
    Auto-populates the ChromaDB database on server startup if not already indexed.
    """
    try:
        client = get_chroma_client()
        client.get_collection(COLLECTION_NAME)
        print("[FastAPI] ChromaDB collection verified.")
    except Exception:
        print("[FastAPI] Collection not found. Initializing database population...")
        populate_database()


@app.get("/")
def read_root():
    return {
        "service": "Zepto Support Assistant",
        "status": "running",
        "mode": "Mock Mode (Default)" if os.environ.get("MOCK_LLM", "1") != "0" else "Real LLM Mode"
    }


# ------------------------------------------------------------------------------
# 3. Primary Endpoint: POST /ask
# ------------------------------------------------------------------------------
@app.post("/ask", response_model=SupportResponse)
def ask_question(request: QueryRequest):
    """
    Accepts a user query, routes through the LangGraph StateGraph, and returns a validated Pydantic JSON response.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        
    initial_state = {
        "query": request.query,
        "intent": "",
        "retrieved_chunks": [],
        "response": {}
    }
    
    try:
        result = graph.invoke(initial_state)
        response_data = result.get("response", {})
        return SupportResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph orchestration error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("support_assistant.src.main:app", host="0.0.0.0", port=7860, reload=True)

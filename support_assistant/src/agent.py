import os
import json
import requests
from typing import TypedDict, List, Dict, Any
from pydantic import BaseModel, Field

# LangGraph imports
from langgraph.graph import StateGraph, END

# Import database retriever
from support_assistant.src.database import retrieve_relevant_chunks

# ------------------------------------------------------------------------------
# 1. Pydantic JSON Output Schema & State Dictionary
# ------------------------------------------------------------------------------
class SupportResponse(BaseModel):
    """
    Structured output guarantee enforced on the final answer.
    """
    answer: str = Field(description="Grounded answer to the user's query.")
    sources: List[str] = Field(description="IDs of the source documents used, empty for general questions.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")


class AgentState(TypedDict):
    """
    State dictionary managed by the LangGraph orchestrator.
    """
    query: str
    intent: str  # 'policy_question' or 'general_question'
    retrieved_chunks: List[Dict[str, Any]]
    response: Dict[str, Any]


# ------------------------------------------------------------------------------
# 2. LLM Inference Helper (For optional MOCK_LLM=0 real path)
# ------------------------------------------------------------------------------
def call_real_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Helper function to call Groq API (or standard OpenAI endpoint) in real-LLM mode.
    """
    api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return json.dumps({
            "answer": "API Key missing. Please set GROQ_API_KEY environment variable.",
            "sources": [],
            "confidence": 0.0
        })
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return json.dumps({
            "answer": f"Error communicating with LLM API: {str(e)}",
            "sources": [],
            "confidence": 0.0
        })


# ------------------------------------------------------------------------------
# 3. LangGraph Nodes
# ------------------------------------------------------------------------------
def classify_intent(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Classifies query as policy_question or general_question.
    """
    query = state["query"].strip()
    mock_llm = os.environ.get("MOCK_LLM", "1") != "0"
    
    if mock_llm:
        print("[Agent Node] Classifying intent (Mock Mode)...")
        keywords = ["delivery", "return", "refund", "membership", "tracking", "cancel", "gift card", "support hours"]
        query_lower = query.lower()
        
        intent = "general_question"
        for kw in keywords:
            if kw in query_lower:
                intent = "policy_question"
                break
        print(f"[Agent Node] Mock intent classified as: {intent}")
        return {"intent": intent}
        
    else:
        print("[Agent Node] Classifying intent (Real LLM Mode)...")
        system_prompt = (
            "Role: Intent Classifier\n"
            "Task: Classify if the query asks about Zepto policies (delivery, returns, refunds, membership, tracking, cancel, gift card, support hours) or a general question.\n"
            "Format: Output a JSON object with a single key 'intent', which must be either 'policy_question' or 'general_question'.\n"
            "Example 1: 'Can I return open soap?' -> {'intent': 'policy_question'}\n"
            "Example 2: 'Who is the President of India?' -> {'intent': 'general_question'}"
        )
        user_prompt = f"Query: {query}"
        raw_out = call_real_llm(system_prompt, user_prompt)
        try:
            intent = json.loads(raw_out).get("intent", "general_question")
        except Exception:
            intent = "general_question"
        print(f"[Agent Node] Real LLM intent classified as: {intent}")
        return {"intent": intent}


def retrieve_and_answer(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Retrieves documents from ChromaDB and answers grounded context.
    """
    query = state["query"]
    mock_llm = os.environ.get("MOCK_LLM", "1") != "0"
    
    # Cosine search always runs for real in both modes
    print("[Agent Node] Retrieving context from ChromaDB...")
    chunks = retrieve_relevant_chunks(query, top_k=3)
    
    if mock_llm:
        print("[Agent Node] Generating answer (Mock Mode)...")
        if chunks:
            top_chunk = chunks[0]
            top_snippet = top_chunk["content"][:200]
            answer = f"Based on the retrieved context: {top_snippet}"
            sources = [top_chunk["id"]]
        else:
            answer = "Based on the retrieved context: No context found."
            sources = []
            
        response = {
            "answer": answer,
            "sources": sources,
            "confidence": 1.0
        }
        return {"retrieved_chunks": chunks, "response": response}
        
    else:
        print("[Agent Node] Generating answer (Real LLM Mode)...")
        context_str = "\n\n".join([f"[Source: {c['id']}]\n{c['content']}" for c in chunks])
        
        system_prompt = (
            "Role: Zepto Support Assistant\n"
            "Context:\n"
            f"{context_str}\n\n"
            "Task: Answer the query using ONLY the provided Context. If context doesn't answer it, say 'I do not know'.\n"
            "Negative Constraints: Do not answer using information not present in the provided context.\n"
            "Format: Output a JSON object with keys:\n"
            "  - 'answer' (grounded answer string)\n"
            "  - 'sources' (list of document IDs used e.g. ['doc_01'])\n"
            "  - 'confidence' (float 0.0 to 1.0)\n"
            "Example:\n"
            "Query: 'Do you deliver in 10 minutes?' -> {'answer': 'Zepto delivers within 10 to 30 minutes.', 'sources': ['doc_01'], 'confidence': 0.95}"
        )
        user_prompt = f"Query: {query}"
        
        # Retry logic: up to 2 additional retries if JSON output fails to validate
        for attempt in range(3):
            raw_out = call_real_llm(system_prompt, user_prompt)
            try:
                data = json.loads(raw_out)
                validated = SupportResponse(**data)
                return {"retrieved_chunks": chunks, "response": validated.dict()}
            except Exception as e:
                print(f"[Agent Node] Validation failed (Attempt {attempt+1}): {str(e)}")
                user_prompt += f"\nCorrection: Output failed validation. Please output valid JSON matching the schema."
                
        return {
            "retrieved_chunks": chunks,
            "response": {
                "answer": "Error: Failed to generate a validated JSON response from LLM.",
                "sources": [],
                "confidence": 0.0
            }
        }


def direct_answer(state: AgentState) -> Dict[str, Any]:
    """
    Node 3: Answers general queries without retrieval.
    """
    query = state["query"]
    mock_llm = os.environ.get("MOCK_LLM", "1") != "0"
    
    if mock_llm:
        print("[Agent Node] Generating direct answer (Mock Mode)...")
        response = {
            "answer": "I can only answer questions about Zepto policies right now.",
            "sources": [],
            "confidence": 1.0
        }
        return {"response": response}
        
    else:
        print("[Agent Node] Generating direct answer (Real LLM Mode)...")
        system_prompt = (
            "Role: Support Assistant\n"
            "Task: Answer the query directly. Keep it concise.\n"
            "Format: Output a JSON object with keys:\n"
            "  - 'answer' (answer string)\n"
            "  - 'sources' (empty list [])\n"
            "  - 'confidence' (1.0)"
        )
        user_prompt = f"Query: {query}"
        raw_out = call_real_llm(system_prompt, user_prompt)
        try:
            data = json.loads(raw_out)
            validated = SupportResponse(**data)
            return {"response": validated.dict()}
        except Exception:
            return {
                "response": {
                    "answer": "I can only answer questions about Zepto policies right now.",
                    "sources": [],
                    "confidence": 1.0
                }
            }


# ------------------------------------------------------------------------------
# 4. LangGraph StateGraph Assembly
# ------------------------------------------------------------------------------
def route_intent(state: AgentState) -> str:
    """
    Conditional edge function routing based on classified intent.
    """
    return "retrieve_and_answer" if state["intent"] == "policy_question" else "direct_answer"


# Build the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_and_answer", retrieve_and_answer)
workflow.add_node("direct_answer", direct_answer)

# Add Edges
workflow.set_entry_point("classify_intent")
workflow.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer"
    }
)
workflow.add_edge("retrieve_and_answer", END)
workflow.add_edge("direct_answer", END)

# Compile Graph
graph = workflow.compile()
print("[Agent] LangGraph StateGraph successfully assembled and compiled!")

import os
import chromadb
from sentence_transformers import SentenceTransformer

# 1. Define paths and constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DB_PATH = os.path.join(BASE_DIR, "data", "chroma")

COLLECTION_NAME = "zepto_policies"
MODEL_NAME = "all-MiniLM-L6-v2"

# 2. Initialize the local SentenceTransformer model (fully offline)
print("[Database] Loading SentenceTransformer model...")
model = SentenceTransformer(MODEL_NAME)
print("[Database] Embedding model loaded.")


def get_chroma_client():
    """
    Creates and returns a persistent ChromaDB client.
    """
    return chromadb.PersistentClient(path=DB_PATH)


def populate_database():
    """
    Reads the 8 policy text documents, embeds them, and stores them in ChromaDB.
    """
    client = get_chroma_client()
    
    # Get or create the collection (reset it if it already exists)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("[Database] Existing collection deleted for fresh indexing.")
    except Exception:
        pass
        
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity
    )
    
    documents = []
    ids = []
    metadatas = []
    
    # Read the 8 files from support_assistant/docs/
    for i in range(1, 9):
        filename = f"doc_0{i}.txt"
        filepath = os.path.join(DOCS_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"[Database] Warning: {filepath} not found. Skipping.")
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        documents.append(content)
        ids.append(f"doc_0{i}")
        metadatas.append({"source": filename})
        
    if not documents:
        print("[Database] Error: No documents found to index.")
        return
        
    print(f"[Database] Generating embeddings for {len(documents)} documents...")
    # Generate embeddings locally using sentence-transformers
    embeddings = model.encode(documents).tolist()
    
    # Store in ChromaDB
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    print(f"[Database] ChromaDB collection '{COLLECTION_NAME}' successfully populated!")


def retrieve_relevant_chunks(query, top_k=3):
    """
    Embeds the user query and retrieves the top-k most similar chunks from ChromaDB.
    """
    client = get_chroma_client()
    collection = client.get_collection(COLLECTION_NAME)
    
    # Embed query locally
    query_embedding = model.encode([query]).tolist()
    
    # Query ChromaDB collection
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    
    # Format outputs
    retrieved_items = []
    if results and results["documents"]:
        for doc, doc_id, distance in zip(
            results["documents"][0],
            results["ids"][0],
            results["distances"][0]
        ):
            retrieved_items.append({
                "content": doc,
                "id": doc_id,
                "score": 1 - distance  # Convert distance to cosine similarity
            })
            
    return retrieved_items


if __name__ == "__main__":
    # If run directly, populate the DB for testing
    populate_database()
    
    # Quick verification check
    print("\n[Database] Running test retrieval check:")
    test_query = "What is the delivery fee for orders below 149?"
    results = retrieve_relevant_chunks(test_query, top_k=1)
    for r in results:
        print(f" - [ID: {r['id']}] Score: {r['score']:.4f}\n - Content: {r['content']}")

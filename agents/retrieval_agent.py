# agents/retrievalagent.py

import faiss
import pickle
import numpy as np
from utils.embedding import get_embedding
import json

def handle_retrieval_message(mcp_message):
    print("\n🔍 [RetrievalAgent] Received MCP message:")
    print(json.dumps(mcp_message, indent=2))

    query = mcp_message["payload"]["query"]
    trace_id = mcp_message["trace_id"]

    embedding = get_embedding(query)
    embedding = np.array(embedding).astype("float32").reshape(1, -1)

    # Load FAISS index and doc map
    index = faiss.read_index("D:/SLRIS/agents/vector_index.faiss")
    with open("chunk_metadata.json", "r", encoding="utf-8") as f:
        doc_store = json.load(f)

    print("Query embedding shape:", embedding.shape)
    print("FAISS index dimension:", index.d)

    D, I = index.search(embedding, 5)  # top 5 results
    retrieved_chunks = [doc_store[i] for i in I[0] if i in doc_store]

    print(f"\n📦 Top retrieved chunks ({len(retrieved_chunks)}):")
    for idx, chunk in enumerate(retrieved_chunks, 1):
        print(f"{idx}. {chunk[:200]}...")

    response_msg = {
        "type": "RETRIEVAL_RESULT",
        "sender": "RetrievalAgent",
        "receiver": "LLMResponseAgent",
        "trace_id": trace_id,
        "payload": {
            "retrieved_context": retrieved_chunks,
            "query": query
        }
    }

    print("\n✅ RetrievalAgent → LLMResponseAgent MCP Message:")
    print(json.dumps(response_msg, indent=2))
    return response_msg


if __name__ == "__main__":
    with open("sample_retrieval_message.json", "r") as f:
        mcp_message = json.load(f)
    handle_retrieval_message(mcp_message)

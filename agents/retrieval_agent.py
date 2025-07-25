import json
import faiss
import numpy as np
from utils.embedding import get_embedding
from core_mcp.mcp import MCPMessage

def handle_retrieval_message(mcp_message):
    payload = mcp_message.payload
    query = payload["query"]

    print("🔍 [RetrievalAgent] Received MCP message:")
    print(json.dumps(mcp_message.to_dict(), indent=2))

    # ✅ Load FAISS index
    index = faiss.read_index("vector_index.faiss")
    dim = index.d
    print("FAISS index dimension:", dim)

    # ✅ Load metadata
    with open("chunk_metadata.json", "r") as f:
        metadata = json.load(f)

    # ✅ Embed the query
    query_embedding = get_embedding(query)
    query_vector = np.array([query_embedding], dtype="float32")
    print("Query embedding shape:", query_vector.shape)

    # 🔍 Search
    k = 15  # top-k results (increase for more context)
    distances, indices = index.search(query_vector, k)

    # ✅ Collect retrieved chunks
    retrieved_chunks = []
    for idx in indices[0]:
        if idx < len(metadata):
            retrieved_chunks.append(metadata[idx]["chunk"])

    print(f"\n📦 Top retrieved chunks ({len(retrieved_chunks)}):\n")
    for chunk in retrieved_chunks:
        print("🔹", chunk)

    # ✅ Return MCP message to LLMResponseAgent
    response = {
        "type": "RETRIEVAL_RESULT",
        "sender": "RetrievalAgent",
        "receiver": "LLMResponseAgent",
        "trace_id": mcp_message.trace_id,
        "payload": {
            "retrieved_context": retrieved_chunks,
            "query": query
        }
    }

    print("\n✅ RetrievalAgent → LLMResponseAgent MCP Message:")
    print(json.dumps(response, indent=2))
    return response

# -------------------------------
# 🚀 Simulate retrieval from a query
# -------------------------------
if __name__ == "__main__":
    test_message = {
        "type": "retrieve",
        "sender": "CoordinatorAgent",
        "receiver": "RetrievalAgent",
        "trace_id": "test-trace-002",
        "payload": {
            "query": "Give some ideas about encoder-decoder architecture"
        }
    }

    handle_retrieval_message(test_message)

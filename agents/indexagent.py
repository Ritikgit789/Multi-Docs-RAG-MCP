import json
import faiss
import numpy as np
import os
from utils.embedding import get_embedding

def handle_index_message(mcp_message):
    payload = mcp_message["payload"]
    chunks = payload["chunks"]
    source_file = payload["source_file"]
    trace_id = mcp_message["trace_id"]

    # ✅ Generate embeddings using real get_embedding
    embeddings = [get_embedding(chunk) for chunk in chunks]
    embeddings_np = np.array(embeddings).astype("float32")
    print("🔢 embeddings_np.shape:", embeddings_np.shape)

    dim = embeddings_np.shape[1]

    # Load or create FAISS index
    if os.path.exists("vector_index.faiss"):
        index = faiss.read_index("vector_index.faiss")
        print("📂 Loaded existing FAISS index")
        with open("chunk_metadata.json", "r") as f:
            metadata = json.load(f)
    else:
        index = faiss.IndexFlatL2(dim)
        metadata = []
        print("📦 Created new FAISS index")

    index.add(embeddings_np)

    for chunk in chunks:
        metadata.append({
            "chunk": chunk,
            "source_file": source_file
        })

    faiss.write_index(index, "vector_index.faiss")
    with open("chunk_metadata.json", "w") as f:
        json.dump(metadata, f)

    print(f"✅ Indexed {len(chunks)} new chunks from '{source_file}'")
    print(f"📊 Total vectors in FAISS index: {index.ntotal} | Dimension: {dim}")

# --------------------------
# 🚀 Read doc.txt internally and index
# --------------------------
def simulate_from_doc_txt():
    with open("D:/SLRIS/documents/doc.txt", "r") as f:
        full_text = f.read()

    # Simple chunking: split by periods (better to use langchain/recursive splitters)
    raw_chunks = [chunk.strip() for chunk in full_text.split('.') if chunk.strip()]
    
    mcp_message = {
        "type": "index",
        "sender": "IngestionAgent",
        "receiver": "IndexAgent",
        "trace_id": "trace-doc-txt-direct",
        "payload": {
            "chunks": raw_chunks,
            "source_file": "doc.txt"
        }
    }

    handle_index_message(mcp_message)

if __name__ == "__main__":
    simulate_from_doc_txt()

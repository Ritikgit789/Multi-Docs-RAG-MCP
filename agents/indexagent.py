import json
import faiss
import numpy as np
import os

def handle_index_message(mcp_message):
    payload = mcp_message["payload"]
    chunks = payload["chunks"]
    embeddings = payload["embeddings"]
    source_file = payload["source_file"]

    # Convert to numpy float32
    embeddings_np = np.array(embeddings).astype("float32")
    print("🔢 embeddings_np.shape:", embeddings_np.shape)

    # Dimension check
    dim = embeddings_np.shape[1]
    # if dim != 768:
    #     raise ValueError(f"❌ Embedding dimension is {dim}, but expected 768. Check your embedding function.")

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

    # Add embeddings to index
    index.add(embeddings_np)

    # Save associated metadata
    for chunk in chunks:
        metadata.append({
            "chunk": chunk,
            "source_file": source_file
        })

    # Save index and metadata
    faiss.write_index(index, "vector_index.faiss")
    with open("chunk_metadata.json", "w") as f:
        json.dump(metadata, f)

    print(f"✅ Indexed {len(chunks)} new chunks from '{source_file}'")
    print(f"📊 Total vectors in FAISS index: {index.ntotal} | Dimension: {dim}")

# Simulate receiving an MCP message (paste message from ingestion agent)
if __name__ == "__main__":
    with open("sample_index_message.json", "r") as f:
        mcp_message = json.load(f)
    handle_index_message(mcp_message)

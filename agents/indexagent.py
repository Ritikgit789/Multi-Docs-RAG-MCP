import json
import faiss
import numpy as np
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.embedding import get_embedding
from agents.ingestion_agent import read_pdf, read_docx, read_csv, read_pptx, read_txt


def handle_index_message(mcp_message):
    payload = mcp_message.payload
    chunks = payload["chunks"]
    source_file = payload["source_file"]
    trace_id = mcp_message.trace_id

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
def simulate_from_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        full_text = read_pdf(file_path)
    elif ext == ".docx":
        full_text = read_docx(file_path)
    elif ext == ".csv":
        full_text = read_csv(file_path)
    elif ext == ".pptx":
        full_text = read_pptx(file_path)
    elif ext == ".txt":
        full_text = read_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # 🔹 Simple chunking
    raw_chunks = [chunk.strip() for chunk in full_text.split('.') if chunk.strip()]

    mcp_message = {
        "type": "index",
        "sender": "IngestionAgent",
        "receiver": "IndexAgent",
        "trace_id": "trace-generic-file",
        "payload": {
            "chunks": raw_chunks,
            "source_file": os.path.basename(file_path)
        }
    }

    handle_index_message(mcp_message)

if __name__ == "__main__":
    simulate_from_file("D:/SLRIS/documents/NIPS-2017-attention-is-all-you-need-Paper.pdf")
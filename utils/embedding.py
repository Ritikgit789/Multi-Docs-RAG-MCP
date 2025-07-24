# utils/embedding.py

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")  # 768-dimensional output

def get_embedding(text):
    embedding = model.encode(text)
    return embedding.tolist()

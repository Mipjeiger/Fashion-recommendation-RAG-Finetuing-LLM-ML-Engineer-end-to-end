import faiss
import pickle
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Create BASE_DIR and index path
BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "models"/ "RAG_FAISS_LLM" / "faiss" / "index.faiss"

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
index = faiss.read_index(INDEX_PATH)

with open(BASE_DIR / "models" / "RAG_FAISS_LLM" / "faiss" / "chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

def retrieve(query: str):
    emb = embedding_model.encode([query])
    D, I = index.search(emb, k=5)
    return [chunks[i] for i in I[0]]
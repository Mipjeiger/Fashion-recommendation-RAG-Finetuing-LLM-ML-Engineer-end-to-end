import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# ==============================
# 1. ENV SETUP
# ==============================

BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

HF_TOKEN = os.getenv("HF_TOKEN")
QDRANT_API_KEY = os.getenv("Qdrant_API_KEY")
QDRANT_CLUSTER_ENDPOINT = os.getenv("Qdrant_Cluster_Endpoint")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ==============================
# 2. EMBEDDINGS
# ==============================

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=HF_TOKEN
)

# ==============================
# 3. VECTOR STORE CONNECTION
# ==============================

vector_store = QdrantVectorStore.from_existing_collection(
    url=QDRANT_CLUSTER_ENDPOINT,
    api_key=QDRANT_API_KEY,
    collection_name="ecommerce_rag",
    embedding=embeddings
)

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 6, "fetch_k": 12}
)

print("✅ Connected to Qdrant.")

# ==============================
# 4. LLM
# ==============================

chat_model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    max_tokens=8192,
    top_p=0.9,
    groq_api_key=GROQ_API_KEY
)

print("✅ LLM initialized.")

# ==============================
# 5. PROMPT
# ==============================

prompt = ChatPromptTemplate.from_template("""
You are a Senior E-Commerce Business Analyst.

CONTEXT:
{context}

QUESTION:
{question}

Provide detailed strategic analysis.
""")

# ==============================
# 6. RAG CHAIN (LCEL)
# ==============================

def format_docs(docs):
    context = ""
    for i, d in enumerate(docs):
        page = d.metadata.get("page", "unknown")
        context += f"\n\n[Chunk {i+1} | Page {page}]\n{d.page_content}\n"
    return context


rag_chain = (
    {
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnableLambda(lambda x: x),
    }
    | prompt
    | chat_model
    | StrOutputParser()
)
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from qdrant_client import QdrantClient


# Define BASE_DIR and load environment variables
BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

# Define constants for PDF file path
PDF_FILE_PATH = BASE_DIR / "ai_engineer" / "docs" / "RAG_Analysis_Report.pdf"

# Load tokens and API keys from environment variables
HF_TOKEN = os.getenv('HF_TOKEN')
QDRANT_API_KEY = os.getenv('Qdrant_API_KEY')
QDRANT_CLUSTER_ENDPOINT = os.getenv('Qdrant_Cluster_Endpoint')

# 1. Load PDF
def load_pdf(file_path):
    loader = PyPDFLoader(file_path=file_path)
    documents = loader.load()
    return documents
documents = load_pdf(PDF_FILE_PATH)
print(f"Number of documents loaded: {len(documents)}")

# 2. Chunking
def chunk_documents(documents, chunk_size=800, chunk_overlap=150):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents=documents)
    return chunks
chunks = chunk_documents(documents=documents)
print(f"Number of chunks created: {len(chunks)}")

# 3. Embedding Model
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=HF_TOKEN
)
print("Embedding model initialized successfully.")


# 4. Connect Qdrant
qdrant_client = QdrantClient(
    url=QDRANT_CLUSTER_ENDPOINT,
    api_key=QDRANT_API_KEY,
    prefer_grpc=False
)
print(f"Connected to Qdrant at {QDRANT_CLUSTER_ENDPOINT} successfully.")

# 5. Create Vector Store
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="ecommerce_rag",
    url=QDRANT_CLUSTER_ENDPOINT,
    api_key=QDRANT_API_KEY,
)
print("Vector store created and documents ingested successfully.")
print(f"Total documents in vector store: {qdrant_client.get_collection('ecommerce_rag').points_count}")
print("Ingestion process completed successfully.")
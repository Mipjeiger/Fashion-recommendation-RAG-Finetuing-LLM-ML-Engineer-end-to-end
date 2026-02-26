import os
import torch
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEndpointEmbeddings
from qdrant_client import QdrantClient
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

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

# Create question for RAG Chain
EVAL_QUESTION = [
    "What are the key factors affecting revenue growth?",
    "How does customer will be increased when prices are reduced?",
    "What are the main challenges in forecasting sales face on stock values?",
    "what's business analyst strategy to increase sales and profit in e-commerce?",
    "What's deep learning using LSTM impact to sales forecasting in e-commerce?"
]

# 1. Cloud Embeddings (Zero Local Memory)
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=HF_TOKEN
)
print("Embedding model initialized successfully.")

# 2. Cloud Vector Store (Qdrant Cloud)
qdrant_client = QdrantClient(
    url=QDRANT_CLUSTER_ENDPOINT,
    api_key=QDRANT_API_KEY,
    collection_name="ecommerce_rag",
    prefer_grpc=False
)
print(f"Connected to Qdrant at {QDRANT_CLUSTER_ENDPOINT} successfully.")

# Create chunking from PDF and ingest to Qdrant vector store
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
loader = PyPDFLoader(file_path=PDF_FILE_PATH)
documents = loader.load()

# Define chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
chunks = text_splitter.split_documents(documents=documents)

# 3. Create Vector Store
def vector_store():
    vectore_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="ecommerce_rag",
        url=QDRANT_CLUSTER_ENDPOINT,
        api_key=QDRANT_API_KEY,
        prefer_grpc=False
    )
    return vectore_store
vector_store = vector_store()

# 4. Cloud LLM (Hugging Face Inference Endpoint)
# This sends the text to HF servers; no model is downloaded to your Machine
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=512,
    task="text-generation",
    temperature=0.7
)
print("LLM initialized successfully.")

# 5. RAG Chain Construction
class RAGChain(RunnablePassthrough):
    def __init__(self, llm, vector_store, top_k=3):
        self.llm = llm
        self.vector_store = vector_store
        self.top_k = top_k
        self.prompt_template = PromptTemplate(
            input_variables=["query", "retrieved_docs"],
            template=("""
You are an e-commerce senior business analyst.
Use ONLY the following context from document to answer the question.
If the context is insufficient to answer the question, make hypothesis based on your knowledge and reasoning. 

Context:
{context}

Question: {question}

Notes:
1. Minimal 500 words explanation
2. Explaining the reasoning process step by step, including any assumptions made and how you arrived at the conclusion.
3. Provide detailed analysis and insights based on the retrieved context
4. If the context doesn't contain specific data or figures relevant to document, infer possible as senior business analyst, and clearly state.
5. Make it statement clearly based on similar to document, if nothing cite specific data or figures in source_pages, infer possible values based on industry standards and trends, and clearly state that these are assumptions.
6. Don't hallucinate
""")
)

    def invoke(self, query):
        # Step 1: Retrieve relevant documents from Qdrant
        retrieved_docs = self.vector_store.similarity_search(query, k=self.top_k)
        retrieved_texts = "\n\n".join([d.page_content for d in retrieved_docs])

        # Step 2: Format the prompt with the retrieved documents and the query
        prompt = self.prompt_template.format(query=query, context=retrieved_texts)

        # Step 3: Generate the answer using LLM
        answer = self.llm(prompt)
        return answer
    
# 6. Usage

if __name__ == "__main__":
    rag_chain = RAGChain(llm=llm, vector_store=vector_store, top_k=3)
    # Query for loopping
    rag_results = []
    for i, q in enumerate(tqdm(EVAL_QUESTION, desc="Processing question:")):
        docs = rag_chain.invoke(q)
        answer = {
            "question": q,
            "answer": docs,
            "retrieved_docs": (len(docs) if isinstance(docs, list) else 1),
            "source_pages": [d.metadata.get("source", "N/A") for d in rag_chain.vector_store.similarity_search(q, k=rag_chain.top_k)]
        }
        rag_results.append(answer)
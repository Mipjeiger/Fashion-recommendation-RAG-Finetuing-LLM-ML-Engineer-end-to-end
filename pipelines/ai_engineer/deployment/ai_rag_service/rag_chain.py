import os
import torch
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

# 3. Cloud LLM (Hugging Face Inference Endpoint)
# This sends the text to HF servers; no model is downloaded to your Machine
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=512,
    task="text-generation",
    temperature=0.7
)
print("LLM initialized successfully.")

# 4. RAG Chain Construction
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


# 5. Usage
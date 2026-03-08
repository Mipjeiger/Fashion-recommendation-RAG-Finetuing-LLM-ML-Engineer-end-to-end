import os
import pandas as pd
import gradio as gr
import torch
from pathlib import Path
from qdrant_client import QdrantClient
from IPython.display import Markdown, display
from qdrant_client.models import Distance, VectorParams
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from tqdm.auto import tqdm

"""
Fashion AI Assistant Engineer - HuggingFace Spaces Deployment
Stack: Langchain + HuggingFaceEndpoint + HuggingFaceEmbeddings + Qdrant Cloud + Gradio"""

# 1. Configuration - Credentials KEY
BASE_DIR = Path(__file__).parents[3]  # Adjust the number based on your directory structure
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

if not os.path.exists(ENV_PATH):
    raise FileNotFoundError(f"Environment file not found at {ENV_PATH}")
else:
    print(f"Environment file loaded from {ENV_PATH}")

QDRANT_CLUSTER = os.environ.get("Qdrant_Cluster_Endpoint")
QDRANT_API_KEY = os.environ.get("Qdrant_API_KEY")
HF_API_KEY = os.environ.get("HF_TOKEN")

# Configurations - variables
COLLECTION = "fashion_products"
PDF_COLLECTION = "rag_report"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "Qwen/Qwen3.5-35B-A3B"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

# 2. Initialize AI Engineering steps components with progress bar

steps = ["Qdrant-cloud Endpoint", "Huggingface-endpoint LLM", "VectorStore Initialization", "Retrievers"]

with tqdm(total=len(steps), desc="🔧 Setting up LLM RAG Chain", unit="step", ncols=70) as pbar:
    for step in steps:
        pbar.set_postfix(step=step)
        pbar.update(1)

# Qdrant Client Initialization
qdrant_client = QdrantClient(
    url=QDRANT_CLUSTER,
    api_key=QDRANT_API_KEY,
    prefer_grpc=False, # Set to True if you want to use gRPC, False for REST API
    timeout=60
)

# Langchain Components Initialization
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": DEVICE},
    encode_kwags={"normalize_embeddings": True, "batch_size": 32}
)

llm_endpoint = HuggingFaceEndpoint(
    repo_id=LLM_MODEL,
    huggingfacehub_api_token=HF_API_KEY,
    max_new_tokens=800,
    temperature=0.7,
    repetition_penalty=1.1,   
)

# Wrap it chat to HuggingFace
pbar.set_description("🔧 Setting up LLM RAG Chain - Wrapping LLM to Chat")
llm = ChatHuggingFace(llm=llm_endpoint)

# VectorStore Initialization
product_vectorstore = QdrantVectorStore(
    client=qdrant_client,
    collection_name=COLLECTION,
    embeddings=embeddings
)
pdf_vectorstore = QdrantVectorStore(
    client=qdrant_client,
    collection_name=PDF_COLLECTION,
    embeddings=embeddings
)

# Retriever Initialization
product_retriever = product_vectorstore.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k": 5}
)
pdf_retriever = pdf_vectorstore.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k": 3}
)

# 3. RAG Chain Construction
pbar.set_description("🧠 Setting up LLM RAG Chain - Constructing RAG Chain")
RAG_PROMPT = PromptTemplate.from_template("""
<s>[INST] You are a senior machine learning engineer specializing in the fashion industry where works in ecommerce companies.
Use the product catalog and report insights below to answer properly.
                                          

### Product Catalog:
{products}

### Report Insights:
{pdf_context}

### Question:
{question} / [/INST]                                          
""")

def format_products(docs: list) -> str:
    return "\n".join([
        f"- {d.metadata.get('brand', 'unknown brand')} | "
        f" {d.metadata.get('category', 'unknown category')} | "
        f"Rp.{d.metadata.get('price', 'unknown price')}"
        for d in docs
    ])

def format_pdf(docs: list) -> str:
    return "\n\n".join([
        f"[{d.metadata.get('source', 'unknown source')} p.{d.metadata.get('page', 'unknown page')}]:"
        f"{d.page_content[:300]}"
        for d in docs
    ])

# RAG Chain
rag_chain = (
    {
        "products": product_retriever | RunnableLambda(format_products),
        "pdf_context": pdf_retriever | RunnableLambda(format_pdf),
        "question": RunnablePassthrough(),
    }
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)

display(Markdown("✅ **RAG chain built** — LangChain + HuggingFaceEndpoint + Qdrant Cloud"))

# 4. Gradio Chat Function + Gradio Interface (UI)
import gradio as gr
import re
import numpy as np
import pandas as pd


def gradio_chat(message: str, history: list) -> str:
    try:
        answer = rag_chain.invoke(message)

        prod_docs = product_retriever.invoke(message)
        rows = []
        for d in prod_docs:
            meta = d.metadata
            rows.append({
                "brand":              meta.get("brand",             "Unknown"),
                "category":           meta.get("category",          "—"),
                "subcategory":        meta.get("subcategory",       "—"),
                "price":              meta.get("price",             "—"),
                "sales":              meta.get("sales",             "—"),
                "size_range":         meta.get("size_range",        "—"),
                "stock_value_retail": meta.get("stock_value_retail","—")
            })

            for k, v in rows[-1].items():
                try:
                    if isinstance(v, np.integer):    rows[-1][k] = int(v)
                    elif isinstance(v, np.floating): rows[-1][k] = float(v)
                    elif isinstance(v, np.bool_):    rows[-1][k] = bool(v)
                    elif pd.isna(v):                 rows[-1][k] = None
                except Exception:
                    pass

        if rows:
            header = "| " + " | ".join(rows[0].keys()) + " |"
            sep    = "| " + " | ".join(["---"] * len(rows[0])) + " |"
            body   = "\n".join(
                "| " + " | ".join(str(v) if v is not None else "—" for v in r.values()) + " |"
                for r in rows
            )
            table = f"{header}\n{sep}\n{body}"
        else:
            table = "_No products found._"

        return f"{answer}\n\n### 🛍️ Recommended Products:\n{table}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 🛍️ Fashion Assistant Engineer")
    gr.Markdown("LangChain · HuggingFaceEndpoint · Qdrant Cloud")
    gr.ChatInterface(
        fn=gradio_chat,
        # ✅ removed type="messages" — not supported in Gradio < 4.x
        examples=[
            "What are the top recommended brands product for casual wear with high sales and how many stocks do they have?",
            "Which products fit to top and bottoms with size range S-XXL?",
            "Show me the best-selling products in under Rp.290.000 price range"
        ],
    )

# Usage
if __name__ == "__main__":
    demo.launch(share=True, debug=True)
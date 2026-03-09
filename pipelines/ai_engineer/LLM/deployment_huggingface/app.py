import os
import re
import numpy as np
import pandas as pd
import gradio as gr
import torch
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

"""
Fashion AI Assistant Engineer - HuggingFace Spaces Deployment
Stack: Langchain + HuggingFaceEndpoint + HuggingFaceEmbeddings + Qdrant Cloud + Gradio
"""

# ─────────────────────────────────────────────
# 1. Configuration - Load Credentials
# ─────────────────────────────────────────────
load_dotenv()

QDRANT_CLUSTER = os.environ.get("Qdrant_Cluster_Endpoint")
QDRANT_API_KEY = os.environ.get("Qdrant_API_KEY")
HF_API_KEY     = os.environ.get("HF_TOKEN")

if not all([QDRANT_CLUSTER, QDRANT_API_KEY, HF_API_KEY]):
    raise ValueError("❌ One or more required credentials not found. Check .env or HF Secrets.")

# Configurations
COLLECTION     = "fashion_products"
PDF_COLLECTION = "rag_report"
EMBED_MODEL    = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL      = "Qwen/Qwen3.5-35B-A3B"
DEVICE         = "cpu"

# ─────────────────────────────────────────────
# 2. Initialize Components (logged to console)
# ─────────────────────────────────────────────

# Step 1: Qdrant Client
print("⏳ [1/5] Connecting to Qdrant Cloud...")
qdrant_client = QdrantClient(
    url=QDRANT_CLUSTER,
    api_key=QDRANT_API_KEY,
    prefer_grpc=False,
    timeout=60
)
print(f"✅ [1/5] Qdrant Cloud connected → {QDRANT_CLUSTER}")

# Step 2: HuggingFace Embeddings
print(f"⏳ [2/5] Loading embeddings model: {EMBED_MODEL}...")
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": DEVICE},
    encode_kwargs={"normalize_embeddings": True, "batch_size": 32}
)
print(f"✅ [2/5] Embeddings ready on device: {DEVICE}")

# Step 3: HuggingFace LLM Endpoint
print(f"⏳ [3/5] Connecting to HuggingFace Endpoint: {LLM_MODEL}...")
llm_endpoint = HuggingFaceEndpoint(
    repo_id=LLM_MODEL,
    huggingfacehub_api_token=HF_API_KEY,
    max_new_tokens=800,
    temperature=0.7,
    repetition_penalty=1.1,
)
llm = ChatHuggingFace(llm=llm_endpoint)
print(f"✅ [3/5] LLM ready → {LLM_MODEL}")

# Step 4: VectorStore
print("⏳ [4/5] Initializing VectorStores...")
product_vectorstore = QdrantVectorStore(
    client=qdrant_client,
    collection_name=COLLECTION,
    embedding=embeddings       # ✅ fixed: embedding= not embeddings=
)
pdf_vectorstore = QdrantVectorStore(
    client=qdrant_client,
    collection_name=PDF_COLLECTION,
    embedding=embeddings       # ✅ fixed: embedding= not embeddings=
)
print(f"✅ [4/5] VectorStores ready → [{COLLECTION}] [{PDF_COLLECTION}]")

# Step 5: Retrievers
print("⏳ [5/5] Setting up Retrievers...")
product_retriever = product_vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)
pdf_retriever = pdf_vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)
print("✅ [5/5] Retrievers ready")

# ─────────────────────────────────────────────
# 3. RAG Chain Construction
# ─────────────────────────────────────────────
print("⏳ Building RAG Chain...")

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
        f"{d.metadata.get('category', 'unknown category')} | "
        f"Rp.{d.metadata.get('price', 'unknown price')}"
        for d in docs
    ])

def format_pdf(docs: list) -> str:
    return "\n\n".join([
        f"[{d.metadata.get('source', 'unknown source')} p.{d.metadata.get('page', 'unknown page')}]: "
        f"{d.page_content[:300]}"
        for d in docs
    ])

rag_chain = (
    {
        "products":    product_retriever | RunnableLambda(format_products),
        "pdf_context": pdf_retriever     | RunnableLambda(format_pdf),
        "question":    RunnablePassthrough(),
    }
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)

print("✅ RAG Chain built — LangChain + HuggingFaceEndpoint + Qdrant Cloud")

# ─────────────────────────────────────────────
# 4. Gradio Chat Function with gr.Progress
# ─────────────────────────────────────────────

def gradio_chat(message: str, history: list, progress=gr.Progress()) -> str:
    try:
        # Step 1: Retrieve products
        progress(0.1, desc="🔍 Retrieving products from Qdrant...")
        prod_docs = product_retriever.invoke(message)

        # Step 2: Generate answer
        progress(0.4, desc="🤖 Generating AI answer...")
        answer = rag_chain.invoke(message)

        # Step 3: Build table
        progress(0.85, desc="📊 Building recommendation table...")
        rows = []
        for d in prod_docs:
            meta = d.metadata
            row = {
                "brand":              meta.get("brand",             "Unknown"),
                "category":           meta.get("category",          "—"),
                "subcategory":        meta.get("subcategory",       "—"),
                "price":              meta.get("price",             "—"),
                "sales":              meta.get("sales",             "—"),
                "size_range":         meta.get("size_range",        "—"),
                "stock_value_retail": meta.get("stock_value_retail","—")
            }
            # Sanitize numpy types
            for k, v in row.items():
                try:
                    if isinstance(v, np.integer):    row[k] = int(v)
                    elif isinstance(v, np.floating): row[k] = float(v)
                    elif isinstance(v, np.bool_):    row[k] = bool(v)
                    elif pd.isna(v):                 row[k] = None
                except Exception:
                    pass
            rows.append(row)

        # Step 4: Format table
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

        progress(1.0, desc="✅ Done!")
        return f"{answer}\n\n### 🛍️ Recommended Products:\n{table}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ─────────────────────────────────────────────
# 5. Gradio UI
# ─────────────────────────────────────────────
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🛍️ Fashion AI Assistant Engineer
    **Stack:** LangChain · HuggingFaceEndpoint · Qdrant Cloud · Gradio
    """)

    gr.ChatInterface(
        fn=gradio_chat,
        examples=[
            "What are the top recommended brands product for casual wear with high sales and how many stocks do they have?",
            "Which products are most suitable for formal occasions?",
            "Which products fit to top and bottoms with size range S-XXL?",
            "Show me the best-selling products in under Rp.290.000 price range"
        ],
        cache_examples=False,
    )

    gr.Markdown("""
    ---
    > 🔒 Powered by **Qdrant Cloud** · **HuggingFace Inference API** · **LangChain RAG**
    """)


# ─────────────────────────────────────────────
# 6. Launch
# ─────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(share=True, debug=True)
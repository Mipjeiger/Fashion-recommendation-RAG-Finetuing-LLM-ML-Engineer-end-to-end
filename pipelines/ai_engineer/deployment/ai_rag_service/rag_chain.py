import os
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser

# ==============================
# 1. ENV SETUP
# ==============================

BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

PDF_FILE_PATH = BASE_DIR / "ai_engineer" / "docs" / "RAG_Analysis_Report.pdf"
REPORT_OUTPUT_PATH = BASE_DIR / "ai_engineer" / "docs" / "RAG_Analysis_Output.txt"

HF_TOKEN = os.getenv('HF_TOKEN')
QDRANT_API_KEY = os.getenv('Qdrant_API_KEY')
QDRANT_CLUSTER_ENDPOINT = os.getenv('Qdrant_Cluster_Endpoint')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

EVAL_QUESTION = [
    "What are the key factors affecting revenue growth?",
    "How does customer will be increased when prices are reduced?",
    "What are the main challenges in forecasting sales face on stock values?",
    "what's business analyst strategy to increase sales and profit in e-commerce?",
    "What's deep learning using LSTM impact to sales forecasting in e-commerce?"
]

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

vector_store = QdrantVectorStore(
    url=QDRANT_CLUSTER_ENDPOINT,
    api_key=QDRANT_API_KEY,
    collection_name="ecommerce_rag",
    embedding=embeddings
)

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 8}
)

print("✅ Connected to Qdrant.")

# ==============================
# 4. LLM
# ==============================

chat_model = HuggingFaceEndpoint(
    endpoint_url=os.getenv('HF_ENDPOINT_URL'),
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=2048,
    temperature=0.4,
    timeout=180
)

print("✅ LLM initialized.")

# ==============================
# 5. PROMPT
# ==============================

prompt = ChatPromptTemplate.from_template("""
You are a Senior E-Commerce Business Analyst and Strategic Advisor with 15+ years of enterprise experience
in revenue optimization, pricing strategy, AI-driven forecasting, customer analytics, and P&L management.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THINKING PROCESS (Chain-of-Thought)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Before answering, reason through the following steps internally:

STEP 1 — Understand the question deeply. What is really being asked?
STEP 2 — Scan the document context. What relevant evidence exists?
STEP 3 — Identify gaps. What does the document NOT cover that I need to address from expertise?
STEP 4 — Plan the structure of the answer before writing it.
STEP 5 — Write the full analysis following the structure below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPONSE STRUCTURE (Follow Strictly)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🧠 Reasoning Trace
Briefly explain your thought process: what you found in the document, what gaps exist, and how you will fill them.

## 📋 Executive Summary
Provide a 200–300 word high-level overview of the answer. 
This should be readable by a C-suite executive with no technical background.

## 🔍 Strategic Deep-Dive Analysis (800–1200 words)

### 1. Key Drivers
Explain the primary factors at play. Use the Revenue Formula:
**Revenue = Traffic × Conversion Rate × Average Order Value (AOV)**
Break down each component's contribution.

### 2. Financial Impact Analysis
Quantify impacts where possible. Use:
- Margin structure (Gross Margin, Net Margin)
- Customer Lifetime Value (LTV) formula: LTV = AOV × Purchase Frequency × Customer Lifespan
- CAC (Customer Acquisition Cost) efficiency: LTV:CAC ratio benchmarks (healthy = 3:1 or higher)

### 3. Operational Implications
What does this mean for day-to-day operations?
- Inventory management
- Supply chain effects
- Pricing team workflows
- Tech/data infrastructure needs

### 4. Risk Considerations
- Market risks
- Execution risks
- Data/model risks (if AI/ML involved)
- Competitive response risks

## 📄 Document-Grounded Insights
Cite specific findings from the retrieved document context below.
Format: > "[Key insight from document]" — Source Page X
If the document lacks coverage on a subtopic, explicitly state: "Document does not address this aspect."

## 💡 Enterprise-Level Recommendations
Provide 5–7 concrete, prioritized action items a C-suite team can act on.
Format each as:
**Priority [1-7] | [Action Title]**: [2-3 sentence explanation of what to do and why]

## 📊 Industry Benchmarks & Assumptions
List any industry-standard figures used.
Label each clearly as: ⚠️ Industry-Based Insight (Not from document)
Example: ⚠️ Industry-Based Insight: Average e-commerce conversion rate = 2–4% (Shopify/Statista 2024)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Do NOT truncate or summarize prematurely. Write the FULL analysis.
- Do NOT fabricate document statistics. Only cite what is in the context.
- Distinguish clearly between document evidence and expert knowledge.
- Minimum response length: 1200 words. Target: 1500–2000 words.
- Use markdown formatting for readability.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXT FROM DOCUMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUESTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{question}

Now reason step by step, then write the full analysis:
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
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | chat_model
    | StrOutputParser()
)
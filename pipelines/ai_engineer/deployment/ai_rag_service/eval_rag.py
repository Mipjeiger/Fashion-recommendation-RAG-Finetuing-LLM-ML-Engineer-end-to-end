import os
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
from datetime import datetime

# LangChain & Cloud Integrations
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq

# 1. ENV SETUP
BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

PDF_FILE_PATH = BASE_DIR / "ai_engineer" / "docs" / "RAG_Analysis_Report.pdf"
REPORT_OUTPUT_PATH = BASE_DIR / "ai_engineer" / "docs" / "RAG_Analysis_Output.txt"

HF_TOKEN = os.getenv('HF_TOKEN')
QDRANT_API_KEY = os.getenv('Qdrant_API_KEY')
QDRANT_CLUSTER_ENDPOINT = os.getenv('Qdrant_Cluster_Endpoint')

EVAL_QUESTION = [
    "What are the key factors affecting revenue growth?",
    "How does customer will be increased when prices are reduced?",
    "What are the main challenges in forecasting sales face on stock values?",
    "what's business analyst strategy to increase sales and profit in e-commerce?",
    "What's deep learning using LSTM impact to sales forecasting in e-commerce?"
]

# 2. CLOUD EMBEDDINGS
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=HF_TOKEN
)

# 3. VECTOR STORE
def get_vector_store():
    loader = PyPDFLoader(file_path=PDF_FILE_PATH)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)

    try:
        vector_store = QdrantVectorStore.from_existing_collection(
            url=QDRANT_CLUSTER_ENDPOINT,
            api_key=QDRANT_API_KEY,
            collection_name="ecommerce_rag",
            embedding=embeddings
        )
        print("✅ Connected to existing Qdrant collection.")
    except Exception:
        print("🆕 Creating new Qdrant collection...")
        vector_store = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=QDRANT_CLUSTER_ENDPOINT,
            api_key=QDRANT_API_KEY,
            collection_name="ecommerce_rag"
        )
    return vector_store

vector_store = get_vector_store()

# 4. LLM - Long Reasoning Config
chat_model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,       # Slightly creative but grounded
    max_tokens=8192,       # ✅ Max tokens for long reasoning output
    top_p=0.9,
    groq_api_key=os.getenv('GROQ_API_KEY')
)
print("✅ LLM initialized.")

# 5. RAG CHAIN WITH LONG CHAIN-OF-THOUGHT REASONING
class RAGChain:
    def __init__(self, model, vector_store, top_k=6):
        self.llm = model
        self.retriever = vector_store.as_retriever(
            search_type="mmr",               # ✅ MMR = diverse chunks, avoids duplicate pages
            search_kwargs={"k": top_k, "fetch_k": 12}
        )

        # ✅ Chain-of-Thought + Long Reasoning Prompt
        self.prompt = ChatPromptTemplate.from_template("""
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

    def invoke(self, query):
        retrieved_docs = self.retriever.invoke(query)

        # Build rich context with page labels
        context = ""
        for i, d in enumerate(retrieved_docs):
            page = d.metadata.get('page', 'unknown')
            context += f"\n\n{'='*50}\n[Chunk {i+1} | Source Page {page}]\n{'='*50}\n{d.page_content}\n"

        formatted_prompt = self.prompt.format(question=query, context=context)
        answer_obj = self.llm.invoke(formatted_prompt)
        answer = answer_obj.content if hasattr(answer_obj, 'content') else str(answer_obj)

        return {
            "answer": answer,
            "context": context,
            "retrieved_docs": retrieved_docs
        }


# 6. EXECUTION + SAVE FULL REPORT
if __name__ == "__main__":
    rag_chain = RAGChain(model=chat_model, vector_store=vector_store)
    final_results = []

    for q in tqdm(EVAL_QUESTION, desc="🔍 Analyzing Documents"):
        res = rag_chain.invoke(q)
        pages = list(set([  # ✅ Deduplicate page numbers
            doc.metadata.get('page', doc.metadata.get('page_number', 'Unknown'))
            for doc in res['retrieved_docs']
        ]))
        final_results.append({
            "question": q,
            "answer": res["answer"],
            "pages": sorted(pages)
        })

    # ✅ Print FULL answers to terminal
    for i, item in enumerate(final_results, 1):
        separator = "=" * 80
        print(f"\n{separator}")
        print(f"  REPORT {i} OF {len(final_results)}")
        print(f"{separator}")
        print(f"\n❓ QUESTION:\n{item['question']}\n")
        print(f"📝 FULL ANSWER:\n{item['answer']}")
        print(f"\n📌 Source Pages: {item['pages']}")
        print(f"{separator}\n")

    # ✅ Save full report to .txt file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = REPORT_OUTPUT_PATH.parent / f"RAG_Report_{timestamp}.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"RAG ANALYSIS REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: llama-3.3-70b-versatile\n")
        f.write("=" * 80 + "\n\n")

        for i, item in enumerate(final_results, 1):
            f.write(f"{'='*80}\n")
            f.write(f"REPORT {i}: {item['question']}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"{item['answer']}\n\n")
            f.write(f"Source Pages: {item['pages']}\n")
            f.write(f"{'='*80}\n\n")

    print(f"\n✅ Full report saved to: {output_file}")
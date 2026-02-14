import faiss
import numpy as np
import os
import re
from pathlib import Path
from pypdf import PdfReader
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Create BASE_DIR and output path
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file FIRST
load_dotenv(BASE_DIR / ".env")

OUTPUT_PATH = BASE_DIR / "models" / "faiss" / "index.faiss"
HF_TOKEN = os.getenv("HF_TOKEN")

# Create directory if it doesn't exist
os.makedirs(OUTPUT_PATH.parent, exist_ok=True)

# Refactor code with Class
class FaissLoader():
    def load_pdf(self, file_path):
        """Load PDF as PDF reader to explain the content based on PDF -> Chunking"""
        reader = PdfReader(file_path)
        text = ""
        for p in reader.pages:
            text += p.extract_text() + "\n"
        return text
    
    def clean_pdf_text(self, text):
        """Remove headers, emails, URLs, and metadata"""
        # Remove emails, URLs, page numbers
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'http\S+|www\.\S+', '', text)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        
        # Remove author info and affiliations
        text = re.sub(r'.*University.*', '', text)
        text = re.sub(r'.*,\s+[A-Z]{2,}.*', '', text)
        
        # Clean whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()

    def chunk_text(self, text, chunk_size=500, overlap=100):
        """Smart chunking with cleanup"""
        # Clean text first
        text = self.clean_pdf_text(text)
        
        # Skip first 500 chars (usually title/authors)
        text = text[500:]
        
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            
            # Only add chunks with real content (>50 chars, mostly letters)
            if len(chunk) > 50 and sum(c.isalpha() for c in chunk) > len(chunk) * 0.5:
                chunks.append(chunk)
            
            start += chunk_size - overlap
    
        return chunks
    
    def hf_inference_client(self, model_name):
        """HuggingFace Inference Client"""
        client = SentenceTransformer(model_name)
        return client
    
    def generate_embeddings(self, model, text_chunks):
        """Generate embeddings from text chunks"""
        embeddings = model.encode(text_chunks)
        return embeddings
    
    def build_prompt(self):
        """Build prompt for LLM Retrieval"""
        # Prepare data
        user_preferences = {
            "category": "tops, bottoms",
            "season": "summer, winter, spring, fall",
            "occasion": "casual, formal, party, sports",
            "size": "S, M, L, XL",
            "brand": "ZARA, H&M, Tommy Hilfiger, Nike, Adidas"
        }
        context = """
        Retrieved fashion items:
        1. ZARA brand fit with size range M-L, perfect for casual occasion in summer season.
        2. H&M lightweight cotton tops, available in sizes S-XL, ideal for casual occasion in winter season.
        3. Tommy Hilfiger formal shirts, size M-L, suitable for formal occasions in spring season.
        4. Nike sports shorts, size L-XL, great for sports occasions in fall season.
        5. Adidas trendy bottoms, size S-M, perfect for party occasions in summer season.
        """
        # Build prompt
        prompt = f"""
You are an AI assistant specialized in fashion recommendations.
Given a user's preferences and context, provide personalized fashion item suggestions.

User Preferences: {user_preferences}
Context: {context}

Notes:  1. Don't be hallucinated about the fashion items.
        2. Provide recommendations based on the context only.
        3. Minimal 1500 words in the answer.
"""
        return prompt  # MISSING return statement
    
    def generate_answer(self, llm_client, prompt):
        """Generate answer from LLM"""
        # Use InferenceClient for text generation, not SentenceTransformer
        try:
            response = llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a specialized fashion recommendation assistant."},
                    {"role": "user", "content": prompt}
                ],
                model="meta-llama/Llama-3.2-3B-Instruct",
                max_tokens=700,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating answer: {e}")
            print("Trying alternative model...")
            try:
                # Fallback to a simpler model if the first one fails
                response = llm_client.text_generation(
                    prompt=prompt,
                    model="google/flan-t5-large",
                    max_new_tokens=700,
                    temperature=0.7
                )
                return response
            except Exception as e:
                print(f"Error with fallback model: {e}")
                return "Unable to generate response. Please check your API key and model availability."

# Usage to call the class
faiss_loader = FaissLoader()

# Load PDF
pdf_text = faiss_loader.load_pdf(os.path.join(BASE_DIR, "data", "pdf", "fashion recommendation LLM.pdf"))
print(f"PDF loaded successfully!")
print(f"Total characters: {len(pdf_text)}")
print(f"First 200 characters:\n{pdf_text[:200]}...\n")

# Chunk Text
text_chunks = faiss_loader.chunk_text(pdf_text)
print(f"Text chunked into {len(text_chunks)} chunks")
print(f"First chunk:\n{text_chunks[0][:200]}...\n")

# Initialize HF client for embeddings
hf_client = faiss_loader.hf_inference_client("sentence-transformers/all-MiniLM-L6-v2")
print("HuggingFace client initialized\n")

# Generate embeddings
embeddings = faiss_loader.generate_embeddings(hf_client, text_chunks)
print(f"Embeddings generated!")
print(f"Number of embeddings: {len(embeddings)}")
print(f"Embedding dimension: {len(embeddings[0]) if len(embeddings) > 0 else 'N/A'}")
print(f"First embedding (first 10 values): {embeddings[0][:10] if len(embeddings) > 0 else 'N/A'}\n")

# Build prompt and generate answer
prompt = faiss_loader.build_prompt()
print("="*60)
print("PROMPT:")
print("="*60)
print(prompt)

# For LLM text generation, use InferenceClient (different from SentenceTransformer)
llm_client = InferenceClient(token=HF_TOKEN)
print("\n" + "="*60)
print("GENERATING ANSWER...")
print("="*60)
answer = faiss_loader.generate_answer(llm_client, prompt)
print(answer)
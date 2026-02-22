## 🛍️ Fashion Recommendation end-to-end enterprise project

## ⚙️ Diagram workflow project
![alt text](images/D454D340-7F97-4CDC-9C79-FEFE160E154A.png)

## 💼 Website displays UI

![alt text](images/17526EDF-8E40-48E3-8D7D-E05290E959E5.png)

![alt text](images/DD312B13-804A-4753-97D7-245C40ED5CE8.png)

## 🎯 Goals Project:

- RAG LLM Finetuning fashion recommendation for giving insights business to user
- Deep learning models usin Pytorch & Tensorflow to solve business problem
- Data engineer for ingesting data in airflow, SQL, hadoop spark

## 📰 Information: The data is suitable for computer vision and deep learning tasks such as image classification, transfer learning, and fashion recommendation systems. Images were collected from an Indian e-commerce platform and cleaned by removing duplicates, corrupted files, and low-quality samples.

## Classes.txt

- casual_shirts
- formal_shirts
- formal_pants
- jeans
- men_cargos
- printed_hoodies
- printed_tshirts
- solid_tshirts

# 👨‍💻 Documentation

- Inference fashion recommendation images

    ![alt text](images/B73C8C74-FC0B-4172-87FF-6F027DA0B888.png)

- Spark init dataset as storage RAM dataset
    
    ![alt text](<images/Screenshot 2026-02-10 at 20.26.11.png>)
    
- Dataset into pandas dataframe from Spark hadoop
    
    ![alt text](<images/Screenshot 2026-02-10 at 20.26.39.png>)
    
- SQL database from Spark init ingested
    
    ![alt text](<images/Screenshot 2026-02-10 at 20.27.25.png>)
    
- ML Engineer decision: Use tensorflow as deep learning model for deep research to solve business problem

- AI Engineer decision: 
    - Retrieval based on PDF relevant about fashion recommendation to Vector Database
    - Integrating LLM-based attribute aware context with fine-grained fashion retrieval. For each attribute in the query the LLM first generates a detailed attribute-aware context for enriching attribute representations with commonsense business insight requirements.

- Django framework to display UI Website integrated with kafka as data ingested

- Create classifiying fashion recommendation based on engagement score which are affected by purchase_count, click_count, view_count. All affected features based on [’subcategory’,‘season’, ‘occasion’] insights

- loss=’binary_crossentropy’ for effecting on classified deep learning similarity search

- Training models to retrieve .keras models → Output:
    - model = .keras result
    - embed_model = .keras result

- Build LLM Finetuning chatbot for business recomendation → business problem solving // RAG Faiss Documentation for embedding Vector Database
    - Output → Fashion similarity recommendation outfit matching
    - Convert PDF text into vectors
    - Retrieve relevant chunks fast
    - Avoid sending everything to the LLM

- Based on experiment i have:
    - ✅ PDF → chunking
    - ✅ SentenceTransformer embeddings (384-dim)
    - ✅ FAISS vector index
    - ✅ LLM generation (RAG)
    - ✅ Neural re-ranker (Keras)

- Create MLOps platform to continue in production

- HuggingFace results
    
    ![alt text](<images/hug 1.png>)
    
- LLM using models meta-llama/Llama-3.2-3B-Instruct based on if error use google/flan-t5-large results:
    
    ![alt text](<images/hug 2.png>)
    
- LLM using models mistralai/Mistral-7B-Instruct-v0.2 based on if error use openchat/openchat-3.5-0106 results:
    
    ![alt text](<images/hug 3.png>)
-

---
# 👷‍♂️ Workflow Project 2

![alt text](<images/Screenshot 2026-02-18 at 15.55.20.png>)

- Build postgreSQL services for migrating database based on airflow orchestration

![alt text](<images/Screenshot 2026-02-17 at 16.27.00.png>)
    
- Airflow orchestrated data ingesting  and retrieval by PostgreSQL
    
![alt text](<images/Screenshot 2026-02-18 at 15.45.14.png>)
    
- Create connection on Apache Spark
    
![alt text](images/12F01B54-23FB-4C66-9D9B-A46FA954939A.png)
    
- Data is retrieved by Apache Spark
    
![alt text](images/538BA704-5D5E-40F9-A62C-C5FA3B159388.png)
    
![alt text](images/1F5FF44E-D588-4DA9-A152-1F0011DDAD56.png)
    
- Build website for integrating User interfaces mlops database production
- Create git stage/staging for preventing automation spammer
- Build docker images dependencies for website environment on Django, FastAPI, and Streamlit
    
![alt text](images/Screenshot 2026-02-19 at 04.58.06.png)
    
- 🧑💻 Build website IndoCloth Market components project backend and frontend integrated each other for showing UI
    
    - 🛍️ Frontend
        
    ![alt text](images/17526EDF-8E40-48E3-8D7D-E05290E959E5.png)
    
    ![alt text](images/DD312B13-804A-4753-97D7-245C40ED5CE8.png)
    
    - 📊 Backend
        
    ![alt text](<images/Screenshot 2026-02-21 at 04.34.00.png>)
        
- Integrating backend as kafka, ariflow, postgresql source database ingested
    - Kafka database
    - Airflow database
    - Postgresql database
- Create & Maintenance slack notifications inference features are integrated with framework added by notify_daily_revenue, notify_weekly_revenue, notify_weekly_learnings
    
    Notifications slack features:
    
- Debugging ci/cd for production grade inference
    
    CI/CD Pipelines


## 💻 Tools

- Data        : Spark + Parquet
- Orchestration: Airflow
- Training    : Tensorflow, Pytorch (Optional)
- LLM         : Hugging Face + PEFT (LoRA)
- Retrieval   : FAISS
- Notebook:  Experiment
- Tracking    : MLflow
- Serving     : FastAPI + Triton
- Infra       : Docker + Kubernetes
- Monitoring: Grafana + Prometheus
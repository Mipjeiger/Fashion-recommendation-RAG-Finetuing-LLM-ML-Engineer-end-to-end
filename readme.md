## 🎯 Goals Project:

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

- 

---

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
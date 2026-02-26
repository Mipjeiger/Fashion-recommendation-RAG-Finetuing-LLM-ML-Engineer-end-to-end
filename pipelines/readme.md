## ⚙️ This pipelines including ETL data pipelines for Extract, Load, and Transform as data engineering.

- We want extract data from fashion_system for only 100,000 rows to analyze

- Loaded data from fashion_system.sql to loss_profit table

- We would transform data into .db file for ingesting API

---

- After ETL -> Create LLM for business problem

- Expriment in notebook for buiding LLM system chatbot using (OpenAI or Huggingfacehub models)

- Target profit_status as forecasting sales prediction using LSTM, Dense by tensorflow for solving business problem indeed

- Creating LLM Models with embedding = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")

- Using Qdrant clound for better performance for preventing memory local issues used

- Prediction
    - Predicting sales and profit_status to ensure LSTM model is relevant for prediction
    - Build chatbot based on PDF document source for inspecting ecommerce business problem
    - Deploy LSTM model as prediction features and FinetuningLLM as chatbot on frontend for adding features

- Deploy LSTM .keras model using Tensorflow Serving

    ![alt text](../images/15ACCF7F-90AD-47F7-9567-A573A95B1C66.png)

- Deploy Finetuning LLM + RAG in HuggingFace and integrating backend API Wrapped by langchain & langserve based on integrating with RAG_Analysis_Report.pdf Docs
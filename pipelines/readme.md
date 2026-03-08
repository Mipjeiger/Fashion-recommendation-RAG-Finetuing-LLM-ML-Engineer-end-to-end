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

    Model is deployed to Tensorflow Serving by using docker pull on tensorlofw/serving
    ![alt text](../images/15ACCF7F-90AD-47F7-9567-A573A95B1C66.png)
    Model is deployed in HTML displays with prediction
    ![alt text](../images/6AA6AC43-D446-456D-85F3-8C3818E4961A.png)
    ![alt text](../images/054B7F7C-BD47-4F51-AB89-73B6E7F219BC.png)

- Deploy Finetuning LLM + RAG in HuggingFace and integrating backend API Wrapped by langchain & langserve based on integrating with RAG_Analysis_Report.pdf Docs
    - Deploy Finetuning integrating backend API Inference with langserve
    ![alt text](../images/828082FE-8616-46D5-AC01-7D6F48A78849.png)
    - Finetuning LLM RAG invoke
    ![alt text](../images/B58F3570-130E-4519-818F-89FA7736D8B3.png)

- Deploy Finetuned LLM in to get started host, deployment, and buld
    - Deploy in AIKit LLMs

- 

## 🤖 Breakdown project on Finetuning LLM → Chatbot integration in UI

- 🎯 Purpose project 

- Add Dataframe (df) features to ensure the LLM prompting is relevant to dataframe
- Integration PDF report to dataframe for as reliable chatbot
- Match recommendation system toward the images for where the product will be shown in UI as ranking recommendation
- Merge LSTM model for sales and profit_status prediction (Optional)
- - AI Engineering structure project concept
    - Experiment in Notebook → Stabilize → Move to Python services → Expose API
- Similarity images search toward to Image_path as ranking recommendation by ‘subcategory’
- Build RAG Chain + Show Recommendations product
    - Models using → HuggingFace Qwen
    ![alt text](ai_engineer/images/CF6767D5-0331-444F-8BB5-4F834778BC14_4_5005_c.jpeg)
    - CPU locals memory preventing → Qdrant Cloud
    ![alt text](ai_engineer/images/86676F1B-F661-467C-BAEF-9CE4E2C6A6EA.png)
    - Fashion recommendation Question to get Answer → featured docs matched
    ![alt text](ai_engineer/images/C8470918-A692-4D11-BC62-DEACF72E5389_1_105_c.jpeg)
    ![alt text](ai_engineer/images/CBBE4AB9-FB46-44F0-A417-C9C43D228D7F_1_105_c.jpeg)
    ![alt text](ai_engineer/images/D77319EB-E625-4BD0-9796-7B862037B66B.png)
    ![alt text](ai_engineer/images/F73CFE60-6316-41E8-8690-251E134D5D03_1_105_c.jpeg)
    ![alt text](ai_engineer/images/A331F5D4-8D44-4AA7-BBEF-D418AD89547B_1_105_c.jpeg)
    - Build Chatbot UI in Gradio
    ![alt text](ai_engineer/images/8CBA55D4-C6AD-4BAE-9FBF-77EDCB6A80DE.png)
    ![alt text](ai_engineer/images/E2CAA9B8-255A-4E68-9EEA-E327A6A06FC3.png)
    ![alt text](ai_engineer/images/3D4CDBA7-4872-4057-998C-88FED0B55F14.png)
    ![alt text](ai_engineer/images/82EC3E66-A755-4C65-A5D6-650BBD7AB62B.png)
    ![alt text](ai_engineer/images/459BE8A8-2A61-4ADA-AA81-A9D36DDBC206.png)
    ![alt text](ai_engineer/images/BBD4ECB8-D4F6-4AAF-AEFD-2E5012B08C4E.png)
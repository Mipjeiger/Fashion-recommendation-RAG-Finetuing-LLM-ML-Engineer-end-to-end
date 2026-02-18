import streamlit as st
from streaming.kafka.consumer import get_consumer

st.set_page_config(layout="wide")
st.title("🧠 Real-Time Recommendation Dashboard")

consumer = get_consumer()
placeholder = st.empty()

# Iterate over Kafka messages and update the dashboard in real-time
for message in consumer:
    data = message.value

    with placeholder.container():
        st.subheader("Session ID")
        st.code(data["session_id"])

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Intent Score",
                data["models"]["tensorflow_recommends"]["intent_score"]
            )

        with col2:
            st.metric(
                "Ranking Confidence",
                data["models"]["pytorch_reranker"]["ranking_confidence"]
            )

        st.json(data)
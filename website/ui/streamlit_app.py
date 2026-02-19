import streamlit as st
import requests
import time

DJANGO_API = "http://mlops-django:8000"

st.set_page_config(
    page_title="🛍️ Real-Time Fashion Recommendation Dashboard",
    layout="wide",
)

# -----------------------
# Sidebar
# -----------------------
st.sidebar.title("⚙️ Controls")

refresh = st.sidebar.slider(
    "Refresh interval (seconds)",
    min_value=1,
    max_value=10,
    value=3
)

if st.sidebar.button("🔄 Check Django Health"):
    try:
        response = requests.get(f"{DJANGO_API}", timeout=2)
        st.sidebar.success("Django API is healthy!")
    except Exception as e:
        st.sidebar.error(str(e))

# -----------------------
# Main Dashboard
# -----------------------
st.title("🧠 Real-Time Recommendation Dashboard")

placeholder = st.empty()

# ---------------------
# POLLING LOOP
# ---------------------
while True:
    try:
        response = requests.get(f"{DJANGO_API}/api/recommendations/latest", timeout=2)
        data = response.json()

        with placeholder.container():
            if data.get("status") == "waiting":
                st.info("Wating for Kafka events...")
            else:
                st.subheader("Session")
                st.code(data.get("session_id", "N/A"))
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

            st.subheader("RAG Assessment")
            st.json(data)

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

    time.sleep(refresh)
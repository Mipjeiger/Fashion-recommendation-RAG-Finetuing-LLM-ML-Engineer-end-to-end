FROM python:3.11-slim

# =====================
# System deps
# =====================
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =====================
# Workdir
# =====================
WORKDIR /app

# =====================
# Install deps
# =====================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =====================
# Copy UI + streaming
# =====================
COPY ui ./ui
COPY streaming ./streaming

# =====================
# Expose
# =====================
EXPOSE 8501

# =====================
# Run
# =====================
CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
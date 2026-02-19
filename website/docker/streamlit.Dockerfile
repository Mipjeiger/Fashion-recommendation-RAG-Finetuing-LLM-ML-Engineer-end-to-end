FROM python:3.11-slim

# ---------------------
# Env
# ---------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# ---------------------
# System deps
# ---------------------
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---------------------
# Workdir
# ---------------------
WORKDIR /app

# ---------------------
# Python deps (WEB ONLY)
# ---------------------
COPY requirements-web.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements-web.txt \
 && rm -rf /root/.cache/pip

# ---------------------
# UI code
# ---------------------
COPY ui ./ui
COPY streaming ./streaming

# ---------------------
# Run
# ---------------------
EXPOSE 8501
CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
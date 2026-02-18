FROM python:3.11-slim

# =====================
# System deps (FAISS / Torch)
# =====================
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
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
# Copy app + models
# =====================
COPY api/fastapi_app ./api/fastapi_app
COPY models ./models

# =====================
# Env
# =====================
ENV PYTHONUNBUFFERED=1

# =====================
# Expose
# =====================
EXPOSE 8001

# =====================
# Run
# =====================
CMD ["uvicorn", "api.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
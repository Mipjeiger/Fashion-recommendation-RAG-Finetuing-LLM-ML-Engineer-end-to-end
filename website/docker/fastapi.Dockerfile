FROM python:3.11-slim

# ---------------------
# Env
# ---------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1

# ---------------------
# System deps (FAISS / BLAS runtime)
# ---------------------
RUN apt-get update && apt-get install -y \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---------------------
# Workdir
# ---------------------
WORKDIR /app

# ---------------------
# Python deps (INFERENCE ONLY)
# ---------------------
COPY requirements-inference.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements-inference.txt

# ---------------------
# App + models
# ---------------------
COPY api/fastapi_app ./api/fastapi_app
COPY models ./models

# ---------------------
# Run
# ---------------------
EXPOSE 8001
CMD ["uvicorn", "api.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
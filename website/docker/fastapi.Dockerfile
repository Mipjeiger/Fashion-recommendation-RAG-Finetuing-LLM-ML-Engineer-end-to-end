FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    MODEL_PATH=/app/models

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# If requirements-inference.txt is inside fastapi_app folder:
COPY requirements-inference.txt /app/requirements-inference.txt
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements-inference.txt

# Copy app source only
COPY . /app/api/fastapi_app

# Do NOT copy models here (models come from volume mount)
EXPOSE 8000
CMD ["uvicorn", "api.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
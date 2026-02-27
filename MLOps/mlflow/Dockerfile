FROM python:3.11-slim

USER root

# Clean up in single layer to avoid bloating image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && pip install --no-cache-dir \
        mlflow==2.15.0 \
        psycopg2-binary==2.9.9 \
        boto3 \
    && apt-get purge -y gcc \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache  # ✅ Remove cache

USER 1000
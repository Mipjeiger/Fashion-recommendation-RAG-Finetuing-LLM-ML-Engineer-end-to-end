# Multi-stage build for IndoCloth Market Backend
FROM python:3.11-slim as builder

WORKDIR /app

# Reduce pip/python cache + bytecode
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHODONTWRITEBYTECODE=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Install deps into isolated venv and copy required files
RUN python -m .venv /opt/.venv
ENV PATH="/opt/.venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Make sure scripts in .local are usable
ENV PATH="/opt/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy Python dependencies from builder
COPY --from=builder /opt/.venv /opt/.venv

# Copy application code
COPY . .

# Expose port
EXPOSE 8030

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8030/health', timeout=5)"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8030"]

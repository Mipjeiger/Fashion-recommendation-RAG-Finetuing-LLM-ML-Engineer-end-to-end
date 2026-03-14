# ─── Stage 1: Builder ─────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1          

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# ✅ Isolated .venv
RUN python -m venv /opt/.venv
ENV PATH="/opt/.venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    # ✅ Strip test/cache/dist-info to reduce .venv size
    && find /opt/.venv -type d -name "__pycache__"  -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/.venv -type d -name "tests"        -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/.venv -type d -name "*.dist-info"  -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/.venv -type f -name "*.pyc"        -delete 2>/dev/null || true

# ─── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PATH="/opt/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # ✅ Prevent BLAS/numpy thread explosion
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1

# ✅ Runtime only — no gcc/g++ in final image
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copy only .venv from builder — no compiler tools
COPY --from=builder /opt/.venv /opt/.venv

# ✅ Copy only app source
COPY . .

EXPOSE 8030

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8030/health || exit 1

# ✅ workers=1 prevents RAM explosion — scale via docker compose instead
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8030", \
     "--workers", "1", \
     "--loop", "uvloop", \
     "--limit-concurrency", "100", \
     "--backlog", "128"]
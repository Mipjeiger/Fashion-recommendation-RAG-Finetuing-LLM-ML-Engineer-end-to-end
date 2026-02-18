FROM python:3.11-slim

# ---------------------
# Env
# ---------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=api.django_app.settings

# ---------------------
# System deps (runtime only)
# ---------------------
RUN apt-get update && apt-get install -y \
    libpq5 \
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
 && pip install --no-cache-dir -r requirements-web.txt

# ---------------------
# App code
# ---------------------
COPY api/django_app ./api/django_app
COPY streaming ./streaming

# ---------------------
# Run
# ---------------------
EXPOSE 8000
CMD ["gunicorn", "api.django_app.wsgi:application", "--bind", "0.0.0.0:8000"]
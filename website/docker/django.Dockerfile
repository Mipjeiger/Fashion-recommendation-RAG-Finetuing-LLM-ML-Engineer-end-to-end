FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
build-essential \
libpq-dev \
curl \
&& rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY api/django_app ./api/django_app
COPY streaming ./streaming

# Env
ENV PYTHONBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=api.django_app.settings

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "api.django_app.wsgi:application", "--bind", "0.0.0.0:8000"]
# ⚠️ AUTO-GENERATED REQUIREMENTS.TXT
# This image uses a synced requirements.txt.
# To regenerate (after editing base):
#    ./sync-requirements.sh
# Then rebuild:
#    docker compose build ingest-service

# Base image
FROM python:3.11-slim

# Prevent Python from writing bytecode and buffer output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r ingest && \
    useradd -r -g ingest -d /app ingestuser && \
    chown -R ingestuser:ingest /app

USER ingestuser

# Expose ingest port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

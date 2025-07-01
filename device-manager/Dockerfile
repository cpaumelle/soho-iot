# Version 1.3.3 – 2025-07-01 01:31
# ⚠️ AUTO-GENERATED REQUIREMENTS.TXT
# This image depends on a generated requirements.txt.
# Do NOT manually edit it — instead, regenerate using:
#    ./sync-requirements.sh
# Then rebuild:
#    docker compose build device-manager

# Base image
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

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

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app

# Create non-root user for security
RUN groupadd -r devicemanager && \
    useradd -r -g devicemanager -d /app deviceuser && \
    chown -R deviceuser:devicemanager /app

# Switch to non-root user
USER deviceuser

# Expose service port
EXPOSE 9000

# Entry point for Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
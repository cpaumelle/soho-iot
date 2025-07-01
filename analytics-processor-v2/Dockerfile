# ⚠️ AUTO-GENERATED REQUIREMENTS.TXT
# This image expects a pre-generated requirements.txt.
# Do NOT edit it manually — regenerate using:
#    ./sync-requirements.sh
# Then rebuild:
#    docker compose build analytics-processor

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1     PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --default-timeout=120 --no-cache-dir -r requirements.txt -i https://pypi.org/simple

COPY . .

RUN groupadd -r analytics && useradd -r -g analytics analyticsuser && chown -R analyticsuser:analytics /app
USER analyticsuser

EXPOSE 7000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7000"]

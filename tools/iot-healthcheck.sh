#!/bin/bash
# iot-healthcheck.sh — SenseMy IoT Environment Verifier
# Version: 1.3.0 (2025-07-01 UTC+00:00)
#
# This script:
# 1. Loads environment variables from /home/charles/iot/.env
# 2. Checks container health for device manager, ingest, and analytics
# 3. Verifies PostgreSQL connection to all databases
# 4. Tests HTTP/S endpoint accessibility via local reverse proxy
#
# Outputs system status and highlights any failure points.

set -euo pipefail

ENV_PATH="/home/charles/iot/.env"
if [[ ! -f "$ENV_PATH" ]]; then
    echo "❌ Missing .env at $ENV_PATH"
    exit 1
fi

echo "🔧 Loading .env from $ENV_PATH"
set -a
source "$ENV_PATH"
set +a

# Ensure required variables exist
: "${DEVICE_DB_USER:?Missing DEVICE_DB_USER in .env}"
: "${DEVICE_DB_PASSWORD:?Missing DEVICE_DB_PASSWORD in .env}"
: "${DEVICE_DB_NAME:?Missing DEVICE_DB_NAME in .env}"
: "${DEVICE_DB_HOST:?Missing DEVICE_DB_HOST in .env}"
: "${DEVICE_DB_PORT:?Missing DEVICE_DB_PORT in .env}"

: "${INGEST_DB_USER:?Missing INGEST_DB_USER in .env}"
: "${INGEST_DB_PASSWORD:?Missing INGEST_DB_PASSWORD in .env}"
: "${INGEST_DB_NAME:?Missing INGEST_DB_NAME in .env}"
: "${INGEST_DB_HOST:?Missing INGEST_DB_HOST in .env}"
: "${INGEST_DB_PORT:?Missing INGEST_DB_PORT in .env}"

: "${ANALYTICS_DB_USER:?Missing ANALYTICS_DB_USER in .env}"
: "${ANALYTICS_DB_PASSWORD:?Missing ANALYTICS_DB_PASSWORD in .env}"
: "${ANALYTICS_DB_NAME:?Missing ANALYTICS_DB_NAME in .env}"
: "${ANALYTICS_DB_HOST:?Missing ANALYTICS_DB_HOST in .env}"
: "${ANALYTICS_DB_PORT:?Missing ANALYTICS_DB_PORT in .env}"

echo ""
echo "🚀 Checking service health endpoints..."

# Local container endpoints
curl -sf "http://localhost:${DEVICE_MANAGER_SERVICE_PORT}/health" && echo "✅ Device Manager OK" || echo "❌ Device Manager NOT responding"
curl -sf "http://localhost:${INGEST_SERVICE_PORT}/health" && echo "✅ Ingest Service OK" || echo "❌ Ingest Service NOT responding"
curl -sf "http://localhost:${ANALYTICS_SERVICE_PORT}/health" && echo "✅ Analytics Processor OK" || echo "❌ Analytics Processor NOT responding"

echo ""
echo "🔗 Checking database connections..."

# PostgreSQL checks
check_pg() {
    local name=$1 host=$2 port=$3 db=$4 user=$5 pass=$6
    echo -n "🔎 $name DB: "
    PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d "$db" -c '\q' 2>/dev/null \
        && echo "✅ Connected" || echo "❌ Failed to connect"
}

check_pg "Device" "localhost" 5434 "$DEVICE_DB_NAME" "$DEVICE_DB_USER" "$DEVICE_DB_PASSWORD"
check_pg "Ingest" "localhost" 5433 "$INGEST_DB_NAME" "$INGEST_DB_USER" "$INGEST_DB_PASSWORD"
check_pg "Analytics" "localhost" 5435 "$ANALYTICS_DB_NAME" "$ANALYTICS_DB_USER" "$ANALYTICS_DB_PASSWORD"

echo ""
echo "🌐 Checking public endpoints..."

# Public URLs
check_url() {
    local name=$1 url=$2
    curl -sf "$url" >/dev/null && echo "✅ $name OK ($url)" || echo "❌ $name NOT responding ($url)"
}

check_url "Adminer UI" "https://adminer.sensemy.cloud"
check_url "Device Manager API" "https://api.sensemy.cloud/health"
check_url "Ingest API" "https://ingest.sensemy.cloud/health"
check_url "Analytics API" "https://analytics.sensemy.cloud/health"
check_url "Device App UI" "https://app.sensemy.cloud/v1/dashboard.html"
echo ""
# frontend API endpoints
echo "🧪 Testing frontend API endpoints used by the UI..."

test_api() {
  name=$1
  url=$2
  if curl -sf "$url" | jq . >/dev/null 2>&1; then
    echo "✅ $name OK ($url)"
  else
    echo "❌ $name FAILED ($url)"
  fi
}

API_BASE="https://api.sensemy.cloud/v1/devices"

test_api "Device Registry" "$API_BASE"
test_api "Uplinks" "$API_BASE/api/uplinks?limit=1"
test_api "Summary" "$API_BASE/api/summary"
test_api "Device Types" "$API_BASE/api/device-types"
test_api "Sites" "$API_BASE/api/sites"
test_api "Locations" "$API_BASE/api/locations"
echo ""
echo "✅ Health check complete."
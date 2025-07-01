#!/bin/bash
# SenseMy IoT Platform: Configuration Export Script
# Version: 1.2.0
# Last Updated: 2025-06-29
# Description: Exports configuration variables from unified-database-config.yml

# Verify yq is installed and working
if ! command -v yq &> /dev/null; then
    echo "Error: yq is not installed. Please install it first."
    exit 1
fi

# Verify configuration file exists
CONFIG_FILE="$HOME/iot/unified-database-config.yml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Test yq can read the file
if ! yq eval '.services' "$CONFIG_FILE" > /dev/null 2>&1; then
    echo "Error: Cannot parse YAML configuration file: $CONFIG_FILE"
    exit 1
fi

# Export Ingest Service Configuration
export INGEST_DB_HOST=$(yq eval '.ingest_database.host' "$CONFIG_FILE")
export INGEST_DB_PORT=$(yq eval '.ingest_database.port' "$CONFIG_FILE")
export INGEST_DB_NAME=$(yq eval '.ingest_database.database' "$CONFIG_FILE")
export INGEST_DB_USER=$(yq eval '.ingest_database.username' "$CONFIG_FILE")
export INGEST_DB_PASSWORD=$(yq eval '.ingest_database.password' "$CONFIG_FILE")
export INGEST_SERVICE_PORT=$(yq eval '.services.ingest.port' "$CONFIG_FILE")

# Export Device Manager Service Configuration
export DEVICE_DB_HOST=$(yq eval '.device_database.host' "$CONFIG_FILE")
export DEVICE_DB_PORT=$(yq eval '.device_database.port' "$CONFIG_FILE")
export DEVICE_DB_NAME=$(yq eval '.device_database.database' "$CONFIG_FILE")
export DEVICE_DB_USER=$(yq eval '.device_database.username' "$CONFIG_FILE")
export DEVICE_DB_PASSWORD=$(yq eval '.device_database.password' "$CONFIG_FILE")
export DEVICE_MANAGER_SERVICE_PORT=$(yq eval '.services.device_manager.port' "$CONFIG_FILE")

# Export Analytics Service Configuration
export ANALYTICS_DB_HOST=$(yq eval '.analytics_database.host' "$CONFIG_FILE")
export ANALYTICS_DB_PORT=$(yq eval '.analytics_database.port' "$CONFIG_FILE")
export ANALYTICS_DB_NAME=$(yq eval '.analytics_database.database' "$CONFIG_FILE")
export ANALYTICS_DB_USER=$(yq eval '.analytics_database.username' "$CONFIG_FILE")
export ANALYTICS_DB_PASSWORD=$(yq eval '.analytics_database.password' "$CONFIG_FILE")
export ANALYTICS_SERVICE_PORT=$(yq eval '.services.analytics.port' "$CONFIG_FILE")

# Export Common Configuration
export LOG_LEVEL=$(yq eval '.logging.level' "$CONFIG_FILE")
export NETWORK_NAME=$(yq eval '.network.name' "$CONFIG_FILE")

# Verify all critical variables are set
REQUIRED_VARS=(
    "INGEST_SERVICE_PORT"
    "DEVICE_MANAGER_SERVICE_PORT" 
    "ANALYTICS_SERVICE_PORT"
    "INGEST_DB_HOST"
    "DEVICE_DB_HOST"
    "ANALYTICS_DB_HOST"
    "LOG_LEVEL"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "null" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "Error: Missing or null required variables:"
    printf '%s\n' "${MISSING_VARS[@]}"
    exit 1
fi

# Success message (only show when script is run directly, not sourced)
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    echo "✅ Configuration variables exported successfully"
    echo "Key variables:"
    echo "  INGEST_SERVICE_PORT: $INGEST_SERVICE_PORT"
    echo "  DEVICE_MANAGER_SERVICE_PORT: $DEVICE_MANAGER_SERVICE_PORT"
    echo "  ANALYTICS_SERVICE_PORT: $ANALYTICS_SERVICE_PORT"
    echo "  LOG_LEVEL: $LOG_LEVEL"
fi

#!/bin/bash
# SenseMy IoT Platform: Deployment Script
# Version: 1.3.1
# Last Updated: 2025-06-29

# Exit on any error
set -e

# Color codes for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[DEPLOY]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Ensure script is run from the correct directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || error "Cannot change to script directory"

# Load configuration
CONFIG_FILE="unified-database-config.yml"
if [ ! -f "$CONFIG_FILE" ]; then
    error "Configuration file $CONFIG_FILE not found"
fi

# Verify required tools
for tool in docker docker-compose yq; do
    if ! command -v "$tool" &> /dev/null; then
        error "$tool is not installed"
    fi
done

# Create external network if not exists
NETWORK_NAME=$(yq e '.network.name' "$CONFIG_FILE")
if ! docker network inspect "$NETWORK_NAME" &> /dev/null; then
    log "Creating external network: $NETWORK_NAME"
    docker network create "$NETWORK_NAME" || error "Failed to create network"
fi

# Source environment variables
log "Sourcing configuration variables"
source ./unified-database-config.sh || error "Failed to source configuration script"

# Pre-deployment cleanup
log "Stopping and removing existing containers"
docker stop $(docker ps -a -q) 2>/dev/null || true
docker rm $(docker ps -a -q) 2>/dev/null || true

# Verify docker-compose files
log "Validating docker-compose configurations"
docker-compose -f docker-compose.yml config > /dev/null || error "Invalid docker-compose configuration"

# Pull latest images
log "Pulling latest images"
docker-compose pull || warn "Some images could not be pulled"

# Deploy services
log "Starting IoT Platform Services"
docker-compose up -d || error "Deployment failed"

# Verify services are running
log "Checking service health"
SERVICES=$(docker-compose ps --services)
for service in $SERVICES; do
    if ! docker-compose ps "$service" | grep -q "Up"; then
        warn "Service $service is not running correctly"
    fi
done

# Final health check
log "Performing health checks"
for domain in ingest.sensemy.cloud api.sensemy.cloud analytics.sensemy.cloud; do
    if curl -s -f "https://$domain/health" > /dev/null; then
        log "✅ $domain is responsive"
    else
        warn "❌ $domain is not responding"
    fi
done

log "🚀 Deployment completed successfully!"

exit 0

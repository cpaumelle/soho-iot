#!/bin/bash
# Verify docker-compose files in service directories

# Base directory
BASE_DIR=~/iot

# Services to verify
SERVICES=(
    "device-manager"
    "ingest-server"
    "analytics-processor-v2"
)

# Function to verify docker-compose file
verify_service_docker_compose() {
    local service_dir="$1"
    local compose_file="$service_dir/docker-compose.yml"
    
    if [ ! -f "$compose_file" ]; then
        echo "No docker-compose.yml found in $service_dir"
        return
    fi

    echo "Verifying $compose_file:"
    
    # Check network name
    if grep -q "sensemy\.net" "$compose_file"; then
        echo "  ❌ Network name 'sensemy.net' still present"
    else
        echo "  ✅ Network name updated"
    fi

    # Check network configuration
    if grep -q "sensemy_network:" "$compose_file" && grep -q "external: true" "$compose_file"; then
        echo "  ✅ Network configuration correct"
    else
        echo "  ❌ Network configuration needs review"
    fi

    # Check port mappings
    echo "  Port mappings:"
    grep "ports:" "$compose_file"
}

# Main script
echo "Verifying service-specific docker-compose files"

for service in "${SERVICES[@]}"; do
    verify_service_docker_compose "$BASE_DIR/$service"
    echo "---"
done

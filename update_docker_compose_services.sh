#!/bin/bash
# Script to update docker-compose files in service directories

# Base directory
BASE_DIR=~/iot

# Services to update
SERVICES=(
    "device-manager"
    "ingest-server"
    "analytics-processor-v2"
)

# Function to update docker-compose file
update_service_docker_compose() {
    local service_dir="$1"
    local compose_file="$service_dir/docker-compose.yml"
    
    if [ ! -f "$compose_file" ]; then
        echo "No docker-compose.yml found in $service_dir"
        return
    fi

    # Backup the original file
    cp "$compose_file" "${compose_file}.bak"

    # Replace network name and configuration
    sed -i 's/sensemy\.net/sensemy_network/g' "$compose_file"

    # Ensure networks section is consistent
    if ! grep -q "networks:" "$compose_file"; then
        # Add networks section at the end of the file
        echo "
networks:
  sensemy_network:
    external: true" >> "$compose_file"
    elif ! grep -q "sensemy_network:" "$compose_file"; then
        # Modify existing networks section
        sed -i 's/networks:/networks:\n  sensemy_network:\n    external: true/g' "$compose_file"
    fi

    echo "Updated $compose_file"
}

# Main script
echo "Updating service-specific docker-compose files"

for service in "${SERVICES[@]}"; do
    update_service_docker_compose "$BASE_DIR/$service"
done

echo "Service docker-compose file updates complete."

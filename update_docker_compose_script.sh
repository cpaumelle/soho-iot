#!/bin/bash
# Script to update docker-compose files in IoT platform services

# Directories to check
SERVICES=(
    "device-manager"
    "ingest-server"
    "analytics-processor-v2"
)

# Function to update docker-compose file
update_docker_compose() {
    local service_dir="$1"
    local compose_file="$service_dir/docker-compose.yml"
    
    if [ ! -f "$compose_file" ]; then
        echo "No docker-compose.yml found in $service_dir"
        return
    fi

    # Replace sensemy.net with sensemy_network
    sed -i 's/sensemy\.net/sensemy_network/g' "$compose_file"

    # Update network configuration
    if ! grep -q "external: true" "$compose_file"; then
        # Add network configuration if not present
        sed -i '/networks:/,/^$/c\networks:\n  sensemy_network:\n    external: true' "$compose_file"
    fi

    echo "Updated $compose_file"
}

# Main script
echo "Updating docker-compose files in IoT platform services"

for service in "${SERVICES[@]}"; do
    update_docker_compose "$HOME/iot/$service"
done

echo "Docker Compose file updates complete."

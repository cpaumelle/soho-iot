#!/bin/bash

OUTPUT_FILE="iot_codebase_complete.txt"
echo "=== IoT MULTI-CONTAINER APPLICATION CODEBASE REVIEW ===" > $OUTPUT_FILE
echo "Generated on: $(date)" >> $OUTPUT_FILE
echo "Directory: $(pwd)" >> $OUTPUT_FILE
echo "System: Linux mint-9dbc 6.1.0-37-amd64" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Function to add file content with header
add_file_content() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "=== FILE: $file ===" >> $OUTPUT_FILE
        echo "" >> $OUTPUT_FILE
        cat "$file" >> $OUTPUT_FILE
        echo "" >> $OUTPUT_FILE
        echo "=== END OF FILE: $file ===" >> $OUTPUT_FILE
        echo "" >> $OUTPUT_FILE
    fi
}

# Add directory structure
echo "=== COMPLETE DIRECTORY STRUCTURE ===" >> $OUTPUT_FILE
tree -a -I '__pycache__|*.pyc|node_modules|.git|*.log|.venv|sensemy-iot-env' >> $OUTPUT_FILE 2>/dev/null
echo "" >> $OUTPUT_FILE

# Main configuration files
echo "=== MAIN CONFIGURATION FILES ===" >> $OUTPUT_FILE
add_file_content "docker-compose.yml"
add_file_content ".env"
add_file_content ".env.example"
add_file_content ".env.local"
add_file_content ".env.production"

# Caddy/Reverse Proxy Configuration
echo "=== REVERSE PROXY CONFIGURATION ===" >> $OUTPUT_FILE
add_file_content "unified-caddyfile"
add_file_content "Caddyfile"
find . -name "*caddy*" -type f | head -10 | while read file; do
    add_file_content "$file"
done

# All Dockerfiles
echo "=== DOCKERFILES ===" >> $OUTPUT_FILE
find . -name "Dockerfile*" -type f | while read file; do
    add_file_content "$file"
done

# Service-specific configurations
echo "=== ANALYTICS PROCESSOR CONFIGURATION ===" >> $OUTPUT_FILE
add_file_content "analytics-processor-v2/requirements.txt"
add_file_content "analytics-processor-v2/app/main.py"
add_file_content "analytics-processor-v2/app/__init__.py"
add_file_content "analytics-processor-v2/config/config.py"
find analytics-processor-v2 -name "*.py" -path "*/api/*" | head -5 | while read file; do
    add_file_content "$file"
done

echo "=== DEVICE MANAGER CONFIGURATION ===" >> $OUTPUT_FILE
add_file_content "device-manager/requirements.txt"
add_file_content "device-manager/app/main.py"
add_file_content "device-manager/app/__init__.py"
find device-manager -name "*.py" -path "*/routers/*" | head -5 | while read file; do
    add_file_content "$file"
done

echo "=== INGEST SERVICE CONFIGURATION ===" >> $OUTPUT_FILE
add_file_content "ingest-server/requirements.txt"
add_file_content "ingest-server/app/main.py"
add_file_content "ingest-server/app/__init__.py"
find ingest-server -name "*.py" -path "*/routers/*" | head -5 | while read file; do
    add_file_content "$file"
done

# Database initialization scripts
echo "=== DATABASE INITIALIZATION ===" >> $OUTPUT_FILE
find . -path "*/initdb/*" -name "*.sql" | while read file; do
    add_file_content "$file"
done

# UI Versions
echo "=== UI VERSIONS CONFIGURATION ===" >> $OUTPUT_FILE
find ui-versions -name "index.html" | while read file; do
    add_file_content "$file"
done

# Any nginx or apache configs
echo "=== WEB SERVER CONFIGS ===" >> $OUTPUT_FILE
find . -name "*.conf" -o -name "nginx.conf" -o -name "*.nginx" | while read file; do
    add_file_content "$file"
done

# Package files
echo "=== PACKAGE DEPENDENCIES ===" >> $OUTPUT_FILE
find . -name "requirements.txt" | while read file; do
    add_file_content "$file"
done
find . -name "package.json" | while read file; do
    add_file_content "$file"
done

# Any shell scripts
echo "=== SHELL SCRIPTS ===" >> $OUTPUT_FILE
find . -name "*.sh" -type f | head -10 | while read file; do
    add_file_content "$file"
done

# Configuration files from services
echo "=== SERVICE CONFIG FILES ===" >> $OUTPUT_FILE
find . -name "config.py" -o -name "settings.py" -o -name "config.yml" -o -name "config.yaml" | while read file; do
    add_file_content "$file"
done

echo "=== COLLECTION COMPLETE ===" >> $OUTPUT_FILE
echo "Total files processed: $(grep -c '=== FILE:' $OUTPUT_FILE)" >> $OUTPUT_FILE

#!/bin/bash
# SenseMy IoT Platform: Deployment Orchestrating Guardian
# Version: 1.3.1
# Last Updated: 2025-06-30
# Description: Enhanced debugging for configuration validation
# Changelog:
#   - Added detailed logging for configuration troubleshooting
#   - Improved error tracking in docker-compose configuration validation

<<'DOCUMENTATION'
# 🌐 IoT Platform Service Management Script

## Purpose
This script provides a robust, centralized management tool for the entire SenseMy IoT platform,
designed to handle complex multi-service deployments with built-in safety and diagnostic features.

## When to Use
- Before major configuration changes
- During system upgrades
- Troubleshooting deployment issues
- Performing full system restarts
- Validating platform configuration

## Key Capabilities
- Graceful stopping of all platform services
- Controlled, step-by-step service startup
- Comprehensive configuration validation
- Detailed logging and error tracking
- Service connectivity verification

## Usage Examples
./iot_deployment_orchestrating_guardian.sh stop      # Completely shut down all services
./iot_deployment_orchestrating_guardian.sh start     # Start all services
./iot_deployment_orchestrating_guardian.sh restart   # Full restart of all services
./iot_deployment_orchestrating_guardian.sh validate  # Check configuration without modifying services

## Safety Features
- Logs all actions with fallback logging locations
- Provides color-coded console output
- Diagnoses and reports specific service failures
- Validates configuration before starting services
- Global error tracking and reporting

## Requirements
- Docker and Docker Compose installed
- Unified configuration file at ~/iot/unified-database-config.yml
- Working unified-database-config.sh script
- Correct yq YAML processor (mikefarah/yq) installed
- Sufficient permissions to manage Docker services

## Fixes in Version 1.3.0
- Fixed validation return logic (bash 0=success, 1=failure)
- Improved configuration loading and error handling
- Enhanced environment variable validation
- Better logging and diagnostics

## Caution
- This script has significant system impact
- Always review logs after execution
- Recommended for use by system administrators
DOCUMENTATION

# Ensure log file is writable and in a location the user can access
LOG_FILE="$HOME/sensemy_service_management.log"

# Ensure log file is writable
touch "$LOG_FILE" 2>/dev/null
if [ ! -w "$LOG_FILE" ]; then
    # Fallback to a log file in a writable directory
    LOG_FILE="/tmp/sensemy_service_management.log"
    touch "$LOG_FILE" 2>/dev/null
fi

# Initialize global error tracking
GLOBAL_ERROR_COUNT=0
FAILED_SERVICES=()

# Color definitions for console output
GREEN='\033[0;32m'    # Success messages
RED='\033[0;31m'      # Error messages
YELLOW='\033[1;33m'   # Warning messages
NC='\033[0m'          # No Color (reset)

# Logging function with enhanced error tracking
log() {
    local level=$1
    local message=$2
    local color=$NC

    case $level in
        "INFO")
            color=$GREEN
            ;;
        "ERROR")
            color=$RED
            ((GLOBAL_ERROR_COUNT++))
            FAILED_SERVICES+=("$message")
            ;;
        "WARN")
            color=$YELLOW
            ;;
    esac

    # Output to console and log file
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] $level: $message${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $level: $message" >> "$LOG_FILE"
}

# Projects to manage (in specific order for startup/shutdown)
PROJECTS_STOP=(
    "$HOME/iot/analytics-processor-v2"
    "$HOME/iot/device-manager"
    "$HOME/iot/ingest-server"
    "$HOME/iot"
)

PROJECTS_START=(
    "$HOME/iot"
    "$HOME/iot/ingest-server"
    "$HOME/iot/device-manager"
    "$HOME/iot/analytics-processor-v2"
)

# Enhanced service management with environment validation and error isolation
manage_project_services() {
    local action=$1
    local project=$2
    local result=0

    log "INFO" "Processing $project with action: $action"

    # Expand to full path and change to project directory
    local expanded_project
    expanded_project=$(eval echo "$project")

    if [ ! -d "$expanded_project" ]; then
        log "ERROR" "Directory does not exist: $expanded_project"
        return 1
    fi

    cd "$expanded_project" || {
        log "ERROR" "Cannot change to directory $expanded_project"
        return 1
    }

    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ] && [ ! -f "docker-compose.yaml" ]; then
        log "WARN" "No docker-compose file found in $expanded_project, skipping..."
        return 0
    fi

    # Validate docker-compose file before proceeding
    log "INFO" "Validating docker-compose configuration in $expanded_project"
    # DEBUG: Detailed logging for configuration troubleshooting
    log "DEBUG" "Current working directory: $(pwd)"
    log "DEBUG" ".env file contents:"
    cat .env | while IFS= read -r line; do
        log "DEBUG" "ENV LINE: $line"
    done

log "DEBUG" "Docker Compose configuration:"
docker-compose config || true
    if ! docker-compose config > /dev/null 2>&1; then
        log "WARN" "Docker-compose configuration has issues in $expanded_project"
        log "INFO" "Attempting to diagnose configuration problems..."

        # Check for .env file issues
        if [ -f ".env" ]; then
            log "INFO" "Checking .env file format..."
            # Check for common .env file issues
            if grep -q "^[[:space:]]*$" .env; then
                log "WARN" "Found empty lines in .env file"
            fi
            if grep -q "^[^A-Za-z_]" .env; then
                log "WARN" "Found invalid line starting in .env file (line 1 issue)"
            fi
        fi

        # For stop operations, try to force stop even with config issues
        if [ "$action" = "down" ]; then
            log "WARN" "Attempting forced stop despite configuration issues..."
            local running_containers
            running_containers=$(docker ps -q --filter "label=com.docker.compose.project=$(basename "$expanded_project")" 2>/dev/null)
            if [ -n "$running_containers" ]; then
                if docker stop $running_containers 2>/dev/null; then
                    log "INFO" "Force stopped containers in $expanded_project"
                fi
            fi
            return 0
        else
            log "ERROR" "Cannot start services with invalid configuration in $expanded_project"
            return 1
        fi
    fi

    # Perform specified action with error handling
    case $action in
        "down")
            log "INFO" "Stopping services in $expanded_project"
            if ! docker-compose down; then
                log "ERROR" "Failed to stop services in $expanded_project"
                result=1
            else
                log "INFO" "Successfully stopped services in $expanded_project"
            fi
            ;;
        "up")
            log "INFO" "Starting services in $expanded_project"
            if ! docker-compose up -d; then
                log "ERROR" "Failed to start services in $expanded_project"
                result=1
            else
                log "INFO" "Successfully started services in $expanded_project"
            fi
            ;;
        *)
            log "ERROR" "Invalid action $action for $expanded_project"
            result=1
            ;;
    esac

    return $result
}

# Comprehensive service stop function
stop_all_services() {
    log "INFO" "🛑 Initiating comprehensive service shutdown..."

    # Track individual project stop results
    local overall_result=0

    for project in "${PROJECTS_STOP[@]}"; do
        manage_project_services "down" "$project" || overall_result=1
    done

    # Forceful cleanup of any remaining containers
    log "WARN" "Performing forceful container cleanup..."
    local running_containers
    running_containers=$(docker ps -q 2>/dev/null)
    if [ -n "$running_containers" ]; then
        if docker stop $running_containers 2>/dev/null; then
            log "INFO" "Stopped remaining running containers"
        fi
    fi

    local all_containers
    all_containers=$(docker ps -a -q 2>/dev/null)
    if [ -n "$all_containers" ]; then
        if docker rm $all_containers 2>/dev/null; then
            log "INFO" "Removed all containers"
        fi
    fi

    return $overall_result
}

# Configuration validation function
validate_configuration() {
    log "INFO" "🔐 Validating platform configuration..."

    # Check configuration files
    local config_files=(
        "$HOME/iot/unified-database-config.yml"
        "$HOME/iot/unified-database-config.sh"
    )

    local config_valid=0  # Fixed: 0=success, 1=failure (bash standard)

    for file in "${config_files[@]}"; do
        local expanded_file
        expanded_file=$(eval echo "$file")
        if [ ! -f "$expanded_file" ]; then
            log "ERROR" "Missing configuration file: $expanded_file"
            config_valid=1  # Fixed: 1=failure
        else
            log "INFO" "Configuration file found: $expanded_file"
        fi
    done

    # Source and check environment variables if config script exists
    local config_script="$HOME/iot/unified-database-config.sh"
    local expanded_config_script
    expanded_config_script=$(eval echo "$config_script")

    if [ -f "$expanded_config_script" ]; then
        log "INFO" "Loading configuration from $expanded_config_script"

        # Source the configuration script and capture any errors
        if source "$expanded_config_script"; then
            log "INFO" "Configuration script loaded successfully"
        else
            log "ERROR" "Failed to source configuration script: $expanded_config_script"
            config_valid=1  # Fixed: 1=failure
            return $config_valid
        fi

        local required_vars=(
            "INGEST_SERVICE_PORT"
            "DEVICE_MANAGER_SERVICE_PORT"
            "ANALYTICS_SERVICE_PORT"
            "INGEST_DB_HOST"
            "DEVICE_DB_HOST"
            "ANALYTICS_DB_HOST"
            "LOG_LEVEL"
        )

        for var in "${required_vars[@]}"; do
            if [ -z "${!var}" ] || [ "${!var}" = "null" ]; then
                log "ERROR" "Required environment variable $var is not set or is null"
                config_valid=1  # Fixed: 1=failure
            else
                log "INFO" "$var is set to ${!var}"
            fi
        done
    else
        log "ERROR" "Configuration script not found: $expanded_config_script"
        config_valid=1  # Fixed: 1=failure
    fi

    return $config_valid  # Now returns 0=success, 1=failure
}

# Comprehensive service start function
start_all_services() {
    log "INFO" "🚀 Initiating comprehensive service startup..."

    # Validate configuration first
    if ! validate_configuration; then
        log "ERROR" "Configuration validation failed. Aborting startup."
        return 1
    fi

    # Source configuration to ensure environment variables are available
    log "INFO" "Loading configuration for service startup..."
    source "$HOME/iot/unified-database-config.sh"

    # Track individual project start results
    local overall_result=0

    for project in "${PROJECTS_START[@]}"; do
        manage_project_services "up" "$project" || overall_result=1
    done

    # Additional connectivity checks
    check_services

    return $overall_result
}

# Service connectivity check
check_services() {
    log "INFO" "🔍 Checking service connectivity..."

    local services=(
        "https://ingest.sensemy.cloud/health"
        "https://api.sensemy.cloud/health"
        "https://analytics.sensemy.cloud/health"
    )

    local connectivity_result=0

    for service in "${services[@]}"; do
        log "INFO" "Checking $service"
        if curl -sf "$service" > /dev/null 2>&1; then
            log "INFO" "✅ $service is responding"
        else
            log "ERROR" "❌ $service is not responding"
            ((connectivity_result++))
        fi
    done

    return $connectivity_result
}

# Final reporting function
report_status() {
    echo ""
    echo "🏁 Service Management Report 🏁"
    echo "============================="
    echo "Total Errors: $GLOBAL_ERROR_COUNT"
    echo "Log file: $LOG_FILE"

    if [ $GLOBAL_ERROR_COUNT -gt 0 ]; then
        echo "Failed Services/Components:"
        printf '%s\n' "${FAILED_SERVICES[@]}"
        echo ""
        echo "❌ Operation completed with errors. Check log file for details."
        exit 1
    else
        echo "✅ All operations completed successfully"
        exit 0
    fi
}

# Main execution function
main() {
    local action=$1

    # Reset global error tracking
    GLOBAL_ERROR_COUNT=0
    FAILED_SERVICES=()

    log "INFO" "🌐 SenseMy IoT Platform Service Management"
    log "INFO" "Version: 1.3.0 (Fixed validation logic)"
    log "INFO" "Action: $action"
    log "INFO" "Log file: $LOG_FILE"

    case $action in
        "stop")
            stop_all_services
            ;;
        "start")
            start_all_services
            ;;
        "restart")
            stop_all_services
            sleep 2  # Brief pause between stop and start
            start_all_services
            ;;
        "validate")
            validate_configuration
            ;;
        *)
            log "ERROR" "Invalid action. Use: stop, start, restart, validate"
            echo ""
            echo "Usage: $0 {stop|start|restart|validate}"
            echo ""
            echo "  stop     - Stop all IoT platform services"
            echo "  start    - Start all IoT platform services (with validation)"
            echo "  restart  - Stop and start all services"
            echo "  validate - Validate configuration without starting/stopping services"
            exit 1
            ;;
    esac

    # Generate final report
    report_status
}

# Script entry point
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$1"
fi
charles@mint-9dbc:~/iot$

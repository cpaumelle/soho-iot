#!/bin/bash
# SenseMy IoT Platform: Python Environment Management Script
# Version: 1.0.0
# Last Updated: 2025-06-29

<<'DOCUMENTATION'
# [Previous documentation remains the same]
DOCUMENTATION

# Prevent script from running if any command fails
set -e

# Ensure robust error handling and logging
set -o pipefail

# Color codes for enhanced output
GREEN='\033[0;32m'     # Success messages
YELLOW='\033[1;33m'    # Warning messages
RED='\033[0;31m'       # Error messages
NC='\033[0m'           # No Color (reset)

# Base directory for storing all virtual environments
VENV_BASE_DIR="$HOME/.sensemy-iot-venvs"

# Create base directory if it doesn't exist
mkdir -p "$VENV_BASE_DIR"

# NEW: Function to ensure virtual environment tools are accessible
ensure_venv_tools() {
    local venv_path=$1

    # Add the virtual environment's bin directory to PATH temporarily
    export PATH="$venv_path/bin:$PATH"

    # Verify tools are now accessible
    echo "Checking installed tools:"
    command -v pip-tools && pip-tools --version
    command -v safety && safety --version
    command -v pip-audit && pip-audit --version
}

# Function to create a new virtual environment
create_venv() {
    local project_name=$1
    local venv_path="$VENV_BASE_DIR/$project_name"

    # Check if virtual environment already exists to prevent accidental overwriting
    if [ -d "$venv_path" ]; then
        echo -e "${YELLOW}Virtual environment for $project_name already exists.${NC}"
        return 1
    fi

    # Create virtual environment using Python's built-in venv module
    python3 -m venv "$venv_path"
    
    # Activate and prepare the environment
    source "$venv_path/bin/activate"
    
    # Upgrade pip to latest version and install essential tools
    pip install --upgrade pip
    pip install pip-tools safety pip-audit
    
    # Ensure tools are accessible
    ensure_venv_tools "$venv_path"
    
    # Deactivate to return to base shell
    deactivate

    echo -e "${GREEN}Virtual environment created for $project_name at $venv_path${NC}"
}

# Function to activate an existing virtual environment
activate_venv() {
    local project_name=$1
    local venv_path="$VENV_BASE_DIR/$project_name"

    # Verify environment exists before attempting activation
    if [ ! -d "$venv_path" ]; then
        echo -e "${RED}Virtual environment for $project_name does not exist. Create it first.${NC}"
        return 1
    fi

    # Activate the virtual environment
    source "$venv_path/bin/activate"
    
    # Ensure tools are accessible
    ensure_venv_tools "$venv_path"

    echo -e "${GREEN}Activated virtual environment for $project_name${NC}"
}

# Function to list all available virtual environments
list_venvs() {
    echo "Available SenseMy IoT Virtual Environments:"
    ls "$VENV_BASE_DIR"
}

# Function to remove a virtual environment
remove_venv() {
    local project_name=$1
    local venv_path="$VENV_BASE_DIR/$project_name"

    # Check if environment exists
    if [ ! -d "$venv_path" ]; then
        echo -e "${RED}Virtual environment for $project_name does not exist.${NC}"
        return 1
    fi

    # Interactive confirmation before deletion
    read -p "Are you sure you want to remove the virtual environment for $project_name? (y/N) " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        rm -rf "$venv_path"
        echo -e "${GREEN}Virtual environment for $project_name removed.${NC}"
    else
        echo -e "${YELLOW}Removal cancelled.${NC}"
    fi
}

# Main script logic with robust argument handling
case "$1" in
    "create")
        create_venv "$2"
        ;;
    "activate")
        activate_venv "$2"
        ;;
    "list")
        list_venvs
        ;;
    "remove")
        remove_venv "$2"
        ;;
    *)
        echo "Usage: $0 {create|activate|list|remove} [project_name]"
        echo ""
        echo "  create [project_name]  - Create a new virtual environment"
        echo "  activate [project_name] - Activate an existing virtual environment"
        echo "  list                   - List available virtual environments"
        echo "  remove [project_name]  - Remove a virtual environment"
        exit 1
        ;;
esac

#!/bin/bash
# Script to verify environment configurations

# Find all .env files
echo "Searching for .env files:"
find ~/iot -name ".env*"

# Check deployment and configuration scripts for .env references
echo -e "\nChecking scripts for .env references:"
echo "Deployment Guardian Script:"
grep -n "\.env" ~/iot/iot_deployment_orchestrating_guardian.sh

# Check Docker Compose files for network and environment configurations
echo -e "\nChecking Docker Compose files for network configurations:"
for file in $(find ~/iot -name "docker-compose.yml"); do
    echo "$file:"
    grep -n "sensemy\." "$file" || echo "No sensemy.net references found"
    grep -n "networks:" "$file" || echo "No networks section found"
done

# Verify root .env file contents
echo -e "\nRoot .env file contents:"
cat ~/iot/.env

# Check for any environment-related configurations in other files
echo -e "\nSearching for additional environment-related configurations:"
grep -r "export " ~/iot | grep -E "\.env|ENVIRONMENT"

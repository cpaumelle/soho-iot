#!/bin/bash
echo "🔒 Database Safety Check"
echo "Current volume created: $(docker volume inspect iot_device_db_data | jq -r '.[0].CreatedAt')"
echo "Expected: Before 2025-06-23T09:00:00"
echo ""
echo "⚠️  NEVER run 'docker compose down -v' or 'docker volume rm'"
echo "✅  ALWAYS use 'docker compose down' (without -v)"
echo "✅  Database backups available in ~/iot/backups/"

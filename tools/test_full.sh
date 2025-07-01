#!/bin/bash
echo "🧪 Running comprehensive tests..."
~/iot/tools/test_locations.sh

echo ""
echo "📊 Database status:"
curl -s http://localhost:9000/v1/sites/ | jq -r 'length as $count | "Sites: \($count)"'

echo ""
echo "🐳 Container status:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(device-manager|soho-iot)"

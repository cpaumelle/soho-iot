#!/bin/bash

# More lenient version for debugging
API_BASE="http://localhost:9000/v1"
FRONTEND_BASE="http://10.44.1.221:8081/v1"

echo "🧪 Quick smoke test..."

# Test backend
echo "  Testing backend..."
if curl -s ${API_BASE}/sites/ > /dev/null; then
    echo "  ✅ Backend working"
else
    echo "  ❌ Backend failed"
    exit 1
fi

# Test frontend proxy
echo "  Testing frontend proxy..."
if curl -s ${FRONTEND_BASE}/sites/ > /dev/null; then
    echo "  ✅ Frontend proxy working"
else
    echo "  ❌ Frontend proxy failed"
    exit 1
fi

# Quick CRUD test
echo "  Testing CRUD..."
SITE_RESPONSE=$(curl -s -X POST ${API_BASE}/sites/ \
    -H "Content-Type: application/json" \
    -d '{"name": "Smoke Test", "latitude": 40.7, "longitude": -74.0}')

if echo $SITE_RESPONSE | grep -q '"id"'; then
    SITE_ID=$(echo $SITE_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
    curl -s -X DELETE ${API_BASE}/sites/${SITE_ID}/ > /dev/null
    echo "  ✅ CRUD working"
else
    echo "  ❌ CRUD failed"
    exit 1
fi

echo "🎉 Smoke test passed!"

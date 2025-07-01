#!/bin/bash
# Network Health Monitor

echo "🔍 IoT Network Health Check - $(date)"
echo "=================================="

# Check container IPs
for container in device-manager analytics-processor; do
    IP=$(docker inspect $container 2>/dev/null | jq -r '.[0].NetworkSettings.Networks."verdegris-iot-network".IPAddress // "NO_IP"')
    if [ "$IP" = "NO_IP" ] || [ -z "$IP" ]; then
        echo "❌ $container: No IP assigned!"
        echo "🔧 Fixing: docker restart $container"
        docker restart $container
    else
        echo "✅ $container: $IP"
    fi
done

# Test DNS resolution
echo -e "\nDNS Resolution Test:"
docker exec device-manager sh -c "getent hosts analytics-processor" > /dev/null 2>&1 && echo "✅ DNS working" || echo "❌ DNS failed"

# Test analytics connectivity
curl -s http://localhost:9000/health | jq -r '.analytics_forwarder.analytics_processor_healthy' | grep -q true && echo "✅ Analytics healthy" || echo "❌ Analytics unhealthy"

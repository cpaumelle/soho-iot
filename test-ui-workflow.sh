#!/bin/bash

# Verdegris IoT Platform - UI Workflow Test Script
# Tests both API endpoints and provides browser test instructions

set -e  # Exit on any error

API_BASE="https://api.sensemy.cloud"
APP_BASE="https://app.sensemy.cloud"

echo "🧪 Verdegris IoT Platform - UI Workflow Tests"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test function that checks HTTP status and validates JSON
test_api_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_fields=$4
    local data=$5
    
    print_status "Testing $method $endpoint - $description"
    
    local curl_cmd="curl -s -w '%{http_code}' -X $method '$API_BASE$endpoint'"
    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -H 'Content-Type: application/json' -d '$data'"
    fi
    
    local response=$(eval $curl_cmd)
    local http_code="${response: -3}"
    local body="${response%???}"
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        print_success "HTTP $http_code - Endpoint responding"
        
        # Validate JSON if expected fields provided
        if [ -n "$expected_fields" ]; then
            for field in $expected_fields; do
                if echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if '$field' in str(data) else 1)" 2>/dev/null; then
                    print_success "  ✓ Field '$field' present"
                else
                    print_warning "  ? Field '$field' not found (might be empty data)"
                fi
            done
        fi
        
        # Pretty print first few characters of response
        echo "  📄 Response preview: $(echo "$body" | head -c 100)..."
        echo ""
        return 0
    else
        print_error "HTTP $http_code - $body"
        echo ""
        return 1
    fi
}

echo "🔌 PART 1: API ENDPOINT TESTS"
echo "=============================="
echo ""

# Test core API endpoints
test_api_endpoint "GET" "/v1/summary" "Dashboard summary data" "total_devices uplinks_24h"
test_api_endpoint "GET" "/v1/sites" "Sites list" "id name"
test_api_endpoint "GET" "/v1/devices" "Devices list" "deveui status"
test_api_endpoint "GET" "/v1/zones" "Zones with hierarchy" "full_path location"
test_api_endpoint "GET" "/v1/locations/hierarchy" "Location hierarchy" "floors"

echo ""
echo "🌐 PART 2: FRONTEND FILE AVAILABILITY"
echo "====================================="
echo ""

# Test that frontend files are accessible
frontend_files=("dashboard.html" "sites.html" "locations.html" "devices.html" "api.js" "style.css")

for file in "${frontend_files[@]}"; do
    print_status "Testing frontend file: $file"
    http_code=$(curl -s -o /dev/null -w '%{http_code}' "$APP_BASE/$file")
    if [ "$http_code" -eq 200 ]; then
        print_success "✓ $file accessible (HTTP $http_code)"
    else
        print_error "✗ $file not accessible (HTTP $http_code)"
    fi
done

echo ""
echo "📊 PART 3: DATA INTEGRATION TEST"
echo "==============================="
echo ""

# Test data consistency across endpoints
print_status "Checking data consistency between endpoints"

# Get summary data
summary_response=$(curl -s "$API_BASE/v1/summary")
total_devices_summary=$(echo "$summary_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_devices', 0))" 2>/dev/null || echo "0")

# Get devices count
devices_response=$(curl -s "$API_BASE/v1/devices")
total_devices_list=$(echo "$devices_response" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [ "$total_devices_summary" -eq "$total_devices_list" ]; then
    print_success "Device counts match: Summary=$total_devices_summary, List=$total_devices_list"
else
    print_warning "Device count mismatch: Summary=$total_devices_summary, List=$total_devices_list"
fi

# Check if zones have proper hierarchy
zones_response=$(curl -s "$API_BASE/v1/zones")
zones_with_hierarchy=$(echo "$zones_response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
count = sum(1 for zone in data if 'full_path' in zone and 'undefined' not in zone['full_path'])
print(count)
" 2>/dev/null || echo "0")

total_zones=$(echo "$zones_response" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [ "$zones_with_hierarchy" -eq "$total_zones" ] && [ "$total_zones" -gt 0 ]; then
    print_success "All $total_zones zones have proper hierarchy (no 'undefined' values)"
elif [ "$total_zones" -eq 0 ]; then
    print_warning "No zones found in system"
else
    print_warning "$zones_with_hierarchy/$total_zones zones have proper hierarchy"
fi

echo ""
echo "🎯 PART 4: BROWSER TESTING CHECKLIST"
echo "===================================="
echo ""

echo "Please test the following manually in your browser:"
echo ""

echo "📱 DASHBOARD ($APP_BASE/dashboard.html):"
echo "  □ Page loads without errors"
echo "  □ Shows device counts (Total: $total_devices_summary)"
echo "  □ Shows uplink statistics"
echo "  □ Navigation links work"
echo "  □ 'Refresh Data' button works"
echo ""

echo "🏢 SITES MANAGER ($APP_BASE/sites.html):"
echo "  □ Lists existing sites"
echo "  □ 'Create New Site' form works"
echo "  □ Can update existing sites"
echo "  □ 'Configure Locations' links work"
echo "  □ Archive confirmation uses proper CRUA language"
echo ""

echo "📍 LOCATIONS MANAGER ($APP_BASE/locations.html):"
echo "  □ Site selector populates"
echo "  □ Hierarchy displays correctly (no 'undefined' values)"
echo "  □ Can add floors, rooms, zones"
echo "  □ 'Assign Devices' link works"
echo "  □ Archive buttons work"
echo ""

echo "📱 DEVICE MANAGER ($APP_BASE/devices.html):"
echo "  □ Shows device statistics correctly"
echo "  □ Device table loads with proper data"
echo "  □ Status filter works (All/Configured/Orphaned)"
echo "  □ Zone dropdown shows: '$zones_with_hierarchy zones with proper hierarchy'"
echo "  □ Device assignment works"
echo "  □ Decommission (not delete) works"
echo ""

echo "🔄 WORKFLOW TESTING:"
echo "  □ Dashboard → Sites → Locations → Devices navigation works"
echo "  □ URL parameters pass correctly (site_id)"
echo "  □ Each page works independently"
echo "  □ No JavaScript errors in browser console"
echo ""

echo "⚡ QUICK DEVICE ASSIGNMENT TEST:"
echo "  1. Go to Device Manager"
echo "  2. Click assign button (📍) on an ORPHAN device"
echo "  3. Select zone: should show proper hierarchy paths"
echo "  4. Assign device and verify it shows as CONFIGURED"
echo "  5. Check location shows in device table"
echo ""

# Summary
echo ""
echo "📋 TEST SUMMARY"
echo "==============="
echo ""

# Count API tests
api_tests=5
frontend_tests=${#frontend_files[@]}

echo "✅ Completed $api_tests API endpoint tests"
echo "✅ Completed $frontend_tests frontend file accessibility tests"
echo "✅ Completed data consistency checks"
echo "📝 Provided browser testing checklist"
echo ""

echo "🚀 NEXT STEPS:"
echo "1. Review any warnings or failures above"
echo "2. Complete the browser testing checklist"
echo "3. Test the device assignment workflow"
echo "4. Report any issues found"
echo ""

echo "Happy testing! 🎉"

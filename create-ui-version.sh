#!/bin/bash

# Verdegris IoT Platform - UI Version Creator
# Creates a new UI version by copying from an existing version
# Usage: ./create-ui-version.sh <source_version> <new_version>

set -e

SOURCE_VERSION=${1:-"v2"}
NEW_VERSION=${2:-"v3"}
IOT_ROOT="$HOME/iot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validation
if [[ ! "$NEW_VERSION" =~ ^v[0-9]+$ ]]; then
    print_error "New version must be in format 'v#' (e.g., v3, v4, v5)"
    exit 1
fi

if [[ ! "$SOURCE_VERSION" =~ ^v[0-9]+$ ]]; then
    print_error "Source version must be in format 'v#' (e.g., v1, v2)"
    exit 1
fi

if [[ ! -d "$IOT_ROOT/ui-versions/$SOURCE_VERSION" ]]; then
    print_error "Source version $SOURCE_VERSION does not exist"
    exit 1
fi

if [[ -d "$IOT_ROOT/ui-versions/$NEW_VERSION" ]]; then
    print_error "Version $NEW_VERSION already exists"
    exit 1
fi

echo "🚀 Creating UI Version $NEW_VERSION from $SOURCE_VERSION"
echo "=================================================="

# Step 1: Create new version directory
print_step "Creating $NEW_VERSION directory structure"
mkdir -p "$IOT_ROOT/ui-versions/$NEW_VERSION/src"
print_success "Directory created: $IOT_ROOT/ui-versions/$NEW_VERSION"

# Step 2: Copy all files from source version
print_step "Copying files from $SOURCE_VERSION to $NEW_VERSION"
cp -r "$IOT_ROOT/ui-versions/$SOURCE_VERSION/src/"* "$IOT_ROOT/ui-versions/$NEW_VERSION/src/"
print_success "Files copied successfully"

# Step 3: Update version badges in HTML files
print_step "Updating version badges in HTML files"
for file in "$IOT_ROOT/ui-versions/$NEW_VERSION/src/"*.html; do
    if [[ -f "$file" ]]; then
        # Replace version badge (e.g., "V2" -> "V3")
        sed -i "s/badge bg-secondary\">V[0-9]/badge bg-secondary\">$(echo $NEW_VERSION | tr '[:lower:]' '[:upper:]')/g" "$file"
        
        # Update page titles
        sed -i "s/- V[0-9] -/- $(echo $NEW_VERSION | tr '[:lower:]' '[:upper:]') -/g" "$file"
        sed -i "s/V[0-9] - Verdegris/$(echo $NEW_VERSION | tr '[:lower:]' '[:upper:]') - Verdegris/g" "$file"
        
        filename=$(basename "$file")
        print_success "Updated version badges in $filename"
    fi
done

# Step 4: Update Caddyfile to include new version
print_step "Adding $NEW_VERSION routing to Caddyfile"

# Create backup of Caddyfile
cp "$IOT_ROOT/unified-caddyfile" "$IOT_ROOT/unified-caddyfile.backup.$(date +%Y%m%d_%H%M%S)"

# Add new version routing before the closing brace
sed -i "/# Version 2 (Experimental)/a\\
\\
    # Version $(echo $NEW_VERSION | sed 's/v//') (Development)\\
    handle_path /$NEW_VERSION/* {\\
        # API calls for $NEW_VERSION\\
        @${NEW_VERSION}api path /$NEW_VERSION/api/*\\
        handle @${NEW_VERSION}api {\\
            uri strip_prefix /$NEW_VERSION/api\\
            reverse_proxy device-manager:9000\\
        }\\
        \\
        # Static files for $NEW_VERSION\\
        root * /var/www/ui-versions/$NEW_VERSION/src\\
        file_server\\
    }" "$IOT_ROOT/unified-caddyfile"

print_success "Added $NEW_VERSION routing to Caddyfile"

# Step 5: Update docker-compose volume mount
print_step "Updating docker-compose volume mount"

# The ui-versions directory is already mounted, so new versions work automatically
print_success "Volume mount already configured for all versions"

# Step 6: Restart Caddy to pick up new routes
print_step "Restarting Caddy to apply new routing"
cd "$IOT_ROOT"
docker compose restart reverse-proxy
print_success "Caddy restarted successfully"

# Step 7: Test new version
print_step "Testing $NEW_VERSION accessibility"
sleep 3

# Test if new version is accessible
test_url="https://app.sensemy.cloud/$NEW_VERSION/dashboard.html"
http_code=$(curl -s -o /dev/null -w '%{http_code}' "$test_url" || echo "000")

if [[ "$http_code" == "200" ]]; then
    print_success "$NEW_VERSION is accessible and working!"
else
    print_warning "$NEW_VERSION might not be fully ready (HTTP $http_code)"
fi

# Step 8: Create version documentation
print_step "Creating version documentation"
cat > "$IOT_ROOT/ui-versions/$NEW_VERSION/README.md" << EOL
# UI Version $NEW_VERSION

**Created**: $(date)
**Source**: $SOURCE_VERSION
**Status**: Development

## URLs
- Dashboard: https://app.sensemy.cloud/$NEW_VERSION/dashboard.html
- Sites: https://app.sensemy.cloud/$NEW_VERSION/sites.html
- Locations: https://app.sensemy.cloud/$NEW_VERSION/locations.html
- Devices: https://app.sensemy.cloud/$NEW_VERSION/devices.html

## Development Notes
- Copied from $SOURCE_VERSION on $(date)
- All functionality should work identically to $SOURCE_VERSION
- Safe to modify without affecting other versions
- Live file editing enabled (no docker restarts needed)

## Next Steps
1. Test all pages work correctly
2. Make your enhancements to this version
3. Keep $SOURCE_VERSION as stable fallback
EOL

print_success "Documentation created"

# Summary
echo ""
echo "🎉 UI Version $NEW_VERSION Created Successfully!"
echo "=============================================="
echo ""
echo "📍 URLs for $NEW_VERSION:"
echo "   Dashboard: https://app.sensemy.cloud/$NEW_VERSION/dashboard.html"
echo "   Sites:     https://app.sensemy.cloud/$NEW_VERSION/sites.html"
echo "   Locations: https://app.sensemy.cloud/$NEW_VERSION/locations.html"
echo "   Devices:   https://app.sensemy.cloud/$NEW_VERSION/devices.html"
echo ""
echo "📂 Files location: $IOT_ROOT/ui-versions/$NEW_VERSION/src/"
echo ""
echo "✅ Ready for development!"
echo "   - Edit files in $NEW_VERSION/src/ directory"
echo "   - Changes appear immediately (no docker restart needed)"
echo "   - $SOURCE_VERSION remains unchanged and stable"
echo ""
echo "🔄 To create another version:"
echo "   ./create-ui-version.sh $NEW_VERSION v$(( $(echo $NEW_VERSION | sed 's/v//') + 1 ))"

#!/bin/bash
#
# Single Shot Site - Caddy Installer
# Sets up Caddy with HTTPS and security headers
#
# Usage: ./install.sh <domain> [--dev]
#

set -e

DOMAIN="${1:-}"
DEV_MODE="${2:-}"

if [[ -z "$DOMAIN" ]]; then
    echo "Usage: $0 <domain> [--dev]"
    echo "  --dev   Use HTTP only (no HTTPS)"
    exit 1
fi

WWW_ROOT="/var/www/$DOMAIN"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Domain: $DOMAIN"
echo "Web root: $WWW_ROOT"
echo ""

# Install Caddy
if ! command -v caddy &> /dev/null; then
    echo "Installing Caddy..."
    apt-get update -qq
    apt-get install -y -qq debian-keyring debian-archive-keyring apt-transport-https curl
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    apt-get update -qq
    apt-get install -y -qq caddy
fi

# Create directories
mkdir -p "$WWW_ROOT"
mkdir -p /var/log/caddy
mkdir -p /etc/caddy

# Copy site files
echo "Copying site files..."
cp "$PROJECT_DIR/www/index.html" "$WWW_ROOT/"
cp "$PROJECT_DIR/www/style.css" "$WWW_ROOT/"

# Replace placeholder domain
sed -i "s/{{DOMAIN}}/$DOMAIN/g" "$WWW_ROOT/index.html"

# Set permissions
chown -R caddy:caddy "$WWW_ROOT"
chown -R caddy:caddy /var/log/caddy

# Create Caddyfile
if [[ "$DEV_MODE" == "--dev" ]]; then
    # HTTP only (development)
    cat > /etc/caddy/Caddyfile << EOF
http://$DOMAIN {
    root * $WWW_ROOT
    encode gzip zstd
    file_server
    
    header {
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        -Server
    }
}
EOF
else
    # HTTPS (production)
    cat > /etc/caddy/Caddyfile << EOF
$DOMAIN {
    root * $WWW_ROOT
    encode gzip zstd
    file_server
    
    header {
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Content-Security-Policy "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'"
        Strict-Transport-Security "max-age=31536000"
        -Server
    }
    
    log {
        output file /var/log/caddy/$DOMAIN.log
    }
}
EOF
fi

# Enable and start
systemctl enable caddy
systemctl restart caddy

echo ""
echo "✅ Done!"
echo ""
echo "Site: https://$DOMAIN"
echo "Web root: $WWW_ROOT"
echo "Config: /etc/caddy/Caddyfile"
echo ""
echo "Edit your site in: $WWW_ROOT/"
echo "Reload Caddy: systemctl reload caddy"
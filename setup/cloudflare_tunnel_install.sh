#!/bin/bash
#
# Cloudflare Tunnel Installer (agieth.ai version)
# Creates tunnel via agieth.ai API - no Cloudflare account needed
#
# Usage: ./cloudflare_tunnel_install.sh <domain> [local_port]
#
# Requirements:
#   - Domain must be registered via agieth.ai
#   - AGIETH_API_KEY environment variable or --api-key flag
#

set -e

DOMAIN="${1:-}"
LOCAL_PORT="${2:-3000}"
API_KEY="${AGIETH_API_KEY:-}"

if [[ -z "$DOMAIN" ]]; then
    echo "Usage: $0 <domain> [local_port]"
    echo ""
    echo "Arguments:"
    echo "  domain     Your domain (must be registered via agieth.ai)"
    echo "  local_port Local port to tunnel (default: 3000)"
    echo ""
    echo "Environment:"
    echo "  AGIETH_API_KEY   API key for agieth.ai"
    echo ""
    echo "Example:"
    echo "  AGIETH_API_KEY=agieth_xxx $0 mysite.com 3000"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Run Python installer
exec python3 "$SCRIPT_DIR/cloudflare_tunnel_install.py" "$DOMAIN" "$LOCAL_PORT" ${API_KEY:+--api-key "$API_KEY"}
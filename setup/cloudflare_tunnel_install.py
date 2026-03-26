#!/usr/bin/env python3
"""
Cloudflare Tunnel Installer - agieth.ai Version

Uses agieth.ai API to create a Cloudflare tunnel without requiring
the user to have their own Cloudflare account.

Usage:
    python cloudflare_tunnel_install.py <domain> [local_port]

Example:
    python cloudflare_tunnel_install.py mysite.com 3000

The user's domain must already be registered through agieth.ai
and configured in Cloudflare DNS.
"""
import os
import sys
import argparse

# Add skill to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "skills", "agieth")
sys.path.insert(0, SKILL_DIR)

from skill import AgiethClient


def print_banner():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        Cloudflare Tunnel Installer (agieth.ai)            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()


def install_cloudflared():
    """Check if cloudflared is installed, offer to install if not."""
    import subprocess
    import platform
    
    if subprocess.run(["which", "cloudflared"], capture_output=True).returncode == 0:
        version = subprocess.run(["cloudflared", "--version"], capture_output=True, text=True)
        print(f"✓ cloudflared already installed: {version.stdout.strip()}")
        return True
    
    print("cloudflared is not installed.")
    print()
    
    system = platform.system().lower()
    
    if system == "linux":
        print("Installing cloudflared for Linux...")
        print()
        print("Run the following commands:")
        print()
        print("  curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared")
        print("  chmod +x cloudflared")
        print("  sudo mv cloudflared /usr/local/bin/")
        print()
    elif system == "darwin":
        print("Installing cloudflared for macOS...")
        print()
        print("Run the following commands:")
        print()
        print("  brew install cloudflared")
        print()
    else:
        print("Please install cloudflared manually:")
        print("  https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/")
        print()
    
    return False


def create_tunnel(client: AgiethClient, domain: str, local_port: int):
    """Create a tunnel via agieth.ai API."""
    print(f"Creating tunnel for {domain}...")
    print()
    
    result = client.create_tunnel(domain, local_port)
    
    if result.get("success"):
        print("✓ Tunnel created successfully!")
        print()
        print(f"  Tunnel ID: {result.get('tunnel_id', 'N/A')}")
        print(f"  Tunnel Token: {result.get('tunnel_token', 'N/A')}")
        print()
        return result
    else:
        print(f"✗ Failed to create tunnel: {result.get('error', 'Unknown error')}")
        print()
        
        # Check if domain is not in Cloudflare
        if "not found" in str(result.get("error", "")).lower():
            print("Possible issues:")
            print("  1. Domain not registered through agieth.ai")
            print("  2. Domain not configured in Cloudflare DNS")
            print()
            print("To use agieth.ai tunnel hosting:")
            print("  1. Register domain via agieth.ai API")
            print("  2. Set up Cloudflare DNS (free)")
        
        return None


def print_instructions(tunnel_token: str, domain: str, local_port: int):
    """Print setup instructions."""
    print("════════════════════════════════════════════════════════════")
    print("                    Setup Instructions")
    print("════════════════════════════════════════════════════════════")
    print()
    print("Your tunnel is ready! Run the following command:")
    print()
    print(f"  cloudflared tunnel run --token {tunnel_token}")
    print()
    print(f"This will connect https://{domain} to http://localhost:{local_port}")
    print()
    print("────────────────────────────────────────────────────────────")
    print("                    Run as Service")
    print("────────────────────────────────────────────────────────────")
    print()
    print("To run cloudflared as a systemd service:")
    print()
    print(f"  sudo cloudflared service install {tunnel_token}")
    print("  sudo systemctl enable cloudflared")
    print("  sudo systemctl start cloudflared")
    print()
    print("────────────────────────────────────────────────────────────")
    print("                    Commands")
    print("────────────────────────────────────────────────────────────")
    print()
    print("  Start:   sudo systemctl start cloudflared")
    print("  Stop:    sudo systemctl stop cloudflared")
    print("  Status:  sudo systemctl status cloudflared")
    print("  Logs:    sudo journalctl -u cloudflared -f")
    print()
    print("────────────────────────────────────────────────────────────")
    print("                    Benefits")
    print("────────────────────────────────────────────────────────────")
    print()
    print("  ✓ No public IP required")
    print("  ✓ No port forwarding needed")
    print("  ✓ DDoS protection included")
    print("  ✓ Origin IP hidden")
    print("  ✓ Automatic SSL/TLS")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Create a Cloudflare tunnel via agieth.ai API"
    )
    parser.add_argument("domain", help="Domain name (must be registered via agieth.ai)")
    parser.add_argument("local_port", nargs="?", type=int, default=3000,
                        help="Local port to tunnel (default: 3000)")
    parser.add_argument("--api-key", "-k", help="API key (or set AGIETH_API_KEY)")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check cloudflared
    if not install_cloudflared():
        print("Please install cloudflared and run again.")
        sys.exit(1)
    
    # Initialize client
    api_key = args.api_key or os.getenv("AGIETH_API_KEY")
    if not api_key:
        print("Error: API key required.")
        print("Set AGIETH_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    client = AgiethClient(api_key=api_key)
    
    # Create tunnel
    result = create_tunnel(client, args.domain, args.local_port)
    
    if result:
        tunnel_token = result.get("tunnel_token")
        if tunnel_token:
            print_instructions(tunnel_token, args.domain, args.local_port)
        else:
            print("Note: Tunnel created but no token was returned.")
            print("Contact support@agieth.ai for assistance.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
# Cloudflare Tunnel via agieth.ai

Host local services securely without a Cloudflare account.

## Overview

This installer uses the agieth.ai API to create Cloudflare tunnels for
domains registered through agieth.ai. Your domain is already in Cloudflare
DNS (included with registration), so tunnels are created automatically.

**Benefits:**
- No Cloudflare account needed
- No manual DNS configuration
- Automatic SSL/TLS
- Hide your origin IP
- Works behind NAT/firewall

## Prerequisites

1. **Domain registered via agieth.ai** - Your domain must already be in agieth's Cloudflare
2. **API key** - Get from agieth.ai
3. **cloudflared installed** (prompted if missing)

## Quick Start

```bash
# Set API key
export AGIETH_API_KEY="agieth_xxxxxxxxxxxx"

# Run installer
cd ~/git/one_shot_site/setup
./cloudflare_tunnel_install.sh mysite.com 3000
```

## What Happens

1. **API Call** → agieth.ai creates tunnel in its Cloudflare account
2. **DNS** → CNAME record created automatically
3. **Token** → You receive a tunnel token
4. **Connect** → Run `cloudflared tunnel run --token <token>`

## Files

```
setup/
├── cloudflare_tunnel_install.sh   # Shell wrapper
├── cloudflare_tunnel_install.py   # Python script (calls skill)
└── CLOUDFLARE_TUNNEL_SETUP.md     # This file
```

## Python API

You can also use the skill directly:

```python
from skills.agieth.skill import AgiethClient

client = AgiethClient(api_key="agieth_xxx")

# Create tunnel — returns credentials + token
result = client.create_tunnel("mysite.com", local_port=3000)
print(f"Tunnel ID: {result['tunnel_id']}")
print(f"Token: {result['tunnel_token']}")
print(f"Credentials: {result['credentials']}")
# Save credentials to file for cloudflared:
# {
#   "AccountTag": "...",
#   "TunnelID": "...",
#   "TunnelName": "...",
#   "TunnelSecret": "..."
# }

# Get existing tunnel credentials (retrieve anytime)
result = client.get_tunnel_token("mysite.com")
print(f"Token: {result['tunnel_token']}")
print(f"Credentials: {result['credentials']}")

# Check status
status = client.get_hosting_status("mysite.com")
print(f"Status: {status['status']}")
```

## Running the Tunnel

### Method 1: JSON Credentials File (Recommended)

The API returns a `credentials` object containing your tunnel credentials. Save it
to a JSON file and run cloudflared with that file:

```bash
# 1. Create credentials directory
mkdir -p ~/.cloudflared

# 2. Save credentials (from API response)
cat > ~/.cloudflared/credentials.json << 'EOF'
{
  "AccountTag": "ed0d16197ca3bf56246ac7f5df806393",
  "TunnelID": "your-tunnel-id",
  "TunnelName": "your-tunnel-name",
  "TunnelSecret": "your-tunnel-secret"
}
EOF

# 3. Run the tunnel
cloudflared tunnel run --config ~/.cloudflared/credentials.json

# Or save with tunnel-specific filename:
mv ~/.cloudflared/credentials.json ~/.cloudflared/YOUR-TUNNEL-ID.json
cloudflared tunnel run --config ~/.cloudflared/YOUR-TUNNEL-ID.json
```

### Method 2: Tunnel Token

```bash
cloudflared tunnel run --token <tunnel_token>
```

### Quick Run (Foreground)

### Run as Service (systemd)

**Using JSON credentials file:**
```bash
sudo cloudflared service install ~/.cloudflared/credentials.json
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

**Using token:**
```bash
sudo cloudflared service install <tunnel_token>
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### Service Commands

```bash
sudo systemctl start cloudflared    # Start
sudo systemctl stop cloudflared     # Stop
sudo systemctl status cloudflared   # Status
sudo journalctl -u cloudflared -f   # Logs
```

## Architecture

```
┌─────────────────┐
│   Your App      │
│  localhost:3000│
└────────┬────────┘
         │
         │ cloudflared tunnel run --token xxx
         │
┌────────▼────────┐
│  Cloudflare     │
│  Edge Network   │
└────────┬────────┘
         │
         │ HTTPS
         │
┌────────▼────────┐
│     User        │
│  https://mysite │
└─────────────────┘
```

- Your app stays on localhost (no public IP needed)
- cloudflared connects outbound to Cloudflare
- Users access via HTTPS (SSL automatic)
- Your IP is hidden behind Cloudflare

## Comparison: Caddy vs agieth Tunnel

| Feature | Caddy | agieth Tunnel |
|---------|-------|----------------|
| Cloudflare account | Not needed | Not needed |
| Public IP | Required | Not required |
| Port forwarding | Required | Not required |
| DDoS protection | None | Included |
| Hide origin IP | No | Yes |
| SSL certificates | Let's Encrypt | Cloudflare |
| API setup | None | API key required |

**Use agieth Tunnel when:**
- Behind NAT/firewall
- Dynamic IP
- Want DDoS protection
- Want to hide origin IP

**Use Caddy when:**
- Have public IP
- Prefer self-hosted
- No external dependencies

## Troubleshooting

### "Domain not found"

Domain must be registered via agieth.ai:
```bash
# Check domain status
client.get_quote("q_xxx")  # If you have a quote
client.list_domains()       # List your domains
```

### "API key invalid"

Get your API key from agieth.ai:
1. Visit api.agieth.ai/api/v1/keys/create
2. Enter your email
3. Click the verification link

### Tunnel won't start

```bash
# Check cloudflared version
cloudflared --version

# Try running with verbose logging
cloudflared tunnel run --token <token> --loglevel debug
```

### Can't connect to local app

```bash
# Verify your app is running
curl http://localhost:3000/health

# Check firewall isn't blocking localhost
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/hosting/tunnel?domain=X&local_port=N | Create tunnel, returns credentials + token |
| GET | /api/v1/hosting/tunnel/{domain}/token | Get tunnel token + credentials |
| DELETE | /api/v1/hosting/tunnel/{domain} | Delete tunnel + DNS + DB record |
| GET | /api/v1/hosting/status/{domain} | Get hosting status |

### Response: Create Tunnel (POST)

```json
{
  "success": true,
  "domain": "mysite.com",
  "tunnel_id": "abc123...",
  "tunnel_token": "eyJh...",
  "credentials": {
    "AccountTag": "ed0d16197ca3bf56246ac7f5df806393",
    "TunnelID": "abc123...",
    "TunnelName": "customer-11-mysite-com-1234567890",
    "TunnelSecret": "base64secret..."
  },
  "instructions": "..."
}
```

Save the `credentials` object to `~/.cloudflared/credentials.json` and run:
```bash
cloudflared tunnel run --config ~/.cloudflared/credentials.json
```

## Support

- Email: support@agieth.ai
- API Docs: https://api.agieth.ai/api/v1/manifest
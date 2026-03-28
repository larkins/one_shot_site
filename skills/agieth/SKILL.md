---
name: agieth
description: Purchase domains, manage DNS and Cloudflare settings via agieth.ai Agent Bridge
version: 1.0.3
metadata:
  openclaw:
    requires:
      env:
        - AGIETH_API_KEY
        - AGIETH_EMAIL
      bins:
        - cloudflared
    primaryEnv: AGIETH_API_KEY
    emoji: "\u2705"
    homepage: https://agieth.ai
    tags:
      - ethereum
      - cryptocurrency
      - domain-registration
      - cloudflare
      - dns
---

# agieth.ai API Skill

Interact with agieth.ai domain registration and management API.

## Requirements

This skill requires an agieth.ai API key and email address:

| Variable | Required | Description |
|----------|----------|-------------|
| `AGIETH_API_KEY` | Yes | Your agieth.ai API key |
| `AGIETH_EMAIL` | Yes | Email associated with your API key |
| `cloudflared` | Yes (for tunnels) | Binary for Cloudflare Tunnel hosting |

**API base URL** is hardcoded to `https://api.agieth.ai` — no configuration needed.

## How Payments Work

Domain registration payments are made **on the Ethereum blockchain** — the agieth API generates a unique payment address and ETH amount for each quote. You provide your own wallet private key when calling `send_payment`; the skill signs and broadcasts the transaction directly from your wallet — agieth.ai never holds or custody your funds.

**Summary:**
- Payments are ETH transfers on the Ethereum blockchain
- You provide your own wallet private key at runtime — the skill signs locally
- No tokens, no smart contracts, no third-party custody of funds
- Payment address and amount are unique per quote and expire with the quote
- External RPC endpoints used: `https://ethereum.publicnode.com` and `https://eth.drpc.org` (for ETH balance checks and transaction broadcasting)

## Installation

1. Get an API key from [api.agieth.ai](https://api.agieth.ai/api/v1/keys/create)
2. Set environment variables:

```bash
export AGIETH_API_KEY="agieth_your_key_here"
export AGIETH_EMAIL="your_email@example.com"
```

Or create a `.env` file in your workspace:

```
AGIETH_API_KEY=agieth_your_key_here
AGIETH_EMAIL=your_email@example.com
```

## Quick Start

```python
from skill import AgiethClient

# Initialize with environment variables
client = AgiethClient()

# Or pass credentials directly
client = AgiethClient(
    api_key="agieth_your_key_here",
    base_url="https://api.agieth.ai"
)

# Check domain availability
result = client.check_availability("example.com")
# {"available": True, "price_usd": 12.99}
```

## All Methods

### Domain Operations

```python
# Check availability
client.check_availability("example.com")

# Create quote (starts registration)
quote = client.create_quote(
    domain="example.com",
    years=1,
    registrar="namecheap"
)

# Get quote status
client.get_quote(quote_id)

# Check payment status
client.check_payment(quote_id)

# Get domain info
client.get_domain_info("example.com")
```

### DNS Management

```python
# List DNS records
client.list_dns_records("example.com")

# Add DNS record
client.add_dns_record(
    domain="example.com",
    record_type="A",
    name="www",
    value="192.168.1.1"
)

# Delete DNS record
client.delete_dns_record("example.com", record_id)
```

### Cloudflare Integration (FREE)

```python
# Create Cloudflare zone
zone = client.create_cloudflare_zone("example.com")

# List zones
zones = client.list_cloudflare_zones()

# Create DNS records in Cloudflare
client.create_cloudflare_dns_record(
    zone_id=zone["zone_id"],
    record_type="A",
    name="@",
    content="192.168.1.1"
)

# Create page rule (www redirect)
client.create_page_rule(
    zone_id=zone["zone_id"],
    target_url="www.example.com/*",
    forward_url="https://example.com/$1"
)
```

### Cloudflare Tunnel Hosting

```python
# Create tunnel (no public IP needed)
result = client.create_tunnel("example.com", local_port=3000)
# Returns tunnel_token

# Run: cloudflared tunnel run --token <tunnel_token>
```

### Balance & Credits

```python
# Check balance
balance = client.get_balance()

# Check credits
credits = client.get_credits()
```

## Pricing

| Service | Cost |
|---------|------|
| Domain registration | Registrar price + markup |
| Cloudflare DNS | FREE |
| Cloudflare Tunnel | FREE |
| SSL Certificates | FREE |

## Cloudflare Authorization

The tunnel feature uses **agieth.ai's Cloudflare account** — not yours. Agieth creates the tunnel, gives you a token, and Cloudflare sees all traffic as agieth's. You do NOT need your own Cloudflare API token for this skill to work.

## Security Notes

- API keys should be treated as secrets
- Only provide keys with minimum required permissions
- **Always verify the `payment_address` returned by the API before sending crypto** — the skill surfaces the address from the server response
- The skill sends the API key via the `Authorization: Bearer` HTTP header exclusively (no query parameters)
- This skill makes network requests to:
  - `https://api.agieth.ai` (main API)
  - `https://ethereum.publicnode.com` and `https://eth.drpc.org` (Ethereum blockchain RPC — for balance checks and transaction broadcasting)
  - `https://cloudflare.com` (via cloudflared tunnel, when tunnel feature is used)
- cloudflared is required only if you use tunnel hosting; install it from the [official Cloudflare source](https://developers.cloudflare.com/cloudflare-one/install-and-input/installation/)

## API Documentation

Full API documentation: https://api.agieth.ai/api/v1/manifest

## Links

- **API Docs:** https://api.agieth.ai/api/v1/manifest
- **Homepage:** https://agieth.ai
- **Skill Guide:** https://github.com/larkins/one_shot_site
- **Support:** support@agieth.ai
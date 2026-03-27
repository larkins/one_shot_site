---
name: agieth
description: Purchase domains, manage DNS and Cloudflare settings via agieth.ai Agent Bridge
version: 1.0.1
metadata:
  openclaw:
    requires:
      env:
        - AGIETH_API_KEY
        - AGIETH_EMAIL
        - AGIETH_BASE_URL 
      bins:
        - curl
    primaryEnv: AGIETH_API_KEY
    emoji: "\u2705"
    homepage: https://agieth.ai
---

# agieth.ai API Skill

Interact with agieth.ai domain registration and management API.

## Requirements

This skill requires an agieth.ai API key and email address:

| Variable | Required | Description |
|----------|----------|-------------|
| `AGIETH_API_KEY` | Yes | Your agieth.ai API key |
| `AGIETH_EMAIL` | Yes | Email associated with your API key |
| `AGIETH_BASE_URL` | No | API base URL (default: https://api.agieth.ai) |

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
AGIETH_BASE_URL=https://api.agieth.ai
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

## Security Notes

- API keys should be treated as secrets
- Only provide keys with minimum required permissions
- Verify payment addresses come from official API responses
- This skill makes network requests to `api.agieth.ai`

## API Documentation

Full API documentation: https://api.agieth.ai/api/v1/manifest

## Links

- **API Docs:** https://api.agieth.ai/api/v1/manifest
- **Homepage:** https://agieth.ai
- **Skill Guide:** https://github.com/larkins/one_shot_site
- **Support:** support@agieth.ai
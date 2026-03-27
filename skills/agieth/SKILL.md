---
name: agieth
description: Purchase domains, manage DNS and cloudflare settings via agieth.ai Agent Bridge
homepage: https://agieth.ai
---

# agieth.ai API Skill

Interact with agieth.ai domain registration and management API.

## Quick Start

```python
from skill import AgiethClient

# Auto-loads from ~/got/agieth-single-shot/.env
client = AgiethClient()

# Check domain availability
result = client.check_availability("example.com")
# {"available": True, "price_usd": 12.99}
```

## Configuration

Create `.env` file with your credentials:

```bash
AGIETH_API_KEY=your_api_key_here
AGIETH_EMAIL=your_email@example.com
AGIETH_BASE_URL=https://api.agieth.ai
```

## All Methods

### Domain Operations

```python
# Check availability
client.check_availability("example.com")

# Create quote (with registrant info)
quote = client.create_quote(
    domain="example.com",
    years=1,
    registrar="namecheap"
)

# Get quote status
client.get_quote(quote_id)

# Check payment status
client.check_payment(quote_id)
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

# Create page rule (www redirect)
client.create_page_rule(
    zone_id=zone["zone_id"],
    target_url="www.example.com/*",
    forward_url="https://example.com/$1"
)
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
| Domain registration | Registrar price + % markup |
| Cloudflare DNS | FREE |
| Cloudflare Tunnel | FREE |
| SSL Certificates | FREE |

## API Endpoints

- `/domains/available` - Check availability
- `/api/v1/domains/quote` - Create quote
- `/api/v1/quotes/{id}` - Get quote
- `/api/v1/balance` - Check balance
- `/api/v1/cloudflare/zones` - Zone management
- `/api/v1/cloudflare/zones/{id}/dns` - DNS records
- `/api/v1/cloudflare/zones/{id}/pagerules` - Page rules
- `/api/v1/manifest` - API documentation
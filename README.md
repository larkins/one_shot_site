# one-shot-site

Single-shot domain registration using agieth.ai API.

## What This Does

1. Register domain 
2. Modify registrar DNS
3. Modify Cloudflare Settings
4. Credit system for failed registrations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

```bash
# Create .env file
cp .env.example .env

# Edit with your credentials
# Get API key from https://agieth.ai
```

### 3. Use the Skill

```python
from skills.agieth.skill import AgiethClient

client = AgiethClient()

# Check availability
result = client.check_availability("example.com")
print(f"Available: {result['available']}, Price: ${result['price_usd']}")

# Create quote
quote = client.create_quote(domain="mynewsite.com", years=1)
print(f"Send {quote['price_eth']} ETH to {quote['payment_address']}")

# After payment, domain registered automatically

# Set up Cloudflare DNS (FREE)
zone = client.create_cloudflare_zone("mynewsite.com")
client.add_dns_record("mynewsite.com", "A", "@", "192.168.1.1")
```

## Documentation

- `AGENTS.md` - End-user quick reference for one-shot usage
- `skills/agieth/SKILL.md` - Skill method reference
- `skills/agieth/TROUBLESHOOTING.md` - RPC failover + payment troubleshooting
- `PAYMENT_FLOW.md` - Payment and registration flow details
- `TROUBLESHOOTING.md` - Common repo-level issues and solutions

## 2026-03-28 Status

Live flow has been re-validated after ownership/RPC/DNS fixes:

- quote creation
- ETH payment + confirmation
- domain registration
- Cloudflare zone + page rule
- Namecheap DNS add/list
- `/domains` owned listing
- `/api/v1/cloudflare/services`
- email send + inbox receipt verification

Reference domain from latest validation: `mllivev1g2a1x5.com`.

## License

MIT License - See LICENSE file

## Contributing

This project is open source. Contributions welcome!

## Support

- Email: support@agieth.ai
- API Docs: https://agieth.ai/api/v1/manifest

# one-shot-site

Single-shot domain registration using agieth.ai API.

## What This Does

1. Register domains via agieth.ai API
2. Use Cloudflare for DNS (FREE)
3. Single wallet architecture - no gas fee hassles
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

- `AGENTS.md` - Full API documentation and examples
- `skills/agieth/SKILL.md` - Skill method reference
- `PAYMENT_FLOW.md` - Payment flow details
- `TROUBLESHOOTING.md` - Common issues and solutions

## License

MIT License - See LICENSE file

## Contributing

This project is open source. Contributions welcome!

## Support

- Email: support@agieth.ai
- API Docs: https://agieth.ai/api/v1/manifest

# one_shot_site Payment Flow

## Architecture

```
User/Agent → API Key Generation → Quote Request → ETH Payment → Domain Registration → DNS Setup
```

## Default Registrar

**Namecheap** is the default registrar. NameSilo is temporarily disabled due to API issues.

## Flow

### 1. API Key Generation
```
POST /api/v1/keys/create
{
  "email": "user@example.com"
}

Response:
{
  "success": true,
  "message": "Verification email sent"
}
```

### 2. Email Verification
```
GET /api/v1/keys/verify?token={verification_token}&email={email}

Response:
{
  "success": true,
  "api_key": "agieth_xxxxxxxxxxxx"
}
```

### 3. Quote Request
```
POST /api/v1/domains/quote
Authorization: Bearer agieth_xxxxxxxxxxxx
{
  "domain": "example.com",
  "years": 1,
  "registrar": "namecheap"  // optional, defaults to namecheap
}

Response:
{
  "quote_id": "q_xxxxx",
  "domain": "example.com",
  "price_usd": 12.99,
  "price_eth": "0.004",
  "payment_address": "0x...",
  "expires_at": "2026-03-26T12:00:00Z"
}
```

### 4. Payment
Send ETH/USDC/USDT to the payment address. The system monitors for payment confirmations automatically.

### 5. Domain Registration
After payment confirmation, domain registration begins automatically via Namecheap API.

## Credit System

If registration fails (domain taken, etc.), the payment is converted to credits:
- Credits stored in user's account
- Can be used for future registrations
- Refund available on request (gas fee deducted)

## Cloudflare Integration (FREE)

After registration, use the agieth.ai API to configure everything:

```python
# Create Cloudflare zone (handled by agieth.ai)
zone = client.create_cloudflare_zone("example.com")
print(f"Nameservers: {zone['nameservers']}")

# Update nameservers at your registrar (Namecheap, NameSilo, etc.)
# to point to: zone['nameservers']

# Add DNS records via API
client.add_dns_record("example.com", "A", "@", "192.168.1.1")
client.add_dns_record("example.com", "CNAME", "www", "example.com")

# Add page rule for www redirect (optional)
client.create_page_rule(
    zone_id=zone["zone_id"],
    target_url="www.example.com/*",
    forward_url="https://example.com/$1"
)
```

**No Cloudflare account needed!** agieth.ai handles all Cloudflare integration.

## Security

- API keys are bearer tokens (store securely)
- Payment addresses are unique per quote
- Quotes expire after 30 minutes
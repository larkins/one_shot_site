# AGENTS.md - one-shot-site

Quick start for AI agents using agieth.ai domain registration API.

## Documentation

| File | Purpose |
|------|---------|
| **README.md** | Project overview and setup instructions |
| **PAYMENT_FLOW.md** | Detailed payment and registration flow |
| **AGENTS.md** | This file - AI agent quick reference |

## Step 0: Get an API Key

Before using the API, you need to generate an API key at agieth.ai.

### 0.1 Request API Key

```bash
# Via API
curl -X POST https://api.agieth.ai/api/v1/keys/create \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com"}'

# Response: {"success": true, "message": "Verification email sent"}
```

### 0.2 Check Your Email

You'll receive an email from `support@agieth.ai` with a verification code.

**Email subject:** "Your Agieth API Key Verification Code"

### 0.3 Verify and Get API Key

```bash
# Click the link in the email OR use the verification code WITH your email:
curl "https://api.agieth.ai/api/v1/keys/verify?token=YOUR_VERIFICATION_CODE&email=your@email.com"

# Response: {"verified": true, "message": "API key verified successfully"}
```

**Note:** Both token AND email are required for verification. This prevents brute force attacks.

### 0.4 Store Your API Key

```bash
# Option 1: Environment variable
export AGIETH_API_KEY="agieth_xxxxxxxxxxxx"

# Option 2: .env file
echo "AGIETH_API_KEY=agieth_xxxxxxxxxxxx" >> ~/.env

# Option 3: For one-shot-site specifically
cp .env.example .env
# Edit .env and add your API key
```

## Quick Start

```python
from skills.agieth.skill import AgiethClient

# Load credentials from .env
client = AgiethClient()  # Auto-loads from project .env / environment

# Or specify manually
client = AgiethClient(api_key="agieth_xxx")
```

## Core API Operations

### 1. Check Domain Availability

```python
result = client.check_availability("example.com")
# Returns: {"available": True, "price_usd": 12.99}
```

### 2. Register Domain

```python
# Create quote
quote = client.create_quote(
    domain="mynewsite.com",
    years=1,
    registrar="namecheap"
)
quote_id = quote["quote_id"]
payment_address = quote["payment_address"]
payment_amount = quote["price_eth"]

# Send payment (use your wallet)
# ... send {payment_amount} ETH to {payment_address}

# Check payment status
status = client.get_quote(quote_id)
if status["status"] == "paid":
    print("Domain registered!")
```

### 3. Check Balance & Credits

```python
balance = client.get_balance()
print(f"Balance: ${balance['balance_usd_cents']/100}")
print(f"Credits: ${balance['credit_usd_cents']/100}")
```

### 4. Cloudflare Integration (FREE)

```python
# Create Cloudflare zone
zone = client.create_cloudflare_zone("mynewsite.com")
nameservers = zone["name_servers"]

# Add DNS records
client.add_dns_record(
    domain="mynewsite.com",
    record_type="A",
    name="@",
    value="192.168.1.1"
)

# Add www redirect
client.create_page_rule(
    zone_id=zone["zone_id"],
    target_url="www.mynewsite.com/*",
    forward_url="https://mynewsite.com/$1"
)
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/domains/available` | Check domain availability |
| `/api/v1/domains/quote` | Create registration quote |
| `/api/v1/quotes/{id}` | Get quote status |
| `/api/v1/balance` | Check account balance |
| `/api/v1/cloudflare/zones` | Create Cloudflare zone |
| `/api/v1/cloudflare/zones/{id}/dns` | DNS record management |
| `/api/v1/cloudflare/zones/{id}/pagerules` | Page rules |
| `/domains` | Owned domains for current API key user (default mode) |
| `/api/v1/cloudflare/services` | Cloudflare/hosting pricing metadata |

## Optional: Static Site Hosting

After registering a domain, you have two hosting options:

### Option A: Self-Hosted with Caddy

Use when you have a public IP and port forwarding access.

**Files:**
```
setup/
├── caddy_install.sh   # Caddy installer
└── CADDY_README.md    # Documentation

www/
├── index.html         # Template
└── style.css          # Stylesheet
```

**Install:**
```bash
cd ~/git/one_shot_site/setup
sudo ./caddy_install.sh yourdomain.com
```

**Features:**
- HTTPS auto-provision (Let's Encrypt)
- Security headers included
- Static file serving
- Requires public IP and open ports 80/443

### Option B: Cloudflare Tunnel (via agieth.ai)

No Cloudflare account needed - tunnel is created in agieth's Cloudflare.

**Files:**
```
setup/
├── cloudflare_tunnel_install.py   # Python script (calls skill)
├── cloudflare_tunnel_install.sh   # Shell wrapper
└── CLOUDFLARE_TUNNEL_SETUP.md     # Documentation
```

**Install:**
```bash
export AGIETH_API_KEY="agieth_xxx"
cd ~/git/one_shot_site/setup
python cloudflare_tunnel_install.py yourdomain.com 3000
```

**Or use the skill directly:**
```python
client = AgiethClient()
result = client.create_tunnel("yourdomain.com", local_port=3000)
token = result["tunnel_token"]  # Run: cloudflared tunnel run --token <token>
```

**Features:**
- No Cloudflare account required (uses agieth's account)
- No public IP required
- No port forwarding needed
- DDoS protection included
- Origin IP hidden
- Auto SSL via Cloudflare
- Domain must be registered via agieth

**Comparison:**

| Feature | Caddy | Cloudflare Tunnel |
|---------|-------|-------------------|
| Public IP required | Yes | No |
| Port forwarding | Yes | No |
| DDoS protection | No | Yes |
| Hide origin IP | No | Yes |
| Free tier | Yes | Yes |

### Security Headers (Caddy Only)

| Header | Value |
|--------|-------|
| X-Frame-Options | DENY |
| X-Content-Type-Options | nosniff |
| X-XSS-Protection | 1; mode=block |
| Content-Security-Policy | default-src 'self' |
| Strict-Transport-Security | max-age=31536000 |

### 2026-03-28 Troubleshooting Notes

**RPC failover behavior:** The skill and backend use primary/fallback Ethereum RPC failover. If a payment seems stuck, the system may have retried on the fallback endpoint. Check `rpc_used` and `rpc_failover_used` in response fields.

**Email send endpoint:** The `/api/v1/emails/send` endpoint accepts parameters as query params: `?api_key=...&to=...&subject=...&body=...`.

**Owned domains listing:** `GET /domains` (no prefix) returns user-owned domains from the agieth DB. This is the default mode. Use `provider=namesilo|godaddy` to get registrar-account listing instead.

### After Install

```bash
# Edit your site
nano /var/www/yourdomain.com/index.html

# Reload Caddy after changes
sudo systemctl reload caddy
```

## Optional: Setup Files Reference

The `setup/` directory contains helper scripts for deployment:

| File | Purpose | Requirements |
|------|---------|--------------|
| `caddy_install.sh` | Self-hosted HTTPS via Caddy | Public IP, ports 80/443 |
| `cloudflare_tunnel_install.sh` | Shell wrapper for tunnel | agieth API key |
| `cloudflare_tunnel_install.py` | Python tunnel installer (calls skill) | agieth API key |
| `CADDY_README.md` | Caddy documentation | - |
| `CLOUDFLARE_TUNNEL_SETUP.md` | Tunnel documentation | - |

**Usage Examples:**

```bash
# Self-hosted (Caddy) - requires public IP
sudo ./setup/caddy_install.sh example.com

# Tunnel (via agieth) - no public IP needed
export AGIETH_API_KEY="agieth_xxx"
python setup/cloudflare_tunnel_install.py example.com 3000
```

**Python Skill (Alternative):**

```python
from skills.agieth.skill import AgiethClient

client = AgiethClient(api_key="agieth_xxx")

# Create tunnel
result = client.create_tunnel("example.com", local_port=3000)
token = result["tunnel_token"]

# Use token
# cloudflared tunnel run --token <token>
```

## Pricing (All Cloudflare services FREE)

| Service | Cost |
|----------|------|
| Domain registration | Registration price + 20% markup |
| Cloudflare DNS | FREE |
| Cloudflare Tunnel | FREE |
| Cloudflare Proxy | FREE |
| SSL Certificates | FREE |
| Page Rules | FREE |

## Error Handling

### API Key Issues

```python
# If you get 401 Unauthorized:
# 1. Check your API key is valid
# 2. Make sure it starts with "agieth_"
# 3. Generate a new key if needed

# If verification code expired:
# 1. Request a new key at https://agieth.ai
# 2. Verification codes expire after 24 hours
# 3. Email support@agieth.ai if issues persist
```

### Domain Registration Issues

When domain is taken during registration:
```python
if result["status"] == "failed":
    # Credit automatically added
    credit = result["credit"]
    print(f"Credit: ${credit['credit_usd']}")
    
    # Use credit for another domain
    result2 = client.create_quote("alternative-domain.com")
```

## ⚠️ IMPORTANT: Verify Contact Information

After domain registration, you **MUST** verify your contact information:

1. **Check your email inbox** (the email you registered with)
2. **Look for "Verify Contact Information" email** from Namecheap/NameSilo
3. **Click the verification link** in the email
4. **Follow instructions** to verify your contact details

**If you don't verify within 7-14 days, your domain may be suspended by ICANN.**

Set a reminder: After domain registration, check inbox for verification email!

## Full Example

```python
from skills.agieth.skill import AgiethClient

# Initialize
client = AgiethClient()

# Check availability
domain = "myawesomeapp.com"
avail = client.check_availability(domain)
if not avail["available"]:
    print(f"Domain taken: {domain}")
    exit(1)

# Create quote
quote = client.create_quote(domain, years=1)
print(f"Send {quote['price_eth']} ETH to {quote['payment_address']}")

# After sending payment, poll for confirmation
import time
while True:
    status = client.get_quote(quote["quote_id"])
    if status["status"] == "paid":
        print("Domain registered!")
        break
    time.sleep(30)

# Set up Cloudflare
zone = client.create_cloudflare_zone(domain)
print(f"Nameservers: {zone['name_servers']}")

# Add DNS records
client.add_dns_record(domain, "A", "@", "192.168.1.1")
client.add_dns_record(domain, "CNAME", "www", domain)
```

## Files

```
one-shot-site/
├── AGENTS.md          # This file
├── .env.example       # Configuration template
├── requirements.txt   # Python dependencies
├── scripts/
│   ├── one_shot.py    # One-shot domain registration
│   └── check_balance.py
└── skills/
    └── agieth/
        ├── SKILL.md   # Skill documentation
        └── skill.py   # AgiethClient class
```

## Support

- Email: support@agieth.ai
- API Docs: https://agieth.ai/api/v1/manifest
- Status: https://status.agieth.ai
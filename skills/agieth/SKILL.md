---
name: agieth
description: Purchase domains, manage DNS, Cloudflare settings, and inbound email workers via agieth.ai Agent Bridge
version: 1.0.15
metadata:
  openclaw:
    requires:
      env:
        - AGIETH_API_KEY
        - AGIETH_EMAIL
      bins: []
    primaryEnv: AGIETH_API_KEY
    emoji: "\u2705"
    homepage: https://agieth.ai
    tags:
      - ethereum
      - cryptocurrency
      - domain-registration
      - cloudflare
      - dns
      - email-routing
---

# agieth.ai API Skill

Interact with agieth.ai domain registration and management API.

## Requirements

This skill requires an agieth.ai API key and email address:

| Variable | Required | Description |
|----------|----------|-------------|
| `AGIETH_API_KEY` | Yes | Your agieth.ai API key |
| `AGIETH_EMAIL` | Yes | Email associated with your API key |
| `ETH_WALLET_PRIVATE_KEY` | Only for payments | Ethereum private key — only needed for `send_payment`. You can also use any external wallet instead. |
| `ETH_RPC_PRIMARY` | No | Ethereum RPC endpoint — defaults to `https://ethereum.publicnode.com` |
| `ETH_RPC_FALLBACK` | No | Fallback RPC — defaults to `https://eth.drpc.org` |
| `cloudflared` | No | Only needed for Cloudflare Tunnel hosting. If you have a static IP, you can point DNS A records at it instead — no tunnel needed. |

**API base URL** is hardcoded to `https://api.agieth.ai` — no configuration needed.

## How Payments Work

Domain registration payments are made **on the Ethereum blockchain** — the agieth API generates a unique payment address and ETH amount for each quote. You can pay using **any Ethereum wallet** (MetaMask, Rabby, hardware wallet, etc.) by sending the exact ETH amount to the address returned by the API — no private key needs to be provided to this skill.

The `send_payment` method is included as a convenience for fully-automated workflows. If you prefer manual payment or a different wallet, simply use the `payment_address` and `price_eth` from the quote response in your own wallet.

**Summary:**
- Payments are ETH transfers on the Ethereum blockchain
- No tokens, no smart contracts, no third-party custody of funds
- Payment address and amount are unique per quote and expire with the quote
- External RPC endpoints used: `https://ethereum.publicnode.com` and `https://eth.drpc.org`

## Installation

1. Get an API key from [api.agieth.ai](https://api.agieth.ai/api/v1/keys/create)
2. Set environment variables:

```bash
export AGIETH_API_KEY="agieth_your_key_here"
export AGIETH_EMAIL="your_email@example.com"
# Only needed for automated payments (optional — see How Payments Work above):
export ETH_WALLET_PRIVATE_KEY="0x..."
```

Or create a `.env` file in your workspace:

```
AGIETH_API_KEY=agieth_your_key_here
AGIETH_EMAIL=your_email@example.com
# Only needed for automated payments:
ETH_WALLET_PRIVATE_KEY=0x...
# Optional RPC overrides:
ETH_RPC_PRIMARY=https://your-preferred-rpc
ETH_RPC_FALLBACK=https://your-fallback-rpc
```

## Quick Start

```python
from skill import AgiethClient

# Initialize with environment variables
client = AgiethClient()

# Or pass credentials directly
client = AgiethClient(
    api_key="agieth_your_key_here",
    email="your_email@example.com"
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
    value="203.0.113.10"
)

# Update DNS record — change proxied, content, TTL, etc.
client.update_dns_record(
    "example.com",
    record_id="abc123",
    content="203.0.113.11",   # optional
    ttl=7200,               # optional
    proxied=False           # optional — set to False for tunnel/DNS-only mode
)

# Delete DNS record
client.delete_dns_record("example.com", record_id)
```

### Registrar Nameservers

**You must use the correct registrar endpoint for your domain.** After registration, point your domain to Cloudflare nameservers:

```python
# For Namecheap domains:
nameservers = ["ns1.cloudflare.com", "ns2.cloudflare.com"]
client.set_namecheap_nameservers("example.com", nameservers)

# For NameSilo domains:
client.set_namesilo_nameservers("example.com", nameservers)

# Check current nameservers:
client.get_namecheap_nameservers("example.com")   # Namecheap
client.get_namesilo_nameservers("example.com")    # NameSilo
```

> Both `set_*_nameservers` methods send a JSON body: `{"domain": "...", "nameservers": [...]}`

### Cloudflare Integration (FREE)

```python
# Create Cloudflare zone (or get existing by domain name)
zone = client.create_cloudflare_zone("example.com")

# List zones
zones = client.list_cloudflare_zones()

# Create DNS records in Cloudflare (use domain name, not zone_id)
client.create_cloudflare_dns_record(
    domain="example.com",
    record_type="CNAME",          # CNAME required for tunnel hosting
    name="@",
    content="<tunnel_id>.cfargotunnel.com",
    proxied=True   # REQUIRED — Cloudflare proxy routes traffic to the tunnel
)

# Update a DNS record (e.g. turn on proxy for tunnel traffic)
client.update_dns_record(
    "example.com",
    record_id="abc123",
    proxied=True,
    registrar="cloudflare"   # Cloudflare proxy must be ON for tunnel traffic to work
)

# Create page rule (www redirect)
client.create_page_rule(
    zone_id=zone["zone_id"],
    target_url="www.example.com/*",
    forward_url="https://example.com/$1"
)
```

### Cloudflare Workers (Inbound Email)

```python
WORKER_JS = """
export default {
  async email(message, env) {
    await fetch(env.WEBHOOK_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Webhook-Secret": env.WEBHOOK_SECRET
      },
      body: JSON.stringify({
        from: message.from,
        to: message.to,
        subject: message.headers.get("subject") || ""
      })
    });
  }
};
"""

# Deploy a Worker for an owned agieth domain
client.deploy_cloudflare_worker(
    script_name="email-example-com",
    domain="example.com",
    content=WORKER_JS,
    bindings=[
        {
            "type": "plain_text",
            "name": "WEBHOOK_URL",
            "text": "https://mail.example.com/inbound"
        }
    ],
    tags=["inbound-email"]
)

# Add a secret used by the Worker
client.set_cloudflare_worker_secret(
    "email-example-com",
    "WEBHOOK_SECRET",
    "replace-me"
)

# Route all unmatched inbound mail for the domain to the Worker
client.set_cloudflare_worker_catch_all(
    domain="example.com",
    script_name="email-example-com"
)

# Inspect or update the Worker later
client.list_cloudflare_workers("example.com")
client.get_cloudflare_worker("email-example-com")
client.get_cloudflare_worker_settings("email-example-com")
client.get_cloudflare_worker_catch_all("example.com")
client.update_cloudflare_worker_settings(
    "email-example-com",
    tags=["inbound-email", "production"]
)
```

- Worker routes are restricted to domains owned by the authenticated API key.
- Deploy requests automatically add agieth ownership tags to the script.
- Use deploy `bindings` for plain-text config like `WEBHOOK_URL`.
- Use `set_cloudflare_worker_secret` for secret values like `WEBHOOK_SECRET`.
- Use `set_cloudflare_worker_catch_all` to configure Cloudflare Email Routing catch-all delivery to the Worker.
- Worker settings endpoints manage Cloudflare script settings such as tags, `logpush`, observability, and tail consumers.
- Catch-all routing also requires Cloudflare Email Routing to be enabled for the zone.

### Cloudflare Email Routing Rules (granular per-zone CRUD)

For more granular control than the catch-all helper, manage individual email routing rules per zone. Required token on the agieth server: `CLOUDFLARE_ALL_ZONE_EMAIL_ROUTING` with Email Routing Rules Edit permission.

```python
# List existing rules for a zone
rules = client.list_email_routing_rules(zone_id="80f8043960db99916b554eb82be2666c")

# Create a catch-all rule (use when no other catch-all rule exists)
client.create_email_routing_rule(
    zone_id="80f8043960db99916b554eb82be2666c",
    name="Forward all to email-forwarder Worker",
    matchers=[{"type": "all"}],
    actions=[{"type": "worker", "value": ["email-forwarder"]}],
    enabled=True
)

# Create a specific address rule (use this if a catch-all drop rule already exists)
client.create_email_routing_rule(
    zone_id="80f8043960db99916b554eb82be2666c",
    name="Forward info@ to Worker",
    matchers=[{"type": "literal", "field": "to", "value": "info@example.com"}],
    actions=[{"type": "worker", "value": ["email-forwarder"]}],
    enabled=True
)

# Update or delete an existing rule
client.update_email_routing_rule(
    zone_id="80f8043960db99916b554eb82be2666c",
    rule_id="d088e9b5a72f435ea2caf88b1b695771",
    actions=[{"type": "worker", "value": ["email-forwarder"]}],
    enabled=True
)
client.delete_email_routing_rule(
    zone_id="80f8043960db99916b554eb82be2666c",
    rule_id="d088e9b5a72f435ea2caf88b1b695771"
)
```

**Matcher types:**
- `{"type": "all"}` — catch-all (only ONE allowed per zone; conflicts with existing drop rules)
- `{"type": "literal", "field": "to", "value": "info@example.com"}` — specific address

**Action types:**
- `{"type": "worker", "value": ["email-forwarder"]}` — route to a Cloudflare Worker
- `{"type": "forward", "value": ["you@gmail.com"]}` — forward to another email (must be verified)
- `{"type": "drop"}` — silently drop the email (no delivery)

**Known issues:**
- Error 2020 "Invalid rule operation": existing catch-all drop rule blocks updates. Workaround: use specific `literal` matchers.
- Error 2007 "must specify worker id": worker value should be the script name in a list: `["email-forwarder"]`
- Error 2054 "Destination address is not verified": forward action requires a verified destination email.
- Cloudflare only allows ONE catch-all rule per zone. If a disabled drop rule already exists, use `literal` matchers for additional rules.

### Cloudflare Tunnel Hosting (optional — cloudflared not required)

```python
# Create tunnel (no public IP needed)
result = client.create_tunnel("example.com", local_port=3000)
# Returns: tunnel_id, tunnel_token, credentials, instructions

hostname = f"{result['tunnel_id']}.cfargotunnel.com"

# Run: cloudflared tunnel run --token <tunnel_token>

# DNS setup (REQUIRED for HTTPS to work):
client.create_cloudflare_dns_record(
    domain="example.com",
    record_type="CNAME",
    name="@",
    content=hostname,
    proxied=True                  # REQUIRED — Cloudflare routes traffic here
)

# Also add www:
client.create_cloudflare_dns_record(
    domain="example.com",
    record_type="CNAME",
    name="www",
    content=hostname,
    proxied=True
)
```

**⚠️ Critical:** The DNS record MUST be `CNAME` → `*.cfargotunnel.com` with `proxied=True`. Do NOT use A/AAAA records pointing to tunnel IPs — Cloudflare will block them with a 403 error. This is the #1 cause of broken HTTPS with tunnels.

**Alternative:** If you have a static IP, you can skip cloudflared entirely. Add an A record pointing to your static IP instead (and set `proxied=False`).

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

The Cloudflare tunnel and worker features use **agieth.ai's Cloudflare account** — not yours. Agieth creates the resources, returns the data you need, and Cloudflare sees the traffic as agieth-managed infrastructure. You do NOT need your own Cloudflare API token for this skill to work.

## Security Notes

- API keys should be treated as secrets
- Only provide keys with minimum required permissions
- **Always verify the `payment_address` returned by the API before sending crypto** — the skill surfaces the address from the server response
- The skill sends the API key via the `Authorization: Bearer` HTTP header exclusively (no query parameters)
- This skill makes network requests to:
  - `https://api.agieth.ai` (main API)
  - `https://ethereum.publicnode.com` and `https://eth.drpc.org` (Ethereum blockchain RPC — for ETH balance checks and transaction broadcasting)
  - `https://cloudflare.com` (via cloudflared tunnel, when tunnel feature is used — optional)

## API Documentation

Full API documentation: https://api.agieth.ai/api/v1/manifest

## Links

- **API Docs:** https://api.agieth.ai/api/v1/manifest
- **Homepage:** https://agieth.ai
- **Skill Guide:** https://github.com/larkins/one_shot_site
- **Support:** support@agieth.ai

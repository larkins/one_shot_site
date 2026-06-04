#!/usr/bin/env python3
"""
agieth.ai API Skill

Provides access to agieth.ai domain registration and management API.
"""
import os
import json
import requests
from typing import Optional, Dict, List

# Skill metadata
SKILL_NAME = "agieth"
SKILL_VERSION = "1.0.18"

# Hardcoded production API base — agieth.ai is the product, no configurable alternative
DEFAULT_BASE_URL = "https://api.agieth.ai"


class AgiethClient:
    """Client for agieth.ai API.

    Requires AGIETH_API_KEY and AGIETH_EMAIL credentials.
    Set via environment variables or pass directly to constructor.
    """

    def __init__(self, api_key: str = None, email: str = None):
        """Initialize client.

        Credentials are loaded in this order:
        1. Arguments passed to constructor
        2. Environment variables (AGIETH_API_KEY, AGIETH_EMAIL)

        Args:
            api_key: API key (required if not in env)
            email: Email address (required if not in env)

        Raises:
            ValueError: If API key is not provided and not in environment
        """
        self.base_url = DEFAULT_BASE_URL
        self.api_key = api_key or os.getenv("AGIETH_API_KEY", "")
        self.email = email or os.getenv("AGIETH_EMAIL", "")

        # Validate API key is present
        if not self.api_key:
            raise ValueError(
                "AGIETH_API_KEY is required. "
                "Set environment variable or pass api_key parameter. "
                "Get your API key at https://api.agieth.ai/api/v1/keys/create"
            )

        # RPC failover order (primary first, then fallback)
        self.rpc_endpoints = [
            os.getenv("ETH_RPC_PRIMARY", "https://ethereum.publicnode.com"),
            os.getenv("ETH_RPC_FALLBACK", "https://eth.drpc.org"),
        ]

    def _headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _get(self, endpoint: str, params: Dict = None) -> Dict:
        """Make GET request."""
        url = f"{self.base_url}{endpoint}"
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        return resp.json()

    def _post(self, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make POST request."""
        url = f"{self.base_url}{endpoint}"
        resp = requests.post(url, headers=self._headers(), json=data, params=params, timeout=30)
        return resp.json()

    def _post_form(self, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make POST request with form-encoded data."""
        url = f"{self.base_url}{endpoint}"
        headers = self._headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        resp = requests.post(url, headers=headers, data=data, params=params, timeout=30)
        return resp.json()

    def _put(self, endpoint: str, params: Dict = None) -> Dict:
        """Make PUT request."""
        url = f"{self.base_url}{endpoint}"
        resp = requests.put(url, headers=self._headers(), params=params, timeout=30)
        return resp.json()

    def _put_json(self, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make PUT request with JSON body."""
        url = f"{self.base_url}{endpoint}"
        resp = requests.put(url, headers=self._headers(), json=data, params=params, timeout=30)
        return resp.json()

    def _patch(self, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make PATCH request with JSON body."""
        url = f"{self.base_url}{endpoint}"
        resp = requests.patch(url, headers=self._headers(), json=data, params=params, timeout=30)
        return resp.json()

    def _delete(self, endpoint: str, params: Dict = None) -> Dict:
        """Make DELETE request."""
        url = f"{self.base_url}{endpoint}"
        resp = requests.delete(url, headers=self._headers(), params=params, timeout=30)
        return resp.json()

    # ========== API Key ==========

    def create_api_key(self, email: str = None) -> Dict:
        """Request API key creation.

        Sends verification email to the provided address.

        Args:
            email: Email address (uses default if not provided)

        Returns:
            Dict with success status
        """
        email = email or self.email
        return self._post("/api/v1/keys/create", {"email": email})

    def verify_api_key(self, token: str, email: str) -> Dict:
        """Verify email and get API key.

        Args:
            token: Verification token from email
            email: Email address used for registration

        Returns:
            Dict with verification status
        """
        return self._get("/api/v1/keys/verify", params={"token": token, "email": email})

    # ========== Domains ==========

    def check_availability(self, domain: str, registrar: str = "namesilo") -> Dict:
        """Check domain availability.

        Args:
            domain: Domain name to check
            registrar: Registrar to use (namesilo, godaddy, namecheap)

        Returns:
            Dict with availability and pricing
        """
        return self._get("/domains/available", params={"domain": domain, "provider": registrar})

    def list_domains(self, provider: str = "owned") -> Dict:
        """List all domains.

        Args:
            provider: Domain source — "owned" (default, your registered domains),
                      or "namesilo"/"godaddy" (registrar account listing)

        Returns:
            Dict with list of domains
        """
        return self._get("/domains", params={"provider": provider})

    def get_domain_info(self, domain: str) -> Dict:
        """Get domain details.

        Args:
            domain: Domain name

        Returns:
            Dict with domain details
        """
        return self._get(f"/domains/{domain}")

    def create_quote(self, domain: str, years: int = 1, registrar: str = "namecheap",
                     registrant: Dict = None) -> Dict:
        """Create a quote for domain registration.

        Args:
            domain: Domain name
            years: Registration years (1-10)
            registrar: Registrar (namecheap, namesilo)
            registrant: Registrant info dict with:
                - full_name: Full name
                - email: Email address
                - address_line1: Street address
                - city: City
                - postal_code: Postal code
                - country_code: ISO 3166-1 alpha-2 (e.g., AU, US)
                - phone: Phone number

        Returns:
            Dict with:
                - quote_id: Unique quote identifier
                - price_usd: Price in USD
                - price_eth: Price in ETH
                - payment_address: Ethereum address to send payment to
                - expires_at: Quote expiration time

        Note:
            payment_address is set by the server and may change.
            Always use the payment_address from the quote response,
            not a hardcoded address.
        """
        data = {
            "domain": domain,
            "years": years,
            "provider": registrar,
        }

        if registrant:
            data["registrant"] = registrant

        return self._post("/api/v1/domains/quote", data=data)

    def get_quote(self, quote_id: str) -> Dict:
        """Get quote status.

        Args:
            quote_id: Quote ID

        Returns:
            Dict with quote status and payment details
        """
        return self._get(f"/api/v1/quotes/{quote_id}")

    def check_payment(self, quote_id: str) -> Dict:
        """Check payment status for a quote.

        Args:
            quote_id: Quote ID

        Returns:
            Dict with payment status
        """
        return self._get(f"/api/v1/quotes/{quote_id}/payment")

    def confirm_payment(self, quote_id: str, tx_hash: str, currency: str = "ETH") -> Dict:
        """Confirm a payment for a quote.

        Args:
            quote_id: Quote ID
            tx_hash: Transaction hash
            currency: Currency (ETH, USDC, USDT)

        Returns:
            Dict with confirmation status
        """
        data = {
            "tx_hash": tx_hash,
            "currency": currency,
        }
        return self._post_form(f"/api/v1/quotes/{quote_id}/confirm", data=data)

    def register_domain(self, quote_id: str) -> Dict:
        """Register a domain after payment is confirmed.

        Args:
            quote_id: Quote ID

        Returns:
            Dict with registration status
        """
        return self._post_form(f"/api/v1/quotes/{quote_id}/register")

    # ========== DNS Management ==========

    def list_dns_records(self, domain: str, registrar: str = "namecheap") -> Dict:
        """List DNS records for a domain.

        Args:
            domain: Domain name
            registrar: Registrar (namecheap, namesilo)

        Returns:
            Dict with list of DNS records
        """
        return self._get(f"/api/v1/domains/{domain}/dns", params={"registrar": registrar})

    def add_dns_record(self, domain: str, record_type: str, name: str, value: str,
                       ttl: int = 3600, priority: int = None,
                       registrar: str = "namecheap") -> Dict:
        """Add a DNS record.

        Args:
            domain: Domain name
            record_type: A, AAAA, CNAME, MX, TXT, NS
            name: Record name (www, @, etc.)
            value: Record value
            ttl: TTL in seconds
            priority: Priority for MX records
            registrar: Registrar (namecheap, namesilo)

        Returns:
            Dict with success status
        """
        params = {
            "registrar": registrar,
            "record_type": record_type,
            "name": name,
            "value": value,
            "ttl": ttl,
            }
        if priority is not None:
            params["priority"] = priority

        return self._post(f"/api/v1/domains/{domain}/dns", params=params)

    def update_dns_record(self, domain: str, record_id: str,
                          name: str = None, content: str = None,
                          ttl: int = None, proxied: bool = None,
                          registrar: str = "cloudflare") -> Dict:
        """Update a DNS record.

        Routes to Cloudflare when the domain has a Cloudflare zone, otherwise
        uses the registrar API.

        Args:
            domain: Domain name
            record_id: Record ID to update
            name: New record name (optional)
            content: New record value (optional)
            ttl: New TTL in seconds (optional)
            proxied: Enable Cloudflare proxy (optional — cloudflare only)
            registrar: Provider — cloudflare (default), namecheap, or namesilo

        Returns:
            Dict with success status
        """
        params = {}
        if name is not None:
            params["name"] = name
        if content is not None:
            params["content"] = content
        if ttl is not None:
            params["ttl"] = ttl
        if proxied is not None:
            params["proxied"] = "true" if proxied else "false"

        return self._put(
            f"/api/v1/domains/{domain}/dns/{record_id}",
            params={"registrar": registrar, **params}
        )

    def delete_dns_record(self, domain: str, record_id: str,
                          registrar: str = "namecheap") -> Dict:
        """Delete a DNS record.

        Args:
            domain: Domain name
            record_id: Record ID to delete
            registrar: Registrar (namecheap, namesilo)

        Returns:
            Dict with success status
        """
        return self._delete(f"/api/v1/domains/{domain}/dns/{record_id}", params={"registrar": registrar})

    # ========== Cloudflare ==========

    def create_cloudflare_zone(self, domain: str) -> Dict:
        """Create a Cloudflare zone for a domain.

        Args:
            domain: Domain name

        Returns:
            Dict with zone_id and nameservers
        """
        return self._post("/api/v1/cloudflare/zones", data={"domain": domain})

    def list_cloudflare_zones(self) -> Dict:
        """List all Cloudflare zones."""
        return self._get("/api/v1/cloudflare/zones")

    def get_cloudflare_zone(self, domain: str) -> Dict:
        """Get or create the Cloudflare zone record for an owned domain.

        Args:
            domain: Owned domain name

        Returns:
            Dict with Cloudflare zone metadata
        """
        return self._get(f"/api/v1/cloudflare/zones/{domain}")

    def list_cloudflare_dns_records(self, zone_id_or_domain: str) -> Dict:
        """List DNS records for a Cloudflare zone.

        Args:
            zone_id_or_domain: Cloudflare zone ID or owned domain name

        Returns:
            Dict with Cloudflare DNS records
        """
        return self._get(f"/api/v1/cloudflare/zones/{zone_id_or_domain}/dns")

    def create_cloudflare_dns_record(
        self,
        domain: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 3600,
        proxied: bool = False,
        priority: int = None,
    ) -> Dict:
        """Create a DNS record directly in Cloudflare.

        Args:
            domain: Owned domain name or Cloudflare zone ID
            record_type: DNS record type
            name: DNS name
            content: DNS value/content
            ttl: TTL in seconds
            proxied: Enable Cloudflare proxy when supported
            priority: Optional MX priority

        Returns:
            Dict with created record metadata
        """
        params = {
            "record_type": record_type,
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": "true" if proxied else "false",
        }
        if priority is not None:
            params["priority"] = priority
        return self._post(f"/api/v1/cloudflare/zones/{domain}/dns", params=params)

    # ========== Cloudflare Workers (Inbound Email) ==========

    def list_cloudflare_workers(self, domain: str = None) -> Dict:
        """List Cloudflare Workers for your owned agieth domains.

        Args:
            domain: Optional owned domain filter

        Returns:
            Dict with worker metadata for scripts tagged to your domains
        """
        params = {"domain": domain} if domain else None
        return self._get("/api/v1/cloudflare/worker/scripts", params=params)

    def get_cloudflare_worker(self, script_name: str) -> Dict:
        """Get Cloudflare Worker metadata, settings, and raw content.

        Args:
            script_name: Worker script name

        Returns:
            Dict with worker metadata, script settings, and content
        """
        return self._get(f"/api/v1/cloudflare/worker/scripts/{script_name}")

    def deploy_cloudflare_worker(
        self,
        script_name: str,
        domain: str,
        content: str,
        bindings: List[Dict] = None,
        tags: List[str] = None,
        compatibility_date: str = None,
        compatibility_flags: List[str] = None,
        logpush: bool = None,
    ) -> Dict:
        """Deploy or update a Cloudflare Worker for an owned domain.

        Args:
            script_name: Worker script name
            domain: Registered agieth domain owned by the authenticated API key
            content: Worker source code (module-style JavaScript/TypeScript)
            bindings: Optional Cloudflare Worker bindings to include on deploy
            tags: Optional additional Cloudflare tags
            compatibility_date: Optional Cloudflare compatibility date
            compatibility_flags: Optional Cloudflare compatibility flags
            logpush: Optional Cloudflare logpush setting

        Returns:
            Dict with deployed worker metadata
        """
        data = {
            "domain": domain,
            "content": content,
        }
        if bindings is not None:
            data["bindings"] = bindings
        if tags is not None:
            data["tags"] = tags
        if compatibility_date is not None:
            data["compatibility_date"] = compatibility_date
        if compatibility_flags is not None:
            data["compatibility_flags"] = compatibility_flags
        if logpush is not None:
            data["logpush"] = logpush

        return self._put_json(f"/api/v1/cloudflare/worker/scripts/{script_name}", data=data)

    def delete_cloudflare_worker(self, script_name: str) -> Dict:
        """Delete an owned Cloudflare Worker.

        Args:
            script_name: Worker script name

        Returns:
            Dict with deletion status
        """
        return self._delete(f"/api/v1/cloudflare/worker/scripts/{script_name}")

    def get_cloudflare_worker_settings(self, script_name: str) -> Dict:
        """Get script-level settings for an owned Cloudflare Worker.

        Args:
            script_name: Worker script name

        Returns:
            Dict with logpush, tags, observability, and tail consumer settings
        """
        return self._get(f"/api/v1/cloudflare/worker/scripts/{script_name}/settings")

    def update_cloudflare_worker_settings(
        self,
        script_name: str,
        logpush: Optional[bool] = None,
        observability: Dict = None,
        tail_consumers: List[Dict] = None,
        tags: List[str] = None,
    ) -> Dict:
        """Patch script-level settings for an owned Cloudflare Worker.

        Args:
            script_name: Worker script name
            logpush: Optional logpush toggle
            observability: Optional Cloudflare observability settings object
            tail_consumers: Optional tail worker consumers list
            tags: Optional additional tags

        Returns:
            Dict with updated settings
        """
        data = {}
        if logpush is not None:
            data["logpush"] = logpush
        if observability is not None:
            data["observability"] = observability
        if tail_consumers is not None:
            data["tail_consumers"] = tail_consumers
        if tags is not None:
            data["tags"] = tags

        return self._patch(f"/api/v1/cloudflare/worker/scripts/{script_name}/settings", data=data)

    def get_cloudflare_worker_catch_all(self, domain: str) -> Dict:
        """Get the Cloudflare Email Routing catch-all rule for an owned domain.

        Args:
            domain: Owned domain name

        Returns:
            Dict with catch-all rule metadata
        """
        return self._get(f"/api/v1/cloudflare/worker/domains/{domain}/catch-all")

    def set_cloudflare_worker_catch_all(
        self,
        domain: str,
        script_name: str,
        enabled: bool = True,
        name: str = None,
    ) -> Dict:
        """Route catch-all inbound mail for an owned domain to an owned Worker.

        Args:
            domain: Owned domain name
            script_name: Cloudflare Worker script name
            enabled: Enable or disable the catch-all rule
            name: Optional Cloudflare rule name

        Returns:
            Dict with updated catch-all rule metadata
        """
        data = {
            "script_name": script_name,
            "enabled": enabled,
        }
        if name is not None:
            data["name"] = name
        return self._put_json(f"/api/v1/cloudflare/worker/domains/{domain}/catch-all", data=data)

    # ── Granular Email Routing Rules (per-zone) ─────────────────────────────
    # These provide full CRUD on Cloudflare Email Routing rules — useful when
    # you need specific address rules instead of (or alongside) a catch-all.
    # Requires CLOUDFLARE_ALL_ZONE_EMAIL_ROUTING on the agieth server.

    def list_email_routing_rules(self, zone_id: str) -> Dict:
        """List all email routing rules for a Cloudflare zone.

        Args:
            zone_id: Cloudflare zone ID (e.g. "80f8043960db99916b554eb82be2666c")

        Returns:
            Dict with "rules" list and "total" count
        """
        return self._get(f"/api/v1/cloudflare/zones/{zone_id}/email/routing/rules")

    def create_email_routing_rule(
        self,
        zone_id: str,
        matchers: List[Dict],
        actions: List[Dict],
        name: str = None,
        enabled: bool = True,
        priority: int = None,
    ) -> Dict:
        """Create a new email routing rule for a Cloudflare zone.

        Typical use: route all inbound mail for the zone (or specific addresses)
        to a Cloudflare Worker (e.g. "email-forwarder").

        Matcher examples:
            [{"type": "all"}]                                       # catch-all
            [{"type": "literal", "field": "to", "value": "info@x"}]  # specific

        Action examples:
            [{"type": "worker", "value": ["email-forwarder"]}]
            [{"type": "forward", "value": ["you@gmail.com"]}]
            [{"type": "drop"}]

        Args:
            zone_id: Cloudflare zone ID
            matchers: List of matcher dicts
            actions: List of action dicts
            name: Optional Cloudflare rule name
            enabled: Enable or disable the rule
            priority: Optional priority (lower = higher precedence)

        Returns:
            Dict with created "rule" object
        """
        data = {
            "matchers": matchers,
            "actions": actions,
            "enabled": enabled,
        }
        if name is not None:
            data["name"] = name
        if priority is not None:
            data["priority"] = priority
        return self._post(f"/api/v1/cloudflare/zones/{zone_id}/email/routing/rules", data=data)

    def update_email_routing_rule(
        self,
        zone_id: str,
        rule_id: str,
        name: str = None,
        matchers: List[Dict] = None,
        actions: List[Dict] = None,
        enabled: bool = None,
        priority: int = None,
    ) -> Dict:
        """Update an existing email routing rule (full replace via PUT).

        Args:
            zone_id: Cloudflare zone ID
            rule_id: Routing rule ID
            name: New rule name (or None to keep)
            matchers: New matchers list (or None to keep)
            actions: New actions list (or None to keep)
            enabled: New enabled state (or None to keep)
            priority: New priority (or None to keep)

        Returns:
            Dict with updated "rule" object
        """
        data = {}
        if name is not None:
            data["name"] = name
        if matchers is not None:
            data["matchers"] = matchers
        if actions is not None:
            data["actions"] = actions
        if enabled is not None:
            data["enabled"] = enabled
        if priority is not None:
            data["priority"] = priority
        return self._put_json(f"/api/v1/cloudflare/zones/{zone_id}/email/routing/rules/{rule_id}", data=data)

    def delete_email_routing_rule(self, zone_id: str, rule_id: str) -> Dict:
        """Delete an email routing rule.

        Args:
            zone_id: Cloudflare zone ID
            rule_id: Routing rule ID

        Returns:
            Dict with "deleted": True
        """
        return self._delete(f"/api/v1/cloudflare/zones/{zone_id}/email/routing/rules/{rule_id}")

    def set_cloudflare_worker_secret(
        self,
        script_name: str,
        secret_name: str,
        text: str,
        require_ownership: bool = True,
    ) -> Dict:
        """Create or update a Cloudflare Worker secret.

        Args:
            script_name: Worker script name
            secret_name: Secret binding name (for example WEBHOOK_SECRET)
            text: Secret value
            require_ownership: If False, skip the user-ownership check
                (use for shared/managed Workers like `email-forwarder`)

        Returns:
            Dict with secret metadata
        """
        params = {} if require_ownership else {"require_ownership": "false"}
        return self._put_json(
            f"/api/v1/cloudflare/worker/scripts/{script_name}/secrets/{secret_name}",
            data={"text": text},
            params=params or None,
        )

    def rotate_cloudflare_worker_secret(
        self,
        script_name: str,
        secret_name: str,
        require_ownership: bool = True,
        random_bytes: int = 32,
    ) -> Dict:
        """Rotate a Cloudflare Worker secret — generate a new value and return it.

        Generates a cryptographically random secret, sets it on the Worker,
        and returns the new value. Use this to rotate the upstream (Cloudflare
        Worker) and downstream (mail server) independently:

        1. Call this method — get the new_value in the response
        2. Set that value as SMTP2GO_WEBHOOK_SECRET in the mail server's .env
        3. Restart the mail server
        4. Both upstream and downstream now use the new secret

        Args:
            script_name: Worker script name (e.g. "email-forwarder")
            secret_name: Secret binding name (e.g. "WEBHOOK_SECRET")
            require_ownership: If False, skip the user-ownership check
                (use for shared/managed Workers)
            random_bytes: Random secret size in bytes (default 32, range 16-64)

        Returns:
            Dict with new_value, rotated_at, and other metadata

        Example:
            >>> result = client.rotate_cloudflare_worker_secret(
            ...     "email-forwarder", "WEBHOOK_SECRET", require_ownership=False
            ... )
            >>> new_secret = result["new_value"]
            >>> # Now update the mail server's env and restart it
        """
        params: Dict = {"bytes": str(random_bytes)}
        if not require_ownership:
            params["require_ownership"] = "false"
        return self._post(
            f"/api/v1/cloudflare/worker/scripts/{script_name}/secrets/{secret_name}/rotate",
            params=params,
        )

    def delete_cloudflare_worker_secret(self, script_name: str, secret_name: str) -> Dict:
        """Delete a Cloudflare Worker secret.

        Args:
            script_name: Worker script name
            secret_name: Secret binding name

        Returns:
            Dict with deletion status
        """
        return self._delete(
            f"/api/v1/cloudflare/worker/scripts/{script_name}/secrets/{secret_name}"
        )

    # ========== Cloudflare Tunnel Hosting ==========

    def list_tunnels(
        self,
        domain: str = None,
        include_archived: bool = False,
    ) -> Dict:
        """List Cloudflare Tunnels owned by the authenticated user.

        Returns tunnels associated with the user's domains, enriched with
        live Cloudflare status (status, connection count, deleted_at).

        Args:
            domain: Optional filter — return only tunnels for this domain
            include_archived: Include cancelled/deactivated tunnels (default False)

        Returns:
            Dict with:
                - tunnels: list of tunnel objects (id, name, domain, status, cloudflare info)
                - total: count of tunnels returned

        Example:
            >>> tunnels = client.list_tunnels()
            >>> for t in tunnels["tunnels"]:
            ...     print(f'{t["domain"]}: {t["cloudflare"]["status"]} ({t["cloudflare"]["connections"]} conns)')
        """
        params: Dict = {}
        if domain is not None:
            params["domain"] = domain
        if include_archived:
            params["include_archived"] = "true"
        return self._get("/api/v1/cloudflare/tunnel", params=params)

    def delete_tunnel(self, tunnel_id: str, cleanup_dns: bool = False) -> Dict:
        """Delete a Cloudflare Tunnel owned by the authenticated user.

        Marks the protected_hosting record as cancelled. If cleanup_dns=True,
        also deletes any CNAME records on the domain's zone pointing to
        <tunnel_id>.cfargotunnel.com.

        Note: Cloudflare's DELETE is soft — the tunnel enters a "deleted" state
        for ~30 days before being hard-removed. If the tunnel has active
        connections, Cloudflare returns error 1022 — stop the cloudflared
        process first, then retry.

        Args:
            tunnel_id:   Tunnel ID to delete
            cleanup_dns: Also delete DNS CNAMEs pointing to this tunnel (default False)

        Returns:
            Dict with success, tunnel_id, domain, deleted_at, cleaned_dns

        Example:
            >>> # List tunnels, find the one to delete
            >>> tunnels = client.list_tunnels()
            >>> old = next(t for t in tunnels["tunnels"] if t["domain"] == "old.com")
            >>> # Stop cloudflared first
            >>> # ... systemctl --user stop cloudflared-mail ...
            >>> client.delete_tunnel(old["id"])
            {'success': True, 'tunnel_id': '...', 'domain': 'old.com', ...}
        """
        params: Dict = {}
        if cleanup_dns:
            params["cleanup_dns"] = "true"
        return self._delete(f"/api/v1/cloudflare/tunnel/{tunnel_id}", params=params)

    def create_tunnel(self, domain: str, local_port: int = 3000) -> Dict:
        """Create a Cloudflare Tunnel for protected hosting.

        Allows hosting without a public IP or port forwarding.
        The domain must already be registered and in Cloudflare.

        Args:
            domain: Domain name (must be registered via agieth)
            local_port: Local port to tunnel (default: 3000)

        Returns:
            Dict with:
                - tunnel_id: Cloudflare tunnel ID
                - tunnel_token: Token for cloudflared tunnel run
                - credentials: Full credentials object (AccountTag, TunnelID, TunnelName, TunnelSecret)
                - instructions: Setup instructions

        Example:
            >>> result = client.create_tunnel("myapp.com", 3000)
            >>> print(result["tunnel_token"])
            >>> print(result["credentials"]["TunnelSecret"])
            >>> # Save credentials to a cloudflared credentials file and run:
            >>> # cloudflared tunnel run --config /path/to/cloudflared-credentials.json
        """
        return self._post(
            "/api/v1/hosting/tunnel",
            params={"domain": domain, "local_port": local_port}
        )

    def get_tunnel_token(self, domain: str) -> Dict:
        """Get tunnel token for an existing domain.

        If tunnel doesn't exist, creates one.

        Args:
            domain: Domain name

        Returns:
            Dict with tunnel_token and setup instructions
        """
        return self._get(f"/api/v1/hosting/tunnel/{domain}/token")

    def get_hosting_status(self, domain: str) -> Dict:
        """Get protected hosting status for a domain.

        Args:
            domain: Domain name

        Returns:
            Dict with hosting status and details
        """
        return self._get(f"/api/v1/hosting/status/{domain}")

    def cancel_hosting(self, domain: str) -> Dict:
        """Cancel protected hosting for a domain.

        Args:
            domain: Domain name

        Returns:
            Dict with cancellation status
        """
        return self._delete(f"/api/v1/hosting/{domain}")

    # ========== Registrar Nameservers ==========

    def get_namecheap_nameservers(self, domain: str) -> Dict:
        """Get current nameservers for a domain at Namecheap.

        Args:
            domain: Domain name

        Returns:
            Dict with domain and nameservers list
        """
        return self._get(f"/api/v1/namecheap/nameservers/{domain}")

    def set_namecheap_nameservers(self, domain: str, nameservers: List[str]) -> Dict:
        """Change nameservers for a domain at Namecheap.

        Use this to point a domain's DNS to Cloudflare after registration.

        Args:
            domain: Domain name (e.g. "example.com")
            nameservers: List of nameserver hostnames
                         e.g. ["ns1.cloudflare.com", "ns2.cloudflare.com"]

        Returns:
            Dict with success status
        """
        return self._post(
            "/api/v1/namecheap/nameservers",
            data={"domain": domain, "nameservers": nameservers}
        )

    def get_namesilo_nameservers(self, domain: str) -> Dict:
        """Get current nameservers for a domain at NameSilo.

        Args:
            domain: Domain name

        Returns:
            Dict with domain and nameservers list
        """
        return self._get(f"/api/v1/namesilo/nameservers/{domain}")

    def set_namesilo_nameservers(self, domain: str, nameservers: List[str]) -> Dict:
        """Change nameservers for a domain at NameSilo.

        Use this to point a domain's DNS to Cloudflare after registration.

        Args:
            domain: Domain name (e.g. "example.com")
            nameservers: List of nameserver hostnames
                         e.g. ["ns1.cloudflare.com", "ns2.cloudflare.com"]

        Returns:
            Dict with success status
        """
        return self._post(
            "/api/v1/namesilo/nameservers",
            data={"domain": domain, "nameservers": nameservers}
        )

    # ========== Balance & Credits ==========

    def get_balance(self) -> Dict:
        """Get account balance and credits."""
        return self._get("/api/v1/balance")

    def get_credits(self) -> Dict:
        """Get credit balance and history."""
        return self._get("/api/v1/credits")

    # ========== Cloudflare Page Rules ==========

    def list_page_rules(self, zone_id: str) -> Dict:
        """List all page rules for a Cloudflare zone.

        Args:
            zone_id: Cloudflare zone ID

        Returns:
            Dict with list of page rules
        """
        return self._get(f"/api/v1/cloudflare/zones/{zone_id}/pagerules")

    def create_page_rule(self, zone_id: str, target_url: str, forward_url: str,
                         status_code: int = 301) -> Dict:
        """Create a page rule to redirect traffic.

        Args:
            zone_id: Cloudflare zone ID
            target_url: URL pattern to match (e.g., "www.example.com/*")
            forward_url: URL to forward to (e.g., "https://example.com/$1")
            status_code: HTTP status code (301 for permanent, 302 for temporary)

        Returns:
            Dict with rule_id and success status
        """
        return self._post(
            f"/api/v1/cloudflare/zones/{zone_id}/pagerules",
            data={"target_url": target_url, "forward_url": forward_url, "status_code": status_code},
        )

    def delete_page_rule(self, zone_id: str, rule_id: str) -> Dict:
        """Delete a page rule.

        Args:
            zone_id: Cloudflare zone ID
            rule_id: Page rule ID

        Returns:
            Dict with success status
        """
        return self._delete(f"/api/v1/cloudflare/zones/{zone_id}/pagerules/{rule_id}")

    # ========== Subscriptions ==========

    def get_subscription_pricing(self, service_type: str, months: int = 1,
                                  country_code: str = None) -> Dict:
        """Get subscription pricing.

        Args:
            service_type: static_hosting, tunnel_hosting, or combined
            months: Number of months (1-36)
            country_code: ISO 3166-1 alpha-2 for GST calculation

        Returns:
            Dict with pricing breakdown
        """
        params = {"service_type": service_type, "months": months}
        if country_code:
            params["country_code"] = country_code
        return self._get("/api/v1/subscriptions/pricing", params=params)

    def list_subscriptions(self) -> Dict:
        """List all subscriptions for the authenticated customer.

        Returns:
            Dict with list of subscriptions
        """
        return self._get("/api/v1/subscriptions")

    def get_subscription(self, subscription_id: int) -> Dict:
        """Get subscription status and details.

        Args:
            subscription_id: Subscription ID

        Returns:
            Dict with subscription details
        """
        return self._get(f"/api/v1/subscriptions/{subscription_id}")

    def create_subscription(self, domain: str, service_type: str, months: int,
                            zone_id: str = None) -> Dict:
        """Create a hosting subscription.

        Args:
            domain: Domain name
            service_type: static_hosting, tunnel_hosting, or combined
            months: Number of months to pre-pay (1-36)
            zone_id: Cloudflare zone ID (if already created)

        Returns:
            Dict with subscription details and next_step
        """
        params = {
            "domain": domain,
            "service_type": service_type,
            "months": months,
            }
        if zone_id:
            params["zone_id"] = zone_id
        return self._post("/api/v1/subscriptions", data=params)

    # ========== Wallet & Payment Utilities ==========

    def generate_wallet(self) -> Dict:
        """Generate a new Ethereum wallet.

        Returns:
            Dict with address, private_key (hex), and mnemonic (if available)

        Note: Store the private key securely! This is NOT saved by agieth.ai.
        """
        from eth_account import Account
        import secrets

        # Generate new account
        account = Account.create()

        return {
            "address": account.address,
            "private_key": account.key.hex(),
            "success": True,
            "warning": "Store your private key securely! Never share it."
        }

    def send_payment(self, to_address: str, amount_eth: float,
                     private_key: str = None) -> Dict:
        """Send ETH payment to an address.

        Args:
            to_address: Recipient address (0x...)
            amount_eth: Amount in ETH
            private_key: Sender's private key (uses wallet from .env if not provided)

        Returns:
            Dict with tx_hash, status, and gas_used
        """
        from web3 import Web3
        from eth_account import Account

        # Get private key
        if private_key is None:
            private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
            if not private_key:
                return {"success": False, "error": "No private key provided"}

        account = Account.from_key(private_key)
        last_error = None

        # Try primary RPC first, then fallback on first failure
        for idx, rpc_url in enumerate(self.rpc_endpoints):
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                nonce = w3.eth.get_transaction_count(account.address, "pending")
                gas_price = w3.eth.gas_price

                tx = {
                    "from": account.address,
                    "to": Web3.to_checksum_address(to_address),
                    "value": w3.to_wei(amount_eth, "ether"),
                    "gasPrice": gas_price,
                    "nonce": nonce,
                    "chainId": 1
                }

                tx["gas"] = w3.eth.estimate_gas(tx)
                signed = w3.eth.account.sign_transaction(tx, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

                return {
                    "success": receipt.status == 1,
                    "tx_hash": tx_hash.hex(),
                    "from": account.address,
                    "to": to_address,
                    "amount_eth": amount_eth,
                    "gas_used": receipt.gasUsed,
                    "block_number": receipt.blockNumber,
                    "rpc_used": rpc_url,
                    "rpc_failover_used": idx > 0,
                }
            except Exception as e:
                last_error = f"{rpc_url}: {e}"
                continue

        return {"success": False, "error": f"All RPC endpoints failed. Last error: {last_error}"}

    def send_erc20(self, token_address: str, to_address: str, amount: float,
                    private_key: str = None, decimals: int = 6) -> Dict:
        """Send ERC20 token payment (USDC, USDT, etc).

        Args:
            token_address: Token contract address (e.g., USDC mainnet)
            to_address: Recipient address
            amount: Amount in human units (e.g., 10.5 USDC)
            private_key: Sender's private key
            decimals: Token decimals (6 for USDC/USDT, 18 for most others)

        Returns:
            Dict with tx_hash and status
        """
        from web3 import Web3
        from eth_account import Account

        if private_key is None:
            private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
            if not private_key:
                return {"success": False, "error": "No private key provided"}

        account = Account.from_key(private_key)
        last_error = None

        # ERC20 transfer ABI
        erc20_abi = [
            {"constant": False, "inputs": [{"name": "_to", "type": "address"},
             {"name": "_value", "type": "uint256"}], "name": "transfer",
             "outputs": [{"name": "", "type": "bool"}], "type": "function"}
        ]

        for idx, rpc_url in enumerate(self.rpc_endpoints):
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                token = w3.eth.contract(
                    address=Web3.to_checksum_address(token_address),
                    abi=erc20_abi
                )

                amount_wei = int(amount * (10 ** decimals))
                nonce = w3.eth.get_transaction_count(account.address, "pending")
                tx = {
                    "from": account.address,
                    "nonce": nonce,
                    "gasPrice": w3.eth.gas_price,
                    "chainId": 1
                }

                contract_tx = token.functions.transfer(
                    Web3.to_checksum_address(to_address),
                    amount_wei
                ).build_transaction(tx)

                contract_tx["gas"] = w3.eth.estimate_gas(contract_tx)
                signed = w3.eth.account.sign_transaction(contract_tx, private_key)
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

                return {
                    "success": receipt.status == 1,
                    "tx_hash": tx_hash.hex(),
                    "from": account.address,
                    "to": to_address,
                    "amount": amount,
                    "token": token_address,
                    "rpc_used": rpc_url,
                    "rpc_failover_used": idx > 0,
                }
            except Exception as e:
                last_error = f"{rpc_url}: {e}"
                continue

        return {"success": False, "error": f"All RPC endpoints failed. Last error: {last_error}"}

    # ========== Manifest ==========

    def get_manifest(self) -> Dict:
        """Get API manifest for AI agents."""
        return self._get("/api/v1/manifest")

    def list_endpoints(self) -> Dict:
        """Get simple list of all endpoints."""
        return self._get("/api/v1/endpoints")

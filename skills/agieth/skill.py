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
SKILL_VERSION = "1.0.0"


class AgiethClient:
    """Client for agieth.ai API.
    
    Requires AGIETH_API_KEY and AGIETH_EMAIL credentials.
    Set via environment variables or pass directly to constructor.
    """
    
    def __init__(self, api_key: str = None, email: str = None, base_url: str = None):
        """Initialize client.
        
        Credentials are loaded in this order:
        1. Arguments passed to constructor
        2. Environment variables (AGIETH_API_KEY, AGIETH_EMAIL, AGIETH_BASE_URL)
        
        Args:
            api_key: API key (required if not in env)
            email: Email address (required if not in env)
            base_url: API base URL (default: https://api.agieth.ai)
        
        Raises:
            ValueError: If API key is not provided and not in environment
        """
        self.base_url = base_url or os.getenv("AGIETH_BASE_URL", "https://api.agieth.ai")
        self.api_key = api_key or os.getenv("AGIETH_API_KEY", "")
        self.email = email or os.getenv("AGIETH_EMAIL", "")
        
        # Validate API key is present
        if not self.api_key:
            raise ValueError(
                "AGIETH_API_KEY is required. "
                "Set environment variable or pass api_key parameter. "
                "Get your API key at https://api.agieth.ai/api/v1/keys/create"
            )
    
    def create_api_key(self) -> dict:
        """Create a new API key via the API.
        
        Returns:
            Dict with api_key and email
        """
        result = self._post("/api/v1/keys/create", {"email": self.email})
        return result
    
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
        params = {"token": token, "email": email}
        return self._get("/api/v1/keys/verify", params)
    
    # ========== Domains ==========
    
    def check_availability(self, domain: str, registrar: str = "namesilo") -> Dict:
        """Check domain availability.
        
        Args:
            domain: Domain name to check
            registrar: Registrar to use (namesilo, godaddy, namecheap)
            
        Returns:
            Dict with availability and pricing
        """
        params = {
            "domain": domain,
            "provider": registrar,
            "api_key": self.api_key,
        }
        return self._get("/domains/available", params)
    
    def list_domains(self, registrar: str = "namesilo") -> Dict:
        """List all domains in account.
        
        Args:
            registrar: Registrar (namesilo, godaddy)
            
        Returns:
            Dict with list of domains
        """
        params = {"provider": registrar, "api_key": self.api_key}
        return self._get("/domains", params)
    
    def get_domain_info(self, domain: str, registrar: str = "namesilo") -> Dict:
        """Get domain details.
        
        Args:
            domain: Domain name
            registrar: Registrar (namesilo, godaddy)
            
        Returns:
            Dict with domain details
        """
        params = {"provider": registrar, "api_key": self.api_key}
        return self._get(f"/domains/{domain}", params)
    
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
        
        params = {"authorization": self.api_key}
        return self._post("/api/v1/domains/quote", data=data, params=params)
    
    def get_quote(self, quote_id: str) -> Dict:
        """Get quote status.
        
        Args:
            quote_id: Quote ID
            
        Returns:
            Dict with quote status and payment details
        """
        params = {"api_key": self.api_key}
        return self._get(f"/api/v1/quotes/{quote_id}", params)
    
    def check_payment(self, quote_id: str) -> Dict:
        """Check payment status for a quote.
        
        Args:
            quote_id: Quote ID
            
        Returns:
            Dict with payment status
        """
        params = {"api_key": self.api_key}
        return self._get(f"/api/v1/quotes/{quote_id}/payment", params)
    
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
        params = {"api_key": self.api_key}
        return self._post_form(f"/api/v1/quotes/{quote_id}/confirm", data=data, params=params)
    
    def register_domain(self, quote_id: str) -> Dict:
        """Register a domain after payment is confirmed.
        
        Args:
            quote_id: Quote ID
            
        Returns:
            Dict with registration status
        """
        params = {"api_key": self.api_key}
        return self._post_form(f"/api/v1/quotes/{quote_id}/register", params=params)
    
    # ========== DNS Management ==========
    
    def list_dns_records(self, domain: str, registrar: str = "namecheap") -> Dict:
        """List DNS records for a domain.
        
        Args:
            domain: Domain name
            registrar: Registrar (namecheap, namesilo)
            
        Returns:
            Dict with list of DNS records
        """
        # Some endpoints require api_key as query param
        params = {"registrar": registrar, "api_key": self.api_key}
        return self._get(f"/api/v1/domains/{domain}/dns", params)
    
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
            "api_key": self.api_key,
        }
        if priority is not None:
            params["priority"] = priority
            
        return self._post(f"/api/v1/domains/{domain}/dns", params=params)
    
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
        params = {"registrar": registrar, "api_key": self.api_key}
        return self._delete(f"/api/v1/domains/{domain}/dns/{record_id}", params)
    
    # ========== Cloudflare ==========
    
    def create_cloudflare_zone(self, domain: str) -> Dict:
        """Create a Cloudflare zone for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dict with zone_id and nameservers
        """
        params = {"domain": domain, "api_key": self.api_key}
        return self._post("/api/v1/cloudflare/zones", params=params)
    
    def list_cloudflare_zones(self) -> Dict:
        """List all Cloudflare zones."""
        params = {"api_key": self.api_key}
        return self._get("/api/v1/cloudflare/zones", params)
    
    # ========== Cloudflare Tunnel Hosting ==========
    
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
                - instructions: Setup instructions
                
        Example:
            >>> result = client.create_tunnel("myapp.com", 3000)
            >>> print(result["tunnel_token"])
            >>> # Run: cloudflared tunnel run --token <tunnel_token>
        """
        data = {
            "domain": domain,
            "local_port": local_port,
        }
        params = {"api_key": self.api_key}
        return self._post("/api/v1/hosting/tunnel", data=data, params=params)
    
    def get_tunnel_token(self, domain: str) -> Dict:
        """Get tunnel token for an existing domain.
        
        If tunnel doesn't exist, creates one.
        
        Args:
            domain: Domain name
            
        Returns:
            Dict with tunnel_token and setup instructions
        """
        params = {"api_key": self.api_key}
        return self._get(f"/api/v1/hosting/tunnel/{domain}/token", params)
    
    def get_hosting_status(self, domain: str) -> Dict:
        """Get protected hosting status for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dict with hosting status and details
        """
        params = {"api_key": self.api_key}
        return self._get(f"/api/v1/hosting/status/{domain}", params)
    
    def cancel_hosting(self, domain: str) -> Dict:
        """Cancel protected hosting for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dict with cancellation status
        """
        params = {"api_key": self.api_key}
        return self._delete(f"/api/v1/hosting/{domain}", params)
    
    # ========== Balance & Credits ==========
    
    def get_balance(self) -> Dict:
        """Get account balance and credits."""
        params = {"authorization": self.api_key}
        return self._get("/api/v1/balance", params)
    
    def get_credits(self) -> Dict:
        """Get credit balance and history."""
        params = {"authorization": self.api_key}
        return self._get("/api/v1/credits", params)
    
    # ========== Cloudflare Page Rules ==========
    
    def list_page_rules(self, zone_id: str) -> Dict:
        """List all page rules for a Cloudflare zone.
        
        Args:
            zone_id: Cloudflare zone ID
            
        Returns:
            Dict with list of page rules
        """
        params = {"api_key": self.api_key}
        return self._get(f"/api/v1/cloudflare/zones/{zone_id}/pagerules", params)
    
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
        params = {
            "zone_id": zone_id,
            "target_url": target_url,
            "forward_url": forward_url,
            "status_code": status_code,
            "api_key": self.api_key,
        }
        return self._post(f"/api/v1/cloudflare/zones/{zone_id}/pagerules", params=params)
    
    def delete_page_rule(self, zone_id: str, rule_id: str) -> Dict:
        """Delete a page rule.
        
        Args:
            zone_id: Cloudflare zone ID
            rule_id: Page rule ID
            
        Returns:
            Dict with success status
        """
        params = {"api_key": self.api_key}
        return self._delete(f"/api/v1/cloudflare/zones/{zone_id}/pagerules/{rule_id}", params)
    
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
        return self._get("/api/v1/subscriptions/pricing", params)
    
    def list_subscriptions(self) -> Dict:
        """List all subscriptions for the authenticated customer.
        
        Returns:
            Dict with list of subscriptions
        """
        params = {"api_key": self.api_key}
        return self._get("/api/v1/subscriptions", params)
    
    def get_subscription(self, subscription_id: int) -> Dict:
        """Get subscription status and details.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Dict with subscription details
        """
        params = {"api_key": self.api_key}
        return self._get(f"/api/v1/subscriptions/{subscription_id}", params)
    
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
            "api_key": self.api_key,
        }
        if zone_id:
            params["zone_id"] = zone_id
        return self._post("/api/v1/subscriptions", params=params)
    
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
        
        # Connect to Ethereum
        w3 = Web3(Web3.HTTPProvider("https://ethereum.publicnode.com"))
        
        # Get private key
        if private_key is None:
            private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
            if not private_key:
                return {"success": False, "error": "No private key provided"}
        
        account = Account.from_key(private_key)
        
        # Build transaction
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price
        
        tx = {
            "from": account.address,
            "to": Web3.to_checksum_address(to_address),
            "value": w3.to_wei(amount_eth, "ether"),
            "gasPrice": gas_price,
            "nonce": nonce,
            "chainId": 1
        }
        
        # Dynamically estimate gas (more reliable than hardcoding)
        tx["gas"] = w3.eth.estimate_gas(tx)
        
        # Sign and send
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        return {
            "success": receipt.status == 1,
            "tx_hash": tx_hash.hex(),
            "from": account.address,
            "to": to_address,
            "amount_eth": amount_eth,
            "gas_used": receipt.gasUsed,
            "block_number": receipt.blockNumber
        }
    
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
        
        w3 = Web3(Web3.HTTPProvider("https://ethereum.publicnode.com"))
        
        if private_key is None:
            private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
            if not private_key:
                return {"success": False, "error": "No private key provided"}
        
        account = Account.from_key(private_key)
        
        # ERC20 transfer ABI
        erc20_abi = [
            {"constant": False, "inputs": [{"name": "_to", "type": "address"}, 
             {"name": "_value", "type": "uint256"}], "name": "transfer",
             "outputs": [{"name": "", "type": "bool"}], "type": "function"}
        ]
        
        token = w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=erc20_abi
        )
        
        # Convert amount to token units
        amount_wei = int(amount * (10 ** decimals))
        
        # Build transaction (without gas - will estimate)
        nonce = w3.eth.get_transaction_count(account.address)
        tx = {
            "from": account.address,
            "nonce": nonce,
            "gasPrice": w3.eth.gas_price,
            "chainId": 1
        }
        
        # Build the contract call
        contract_tx = token.functions.transfer(
            Web3.to_checksum_address(to_address),
            amount_wei
        ).build_transaction(tx)
        
        # Dynamically estimate gas (token transfers need ~50,000-65,000)
        contract_tx["gas"] = w3.eth.estimate_gas(contract_tx)
        
        signed = w3.eth.account.sign_transaction(contract_tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        return {
            "success": receipt.status == 1,
            "tx_hash": tx_hash.hex(),
            "from": account.address,
            "to": to_address,
            "amount": amount,
            "token": token_address
        }
    
    # ========== Manifest ==========
    
    def get_manifest(self) -> Dict:
        """Get API manifest for AI agents."""
        return self._get("/api/v1/manifest")
    
    def list_endpoints(self) -> Dict:
        """Get simple list of all endpoints."""
        return self._get("/api/v1/endpoints")


# Skill entry point
skill = AgiethClient


if __name__ == "__main__":
    # Test the skill
    client = AgiethClient()
    
    print("agieth.ai API Skill")
    print("=" * 50)
    
    # Test manifest
    manifest = client.get_manifest()
    print(f"Service: {manifest.get('service')}")
    print(f"Version: {manifest.get('version')}")
    
    # List endpoints
    endpoints = client.list_endpoints()
    print(f"\nEndpoints available: {len(endpoints.get('endpoints', []))}")
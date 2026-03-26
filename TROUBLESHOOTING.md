# Troubleshooting Guide

Common issues and solutions for one-shot-site users.

## Domain Registration Issues

### "Domain already taken"

**What it means:** Someone else registered the domain before you completed payment.

**Solution:**
1. The system automatically adds credit to your account
2. Try a different domain name
3. Use the credit for your next registration

### "Payment not detected"

**What it means:** The blockchain transaction hasn't been confirmed yet.

**Solutions:**
1. Wait 2-5 minutes for blockchain confirmations
2. Make sure you sent the correct amount (check the quote price)
3. Make sure you sent to the correct payment address

**If still not detected after 30 minutes:**
- Contact support@agieth.ai with your quote ID and transaction hash

### "Registration failed"

**What it means:** The registrar (Namecheap) couldn't complete the registration.

**Common causes:**
- Domain was taken by someone else
- Registrar account issue
- Contact information verification needed

**Solution:** Your payment is automatically converted to credit. Try another domain.

## DNS and Nameserver Issues

### "Domain not loading"

**Checklist:**

1. **Did you update nameservers?**
   - After registration, update your domain's nameservers at your registrar
   - Cloudflare nameservers look like: `chelsea.ns.cloudflare.com`
   - Wait 5-60 minutes for propagation

2. **Did you add DNS records?**
   - Add an A record pointing to your server IP
   - Example: `A @ 192.168.1.1`

3. **Is port 80/443 accessible?**
   - Your server needs ports 80 and 443 open
   - If behind a router, configure port forwarding

### "DNS propagation taking too long"

DNS propagation typically takes 5-60 minutes, sometimes up to 48 hours.

**Check propagation status:**
- https://dnschecker.org/#A/yourdomain.com

**Quick fixes:**
- Try from a different network (mobile data, different WiFi)
- Flush DNS cache: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)
- Use Google DNS (8.8.8.8) or Cloudflare DNS (1.1.1.1)

## Cloudflare Issues

### "Error 521: Web server is down"

**What it means:** Cloudflare can't reach your server.

**Checklist:**
1. Is your web server running? (`systemctl status caddy` or `systemctl status nginx`)
2. Are ports 80/443 open on your firewall?
3. Is your server IP correct in Cloudflare DNS?

### "Error 522: Connection timed out"

**Same as 521** - Cloudflare can't reach your server.

**Solutions:**
- Check if your server is online
- Verify port forwarding (if behind NAT/router)
- Check firewall rules

### "Error 523: Origin unreachable"

**What it means:** Your server is reachable but doesn't respond properly.

**Solutions:**
- Restart your web server
- Check web server logs for errors
- Verify your web server configuration

### "Error 524: Timeout"

**What it means:** Your server is too slow to respond.

**Solutions:**
- Optimize your application
- Increase server resources
- Check for slow database queries

## Contact Verification Issues

### "I didn't receive verification email"

**Check:**
1. Check spam/junk folder
2. Make sure you typed your email correctly
3. Add support@agieth.ai to your contacts

**Note:** Contact verification is required by ICANN. If you don't verify within 7-14 days, your domain may be suspended.

### "Contact verification link expired"

**Solution:** Request a new verification email from your registrar (Namecheap/NameSilo).

## Error Codes

| Code | Meaning | What to do |
|------|---------|------------|
| 400 | Bad request | Check your input parameters |
| 401 | Unauthorized | Check your API key |
| 404 | Not found | Domain or resource doesn't exist |
| 429 | Rate limited | Wait a few minutes before retrying |
| 500 | Server error | Try again, contact support if persists |

## Getting Help

### Contact Support

- **Email:** support@agieth.ai
- **Response time:** Usually within 24 hours

### Information to Include

When contacting support, please provide:
1. Your API key (starts with `agieth_`)
2. The error message you received
3. The domain you were trying to register
4. Your transaction hash (if payment-related)

### Status Page

Check system status at: https://status.agieth.ai

## Quick Diagnostic

Run this command to check your setup:

```bash
# Check if API is responding
curl https://api.agieth.ai/health

# Check domain availability
curl "https://api.agieth.ai/domains/available?domain=example.com"

# Check your balance
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.agieth.ai/api/v1/balance
```

If all commands return results, the API is working. If they fail, check your internet connection and try again.
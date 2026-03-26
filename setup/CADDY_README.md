# Single Shot Site

One-command static site deployment with Caddy + HTTPS.

## Files

```
single_shot_site/
├── www/
│   ├── index.html    # Template (uses style.css)
│   └── style.css     # External stylesheet
├── caddy_install.sh        # Run this to deploy
└── README.md
```

## Usage

```bash
sudo ./caddy_install.sh yourdomain.com
```

For HTTP-only (development):

```bash
sudo ./caddy_install.sh yourdomain.com --dev
```

## What It Does

1. Installs Caddy (if not installed)
2. Creates `/var/www/yourdomain.com/`
3. Copies `www/index.html` and `www/style.css`
4. Generates secure `Caddyfile` with:
   - HTTPS (auto-certificate via Let's Encrypt)
   - Security headers (X-Frame-Options, CSP, HSTS)
5. Starts Caddy systemd service

## Security Headers

| Header | Value |
|--------|-------|
| X-Frame-Options | DENY |
| X-Content-Type-Options | nosniff |
| X-XSS-Protection | 1; mode=block |
| Referrer-Policy | strict-origin-when-cross-origin |
| Content-Security-Policy | default-src 'self' |
| Strict-Transport-Security | max-age=31536000 |

## Customization

Edit files in `/var/www/yourdomain.com/`:

```bash
nano /var/www/yourdomain.com/index.html
nano /var/www/yourdomain.com/style.css
```

Reload after changes:

```bash
sudo systemctl reload caddy
```

## Template Variables

In `index.html`, replace:

- `{{DOMAIN}}` → Your domain name

## Requirements

- Linux (Debian/Ubuntu)
- Root access
- Ports 80 and 443 open
- DNS A record pointing to server

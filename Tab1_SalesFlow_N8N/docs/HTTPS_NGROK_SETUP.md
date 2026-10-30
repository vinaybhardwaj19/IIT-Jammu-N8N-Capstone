# HTTPS N8N deployment with ngrok

This project exposes local N8N webhooks through a public HTTPS URL while keeping N8N itself on `127.0.0.1`. ngrok terminates TLS and forwards requests to the local N8N editor.

## Start

From PowerShell:

```powershell
cd "C:\Users\HP\Downloads\IIT PROJECT 1\Tab1_SalesFlow_N8N"
.\start_n8n_ngrok.ps1
```

The launcher:

1. Starts an HTTPS ngrok tunnel to port 5678.
2. Reads the generated HTTPS URL from ngrok's local API.
3. Sets `WEBHOOK_URL` and `N8N_EDITOR_BASE_URL` to that HTTPS URL.
4. Starts N8N on `127.0.0.1:5678`.

The printed URL is the one to use for the N8N editor and webhook testing. The URL changes when the free ngrok tunnel restarts.

## First-time setup

Install and authenticate both tools before running the launcher:

```powershell
npm install -g n8n
ngrok config add-authtoken YOUR_NGROK_TOKEN
```

Do not commit the token, credentials, or `runtime-logs/` directory.

## Test an imported webhook

After importing and activating workflow 01, use the printed HTTPS URL:

```powershell
$body = @{
  full_name = 'Rahul Gupta'
  email = 'rahul@example.com'
  company = 'TechVision Solutions'
  industry = 'B2B SaaS'
  budget = '$3,500-$6,000/month'
  source = 'IIT Demo'
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri 'https://YOUR-NGROK-SUBDOMAIN.ngrok-free.app/webhook/capture-lead' `
  -ContentType 'application/json' -Body $body
```

Use the exact URL printed by the launcher; do not guess a subdomain.

## Operational safety

- Use synthetic demo leads during training.
- Keep external email credentials disabled until the approval workflow is verified.
- Treat the public URL as temporary and non-secret, but never expose API keys in webhook payloads.
- Stop the `n8n` and `ngrok` processes after the demo.

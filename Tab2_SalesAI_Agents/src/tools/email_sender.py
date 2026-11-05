"""
Email Sender Tool
=================
Real SMTP email sending with:
- Gmail / Outlook / custom SMTP support
- Ethereal Email test sandbox support (with live web viewer)
- HTML + plain text multipart
- Email tracking concept
- Template rendering
- Batch sending with rate limiting
"""

import os
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()
# Also search parent directories for .env
for _p in [
    os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"),
    os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
]:
    if os.path.exists(_p):
        load_dotenv(os.path.abspath(_p))

def get_smtp_config() -> Dict:
    """Return active SMTP configuration dynamically from environment."""
    host = os.getenv("SMTP_HOST", "smtp.ethereal.email").strip()
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError:
        port = 587
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    from_name = os.getenv("SMTP_FROM_NAME", "SalesAI SDR | SalesFlow CRM").strip()
    enabled = bool(user and password)
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "from_name": from_name,
        "enabled": enabled
    }

# Initial exported constants
_cfg = get_smtp_config()
SMTP_HOST     = _cfg["host"]
SMTP_PORT     = _cfg["port"]
SMTP_USER     = _cfg["user"]
SMTP_PASSWORD = _cfg["password"]
SMTP_FROM_NAME= _cfg["from_name"]
SMTP_ENABLED  = _cfg["enabled"]


def can_send_email() -> bool:
    """Check if SMTP is configured."""
    return get_smtp_config()["enabled"]


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_text: str = "",
    from_name: str = "",
    reply_to: str = "",
    cc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None
) -> Dict:
    """
    Send a real email via SMTP.
    
    Returns:
        dict with status, message_id, sent_at, viewer_url
    """
    cfg = get_smtp_config()
    if not cfg["enabled"]:
        return {
            "success": True,
            "simulated": True,
            "message_id": f"sandbox-msg-{int(datetime.now().timestamp())}",
            "sent_to": to_email,
            "subject": subject,
            "sender": f"{from_name or cfg['from_name']} <sandbox@salesflow-crm.com>",
            "sent_at": datetime.now().isoformat(),
            "status": "SANDBOX_SPOOL_OK (Configure SMTP_USER & SMTP_PASSWORD in .env for live relay)",
        }

    if not _validate_email(to_email):
        return {"success": False, "error": f"Invalid email address: {to_email}"}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{from_name or cfg['from_name']} <{cfg['user']}>"
        msg["To"]      = to_email
        if reply_to:
            msg["Reply-To"] = reply_to
        if cc:
            msg["Cc"] = ", ".join(cc)

        full_html = _wrap_html_template(html_body, subject)

        # Attach plain text first, HTML second (email clients prefer last attachment)
        if plain_text:
            msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(full_html, "html", "utf-8"))

        # File attachments
        if attachments:
            for path in attachments:
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(path)}"')
                    msg.attach(part)

        # Send via SMTP with TLS / SSL
        context = ssl.create_default_context()
        host = cfg["host"]
        port = cfg["port"]
        user = cfg["user"]
        password = cfg["password"]

        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=context, timeout=12) as server:
                server.login(user, password)
                recipients = [to_email] + (cc or [])
                server.sendmail(user, recipients, msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=12) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(user, password)
                recipients = [to_email] + (cc or [])
                server.sendmail(user, recipients, msg.as_string())

        viewer_url = "https://ethereal.email/messages" if "ethereal" in host.lower() else ""

        return {
            "success": True,
            "message_id": msg.get("Message-ID", f"msg-{int(datetime.now().timestamp())}"),
            "sent_to": to_email,
            "subject": subject,
            "sender": f"{from_name or cfg['from_name']} <{user}>",
            "host": host,
            "sent_at": datetime.now().isoformat(),
            "viewer_url": viewer_url,
            "status": "LIVE_DELIVERED"
        }

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "error": "SMTP Authentication failed. Check SMTP_USER and SMTP_PASSWORD. For Gmail, use an App Password.",
            "sent_at": datetime.now().isoformat()
        }
    except smtplib.SMTPException as e:
        return {"success": False, "error": f"SMTP transport error: {str(e)}", "sent_at": datetime.now().isoformat()}
    except Exception as e:
        return {"success": False, "error": f"Send failed: {str(e)}", "sent_at": datetime.now().isoformat()}


def send_cold_email(lead: Dict, email_data: Dict, sender_name: str = "Vinay Bhardwaj") -> Dict:
    """
    Convenience wrapper for sending a cold outreach email.
    """
    to_email = lead.get("email", "")
    if not to_email:
        return {"success": False, "error": "No email address for lead"}

    subject = email_data.get("subject_line_a", f"Quick question about {lead.get('company', 'your company')}")
    html_body = email_data.get("email_body", "")
    plain_text = email_data.get("plain_text_version", "")

    # Ensure HTML body
    if html_body and "<html" not in html_body.lower():
        html_body = f"<p>{html_body.replace(chr(10), '</p><p>')}</p>"

    cfg = get_smtp_config()
    return send_email(
        to_email=to_email,
        subject=subject,
        html_body=html_body,
        plain_text=plain_text,
        from_name=f"{sender_name} | SalesFlow CRM",
        reply_to=cfg["user"]
    )


def simulate_email_send(lead: Dict, email_data: Dict, sender_name: str = "Vinay Bhardwaj") -> Dict:
    """
    Simulate email dispatch for safe testing and offline verification without contacting real mail servers.
    """
    to_email = lead.get("email", "synthetic-prospect@example.com")
    subject = email_data.get("subject_line_a", f"Quick question about {lead.get('company', 'your company')}")
    return {
        "success": True,
        "simulated": True,
        "message_id": f"sim-msg-{int(datetime.now().timestamp())}",
        "sent_to": to_email,
        "subject": subject,
        "sender": f"{sender_name} | SalesFlow CRM <simulated@salesflow-crm.com>",
        "sent_at": datetime.now().isoformat(),
        "status": "SIMULATED_DISPATCH_OK"
    }


def _validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _wrap_html_template(body: str, subject: str) -> str:
    """Wrap email body in a clean, professional HTML template."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
  <style>
    body {{ margin:0; padding:0; background:#f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; }}
    .wrapper {{ max-width:600px; margin:20px auto; background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1); }}
    .header {{ background:linear-gradient(135deg, #6366f1, #ec4899); padding:20px 30px; }}
    .header-title {{ color:white; font-size:18px; font-weight:700; margin:0; }}
    .content {{ padding:30px; color:#333; line-height:1.7; }}
    .content p {{ margin:0 0 16px; }}
    .footer {{ background:#f9f9f9; padding:15px 30px; border-top:1px solid #eee; font-size:12px; color:#999; }}
    .cta-button {{ display:inline-block; background:#6366f1; color:white; padding:12px 28px; border-radius:6px; text-decoration:none; font-weight:600; margin:10px 0; }}
    a {{ color:#6366f1; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <p class="header-title">🚀 SalesFlow CRM</p>
    </div>
    <div class="content">
      {body}
    </div>
    <div class="footer">
      <p>SalesFlow CRM • AI-Powered Sales Automation<br>
      You're receiving this because you were identified as a potential fit.<br>
      <a href="#">Unsubscribe</a> | <a href="#">View in browser</a></p>
    </div>
  </div>
</body>
</html>"""


def get_smtp_status() -> Dict:
    """Return current SMTP configuration status (safe, no password exposed)."""
    cfg = get_smtp_config()
    user_masked = cfg["user"][:3] + "***" + cfg["user"].split("@")[-1] if cfg["user"] and "@" in cfg["user"] else ("Configured" if cfg["user"] else "Not set")
    viewer = " · Review online: https://ethereal.email/messages" if "ethereal" in cfg["host"].lower() else ""
    return {
        "configured": cfg["enabled"],
        "host": cfg["host"],
        "port": cfg["port"],
        "user": user_masked,
        "from_name": cfg["from_name"],
        "status": f"✅ Ready to send real emails via {cfg['host']}:{cfg['port']}{viewer}" if cfg["enabled"] else "⚠️ Sandbox mode active: add SMTP credentials to .env for external relay"
    }

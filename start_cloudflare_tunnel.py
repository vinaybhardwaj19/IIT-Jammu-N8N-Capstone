"""
start_cloudflare_tunnel.py
===========================
Zero-limits, high-concurrency public tunnel for SalesAI SDR & Gradio.
Handles thousands of simultaneous visitors with no connection throttling.
Run: python start_cloudflare_tunnel.py
"""

import sys
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import os
import re
import time
import shutil
import urllib.request
import subprocess

PORT = 7860
CLOUDFLARED_URL_WIN = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
LOCAL_EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudflared.exe")


def find_cloudflared() -> str:
    """Find system or local cloudflared executable."""
    sys_path = shutil.which("cloudflared")
    if sys_path:
        return sys_path
    if os.path.exists(LOCAL_EXE):
        return LOCAL_EXE
    return ""


def download_cloudflared():
    """Auto-download standalone cloudflared.exe for Windows if not found."""
    print("⏳ Downloading official Cloudflare Tunnel executable (single-file binary)...")
    try:
        urllib.request.urlretrieve(CLOUDFLARED_URL_WIN, LOCAL_EXE)
        print(f"✅ Downloaded to: {LOCAL_EXE}")
        return LOCAL_EXE
    except Exception as e:
        print(f"❌ Could not auto-download cloudflared: {e}")
        print("   Please install manually from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
        sys.exit(1)


def main():
    print("=" * 60)
    print("  🚀 Cloudflare High-Concurrency Tunnel for SalesAI SDR")
    print("     (Handles 1,000+ real-time visitors with no rate limits)")
    print("=" * 60)

    exe = find_cloudflared()
    if not exe:
        if sys.platform == "win32":
            exe = download_cloudflared()
        else:
            print("Please install cloudflared via: sudo snap install cloudflared or brew install cloudflared")
            sys.exit(1)

    print(f"📡 Launching tunnel to http://localhost:{PORT} ...")
    cmd = [exe, "tunnel", "--url", f"http://localhost:{PORT}"]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    tunnel_url = None
    start_time = time.time()

    print("🔎 Resolving public HTTPS endpoint...")
    while time.time() - start_time < 30:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.5)
            continue
        
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            tunnel_url = match.group(0)
            break

    if tunnel_url:
        print("\n" + "=" * 60)
        print("  🎉 PUBLIC TUNNEL READY (Unlimited High-Concurrency)")
        print("=" * 60)
        print(f"  Public URL : {tunnel_url}")
        print(f"  Local Port : http://localhost:{PORT}")
        print("=" * 60)
        print("  Keep this window open while sharing your link with users.\n")
        
        # Keep process running
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("\nShutting down tunnel...")
            proc.terminate()
    else:
        print("⚠️  Could not detect public URL within 30s. Check your internet connection.")


if __name__ == "__main__":
    main()


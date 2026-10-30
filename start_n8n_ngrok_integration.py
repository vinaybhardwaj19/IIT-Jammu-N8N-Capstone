"""
start_n8n_ngrok_integration.py
=================================
IIT Capstone - Start n8n (Docker) + ngrok tunnel, update .env.
Run: python start_n8n_ngrok_integration.py
"""
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import subprocess
import time
import json
import urllib.request
import urllib.error
import os
import sys
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(ROOT, ".env")
N8N_PORT = 5678
NGROK_API = "http://127.0.0.1:4040/api/tunnels"


# ─────────────────────────────────────────────
def check_n8n():
    try:
        urllib.request.urlopen(f"http://localhost:{N8N_PORT}/", timeout=3)
        return True
    except urllib.error.HTTPError:
        return True   # n8n returns redirect — still running
    except Exception:
        return False


def check_docker():
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def check_n8n_cli():
    try:
        r = subprocess.run(["n8n.cmd", "--version"], capture_output=True, text=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def start_n8n_native():
    print("[n8n-cli] Starting local n8n via n8n.cmd start...")
    CREATE_NO_WINDOW = 0x08000000
    subprocess.Popen(
        ["n8n.cmd", "start"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW,
    )
    for i in range(25):
        time.sleep(1)
        if check_n8n():
            return True
        print(f"[n8n-cli] ... booting ({i+1}/25s)")
    return check_n8n()


def start_n8n_docker():
    print("[docker] Starting n8n container via docker-compose...")
    r = subprocess.run(
        ["docker", "compose", "up", "-d", "n8n"],
        cwd=ROOT, capture_output=True, text=True
    )
    if r.returncode != 0:
        print("[docker] ERROR:", r.stderr[:300])
        return False
    print("[docker] n8n container started. Waiting 20s for boot...")
    for i in range(20):
        time.sleep(1)
        if check_n8n():
            return True
        print(f"[docker] ... {i+1}/20")
    return check_n8n()


def get_ngrok_url():
    try:
        r = urllib.request.urlopen(NGROK_API, timeout=3)
        data = json.loads(r.read())
        tunnels = data.get("tunnels", [])
        # prefer tunnel pointing at 5678
        for t in tunnels:
            addr = t.get("config", {}).get("addr", "")
            if t.get("proto") == "https" and str(N8N_PORT) in addr:
                return t["public_url"]
        # fallback: any https
        for t in tunnels:
            if t.get("proto") == "https":
                return t["public_url"]
    except Exception:
        pass
    return None


def start_ngrok():
    print(f"[ngrok] Opening HTTPS tunnel → localhost:{N8N_PORT} ...")
    CREATE_NO_WINDOW = 0x08000000
    subprocess.Popen(
        ["ngrok", "http", str(N8N_PORT), "--log=stdout"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW,
    )
    for _ in range(40):
        time.sleep(0.5)
        url = get_ngrok_url()
        if url:
            return url
    return None


def update_env(base_url):
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    new_line = f"N8N_WEBHOOK_URL={base_url}/webhook"
    if "N8N_WEBHOOK_URL=" in content:
        content = re.sub(r"N8N_WEBHOOK_URL=.*", new_line, content)
    else:
        content += f"\n{new_line}\n"
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[.env]  N8N_WEBHOOK_URL={base_url}/webhook  DONE")


# ─────────────────────────────────────────────
def main():
    print("=" * 58)
    print("  IIT Capstone — n8n + ngrok Integration")
    print("=" * 58)

    # ── Step 1: n8n ──────────────────────────────────────────
    if check_n8n():
        print(f"[n8n]   OK - Already running at http://localhost:{N8N_PORT}")
    else:
        print(f"[n8n]   Not running. Checking Docker / native CLI...")
        if check_docker():
            print("[docker] Docker daemon active. Starting container...")
            start_n8n_docker()
        elif check_n8n_cli():
            print("[n8n-cli] Docker Desktop is offline. Starting native n8n.cmd...")
            start_n8n_native()
        else:
            print("[n8n] ERROR: Neither Docker nor n8n CLI is available.")
            print("         -> Open Docker Desktop or run: npm install -g n8n")
            sys.exit(1)

        if check_n8n():
            print(f"[n8n]   OK - Running at http://localhost:{N8N_PORT}")
        else:
            print("[n8n]   WARNING: Could not confirm n8n is up yet.")

    # ── Step 2: ngrok ─────────────────────────────────────────
    existing = get_ngrok_url()
    if existing:
        print(f"[ngrok] OK - Tunnel already active: {existing}")
        ngrok_url = existing
    else:
        ngrok_url = start_ngrok()
        if not ngrok_url:
            print("[ngrok] FAILED. Check ngrok authtoken: ngrok config add-authtoken <token>")
            sys.exit(1)
        print(f"[ngrok] OK - Tunnel: {ngrok_url}")

    # ── Step 3: Update .env ───────────────────────────────────
    update_env(ngrok_url)

    # ── Step 4: Update n8n WEBHOOK_URL env ───────────────────
    if check_docker():
        print(f"[n8n]   Updating WEBHOOK_URL in Docker container...")
        subprocess.run(
            ["docker", "compose", "exec", "n8n",
             "sh", "-c", f"export WEBHOOK_URL={ngrok_url}/"],
            cwd=ROOT, capture_output=True
        )

    # ── Step 5: Print summary ─────────────────────────────────
    print()
    print("=" * 58)
    print("  >> ALL SYSTEMS GO <<")
    print("=" * 58)
    print(f"  n8n Editor   : http://localhost:{N8N_PORT}")
    print(f"  Public URL   : {ngrok_url}")
    print(f"  Webhook base : {ngrok_url}/webhook")
    print()
    print("  NEXT STEPS:")
    print(f"  1. Open n8n  →  http://localhost:{N8N_PORT}")
    print("  2. Import all 6 workflows:")
    print("       Tab1_SalesFlow_N8N/workflows/*.json")
    print("  3. In each Webhook node, the URL is:")
    print(f"       {ngrok_url}/webhook/<path>")
    print("  4. Toggle ON all 6 workflows")
    print("  5. Restart Gradio:")
    print("       python gradio_app.py")
    print("=" * 58)

    return ngrok_url


if __name__ == "__main__":
    main()

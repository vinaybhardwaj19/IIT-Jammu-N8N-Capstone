"""
SalesFlow AI & SalesAI SDR — Production Cloud Deployment Entry Point
=====================================================================
Optimized for Render / Hugging Face Spaces / Railway / Docker / PaaS
Course: IIT Jammu Summer School 2026 | Vinay Bhardwaj

Unifies:
1. Gradio 6.x Visual Multi-Tab Dashboard (Mounted at /)
2. FastAPI REST API & OpenAPI Documentation (Mounted at /docs and /redoc)
3. Live N8N Webhook Bridge (Mounted at /webhook/n8n)
4. Cloud Health Check Probe (Mounted at /health)
"""

import os
import sys
import uvicorn
import gradio as gr
from dotenv import load_dotenv

# Fix Windows console encoding if needed
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.abspath(__file__))
# Ensure .env is loaded
load_dotenv(os.path.join(ROOT, ".env"), override=False)

# Add module paths
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "Tab2_SalesAI_Agents"))
sys.path.insert(0, os.path.join(ROOT, "Tab2_SalesAI_Agents", "src"))

# Import API server and Gradio UI builder
from api_server import app as fastapi_app
from gradio_app import build_gradio_app

# Build Gradio Blocks demo
demo = build_gradio_app()

# Mount Gradio Dashboard onto FastAPI root application
# This exposes the UI at '/' and keeps all FastAPI endpoints (/docs, /health, /api/*, /webhook/*)
app = gr.mount_gradio_app(
    fastapi_app,
    demo,
    path="/",
    allowed_paths=[
        os.path.join(ROOT, "screenshots"),
        os.path.join(ROOT, "Tab1_SalesFlow_N8N"),
    ]
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("API_PORT", 7860)))
    
    # Check if user requested an instant public worldwide link
    if "--share" in sys.argv or os.environ.get("SHARE", "false").lower() == "true":
        print("=" * 70)
        print("🌍 Launching with instant public worldwide link (Gradio Tunnel)...")
        print("=" * 70)
        demo.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=True,
            allowed_paths=[os.path.join(ROOT, "screenshots")]
        )
    else:
        print("=" * 70)
        print("🚀 SalesFlow AI — Production Server Launching...")
        print(f"   🌐 Dashboard (Gradio UI) : http://0.0.0.0:{port}/")
        print(f"   📖 REST API Documentation: http://0.0.0.0:{port}/docs")
        print(f"   ⚡ Live N8N Webhook Relay: http://0.0.0.0:{port}/webhook/n8n")
        print(f"   💓 Cloud Health Check    : http://0.0.0.0:{port}/health")
        print("=" * 70)
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
        )

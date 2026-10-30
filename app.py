"""
SalesAI SDR — Cloud Deployment Entry Point
Hugging Face Spaces / Render / Railway / PaaS
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "Tab2_SalesAI_Agents"))
sys.path.insert(0, os.path.join(ROOT, "Tab2_SalesAI_Agents", "src"))

from gradio_app import build_gradio_app, THEME, CSS

demo = build_gradio_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        theme=THEME,
        css=CSS,
        share=False,
        show_error=True
    )

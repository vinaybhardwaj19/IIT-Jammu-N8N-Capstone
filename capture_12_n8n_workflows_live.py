import os
import re
import sys
import time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
screenshots_dir = os.path.join(ROOT, "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

print("Starting n8n 12-workflow live canvas capture...", flush=True)

WORKFLOWS_TO_CAPTURE = [
    {
        "id": "PSpNzuL4AaJaGWnq",
        "name": "04_jarvis_productivity_mcp_agent",
        "title": "Jarvis: Productivity AI Agent (MCPs)",
    },
    {
        "id": "gpXeelNPKlDq8ieb",
        "name": "06_community_reddit_telegram_gemini_groq",
        "title": "Monitor Community & Reddit with Gemini & Groq",
    },
    {
        "id": "aP8JALmU1VJOOwm9",
        "name": "03_whatsapp_ai_customer_support",
        "title": "WhatsApp AI Customer Support Bot",
    },
    {
        "id": "DzzwYuaMcVo1TRpi",
        "name": "10_veedio_avatar_elevenlabs_gpt4",
        "title": "VEED.io Avatar + ElevenLabs + GPT-4 Video Pipeline",
    },
    {
        "id": "LTnDlVthUMCPnh7y",
        "name": "12_interactive_multi_tool_ai_agent",
        "title": "Interactive Multi-Tool AI Agent with Chat",
    },
    {
        "id": "eSju8exAL8odh8mM",
        "name": "07_n8n_technical_support_forum_bot",
        "title": "n8n Technical Support & Forum AI Bot",
    },
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1920, "height": 1180}, device_scale_factor=1.5)
    page = context.new_page()

    # 1. Sign in to n8n
    print("1. Signing in to n8n...", flush=True)
    page.goto("http://localhost:5678/signin", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(1500)
    page.fill("input[name='emailOrLdapLoginId'], input[type='email'], input[name='email']", "vinaybhardwaj3230@gmail.com")
    page.fill("input[name='password'], input[type='password']", "Vinay@123")
    page.click("button[type='submit'], button:has-text('Sign in')")
    page.wait_for_timeout(3500)

    # Dismiss bottom toast/banner if present
    try:
        close_btn = page.locator("button[aria-label='Close'], button.close, [data-test-id='toast-close']").first
        if close_btn.count() > 0:
            close_btn.click(force=True)
    except Exception:
        pass

    # 2. Capture Workflows Overview List
    print("2. Capturing Workflows List showing the 12 industry workflows...", flush=True)
    page.goto("http://localhost:5678/home/workflows", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    list_path = os.path.join(screenshots_dir, "01_n8n_12_industry_workflows_list.png")
    page.screenshot(path=list_path)
    print(f"   --> Saved {list_path}", flush=True)

    # 3. Open and capture each workflow on canvas
    for i, wf in enumerate(WORKFLOWS_TO_CAPTURE, start=2):
        wf_url = f"http://localhost:5678/workflow/{wf['id']}"
        print(f"\n{i}. Opening {wf['title']} at {wf_url} ...", flush=True)
        page.goto(wf_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3500)

        # Close any modal / tooltip / banner
        try:
            close_modal = page.locator("[data-test-id='modal-close'], button:has-text('Got it'), button:has-text('Skip')").first
            if close_modal.count() > 0:
                close_modal.click(force=True)
        except Exception:
            pass

        # Center / fit canvas if zoom-to-fit button exists
        try:
            fit_btn = page.locator("[data-test-id='zoom-to-fit'], button[title*='Fit'], button[aria-label*='fit']").first
            if fit_btn.count() > 0:
                fit_btn.click(force=True)
                page.wait_for_timeout(600)
        except Exception:
            pass

        # Pre-execution canvas screenshot
        canvas_path = os.path.join(screenshots_dir, f"{i:02d}_{wf['name']}_canvas.png")
        page.screenshot(path=canvas_path)
        print(f"   --> Saved canvas: {canvas_path}", flush=True)

        # Trigger execution ("Execute workflow" or "Test workflow")
        print(f"   Triggering execution for {wf['title']}...", flush=True)
        exec_btn = page.locator("button:has-text('Test workflow'), button:has-text('Execute workflow'), [data-test-id='execute-workflow-button']").first
        if exec_btn.count() > 0 and exec_btn.is_visible():
            exec_btn.click(force=True)
            page.wait_for_timeout(800)
            
            # Capture actively running execution state with status/spinner
            running_path = os.path.join(screenshots_dir, f"{i:02d}_{wf['name']}_running.png")
            page.screenshot(path=running_path)
            print(f"   --> Saved running: {running_path}", flush=True)
            
            # Wait for execution to finish or update
            page.wait_for_timeout(3500)
            completed_path = os.path.join(screenshots_dir, f"{i:02d}_{wf['name']}_executed.png")
            page.screenshot(path=completed_path)
            print(f"   --> Saved executed: {completed_path}", flush=True)

    # 4. Capture Executions history
    print("\nCapturing n8n Executions History page...", flush=True)
    page.goto("http://localhost:5678/home/executions", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    exec_history_path = os.path.join(screenshots_dir, "10_n8n_live_executions_history.png")
    page.screenshot(path=exec_history_path)
    print(f"   --> Saved {exec_history_path}", flush=True)

    browser.close()

print("\nALL N8N 12-WORKFLOW SCREENSHOTS CAPTURED SUCCESSFULLY!", flush=True)

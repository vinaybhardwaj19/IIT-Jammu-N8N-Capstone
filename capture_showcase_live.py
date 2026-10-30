import os
import sys
import time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
screenshots_dir = os.path.join(ROOT, "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

print("Starting showcase live simulation capture...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1600, "height": 1200}, device_scale_factor=2)
    
    showcase_path = os.path.join(ROOT, "SHOWCASE.html")
    page.goto(f"file:///{showcase_path.replace(os.sep, '/')}", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Scroll to live demo section
    live_sec = page.locator("#live")
    live_sec.scroll_into_view_if_needed()
    page.wait_for_timeout(1000)

    run_btn = page.locator("#runBtn")
    print("Found runBtn:", run_btn.count(), flush=True)

    # 1. Click to trigger swarm execution
    run_btn.click()
    page.wait_for_timeout(1200)

    # Capture Running State (Step 1 or 2 active running with spinner)
    running_path = os.path.join(screenshots_dir, "06_showcase_workflow_running.png")
    page.screenshot(path=running_path)
    print(f"Saved {running_path}", flush=True)

    # Wait for all 4-5 steps to complete (~8-9 seconds total delay)
    page.wait_for_timeout(8000)
    completed_path = os.path.join(screenshots_dir, "07_showcase_workflow_completed.png")
    page.screenshot(path=completed_path)
    print(f"Saved {completed_path}", flush=True)

    # Also capture Gradio live runner with scrolled view showing full JSON output
    print("Capturing full n8n execution response view...", flush=True)
    page.goto("http://127.0.0.1:7860", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    
    tab = page.get_by_role("tab", name="Live Workflow Runner")
    if tab.count() > 0:
        tab.click()
    page.wait_for_timeout(1000)
    
    # Fill details
    page.get_by_placeholder("Priya Sharma").fill("Priya Sharma")
    page.get_by_placeholder("TechVision Solutions").fill("TechVision Solutions")
    page.get_by_placeholder("priya.sharma@techvision.io").fill("priya.sharma@techvision.io")
    page.get_by_placeholder("VP of Sales").fill("VP of Sales")
    page.get_by_placeholder("Series A $8M. 25 sales reps. Manual lead tracking.").fill("Series A $8M. Automated lead qualification pipeline.")
    
    send_btn = page.get_by_role("button", name="Send to active n8n")
    send_btn.click(force=True)
    
    # Wait for response
    page.wait_for_selector("text=Live n8n Execution", timeout=20000)
    page.wait_for_timeout(1500)

    # Scroll down to center the live response
    page.evaluate("window.scrollBy(0, 450)")
    page.wait_for_timeout(800)
    
    exec_detailed_path = os.path.join(screenshots_dir, "08_n8n_execution_detail_200.png")
    page.screenshot(path=exec_detailed_path)
    print(f"Saved {exec_detailed_path}", flush=True)

    browser.close()

print("ALL CAPTURES SUCCESSFULLY FINISHED!", flush=True)

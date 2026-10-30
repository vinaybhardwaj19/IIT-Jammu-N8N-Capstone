import os
import re
import sys
import time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
screenshots_dir = os.path.join(ROOT, "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

print("Starting comprehensive workflow running capture...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1600, "height": 1400}, device_scale_factor=1.5)
    
    # ─────────────────────────────────────────────────────────────
    # PART 1: Live n8n Workflow Runner (Webhook + ngrok + n8n)
    # ─────────────────────────────────────────────────────────────
    print("1. Loading Gradio Dashboard at http://127.0.0.1:7860 ...", flush=True)
    page.goto("http://127.0.0.1:7860", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2500)

    print("2. Opening Tab 1 -> 'Live Workflow Runner'...", flush=True)
    tab = page.get_by_role("tab", name=re.compile("Live Workflow Runner"))
    if tab.count() > 0:
        tab.click()
    page.wait_for_timeout(1000)

    # Populate lead details
    print("3. Populating lead details...", flush=True)
    page.get_by_placeholder("Priya Sharma").fill("Priya Sharma")
    page.get_by_placeholder("TechVision Solutions").fill("TechVision Solutions")
    page.get_by_placeholder("priya.sharma@techvision.io").fill("priya.sharma@techvision.io")
    page.get_by_placeholder("VP of Sales").fill("VP of Sales")
    page.get_by_placeholder("Series A $8M. 25 sales reps. Manual lead tracking.").fill("Series A $8M. Seeking automated qualification and fast outbound sales response.")
    page.wait_for_timeout(600)

    p1_ready = os.path.join(screenshots_dir, "01_n8n_workflow_ready.png")
    page.screenshot(path=p1_ready)
    print(f"   --> Saved {p1_ready}", flush=True)

    print("4. Triggering 'Send to active n8n' button...", flush=True)
    send_btn = page.get_by_role("button", name=re.compile("Send to active n8n"))
    send_btn.click(force=True)

    # Capture Running State (loading indicator active)
    page.wait_for_timeout(300)
    p2_running = os.path.join(screenshots_dir, "02_n8n_workflow_running.png")
    page.screenshot(path=p2_running)
    print(f"   --> Saved {p2_running}", flush=True)

    print("5. Waiting for live HTTP 200 response from n8n...", flush=True)
    try:
        page.wait_for_selector("text=Live n8n Execution", timeout=25000)
        page.wait_for_timeout(1500)
    except Exception as e:
        print(f"   Notice while waiting for n8n: {e}", flush=True)
        page.wait_for_timeout(3000)

    p3_success = os.path.join(screenshots_dir, "03_n8n_workflow_executed_200.png")
    page.screenshot(path=p3_success)
    print(f"   --> Saved {p3_success}", flush=True)

    # ─────────────────────────────────────────────────────────────
    # PART 2: Full Multi-Agent SDR Pipeline Running
    # ─────────────────────────────────────────────────────────────
    print("6. Navigating to Tab 2: AI Agents -> 'Full Pipeline'...", flush=True)
    tab2 = page.get_by_role("tab", name=re.compile("Tab 2: AI Agents"))
    if tab2.count() > 0:
        tab2.click()
        page.wait_for_timeout(1500)

        pipeline_tab = page.get_by_role("tab", name=re.compile("Full Pipeline"))
        if pipeline_tab.count() > 0:
            pipeline_tab.click()
            page.wait_for_timeout(1000)

            # Fill lead details for pipeline
            page.get_by_placeholder("Enter a real contact").fill("Elena Vance")
            page.get_by_placeholder("Company name").fill("Nexus Logistics")
            page.get_by_placeholder("name@company.com").fill("elena@nexuslogistics.com")
            page.get_by_placeholder("Sales Director").fill("VP Operations")
            page.get_by_placeholder("company.com", exact=True).fill("nexuslogistics.com")
            page.get_by_placeholder("Add only verified context for personalization").fill("Series B expansion. Looking to integrate automated lead routing.")
            page.wait_for_timeout(600)

            run_pipeline_btn = page.get_by_role("button", name=re.compile("Run SDR Pipeline"))
            if run_pipeline_btn.count() > 0:
                print("7. Triggering SDR Multi-Agent Pipeline...", flush=True)
                run_pipeline_btn.click(force=True)
                
                # Capture agent swarm running state
                page.wait_for_timeout(800)
                p4_running = os.path.join(screenshots_dir, "04_ai_pipeline_running.png")
                page.screenshot(path=p4_running)
                print(f"   --> Saved {p4_running}", flush=True)

                print("8. Waiting for SDR Multi-Agent execution to complete...", flush=True)
                try:
                    page.wait_for_selector("text=All requested AI/CRM steps returned successfully", timeout=30000)
                    page.wait_for_timeout(1500)
                except Exception as e:
                    print(f"   Pipeline wait notice: {e}", flush=True)
                    page.wait_for_timeout(5000)

                p5_success = os.path.join(screenshots_dir, "05_ai_pipeline_completed.png")
                page.screenshot(path=p5_success)
                print(f"   --> Saved {p5_success}", flush=True)

    # ─────────────────────────────────────────────────────────────
    # PART 3: SHOWCASE.html Interactive Live Multi-Agent Simulation
    # ─────────────────────────────────────────────────────────────
    showcase_path = os.path.join(ROOT, "SHOWCASE.html")
    if os.path.exists(showcase_path):
        print("9. Loading SHOWCASE.html for interactive workflow execution view...", flush=True)
        page.goto(f"file:///{showcase_path.replace(os.sep, '/')}", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        
        live_sec = page.locator("#live")
        if live_sec.count() > 0:
            live_sec.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            
            start_sim_btn = page.locator("#start-sim-btn, button:has-text('Run Multi-Agent Simulation'), button:has-text('Simulate')").first
            if start_sim_btn.count() > 0:
                print("10. Triggering SHOWCASE live simulation...", flush=True)
                start_sim_btn.click(force=True)
                page.wait_for_timeout(600)
                p6_running = os.path.join(screenshots_dir, "06_showcase_workflow_running.png")
                page.screenshot(path=p6_running)
                print(f"   --> Saved {p6_running}", flush=True)
                page.wait_for_timeout(4000)
                p7_success = os.path.join(screenshots_dir, "07_showcase_workflow_completed.png")
                page.screenshot(path=p7_success)
                print(f"   --> Saved {p7_success}", flush=True)

    browser.close()

print("ALL CAPTURES COMPLETED!", flush=True)

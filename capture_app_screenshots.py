"""
Automated Screenshot Capture Script for IIT Jammu Capstone Project
Captures high-resolution, crystal-clear screenshots from:
1. Gradio App (http://127.0.0.1:7860) - Tab 1 & Tab 2
2. SHOWCASE.html - Hero, Architecture, Workflows, Agents, ROI & Live Swarm
"""

import os
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def run_captures():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1600, "height": 950},
            device_scale_factor=2 # Crisp 2x retina images for slides
        )
        page = context.new_page()

        # ---------------------------------------------------------
        # PART 1: SHOWCASE.HTML SCREENSHOTS (Ultra-premium UI)
        # ---------------------------------------------------------
        showcase_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "SHOWCASE.html"))
        if os.path.exists(showcase_path):
            print("Loading SHOWCASE.html...")
            page.goto(f"file:///{showcase_path.replace(os.sep, '/')}", wait_until="networkidle")
            page.wait_for_timeout(2000)

            print("Capturing 01_showcase_hero.png...")
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "01_showcase_hero.png"))

            # Tab 1: N8N Section
            n8n_sec = page.locator("#n8n")
            if n8n_sec.count() > 0:
                n8n_sec.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                print("Capturing 02_showcase_n8n_workflows.png...")
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "02_showcase_n8n_workflows.png"))

            # Tab 2: Agents Section
            agents_sec = page.locator("#agents")
            if agents_sec.count() > 0:
                agents_sec.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                print("Capturing 03_showcase_agents_grid.png...")
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "03_showcase_agents_grid.png"))

            # Live Demo / Swarm Runner section
            live_sec = page.locator("#live")
            if live_sec.count() > 0:
                live_sec.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                print("Capturing 04_showcase_live_demo.png...")
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "04_showcase_live_demo.png"))

            # Impact / ROI table
            impact_sec = page.locator("#impact")
            if impact_sec.count() > 0:
                impact_sec.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                print("Capturing 05_showcase_roi_impact.png...")
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "05_showcase_roi_impact.png"))

        # ---------------------------------------------------------
        # PART 2: GRADIO APP (Tab 1 & Tab 2 Live Execution)
        # ---------------------------------------------------------
        print("\nLoading Gradio App at http://127.0.0.1:7860...")
        try:
            page.goto("http://127.0.0.1:7860", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            # Tab 1 Workflow Gallery
            print("Capturing 06_gradio_tab1_gallery.png...")
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "06_gradio_tab1_gallery.png"))

            # Switch to Tab 1 Project Overview
            try:
                overview_tab = page.locator("button:has-text('Project Overview')").first
                if overview_tab.count() > 0:
                    overview_tab.click()
                    page.wait_for_timeout(1500)
                    print("Capturing 07_gradio_tab1_overview.png...")
                    page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "07_gradio_tab1_overview.png"))
            except Exception as e:
                print("Error opening Tab 1 Overview:", e)

            # Switch to Tab 2: AI Agents
            print("Switching to Tab 2: AI Agents...")
            tab2_btn = page.locator("button:has-text('Tab 2: AI Agents')").first
            if tab2_btn.count() > 0:
                tab2_btn.click()
                page.wait_for_timeout(2000)

                # Tab 2.1 Dashboard
                print("Capturing 08_gradio_tab2_dashboard.png...")
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "08_gradio_tab2_dashboard.png"))

                # Tab 2.2 Research Agent
                try:
                    res_btn = page.locator("button:has-text('Research Agent')").first
                    if res_btn.count() > 0:
                        res_btn.click()
                        page.wait_for_timeout(1500)
                        print("Capturing 09_gradio_tab2_research.png...")
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "09_gradio_tab2_research.png"))
                except Exception as e:
                    print("Error opening Research Agent:", e)

                # Tab 2.3 Qualification Agent
                try:
                    qual_btn = page.locator("button:has-text('Qualification Agent')").first
                    if qual_btn.count() > 0:
                        qual_btn.click()
                        page.wait_for_timeout(1500)
                        print("Capturing 10_gradio_tab2_qualification.png...")
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "10_gradio_tab2_qualification.png"))
                except Exception as e:
                    print("Error opening Qualification Agent:", e)

                # Tab 2.4 Email Writer
                try:
                    email_btn = page.locator("button:has-text('Email Writer')").first
                    if email_btn.count() > 0:
                        email_btn.click()
                        page.wait_for_timeout(1500)
                        print("Capturing 11_gradio_tab2_email_writer.png...")
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "11_gradio_tab2_email_writer.png"))
                except Exception as e:
                    print("Error opening Email Writer:", e)

                # Tab 2.5 Meeting Coordinator
                try:
                    meet_btn = page.locator("button:has-text('Meeting Coordinator')").first
                    if meet_btn.count() > 0:
                        meet_btn.click()
                        page.wait_for_timeout(1500)
                        print("Capturing 12_gradio_tab2_meeting_coord.png...")
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "12_gradio_tab2_meeting_coord.png"))
                except Exception as e:
                    print("Error opening Meeting Coordinator:", e)

                # Tab 2.6 Objection Coach
                try:
                    obj_btn = page.locator("button:has-text('Objection')").first
                    if obj_btn.count() > 0:
                        obj_btn.click()
                        page.wait_for_timeout(1500)
                        print("Capturing 13_gradio_tab2_objection_coach.png...")
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "13_gradio_tab2_objection_coach.png"))
                except Exception as e:
                    print("Error opening Objection Coach:", e)

                # Tab 2.7 CRM Database
                try:
                    crm_btn = page.locator("button:has-text('CRM')").first
                    if crm_btn.count() > 0:
                        crm_btn.click()
                        page.wait_for_timeout(1500)
                        print("Capturing 14_gradio_tab2_crm_database.png...")
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "14_gradio_tab2_crm_database.png"))
                except Exception as e:
                    print("Error opening CRM Database:", e)

        except Exception as e:
            print("Gradio app error:", e)

        browser.close()
        print("\nAll presentation screenshots have been successfully generated and saved to 'screenshots/'!")

if __name__ == "__main__":
    run_captures()

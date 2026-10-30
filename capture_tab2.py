import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1600, "height": 950}, device_scale_factor=2)
    page.goto("http://127.0.0.1:7860", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # Force click Tab 2
    tab2 = page.locator("button:has-text('Tab 2: AI Agents')").first
    tab2.click(force=True)
    page.wait_for_timeout(2000)
    page.screenshot(path=os.path.join(screenshots_dir, "08_gradio_tab2_dashboard.png"))
    print("Tab 2 dashboard captured successfully!")

    # Email Writer subtab
    try:
        email_btn = page.locator("button:has-text('Email Writer')").first
        if email_btn.count() > 0:
            email_btn.click(force=True)
            page.wait_for_timeout(1000)
            page.screenshot(path=os.path.join(screenshots_dir, "09_gradio_tab2_email.png"))
            print("Tab 2 email writer captured successfully!")
    except Exception as e:
        print("Email writer error:", e)

    # Qualification Agent subtab
    try:
        qual_btn = page.locator("button:has-text('Qualification Agent')").first
        if qual_btn.count() > 0:
            qual_btn.click(force=True)
            page.wait_for_timeout(1000)
            page.screenshot(path=os.path.join(screenshots_dir, "10_gradio_tab2_qualification.png"))
            print("Tab 2 qualification captured successfully!")
    except Exception as e:
        print("Qualification error:", e)

    # Objection subtab
    try:
        obj_btn = page.locator("button:has-text('Objection')").first
        if obj_btn.count() > 0:
            obj_btn.click(force=True)
            page.wait_for_timeout(1000)
            page.screenshot(path=os.path.join(screenshots_dir, "11_gradio_tab2_objection.png"))
            print("Tab 2 objection captured successfully!")
    except Exception as e:
        print("Objection error:", e)

    browser.close()
    print("Done capturing Tab 2!")

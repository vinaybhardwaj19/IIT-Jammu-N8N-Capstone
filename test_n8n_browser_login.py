import os
import sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
screenshots_dir = os.path.join(ROOT, "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

print("Starting n8n browser login test...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1600, "height": 1100}, device_scale_factor=1.5)
    page = context.new_page()

    print("Navigating to http://localhost:5678/signin ...", flush=True)
    page.goto("http://localhost:5678/signin", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2000)

    # Fill signin form
    page.fill("input[name='emailOrLdapLoginId'], input[type='email'], input[name='email']", "vinaybhardwaj3230@gmail.com")
    page.fill("input[name='password'], input[type='password']", "Vinay@123")
    page.wait_for_timeout(500)

    # Click Sign In button
    page.click("button[type='submit'], button:has-text('Sign in')")
    print("Clicked Sign in, waiting for navigation...", flush=True)
    page.wait_for_timeout(4000)

    # Screenshot after login
    after_login = os.path.join(screenshots_dir, "n8n_after_login.png")
    page.screenshot(path=after_login)
    print(f"Current URL: {page.url}")
    print(f"Saved: {after_login}")

    browser.close()

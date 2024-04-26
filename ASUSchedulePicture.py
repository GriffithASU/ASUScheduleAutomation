import re
import time
import os
from playwright.sync_api import Playwright, sync_playwright, expect

def login(page):
    username = os.getenv("ASU_USERNAME")
    password = os.getenv("ASU_PASSWORD")

    page.goto("https://weblogin.asu.edu/cas/login?service=https%3A%2F%2Fcanvas.asu.edu%2Flogin%2Fcas")
    page.locator("#username").click()
    page.locator("#username").fill(username)
    page.locator("#password").click()
    page.locator("#password").fill(password)
    page.get_by_role("button", name="Sign In").click()

    # can't use state load since the phone options take a little bit to appear, could use time.sleep but that felt wrong
    page.wait_for_load_state('networkidle')
    page.frame_locator("#duo_iframe").get_by_label("Device").select_option("phone2")
    page.frame_locator("#duo_iframe").get_by_role("button", name="Call Me").click()
    try:
        with page.expect_navigation(timeout=30000):
            pass
        return True

    except Exception as e:
        print("Failed to login within 30 seconds. Restarting.")
        return False

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    success = False
    while not success:
        success = login(page)

    #page.goto("https://canvas.asu.edu/")
    page.get_by_role("link", name="Calendar", exact=True).click()

    page.wait_for_load_state('networkidle')
    page.evaluate("window.scrollBy(0,100)")

    # Now we are ready to take the picture, setup the filepath, then snap
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') if os.name == 'nt' else os.path.join(os.path.expanduser('~'), 'Desktop')
    screenshot_path = os.path.join(desktop_path, 'schedule.png')

    page.screenshot(path=screenshot_path)
    
    # Now we can exit
    context.close()
    browser.close()

    # Open the picture when we are done
    os.startfile(screenshot_path)

with sync_playwright() as playwright:
    run(playwright)
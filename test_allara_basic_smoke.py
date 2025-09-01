# allara_basic_smoke.py
# ONE-FILE SMOKE TEST: opens Allara, checks title, clicks a few nav links,
# tries Contact submit with blanks (expects an error message).
# Works with Selenium + webdriver-manager already installed.

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

BASE_URL = "https://allarahealth.com"

# If your top menu uses different words, change them here:
MENU_LINKS = ["About", "Services", "Contact"]  # adjust if needed (e.g., "Our Services", "Contact Us")

def start_browser():
    opts = Options()
    # Comment out the line below if you want to SEE the browser:
    # opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_window_size(1366, 768)
    return driver

def open_homepage(driver):
    driver.get(BASE_URL)
    time.sleep(2)
    print("Opened:", BASE_URL)
    print("Page title:", driver.title)
    # Basic sanity check — page should have a non-empty title
    if not driver.title:
        raise AssertionError("Homepage title is empty.")

def click_nav_links(driver):
    print("\n--- Navigation check ---")
    for label in MENU_LINKS:
        try:
            # Try exact link text first
            driver.find_element(By.LINK_TEXT, label).click()
        except NoSuchElementException:
            # Try partial match if exact not found
            try:
                driver.find_element(By.PARTIAL_LINK_TEXT, label[:4]).click()
            except NoSuchElementException:
                print(f"  SKIP: Could not find a link labeled '{label}'. Edit MENU_LINKS if wording is different.")
                continue

        time.sleep(2)
        url = driver.current_url.lower()
        print(f"  Clicked '{label}' → now at:", url)

        # Go back to homepage for the next link
        driver.back()
        time.sleep(2)

def contact_required_error(driver):
    print("\n--- Contact required-fields check ---")
    # If Contact is a separate page via header link, try to click it:
    clicked_contact = False
    for label in ["Contact", "Contact Us", "Support"]:
        try:
            driver.find_element(By.LINK_TEXT, label).click()
            clicked_contact = True
            break
        except NoSuchElementException:
            continue

    if not clicked_contact:
        print("  SKIP: Couldn’t find a Contact link in the header. If Contact is on the homepage, that’s OK.")
        # continue on the current page

    time.sleep(2)

    # Try to press a submit button with common selectors
    SUBMIT_SEL = "button[type='submit'], button[data-testid='contact-submit']"
    try:
        driver.find_element(By.CSS_SELECTOR, SUBMIT_SEL).click()
        time.sleep(2)
        page = (driver.page_source or "").lower()
        if ("required" in page) or ("error" in page) or ("invalid" in page):
            print("  PASS: Contact form shows required/invalid error messages when submitted empty.")
        else:
            print("  CHECK: No clear error text found. The form may not validate on empty.")
    except NoSuchElementException:
        print("  SKIP: Couldn’t find a submit button for the contact form (selector may differ).")

def main():
    driver = start_browser()
    try:
        open_homepage(driver)
        click_nav_links(driver)
        contact_required_error(driver)
        print("\n✅ Basic smoke finished.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
def test_homepage_title_loads():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(BASE_URL)  # e.g., "https://allarahealth.com"
    # Pass if page opened and has any title text
    assert driver.title.strip() != ""

    driver.quit()


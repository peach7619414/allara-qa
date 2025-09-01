# allara_login_otp_assert.py
# Purpose: Verify a REAL login works (email or phone OTP) and assert we land on a logged-in page.
# - Prompts you to choose Email or Phone login
# - Clicks "Log in with email" or "Log in with mobile number"
# - Enters your identifier
# - Prompts you to paste the OTP from email/SMS
# - Asserts you're logged in (URL or page content)
# - Saves a screenshot: login_result.png
#
# If anything goes wrong, the test raises AssertionError and exits with a non-zero code
# so you can plug this into a CI pipeline later.

import sys, time
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ---------- Config ----------
BASE_LOGIN_URL = "https://app.allarahealth.com/login"  # go straight to the login experience
EMAIL_ADDRESS = "sunnynelson402@gmail.com"
PHONE_NUMBER  = "646-266-1712"

# Heuristics to confirm login worked:
EXPECTED_URL_KEYWORDS = ["dashboard", "account", "profile", "appointments", "portal"]
EXPECTED_PAGE_KEYWORDS = ["log out", "logout", "my account", "profile", "appointments"]

# ---------- Helpers ----------
def start_browser(show_window=True):
    opts = Options()
    if not show_window:
        opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def click_text(driver, text, timeout=10):
    """Click a button/link by its visible text (case-insensitive contains)."""
    xp = f"//*[self::button or self::a or @role='button'][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xp)))
    el.click()

def type_into(driver, by, sel, value, timeout=10, clear_first=True):
    el = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, sel)))
    if clear_first:
        try:
            el.clear()
        except Exception:
            pass
    el.send_keys(value)
    return el

def wait(seconds=1.5):
    time.sleep(seconds)

# ---------- Steps ----------
def open_login_choice(driver, method):
    driver.get(BASE_LOGIN_URL)
    wait(2)
    if method == "email":
        click_text(driver, "log in with email")
    else:
        click_text(driver, "log in with mobile number")
    wait(1.5)

def enter_identifier_and_request_code(driver, method):
    if method == "email":
        # Common email input patterns
        try:
            type_into(driver, By.CSS_SELECTOR, "input[type='email']", EMAIL_ADDRESS)
        except TimeoutException:
            type_into(driver, By.CSS_SELECTOR, "input[name='email']", EMAIL_ADDRESS)
    else:
        # Common phone input patterns
        try:
            type_into(driver, By.CSS_SELECTOR, "input[type='tel']", PHONE_NUMBER)
        except TimeoutException:
            type_into(driver, By.CSS_SELECTOR, "input[name='phone']", PHONE_NUMBER)

    # Continue / Send code
    try:
        click_text(driver, "continue")
    except TimeoutException:
        # Sometimes the first button says "Send code" or "Next"
        try:
            click_text(driver, "send code")
        except TimeoutException:
            click_text(driver, "next")
    wait(2)

def enter_otp(driver):
    print("\nCheck your email/SMS for the OTP.")
    otp = getpass("Paste the one-time code here (input hidden): ").strip()

    # Try a single OTP field first
    try:
        type_into(driver, By.CSS_SELECTOR, "input[name='code']", otp, timeout=5)
    except TimeoutException:
        # Try generic numeric/tel input
        try:
            type_into(driver, By.CSS_SELECTOR, "input[type='tel']", otp, timeout=5)
        except TimeoutException:
            # Fallback: multiple small boxes named code1..code6
            filled_any = False
            for i, ch in enumerate(otp, start=1):
                try:
                    type_into(driver, By.CSS_SELECTOR, f"input[name='code{i}']", ch, timeout=2)
                    filled_any = True
                except TimeoutException:
                    break
            if not filled_any:
                raise AssertionError("Could not locate OTP input(s). Inspect and adjust selectors.")

    # Verify / Continue
    try:
        click_text(driver, "verify", timeout=6)
    except TimeoutException:
        try:
            click_text(driver, "continue", timeout=6)
        except TimeoutException:
            click_text(driver, "submit", timeout=6)

    wait(3)

def assert_logged_in(driver):
    # Evidence: URL keyword OR page keyword must appear
    url = (driver.current_url or "").lower()
    page = (driver.page_source or "").lower()

    url_hit = any(k in url for k in EXPECTED_URL_KEYWORDS)
    page_hit = any(k in page for k in EXPECTED_PAGE_KEYWORDS)

    # Always capture a screenshot for evidence
    try:
        driver.save_screenshot("login_result.png")
    except Exception:
        pass

    if not (url_hit or page_hit):
        raise AssertionError(
            "Login did not reach a known authenticated page.\n"
            f"URL was: {driver.current_url}\n"
            "Tip: Update EXPECTED_URL_KEYWORDS / EXPECTED_PAGE_KEYWORDS in this script to match the app after login."
        )

# ---------- Main ----------
def main():
    print("Select login method:")
    print("  1) Email (OTP to email)")
    print("  2) Phone (OTP via SMS)")
    method = "email" if input("Enter 1 or 2: ").strip() == "1" else "phone"

    driver = start_browser(show_window=True)
    try:
        open_login_choice(driver, method)
        enter_identifier_and_request_code(driver, method)
        enter_otp(driver)
        assert_logged_in(driver)
        print("✅ PASS: Logged in and authenticated page detected. Screenshot saved: login_result.png")
    except Exception as e:
        print(f"❌ FAIL: {e}")
        try:
            driver.save_screenshot("login_result_error.png")
            print("Saved failure screenshot: login_result_error.png")
        except Exception:
            pass
        # Exit with non-zero code for CI
        sys.exit(1)
    finally:
        wait(2)
        driver.quit()

if __name__ == "__main__":
    main()

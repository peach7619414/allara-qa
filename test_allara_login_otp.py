# allara_login_otp.py
# Login to Allara using Email OTP or SMS OTP.
# Flow:
#   - Choose method (email or phone)
#   - Click the right login button
#   - Enter identifier (email/phone)
#   - Request OTP
#   - Paste OTP in the terminal
#   - Submit and verify login

import time
from getpass import getpass  # hides OTP input in terminal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://app.allarahealth.com/login"

# Your identifiers
EMAIL_ADDRESS = "sunnynelson402@gmail.com"
PHONE_NUMBER  = "646-266-1712"

# ---------- Helpers ----------
def start_browser(show_window=True):
    opts = Options()
    if not show_window:
        opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def wait(seconds=2):
    time.sleep(seconds)

# ---------- Flow ----------
def open_login_page(driver, method="email"):
    driver.get(BASE_URL)
    wait(2)

    if method == "email":
        driver.find_element(By.XPATH, "//button[contains(text(),'Log in with email')]").click()
    else:
        driver.find_element(By.XPATH, "//button[contains(text(),'Log in with mobile number')]").click()
    wait(2)

def enter_identifier(driver, method="email"):
    if method == "email":
        email_field = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email_field.send_keys(EMAIL_ADDRESS)
    else:
        phone_field = driver.find_element(By.CSS_SELECTOR, "input[type='tel']")
        phone_field.send_keys(PHONE_NUMBER)

    # Click continue / send code
    driver.find_element(By.XPATH, "//button[contains(text(),'Continue')]").click()
    wait(2)

def enter_otp_and_submit(driver):
    print("\nCheck your email or SMS for the code.")
    otp = getpass("Paste your OTP here: ").strip()

    # Try one combined OTP field first
    try:
        otp_field = driver.find_element(By.CSS_SELECTOR, "input[name='code'], input[type='tel']")
        otp_field.send_keys(otp)
    except NoSuchElementException:
        # If it’s split into boxes, type digit by digit
        for i, digit in enumerate(otp, start=1):
            try:
                box = driver.find_element(By.CSS_SELECTOR, f"input[name='code{i}']")
                box.send_keys(digit)
            except NoSuchElementException:
                break

    # Click Verify/Continue
    driver.find_element(By.XPATH, "//button[contains(text(),'Verify') or contains(text(),'Continue')]").click()
    wait(3)

def verify_logged_in(driver):
    url = driver.current_url.lower()
    page = driver.page_source.lower()
    if "dashboard" in url or "account" in url or "profile" in page:
        print("✅ Logged in successfully.")
    else:
        print("⚠️ Could not confirm login. Check manually if login succeeded.")

# ---------- Main ----------
def main():
    print("Select login method:")
    print("  1) Email (OTP to email)")
    print("  2) Phone (OTP via SMS)")
    choice = input("Enter 1 or 2: ").strip()
    method = "email" if choice == "1" else "phone"

    driver = start_browser(show_window=True)
    try:
        open_login_page(driver, method)
        enter_identifier(driver, method)
        enter_otp_and_submit(driver)
        verify_logged_in(driver)
    finally:
        wait(5)
        driver.quit()

if __name__ == "__main__":
    main()


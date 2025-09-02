# test_allara_login_otp_assert.py
from selenium.webdriver.common.by import By

def test_basic_text_present(driver, base_url):
    driver.get(base_url)
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    # pass if the page contains any common Allara terms
    assert any(k in body_text for k in ["allara", "health", "care", "women"])

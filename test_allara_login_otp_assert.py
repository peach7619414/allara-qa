# test_allara_login_otp_assert.py
import pytest
from selenium.webdriver.common.by import By

@pytest.mark.smoke
def test_basic_text_present(driver, base_url):
    driver.get(base_url)
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    # Pass if page has any of these words (tweak to something stable on Allara)
    keywords = ["allara", "health", "care", "women"]
    assert any(k in body_text for k in keywords)

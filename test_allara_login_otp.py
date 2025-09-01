# test_allara_login_otp.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.smoke
def test_login_page_renders(driver, base_url):
    # If you have a dedicated login URL, replace with it:
    # login_url = f"{base_url}/login"
    login_url = base_url  # placeholder: homepage renders
    driver.get(login_url)

    # Page loads and has any interactive element (button or input)
    el = WebDriverWait(driver, 10).until(
        EC.any_of(
            EC.presence_of_element_located((By.TAG_NAME, "button")),
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )
    )
    assert el is not None

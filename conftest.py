# conftest.py
import os, pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture
def driver():
    """Headless Chrome for all tests; auto-installs chromedriver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,768")
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=options)
    yield d
    d.quit()

@pytest.fixture
def base_url():
    """Base URL comes from env or defaults to Allara."""
    return os.getenv("BASE_URL", "https://allarahealth.com")

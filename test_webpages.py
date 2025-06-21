import pytest
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configure logging
logger = logging.getLogger(__name__)

# Test data: (URL, Expected Title)
test_data = [
    ("https://www.google.com", "Google"),
    ("https://www.youtube.com", "YouTube"),
    ("https://www.python.org", "Welcome to Python.org")
]


@pytest.mark.parametrize("url,expected_title", test_data)
def test_webpage_title(url, expected_title):
    logger.info(f"🔍 Navigating to {url}")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(2)

    page_title = driver.title
    logger.info(f"✅ Page title: '{page_title}'")

    assert expected_title.lower() in page_title.lower(), f"Expected '{expected_title}' in title but got '{page_title}'"

    driver.quit()

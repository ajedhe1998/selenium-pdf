import os
import time
import requests
import pytest
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fpdf import FPDF
from PIL import Image
from dotenv import load_dotenv
import os

# Load .env explicitly from the script's directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO, filename='test_log.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
print(f"Loaded job name: {os.getenv('JOB_NAME')}")
jenkins_url = os.getenv("JENKINS_URL")
jenkins_user = os.getenv("JENKINS_USER")
jenkins_token = os.getenv("JENKINS_TOKEN")
job_name = os.getenv("JOB_NAME")

# Trigger Jenkins Job
def trigger_jenkins_job():
    logger.info(f"🚀 Triggering Jenkins job: {jenkins_url}/job/{job_name}/build")
    trigger_url = f"{jenkins_url}/job/{job_name}/build/api/json"
    auth = (jenkins_user, jenkins_token)
    response = requests.post(trigger_url, auth=auth)

    if response.status_code == 201 and 'Location' in response.headers:
        queue_url = response.headers['Location'] + 'api/json'
        logger.info(f"✅ Triggered successfully. Queue URL: {queue_url}")
    else:
        logger.error(f"❌ Failed to trigger Jenkins job. Status: {response.status_code}, Text: {response.text}")
        raise Exception("Failed to trigger Jenkins job")

    build_number = None
    logger.info("⏳ Waiting for Jenkins to assign build number...")
    for _ in range(30):
        queue_resp = requests.get(queue_url, auth=auth).json()
        if 'executable' in queue_resp and 'number' in queue_resp['executable']:
            build_number = queue_resp['executable']['number']
            logger.info(f"✅ Build #{build_number} started.")
            break
        time.sleep(2)

    if not build_number:
        logger.error("❌ Jenkins build did not start.")
        raise Exception("Jenkins build did not start")

    return build_number

# Test case: validate pages and Jenkins log screenshot
@pytest.mark.order(1)
def test_webpage_screenshots():
    build_number = trigger_jenkins_job()

    test_urls = [
        ("https://www.google.com", "Google"),
        ("https://www.youtube.com", "YouTube"),
        ("https://www.python.org", "Welcome to Python.org"),
        (f"{jenkins_url}/job/{job_name}/{build_number}/console", "Console")
    ]

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--force-device-scale-factor=1")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1920, 1080)

    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_paths = []

    for i, (url, expected_title) in enumerate(test_urls, 1):
        if "console" in url:
            logger.info("🔐 Logging in to Jenkins for console log access")
            driver.get(jenkins_url + "/login")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "j_username"))).send_keys(jenkins_user)
            driver.find_element(By.NAME, "j_password").send_keys(jenkins_token)
            driver.find_element(By.NAME, "Submit").click()
            time.sleep(3)

        logger.info(f"🔍 Navigating to {url}")
        driver.get(url)
        time.sleep(3)
        page_title = driver.title
        logger.info(f"✅ Page title: '{page_title}'")

        assert expected_title.lower() in page_title.lower(), f"Expected '{expected_title}' in title but got '{page_title}'"

        path = os.path.join(screenshot_dir, f"screenshot_{i}.png")
        driver.save_screenshot(path)
        screenshot_paths.append(path)

    driver.quit()

    pdf = FPDF()
    for path in screenshot_paths:
        img = Image.open(path)
        img = img.convert('RGB')
        img_width, img_height = img.size
        max_width = 210
        width_mm = max_width
        height_mm = (img_height / img_width) * width_mm
        pdf.add_page()
        pdf.image(path, 0, 0, width_mm, height_mm)

    pdf.output("Webpage_Screenshots.pdf")
    logger.info("📄 PDF created successfully!")

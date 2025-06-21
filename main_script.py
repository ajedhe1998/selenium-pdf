import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from fpdf import FPDF
from PIL import Image
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv()
jenkins_url = os.getenv("JENKINS_URL")
jenkins_user = os.getenv("JENKINS_USER")
jenkins_token = os.getenv("JENKINS_TOKEN")
job_name = os.getenv("JOB_NAME")

# Step 1: Trigger Jenkins Job
print(f"\n🚀 Triggering Jenkins job: {jenkins_url}/job/{job_name}/build")
trigger_url = f"{jenkins_url}/job/{job_name}/build/api/json"
auth = (jenkins_user, jenkins_token)

trigger_resp = requests.post(trigger_url, auth=auth)

if trigger_resp.status_code == 201 and 'Location' in trigger_resp.headers:
    queue_url = trigger_resp.headers['Location'] + 'api/json'
    print(f"✅ Triggered successfully. Queue URL: {queue_url}")
else:
    print(f"❌ Failed to trigger Jenkins job. Status: {trigger_resp.status_code}, Text: {trigger_resp.text}")
    exit(1)

# Step 2: Wait for Jenkins to assign a build number
print("⏳ Waiting for Jenkins to assign build number...")
build_number = None
for _ in range(30):
    queue_resp = requests.get(queue_url, auth=auth).json()
    if 'executable' in queue_resp and 'number' in queue_resp['executable']:
        build_number = queue_resp['executable']['number']
        print(f"✅ Build #{build_number} started.")
        break
    time.sleep(2)

if not build_number:
    print("❌ Jenkins build did not start.")
    exit(1)

# Step 3: Define URLs to capture
jenkins_console_url = f"{jenkins_url}/job/{job_name}/{build_number}/console"
webpages = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.python.org",
    jenkins_console_url
]

# Step 4: Setup headless Chrome
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)
screenshot_paths = []

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")
options.add_argument("--force-device-scale-factor=1")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_window_size(1920, 1080)

# Step 5: Capture screenshots
for i, url in enumerate(webpages, 1):
    if "console" in url and "jenkins" in url:
        # Login to Jenkins first
        driver.get(jenkins_url + "/login")
        time.sleep(5)
        driver.find_element("id", "j_username").send_keys(jenkins_user)
        driver.find_element("name", "j_password").send_keys(jenkins_token)
        driver.find_element("name", "Submit").click()
        time.sleep(5)
        driver.get(url)
    else:
        driver.get(url)
    time.sleep(3)
    path = os.path.join(screenshot_dir, f"screenshot_{i}.png")
    driver.save_screenshot(path)
    screenshot_paths.append(path)

driver.quit()

# Step 6: Create PDF
pdf = FPDF()
for path in screenshot_paths:
    img = Image.open(path)
    img = img.convert('RGB')
    img_width, img_height = img.size
    max_width = 210  # A4 width in mm
    width_mm = max_width
    height_mm = (img_height / img_width) * width_mm
    pdf.add_page()
    pdf.image(path, 0, 0, width_mm, height_mm)

pdf.output("Webpage_Screenshots.pdf")
print("\n📄 PDF created successfully!")

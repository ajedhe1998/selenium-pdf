from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fpdf import FPDF
from PIL import Image
import time
import os

# URLs to visit
webpages = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.python.org"
]

# Directories
screenshot_dir = "screenshots"
resized_dir = "resized"
os.makedirs(screenshot_dir, exist_ok=True)
os.makedirs(resized_dir, exist_ok=True)
screenshot_paths = []

# Set up Chrome headless
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Step 1: Take screenshots
for i, url in enumerate(webpages, 1):
    driver.get(url)
    time.sleep(2)
    screenshot_path = os.path.join(screenshot_dir, f"screenshot_{i}.png")
    driver.save_screenshot(screenshot_path)
    screenshot_paths.append(screenshot_path)

driver.quit()

# Step 2: Resize screenshots to A4 size in pixels (794 x 1123)
resized_paths = []
target_size = (794, 1123)

for path in screenshot_paths:
    img = Image.open(path)
    img.thumbnail(target_size, Image.Resampling.LANCZOS)

    # Create white background and center image
    bg = Image.new("RGB", target_size, (255, 255, 255))
    x = (target_size[0] - img.width) // 2
    y = (target_size[1] - img.height) // 2
    bg.paste(img, (x, y))

    resized_path = os.path.join(resized_dir, os.path.basename(path))
    bg.save(resized_path)
    resized_paths.append(resized_path)

# Step 3: Create PDF from resized images
pdf = FPDF(orientation="P", unit="mm", format="A4")

for img_path in resized_paths:
    pdf.add_page()
    pdf.image(img_path, x=0, y=0, w=210, h=297)  # Full page A4

pdf.output("Webpage_Screenshots.pdf")
print("✅ PDF created successfully and images fully visible!")

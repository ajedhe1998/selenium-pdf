from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fpdf import FPDF
from PIL import Image
import time
import os

# === Step 1: URLs to visit ===
webpages = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.python.org"
]

# === Step 2: Setup ===
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)
screenshot_paths = []

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# === Step 3: Capture screenshots ===
for i, url in enumerate(webpages, 1):
    driver.get(url)
    time.sleep(2)  # Wait for page to load
    path = os.path.join(screenshot_dir, f"screenshot_{i}.png")
    driver.save_screenshot(path)
    screenshot_paths.append(path)

driver.quit()

# === Step 4: Create PDF with scaled, centered images ===
pdf = FPDF(orientation="P", unit="mm", format="A4")
pdf.set_auto_page_break(auto=True, margin=0)

for path in screenshot_paths:
    img = Image.open(path)
    img_w, img_h = img.size

    # A4 page size in mm
    page_w, page_h = 210, 297

    # Convert pixels to mm (1 px = 0.264583 mm)
    img_w_mm = img_w * 0.264583
    img_h_mm = img_h * 0.264583

    # Fit image within page while maintaining aspect ratio
    scale = min(page_w / img_w_mm, page_h / img_h_mm)
    new_w = img_w_mm * scale
    new_h = img_h_mm * scale

    # Center image
    x = (page_w - new_w) / 2
    y = (page_h - new_h) / 2

    pdf.add_page()
    pdf.image(path, x=x, y=y, w=new_w, h=new_h)

pdf.output("Webpage_Screenshots.pdf")
print("✅ PDF created successfully!")

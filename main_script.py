from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from fpdf import FPDF
from PIL import Image
import time
import os

def take_screenshots(webpages, screenshot_dir="screenshots"):
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_paths = []

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for i, url in enumerate(webpages, 1):
        driver.get(url)
        time.sleep(2)
        path = os.path.join(screenshot_dir, f"screenshot_{i}.png")
        driver.save_screenshot(path)
        screenshot_paths.append((url, path, driver.title))

    driver.quit()
    return screenshot_paths

def create_pdf(image_paths, output_pdf="Webpage_Screenshots.pdf"):
    pdf = FPDF()
    for _, path, _ in image_paths:
        img = Image.open(path)
        width, height = img.size
        pdf_w = width * 0.264583
        pdf_h = height * 0.264583
        pdf.add_page()
        pdf.image(path, 0, 0, pdf_w, pdf_h)
    pdf.output(output_pdf)
    return output_pdf

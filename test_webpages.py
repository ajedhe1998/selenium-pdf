import os
import main_script

webpages = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.python.org"
]


def test_screenshot_and_pdf_generation():
    screenshots = main_script.take_screenshots(webpages)

    # Assert all screenshots are created
    for url, path, title in screenshots:
        assert os.path.exists(path), f"Screenshot not found for {url}"
        assert len(title) > 0, f"Title not captured for {url}"

    # Create PDF
    pdf_path = main_script.create_pdf(screenshots)
    assert os.path.exists(pdf_path), "PDF was not created"

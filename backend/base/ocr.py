import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import re

# ----------------------
# Preprocessing function
# ----------------------
def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Convert image to grayscale, denoise, sharpen and threshold for OCR.
    """
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Denoise
    gray = cv2.fastNlMeansDenoising(gray, h=30)

    # Enhance contrast
    gray = cv2.equalizeHist(gray)

    # Sharpen
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    gray = cv2.filter2D(gray, -1, kernel)

    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        25, 10
    )

    return thresh

# ----------------------
# Extract text from PDF
# ----------------------
def extract_text_from_pdf(pdf_path: str, languages: str = "eng+deu+por") -> str:
    """
    Convert PDF pages to images and extract text using Tesseract.
    """
    images = convert_from_path(pdf_path, dpi=300)
    full_text = ""

    for i, image in enumerate(images):
        processed = preprocess_image(image)
        text = pytesseract.image_to_string(
            processed,
            lang=languages,
            config="--oem 3 --psm 4"
        )
        full_text += "\n" + text

        # Optional: save processed pages to check OCR visually
        Image.fromarray(processed).save(f"/app/media/test_page_{i+1}.png")

    return full_text

# ----------------------
# Parse menu items
# ----------------------
def parse_menu(text: str) -> list:
    """
    Parse text from OCR into structured menu items:
    [{'name': ..., 'price': ..., 'description': ...}, ...]
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    items = []

    price_pattern = r"(\d+[.,]\d{2})\s*€?"  # Match prices like 12.50 or 12,50

    buffer_name = ""
    buffer_desc = ""

    for line in lines:
        # Try to find price in the line
        match = re.search(price_pattern, line)
        if match:
            price = match.group(1).replace(",", ".")
            name = (buffer_name + " " + line[:match.start()]).strip()
            items.append({
                "name": name,
                "price": float(price),
                "description": buffer_desc.strip()
            })
            buffer_name = ""
            buffer_desc = ""
        else:
            # If line does not contain price, consider it part of name or description
            if buffer_name:
                buffer_name += " " + line
            else:
                buffer_name = line

    return items

# ----------------------
# Example usage
# ----------------------
if __name__ == "__main__":
    pdf_path = "/app/media/event_menus/MaiGarden_2025_DE_EN_XyUNu3c.pdf"
    text = extract_text_from_pdf(pdf_path)
    items = parse_menu(text)

    print("OCR TEXT:")
    print(text[:1000])  # first 1000 chars for preview
    print("\nPARSED ITEMS:")
    for item in items:
        print(item)

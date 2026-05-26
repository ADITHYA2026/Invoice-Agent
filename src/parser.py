import os
import pdfplumber
import pytesseract

from PIL import Image
from pathlib import Path


# Add Tesseract to PATH (Windows Fix)
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Tesseract-OCR"

# Explicit Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_pdf(file_path):

    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        raise Exception(f"PDF parsing failed: {str(e)}")

    return text.strip()


def extract_text_from_image(file_path):

    try:
        image = Image.open(file_path)

        # Better OCR config for invoices/documents
        text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        return text.strip()

    except Exception as e:
        raise Exception(f"OCR failed: {str(e)}")


def parse_document(file_path):

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(file_path)

    raise Exception("Unsupported file format")
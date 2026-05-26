import pdfplumber
import pytesseract

from PIL import Image
from pathlib import Path

from config import TESSERACT_PATH


if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


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
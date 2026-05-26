import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

TESSERACT_PATH = os.getenv("TESSERACT_PATH", "")

INPUT_DIR = "input"
OUTPUT_DIR = "output"

JSON_DIR = f"{OUTPUT_DIR}/extracted_json"
LOG_DIR = f"{OUTPUT_DIR}/logs"
ROUTED_DIR = f"{OUTPUT_DIR}/routed"
ACK_DIR = f"{OUTPUT_DIR}/acknowledgements"

CSV_FILE = f"{ROUTED_DIR}/low_value_invoices.csv"
HUMAN_REVIEW_FILE = f"{LOG_DIR}/human_review.log"
PROCESS_LOG_FILE = f"{LOG_DIR}/process_log.jsonl"
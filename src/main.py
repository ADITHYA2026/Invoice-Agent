import json
import os
import time

from parser import parse_document
from extractor import extract_invoice_data
from router import route_invoice
from logger import log_result
from ack import send_acknowledgement
from utils import save_json
from config import HUMAN_REVIEW_FILE


WEBHOOK_FILE = "webhook_payload.json"


with open(WEBHOOK_FILE, "r") as f:
    payload = json.load(f)


for event in payload["events"]:

    filename = event["attachment"]["filename"]
    sender = event["from"]

    local_path = os.path.join(
        "input",
        filename
    )

    print(f"\nProcessing: {filename}")

    try:

        raw_text = parse_document(local_path)

        if not raw_text:
            raise Exception("Empty extracted text")

        data, error = extract_invoice_data(raw_text)

        if error:

            log_result(filename, "partial", error)

            with open(HUMAN_REVIEW_FILE, "a") as f:
                f.write(json.dumps({
                    "filename": filename,
                    "reason": error
                }) + "\n")

            send_acknowledgement(sender, filename, "partial")

            print(f"Partial Processing: {error}")

            time.sleep(10)

            continue

        save_json(data, filename.replace(".", "_"))

        route = route_invoice(data)

        log_result(filename, "success", route)

        send_acknowledgement(sender, filename, "success")

        print(f"Successfully processed: {filename}")

    except Exception as e:

        error_message = str(e)

        log_result(filename, "failed", error_message)

        with open(HUMAN_REVIEW_FILE, "a") as f:
            f.write(json.dumps({
                "filename": filename,
                "reason": error_message
            }) + "\n")

        send_acknowledgement(sender, filename, "failed")

        print(f"Error: {error_message}")

    print("Waiting before next request...\n")

    time.sleep(10)
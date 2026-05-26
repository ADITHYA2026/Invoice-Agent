import csv
import json
import os

from config import CSV_FILE, HUMAN_REVIEW_FILE


os.makedirs("output/routed", exist_ok=True)
os.makedirs("output/logs", exist_ok=True)


def route_invoice(data):

    doc_type = data["document_type"]
    total = data["total_amount"]
    confidence = data.get("confidence_score", 1)

    if confidence < 0.7:

        with open(HUMAN_REVIEW_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")

        return "human_review_low_confidence"

    if doc_type == "unknown":

        with open(HUMAN_REVIEW_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")

        return "human_review"

    if total > 50000:
        mock_slack_alert(data)
        return "slack"

    append_to_csv(data)

    return "csv"


def mock_slack_alert(data):

    print("\n================ SLACK ALERT ================\n")

    print(f"Vendor Name   : {data['vendor_name']}")
    print(f"Invoice No    : {data['invoice_number']}")
    print(f"Invoice Date  : {data['invoice_date']}")
    print(f"Total Amount  : ₹{data['total_amount']}")
    print(f"Document Type : {data['document_type']}")

    print("\n=============================================\n")

    with open("output/routed/slack_alerts.log", "a") as f:
        f.write(json.dumps(data) + "\n")


def append_to_csv(data):

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "vendor_name",
                "invoice_number",
                "invoice_date",
                "total_amount",
                "document_type"
            ])

        writer.writerow([
            data["vendor_name"],
            data["invoice_number"],
            data["invoice_date"],
            data["total_amount"],
            data["document_type"]
        ])
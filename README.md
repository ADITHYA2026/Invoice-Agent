# AI Invoice Automation Agent

End-to-end invoice automation pipeline that processes vendor invoices from webhook payloads to structured extraction, routing, logging, and acknowledgements using Gemini LLM.

---

## Features

* PDF and image invoice ingestion
* OCR + PDF text extraction (`pdfplumber` + `pytesseract`)
* Gemini 2.5 Flash Lite based invoice classification and extraction
* Structured JSON validation using Pydantic
* Conditional routing:

  * `total_amount > ₹50,000` → Mock Slack alert
  * `total_amount <= ₹50,000` → CSV storage
  * `confidence_score < 0.7` or `unknown` → Human review
* Retry handling with exponential backoff + jitter
* Structured logging and acknowledgement generation
* Docker support

---

## Tech Stack

* Python
* Gemini 2.5 Flash Lite
* pdfplumber
* pytesseract
* Pydantic
* Pillow
* python-dotenv
* Docker

---

## Folder Structure

```text
invoice-agent/
│
├── input/
│   ├── inv_001.pdf
│   ├── ...
│   └── inv_blank.pdf
│
├── sample_output/
│   ├── extracted_json/
│   ├── logs/
│   ├── routed/
│   └── acknowledgements/
│
├── src/
│   ├── main.py
│   ├── parser.py
│   ├── extractor.py
│   ├── router.py
│   ├── logger.py
│   ├── ack.py
│   ├── schemas.py
│   ├── prompts.py
│   ├── config.py
│   └── utils.py
│
├── Dockerfile
├── requirements.txt
├── .env.example
├── webhook_payload.json
└── README.md
```

> `.env.example` is included for configuration reference. Actual `.env` secrets and virtual environments are excluded using `.gitignore`.

---

## Setup

### Local Setup

```bash
pip install -r requirements.txt
```

Install Tesseract OCR:

### Ubuntu/Linux

```bash
sudo apt install tesseract-ocr
```

### Windows

Install from:
https://github.com/UB-Mannheim/tesseract/wiki

Create a local `.env` file:

```env
GEMINI_API_KEY=your_api_key
```

Run locally:

```bash
python src/main.py
```

---

## Docker Setup

```bash
docker build -t invoice-agent .
docker run --env-file .env invoice-agent
```

Docker bundles Python dependencies and Tesseract OCR, so no local Python dependency setup is required.

---

## Design Decisions

* Used Gemini 2.5 Flash Lite for fast and cost-efficient extraction.
* Used Pydantic validation to prevent malformed JSON propagation.
* Used mock Slack + CSV routing to avoid external dependencies.
* Used net payable amount for ambiguous invoice totals (`inv_005`).
* Added retry handling with exponential backoff and jitter for Gemini rate limits.
* Added human-review fallback for low-confidence or corrupted invoices.

---

## Routing Rules

| Condition                    | Action           |
| ---------------------------- | ---------------- |
| `confidence_score < 0.7`     | Human review     |
| `document_type == "unknown"` | Human review     |
| `total_amount > 50000`       | Mock Slack alert |
| `total_amount <= 50000`      | Append to CSV    |

---

## Error Handling

Handled scenarios include:

* Gemini API rate limits (`429 RESOURCE_EXHAUSTED`)
* Malformed LLM JSON
* Empty OCR extraction
* Unsupported file formats
* Corrupted or incomplete invoices

The pipeline fails gracefully — every document generates logs and acknowledgements instead of crashing the workflow.

---

## Output Structure

```text
sample_output/
├── extracted_json/
├── logs/
├── routed/
└── acknowledgements/
```

---

## Video Walkthrough

🎥 Demo Video:
https://drive.google.com/file/d/1eVAJeoIDLazPwSqjJofV6IxCNJPeYpC6/preview

Covers:

* Full pipeline execution
* Slack + CSV routing
* Blank invoice error handling
* JSON outputs and logging
* Design decisions

---

## Known Limitations

* Free-tier Gemini API rate limits slow batch processing.
* OCR quality depends on scan clarity.
* Extremely complex invoice tables may require table-aware parsing models.
* Documents are processed sequentially (no async batching yet).

---

## Future Improvements

* Real Slack webhook integration
* Google Sheets integration
* Async batch processing
* Vision-based multimodal extraction
# AI Invoice Automation Agent

An end-to-end invoice processing pipeline built using Python and Gemini LLM.

---

# Features

- PDF and image invoice ingestion
- OCR and PDF text extraction
- LLM-based classification and field extraction
- Structured JSON validation using Pydantic
- Conditional routing:
  - High-value invoices → Slack alert
  - Low-value invoices → CSV
  - Unknown documents → Human review log
- Error handling and retry logic
- Mock acknowledgement emails
- Exponential backoff retry handling for Gemini API rate limits
- Graceful degradation for malformed or unreadable documents
- Structured processing logs for auditability
- Human-review fallback pipeline for incomplete invoices
- Persistent Slack alert logging

---

# Tech Stack

- Python
- Gemini 2.5 Flash Lite
- pdfplumber
- pytesseract
- Pydantic
- Pillow
- python-dotenv
- CSV (local fallback storage)

---

# Folder Structure

```text
invoice-agent/
│
├── input/
│   ├── inv_001.pdf
│   ├── inv_002.pdf
│   ├── ...
│
├── output/
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
├── sample_output/
├── requirements.txt
├── .env
├── README.md
└── webhook_payload.json
```

---

# Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Tesseract OCR:

## Ubuntu/Linux

```bash
sudo apt install tesseract-ocr
```

## Windows

Install Tesseract OCR from:
https://github.com/UB-Mannheim/tesseract/wiki

Add Tesseract to PATH.

Verify installation:

```bash
tesseract --version
```

Add API key to `.env`

```env
GEMINI_API_KEY=your_key
```

---

# Run

```bash
python src/main.py
```

---

# Design Decisions

- Used Gemini 2.5 Flash Lite for fast and cost-efficient structured extraction.
- Used Pydantic validation to prevent malformed JSON propagation.
- Used mock Slack webhooks instead of real integrations.
- Used CSV fallback instead of Google Sheets for simplicity.
- Used Net Payable amount for ambiguous invoices.
- Added exponential backoff with jitter to handle Gemini API rate limits gracefully.
- Added retry handling to avoid pipeline failure during temporary API exhaustion.
- Used structured logging for operational visibility and debugging.
- Implemented human-review fallback for incomplete or corrupted invoices.
- Used mock Slack alerts with persistent log storage for audit traceability.
- Added acknowledgement file generation for every processed document.

---

# Routing Rules

| Condition | Action |
|---|---|
| total_amount > 50000 | Mock Slack alert |
| total_amount <= 50000 | Append to CSV |
| document_type == unknown | Human review log |

---

# Error Handling Strategy

The pipeline is designed to fail gracefully instead of crashing.

Handled scenarios include:

- Gemini API rate-limit errors (429 RESOURCE_EXHAUSTED)
- Malformed or invalid LLM JSON responses
- Empty OCR extraction
- Unsupported file formats
- Corrupted or incomplete invoice scans
- Missing totals or critical invoice fields

Retry handling uses exponential backoff with randomized jitter to reduce repeated API collisions.

---

# Expected Output Structure

```text
output/
│
├── extracted_json/
│   ├── inv_001_pdf.json
│   ├── inv_002_pdf.json
│
├── logs/
│   ├── process_log.jsonl
│   ├── human_review.log
│
├── routed/
│   ├── low_value_invoices.csv
│   ├── slack_alerts.log
│
└── acknowledgements/
```

---

# Video Walkthrough Checklist

👉 Video Demonstration (Google Drive Link): https://drive.google.com/file/d/1eVAJeoIDLazPwSqjJofV6IxCNJPeYpC6/preview

The walkthrough demonstrates:

- Full pipeline execution on all sample invoices
- One successful Slack routing
- One successful CSV routing
- Human review handling for corrupted invoice
- Generated JSON outputs
- Error handling with retry logic
- Design decisions and architecture overview

---

# Known Limitations

- Free-tier Gemini API rate limits may slow large batch processing.
- OCR quality depends heavily on scan clarity and image resolution.
- Extremely complex invoice layouts may require table-aware parsing models.
- OCR accuracy depends on scan quality.
- Very complex invoice tables may require advanced parsing.

---

# Future Improvements

- Real Slack webhook integration
- Google Sheets integration
- Dockerized deployment
- Async batch invoice processing
- Confidence-score based human escalation
- Vision-based invoice parsing using multimodal models
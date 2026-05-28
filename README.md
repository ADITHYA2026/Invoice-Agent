# AI Invoice Automation Agent

End-to-end pipeline that processes vendor invoice emails with zero human intervention — from raw webhook payload to classified JSON extraction, conditional routing, and structured acknowledgement.

---

## Architecture

```
webhook_payload.json
        │
        ▼
  parser.py          ← pdfplumber (digital PDFs) + pytesseract OCR (scanned images)
        │
        ▼
  extractor.py       ← Gemini 2.5 Flash Lite → JSON → Pydantic validation
        │
        ▼
  router.py          ← confidence < 0.7 → human review
                       unknown type     → human review
                       total > ₹50,000  → mock Slack alert + slack_alerts.log
                       total ≤ ₹50,000  → low_value_invoices.csv
        │
        ▼
  logger.py + ack.py ← structured JSONL log per document + acknowledgement .txt per vendor
```

---

## Quick Start

**Prerequisites:** Python 3.10+, Tesseract OCR installed on the system.

```bash
# 1. Clone and install
git clone <repo-url> && cd Invoice-Agent
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Set GEMINI_API_KEY and optionally TESSERACT_PATH in .env

# 3. Run
python src/main.py
```

### Ubuntu / Linux — Tesseract install

```bash
sudo apt install tesseract-ocr
```

### Windows — Tesseract install

Download from https://github.com/UB-Mannheim/tesseract/wiki, install, and add to PATH.
Then set `TESSERACT_PATH` in `.env` to the full binary path.

### Docker (no local Python setup needed)

```bash
docker build -t invoice-agent .
docker run --env-file .env invoice-agent
```

The Dockerfile bundles Tesseract OCR, all Python dependencies, and the pipeline. To persist generated outputs outside the container, mount the local output directory:

```bash
docker run --env-file .env -v $(pwd)/output:/app/output invoice-agent
```

---

## Design Decisions

**OCR strategy:** `pdfplumber` extracts text from digital PDFs directly. Image files (`.jpg`, `.jpeg`, `.png`) go straight to `pytesseract`. The provided dataset cleanly separated digital PDFs and scanned image invoices, allowing extension-based routing between PDF parsing and OCR extraction.

**Ambiguous invoice — inv_005 (Kalyan Electrical Works):** The invoice shows a gross total of ₹58,480 with an advance deduction of ₹10,000, leaving a net payable of ₹48,480. I used **net payable (₹48,480)** as `total_amount` because the routing rule is meant to flag invoices that require a manager's payment approval — what matters is the cash the company will actually disburse, not the gross value. This causes inv_005 to route to CSV rather than Slack. If your policy is gross-based, change the router threshold logic rather than the extraction.

**Pydantic validation:** All LLM output passes through `InvoiceData` before any downstream step. Malformed or invalid JSON responses trigger capped validation retries before the document is logged as `partial`, preventing malformed data propagation while keeping the pipeline resilient.

**Exponential backoff:** Rate-limit errors (HTTP 429 / `RESOURCE_EXHAUSTED`) use a doubling delay starting at 10 s with ±1–3 s random jitter to avoid thundering-herd retry collisions.

**Confidence-score routing:** The LLM assigns a `confidence_score` (0–1) per document. Any score below 0.7 bypasses the amount-based routing and goes directly to `human_review.log`, regardless of document type or total. This catches structurally valid but uncertain extractions.

**Mock integrations:** Slack alerts write to `output/routed/slack_alerts.log` and print to console. CSV fallback uses Python's `csv` module (no Google Sheets dependency). Both are intentional — The routing integrations are intentionally mock-based so the pipeline remains runnable without external Slack or Google Sheets credentials.

**Secrets:** API key loaded via `python-dotenv`. `.env` is `.gitignore`d; `.env.example` is provided for reference.

---

## Routing Rules

| Condition | Action | Output |
|---|---|---|
| `confidence_score < 0.7` | Human review | `output/logs/human_review.log` |
| `document_type == "unknown"` | Human review | `output/logs/human_review.log` |
| `total_amount > 50000` | Mock Slack alert | `output/routed/slack_alerts.log` |
| `total_amount <= 50000` | Append to CSV | `output/routed/low_value_invoices.csv` |

Every document produces an acknowledgement file regardless of routing outcome (success, partial, or failed).

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Empty OCR output | Raises exception → logged as `failed` → human review |
| Malformed LLM JSON | Capped validation retries, then logged as `partial` |
| Gemini 429 rate limit | Exponential backoff (10 s → 20 s → 40 s + jitter), up to 5 attempts |
| Unsupported file format | Exception at parser → logged as `failed` |
| Corrupt / blank PDF (inv_blank.pdf) | OCR returns empty string → `failed` with reason |

No document is silently dropped. Every input in `webhook_payload.json` produces a log entry and acknowledgement file.

---

## Output Structure

```
sample_output/
├── extracted_json/
│   ├── inv_001_pdf.json
│   ├── inv_002_pdf.json
│   └── ...                    ← one validated JSON per document
├── logs/
│   ├── process_log.jsonl      ← structured log: {timestamp, filename, status, reason}
│   └── human_review.log       ← JSONL of documents needing manual review
├── routed/
│   ├── low_value_invoices.csv ← invoices ≤ ₹50,000
│   └── slack_alerts.log       ← invoices > ₹50,000 (mock Slack payloads)
└── acknowledgements/
    ├── inv_001_pdf.txt
    └── ...                    ← one ack file per vendor, per document
```

---

## Sample Results (10 test documents)

| File | Type | Total | Confidence | Route |
|---|---|---|---|---|
| inv_001.pdf | standard_invoice | ₹28,400 | 0.95 | CSV |
| inv_002.pdf | standard_invoice | ₹1,14,750 | 0.95 | Slack |
| inv_003.pdf | standard_invoice | ₹7,280 | 0.95 | CSV |
| inv_004.pdf | standard_invoice | ₹51,500 | 0.90 | Slack |
| inv_005.pdf | standard_invoice | ₹48,480 (net payable) | 0.90 | CSV |
| inv_006.pdf | credit_note | ₹12,000 | 0.95 | CSV |
| inv_007.pdf | credit_note | ₹9,440 | 0.95 | CSV |
| inv_008.jpg | standard_invoice | — | — | CSV |
| inv_009.jpg | standard_invoice | — | — | CSV |
| inv_010.pdf | standard_invoice | — | 0.6 | Human review (partial) |
| inv_blank.pdf | — | — | — | Failed (empty OCR) |

---

## Tech Stack

| Component | Library / Tool |
|---|---|
| PDF text extraction | `pdfplumber 0.11.4` |
| OCR (scanned images) | `pytesseract 0.3.13` + Tesseract |
| LLM extraction | `google-genai 1.16.1` — Gemini 2.5 Flash Lite |
| Output validation | `pydantic 2.11.4` |
| Image handling | `Pillow 11.2.1` |
| Config / secrets | `python-dotenv 1.1.0` |
| Containerisation | Docker |

---

## Known Limitations

- Free-tier Gemini API rate limits slow batch processing; the 10 s inter-request sleep is a deliberate workaround.
- OCR accuracy degrades significantly on low-DPI scans (below ~150 DPI). inv_008 and inv_009 extraction quality depends entirely on scan clarity.
- `pdfplumber` does not reconstruct complex multi-column table layouts; very dense invoice tables may require a table-aware parser.
- No async processing — documents are handled sequentially. For volumes above ~50/day, parallelism with a task queue would be the next step.

---

## Video Walkthrough

🎥 [Watch the demo](https://drive.google.com/file/d/1eVAJeoIDLazPwSqjJofV6IxCNJPeYpC6/preview)

Covers: full pipeline run on all 10 documents · Slack routing + CSV entry · deliberate error (blank file) · design decision walkthrough (inv_005 ambiguous total).
# ChainCert — Demo Backend

This repository contains the existing Flask demo UI and ChainCert Modules 1–4, plus the integrated Module 5 verification engine, Module 6 access control, and PDF/image ingestion with OCR. The separately developed React frontend was not included in the ZIP you supplied; this package exposes JSON APIs for it to connect to.

## Fast start (Ubuntu/Linux)

```bash
cd EDIL1
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
sudo apt-get update && sudo apt-get install -y tesseract-ocr
python scripts/seed_demo.py
python app.py
```

Open the existing demo frontend at **http://127.0.0.1:5000/**.

Demo accounts on a fresh local setup:

- Platform admin: `demo.admin@chaincert.local` / `ChainCertDemo!2026`
- Institution admin: `issuer@chaincert.local` / `IssuerDemo!2026`

Synthetic test files:

- `demo_documents/CC001_original.pdf` → expected `GENUINE`
- `demo_documents/CC001_modified.pdf` → expected `TAMPERED` (CGPA changed)
- `demo_documents/CERT-A1_scanned.pdf` → image-only PDF to demonstrate OCR; expected `GENUINE` when extraction matches

**Two-laptop demo:** run the Flask backend on one laptop or reachable host; open `http://HOST_LAN_IP:5000/` from the other laptop. Both devices must reach the same backend and persistent storage. Do not expose Flask's development server directly to the public internet.

## Backend details and API contracts

See [README_DEMO_BACKEND.md](README_DEMO_BACKEND.md) for the complete endpoint table, curl examples, upload limits/retention, deployment notes, testing instructions, known limitations, and the short Antigravity audit prompt.

## Tests

```bash
python -m pytest -q
```

The integrated suite currently includes tests for the original Modules 1–4, plus registration, verification statuses, revocation, audit visibility, PDF parsing, OCR, and upload result retrieval.

## Deployment note

Vercel can host the React frontend, but the current Flask backend relies on persistent SQLite and JSON files. For the two-laptop demo, run the Flask app on a reachable host. Before a public/serverless backend deployment, migrate certificate, access-control, upload-result, and verification-history storage to durable shared storage and deploy Flask on a compatible persistent backend host.

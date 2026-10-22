# ChainCert integrated backend — two-laptop demo

This package preserves the existing Flask UI and Modules 1–4, restores/adds Module 5 verification, Module 6 access control, and a PDF/image extraction module. The React frontend is not included in the uploaded ZIP, so the API contracts below are documented for the separately built frontend.

## What is included

- Existing Module 1–4 pipeline: records, SHA-256, Merkle trees, and local block chaining.
- Module 5: compares extracted candidate fields with the trusted record and stored SHA-256. If a Merkle proof exists, validates it using the existing Module 3 verifier; checks the local Module 4 chain.
- Module 6: Argon2id password hashing, signed bearer sessions, roles/permissions, institution boundaries, failed-login throttling, optional TOTP, session revocation, and access-control audit events.
- Document ingestion: text PDFs, scanned PDFs, PNG and JPEG; native PDF text extraction first, Tesseract OCR on pages without usable text; structured candidate fields, warnings, and confidence metadata.
- Persistent verification-attempt history and revocation reason/time.
- JSON API at `/api/v1` while the original Flask HTML demo routes remain available.

## Limitations to keep clear during the demo

- OCR extracts candidate text; it does not prove authenticity and cannot detect every visual overlay or forgery.
- Tesseract's field confidence is a normalized mean token score proxy, not a calibrated probability. Native PDF extraction returns `confidence: null` rather than inventing a score.
- Ambiguous dates and invalid/uncertain CGPA values are left unresolved and flagged for review.
- The local block chain is a local tamper-evident demo structure, not an externally anchored public blockchain.
- SQLite is appropriate for a local demo, not shared serverless deployment storage. For two laptops, host one Flask backend on a reachable machine, or migrate the data stores to managed persistent storage before public deployment.
- The uploaded project ZIP did not contain the separate React/Vite frontend source, so exact frontend-specific service call matching still requires its API client file or repository.

## Install on Ubuntu/Linux

```bash
cd EDIL1
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

If you are running in an offline environment and the repository's vendored Flask is needed, the app adds `vendor_packages/` to `sys.path`. The other dependencies (PyMuPDF, Pillow, pytesseract, argon2-cffi, itsdangerous) must be installed in the active Python environment.

Set demo-only secrets (recommended even locally):

```bash
export CHAINCERT_SECRET_KEY="local-demo-secret-change-this-before-deployment-12345"
export CHAINCERT_TOKEN_SECRET="local-token-secret-change-this-before-deployment-67890"
```

Seed demo users and synthetic records:

```bash
python scripts/seed_demo.py
```

Demo account on a fresh data directory:

- Platform admin: `demo.admin@chaincert.local` / `ChainCertDemo!2026`
- Institution admin: `issuer@chaincert.local` / `IssuerDemo!2026`

These are demo credentials. Do not reuse them in a public deployment. `seed_demo.py` does not delete existing data and refuses to bootstrap a new admin if the access database already contains users.

Start the server:

```bash
python app.py
```

Open the existing demo UI at `http://127.0.0.1:5000/`.

## Two-laptop setup

Run Flask on Laptop 1 (or another host reachable from both laptops):

```bash
python app.py
```

The app listens on `0.0.0.0:5000`. Find the host's LAN IP with `hostname -I`, then from Laptop 2 open `http://HOST_LAN_IP:5000/`. Both devices must be on the same trusted network and the host firewall must allow port 5000. Do not expose the Flask development server directly to the public internet.

For a separately hosted React/Vite frontend, set its API base URL to `http://HOST_LAN_IP:5000/api/v1` for local-network demos and add its origin to `CHAINCERT_CORS_ORIGINS`. For a Vercel-hosted frontend, the Flask backend must be hosted on an HTTPS-capable server and `CHAINCERT_CORS_ORIGINS` must include the exact deployed frontend origin. Do not use SQLite/JSON files on Vercel serverless functions as shared persistent storage.

## API endpoints

All JSON routes are prefixed with `/api/v1`. Use `Authorization: Bearer <access_token>` for protected institution routes.

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| GET | `/health` | Health check | Public |
| POST | `/auth/login` | Login `{email,password}` | Public |
| POST | `/auth/logout` | Revoke session | Bearer |
| GET | `/auth/me` | Current user | Bearer |
| GET | `/certificates?q=&status=` | Registry search | Issuer/admin |
| GET | `/certificates/{certificate_id}` | Certificate details | Issuer/admin |
| POST | `/certificates` | Register certificate JSON | Issuer/admin |
| POST | `/certificates/extract` | Extract PDF/image fields; multipart field `document` | Public demo upload |
| GET | `/uploads/{upload_id}` | Retrieve extraction result for up to 24 hours | Public |
| POST | `/verification/verify` or `/verify` | Verify submitted JSON fields | Public |
| POST | `/verification/verify-upload` | Upload, extract and verify in one call | Public demo upload |
| GET | `/verification/history?limit=100` | Recent verification attempts | Issuer/admin |
| GET | `/audit?limit=100` | Verification audit events | Issuer/admin |
| POST | `/certificates/{id}/revoke` | Revoke with `{reason}` | Authorized admin |

Certificate fields use the existing names: `certificate_id`, `student_name`, `roll_number`, `course`, `cgpa`, `issue_date`, and `institution_id`.

### Example API calls

Login:

```bash
curl -s http://127.0.0.1:5000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo.admin@chaincert.local","password":"ChainCertDemo!2026"}'
```

Extract a sample PDF:

```bash
curl -s http://127.0.0.1:5000/api/v1/certificates/extract \
  -F 'document=@demo_documents/CC001_original.pdf'
```

Upload and verify in one step:

```bash
curl -s http://127.0.0.1:5000/api/v1/verification/verify-upload \
  -F 'document=@demo_documents/CC001_original.pdf'
```

Repeat with `demo_documents/CC001_modified.pdf` to demonstrate a field mismatch. Expected status for the original is `GENUINE`; the modified version should be `TAMPERED`. Upload `demo_documents/CERT-A1_scanned.pdf` to demonstrate scanned-PDF OCR; it is seeded as a separate synthetic credential and should return `GENUINE` when extraction matches. If OCR extraction is incomplete or uncertain, the result should be `REVIEW_REQUIRED` instead.

## Upload and OCR behaviour

- Maximum upload: 10 MB.
- Maximum PDF pages: 10.
- Accepted formats: PDF, PNG, JPEG/JPG.
- Uploaded file bytes are processed in memory and are not persisted as documents.
- Only the structured extraction result is retained for 24 hours; expired result rows are cleaned during upload/result requests.
- The multipart file field is `document` (the alias `file` is accepted for convenience).
- `source_type` is `text_pdf`, `scanned_pdf`, `mixed_pdf`, or `image`.
- OCR confidence uses Tesseract token scores as a proxy; no confidence is invented for native PDF text.

## Run tests

```bash
python -m pytest -q
```

Some legacy tests in this repository refer to sibling directories from the original source ZIPs. If a test import fails because of a missing external sibling, see the test output; the integrated tests under `tests/integration/` exercise the new API and extraction flows.

## Demo run order

1. `python scripts/seed_demo.py`
2. `python app.py`
3. Open `http://127.0.0.1:5000/` to use the original demo UI.
4. Log in to the React frontend using the API endpoint if its login is wired to the backend.
5. Register a certificate or use seeded `CC001`.
6. Upload `CC001_original.pdf` and confirm `GENUINE`.
7. Upload `CC001_modified.pdf` and confirm `TAMPERED` (or `REVIEW_REQUIRED` if extraction is uncertain).
8. Upload `CERT-A1_scanned.pdf` to demonstrate OCR on an image-only PDF.
9. Open the university verification-history page in the frontend, or query `/api/v1/verification/history` with the bearer token.
10. Revoke a certificate with a reason and re-verify it to see `REVOKED`.

## Antigravity low-token audit prompt

> Audit ChainCert backend only; do not modify the frontend or rewrite Modules 1–4. Verify the Flask `/api/v1` routes, auth/role and institution boundaries, certificate registration, Module 5 statuses, PDF/image extraction and OCR, upload limits/retention, audit history, revocation, persistence, and existing/new tests. Run tests and use real code evidence. Report PASS/FAIL/NOT IMPLEMENTED with file/line references and minimal fixes. Never claim OCR proves authenticity or that the local chain is a public blockchain. Finish with exact demo run commands and remaining blockers.

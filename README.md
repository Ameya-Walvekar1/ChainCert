# ChainCert

ChainCert is a certificate issuance, verification, and tamper-evidence platform built with Python, Flask, SQLite, and a React/Vite frontend. It demonstrates end-to-end certificate handling, cryptographic hashing, Merkle proofs, chain validation, document ingestion, and verification workflows.

This project is designed for local development, demos, and academic or prototype use cases where issuers, institutions, students, and public verifiers need a trustworthy evidence trail for certificates.

## Features

- Certificate registration and lifecycle management
- Hash-based certificate integrity checks
- Merkle tree and proof generation
- Tamper detection and audit visibility
- Persistent chain validation with generated blocks
- Access control and role-based authentication
- Upload-based verification for PDF, PNG, JPG, and JPEG documents
- OCR-assisted extraction and review workflow
- Flask backend + React frontend integration

## Tech Stack

- Backend: Python 3.10+, Flask
- Frontend: React 19, Vite, TypeScript
- Data storage: SQLite and JSON state files
- Verification: canonicalization, hashing, Merkle proofs, chain linkage
- OCR: Tesseract

## Repository Structure

```text
EDIL1/
├── app.py                     # Flask application entry point
├── chaincert/                 # Core backend modules
├── data/                      # SQLite and chain state files
├── frontend/                  # React + Vite frontend source
├── templates/                 # Flask-rendered pages
├── static/                    # Static assets
├── tests/                     # Backend tests
├── scripts/                   # Demo seeding and utility scripts
├── demo_documents/            # Sample certificates and documents
├── test_certificates/         # Test certificate fixtures
├── requirements.txt           # Python dependencies
├── README.md                  # Project overview
├── README_DEMO_BACKEND.md     # API and demo backend documentation
├── DEMO_RUNBOOK.md            # Live demonstration guide
├── IMPLEMENTATION_REPORT.md   # Project implementation notes
├── PROJECT_AUDIT.md           # Audit and assessment notes
├── END_TO_END_AUDIT.md        # End-to-end verification notes
└── .env.example               # Example environment configuration
```

## Prerequisites

Before running the app, install the following:

- Python 3.10 or newer
- pip
- Node.js 18+ and npm
- Tesseract OCR

### Install Tesseract

- Ubuntu/Debian:
  ```bash
  sudo apt-get update
  sudo apt-get install -y tesseract-ocr
  ```

- macOS:
  ```bash
  brew install tesseract
  ```

- Windows:
  - Install Tesseract via Chocolatey:
    ```powershell
    choco install tesseract -y
    ```
  - Or install from the official Tesseract Windows build and ensure it is added to PATH.

## Quick Start

From the repository root:

```bash
cd EDIL1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

Then open:

- Backend: http://127.0.0.1:5000/

### Windows (PowerShell)

```powershell
cd EDIL1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

Then open:

- Backend: http://127.0.0.1:5000/

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Frontend (React + Vite)

The project also includes a Vite frontend in `frontend/`.

### Install frontend dependencies

```bash
cd EDIL1/frontend
npm install
```

### Run frontend in development mode

```bash
npm run dev
```

Open the frontend at the URL shown by Vite, usually:

- http://localhost:5173/

### Production frontend build

```bash
npm run build
```

## Demo Accounts

On a fresh local setup, the application is intended to work with demo credentials such as:

- Platform admin: `demo.admin@chaincert.local` / `ChainCertDemo!2026`
- Institution admin: `issuer@chaincert.local` / `IssuerDemo!2026`

Use these only in a clean demo environment and verify the actual live database state before working with real operational data.

## Running Tests

```bash
cd EDIL1
python -m pytest -q
```

## Useful Files

- `README_DEMO_BACKEND.md` — backend endpoint and demo API documentation
- `DEMO_RUNBOOK.md` — live demo runbook and walkthrough
- `PROJECT_AUDIT.md` — audit overview and remediation notes
- `IMPLEMENTATION_REPORT.md` — implementation details and validation results
- `END_TO_END_AUDIT.md` — end-to-end app review

## Notes

- The project stores state in local SQLite and JSON files under `data/`.
- Do not expose the Flask development server publicly without additional security hardening.
- For a public deployment, move persistent storage to durable managed infrastructure and run the backend in a secure environment.

## License

This project is provided for educational and demonstration use. Add a license file if you intend to distribute it publicly under a formal open-source license.

## Contributing

Contributions are welcome. Please make sure to validate the backend and frontend after changes and keep the demo state and documentation aligned with the actual runtime environment.

# ChainCert

ChainCert is a certificate issuance, verification, and tamper-evidence application built with Python, Flask, SQLite, and a React/Vite frontend.

It includes the essential components needed to run the app locally:
- certificate registration and issuance
- verification and tamper detection
- Merkle tree proof logic
- audit and chain validation
- institution and student authentication
- frontend + backend integration

## Required project structure

```text
EDIL1/
├── app.py
├── chaincert/
├── data/
├── frontend/
├── static/
├── templates/
├── .env.example
├── .gitignore
├── README.md
├── DEMO_RUNBOOK.md
├── requirements.txt
└── .git/
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- Tesseract OCR

### Install Tesseract

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

macOS:
```bash
brew install tesseract
```

Windows:
```powershell
choco install tesseract -y
```

## Backend setup

From the project root:

```bash
cd /home/ameya/ChainCert_Demo/EDIL1
python3 -m pip install -r requirements.txt
python3 app.py
```

Then open:
- http://127.0.0.1:5000/

## Frontend setup

```bash
cd /home/ameya/ChainCert_Demo/EDIL1/frontend
npm install
npm run dev
```

Then open the frontend URL shown by Vite, usually:
- http://localhost:5173/

## Working login credentials

Institution login:
- Email: `institute@chaincert.local`
- Password: `Institute12345`

Student login:
- Email: `student@chaincert.local`
- Password: `Student123456`

These credentials were verified against the app’s actual authentication service.

## Notes

- The backend must be running before the frontend can fetch the API data.
- The app uses local SQLite files inside `data/`.
- `DEMO_RUNBOOK.md` contains the user flow and demo steps for the project.

## Important

This repository is intentionally kept minimal and includes only the essential files needed to run the app correctly.

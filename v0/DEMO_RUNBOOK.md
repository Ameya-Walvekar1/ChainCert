# ChainCert Live Demo Runbook

This runbook is based on the actual code in this repository as it exists today. It is intentionally practical and presenter-ready, but it is also honest about what is implemented and what is only simulated.

Important:
- The operational registry is intentionally kept empty for the live app. Do not run `scripts/seed_demo.py` as part of a normal live demo.
- Do not clear or overwrite the live databases or `data/chain.json` just to make a presentation work.
- If you need a fictional demo certificate, create it live through the real institution UI/API after logging in with a valid account.
- If a feature is incomplete or simulated, this runbook labels it clearly rather than claiming it works.

## 1. Project reality check before starting

This repository contains:
- a Flask backend in `app.py`
- a real JSON API under `/api/v1`
- a React/Vite frontend in `frontend/`
- SQLite persistence for certificates and access control
- a local persisted chain in `data/chain.json`
- Merkle proof generation and verification logic in `chaincert/merkle/`
- verification and revocation logic in `chaincert/verification/engine.py`

From the current code:
- the backend starts on `0.0.0.0:5000` by default
- the frontend uses Vite and runs on `http://127.0.0.1:5173` by default
- the frontend API base URL defaults to `/api/v1` and can be overridden via `VITE_API_BASE_URL`
- the credentials model includes these roles: `PLATFORM_ADMIN`, `INSTITUTION_ADMIN`, `ISSUER`, `STUDENT`, `PUBLIC_VERIFIER`
- the actual protected certificate routes require bearer-token auth
- the institution route `/certificates` accepts a JSON object under `certificate`

Do not assume any particular demo user exists unless you have confirmed the actual database state in the current environment.

## 2. Prerequisites and working directory

Use the repository root as the working directory:

```bash
cd /home/ameya/ChainCert_Demo/EDIL1
```

Required:
- Python 3
- a virtual environment
- dependencies from `requirements.txt`
- Tesseract OCR (`tesseract-ocr`) if you want document-upload verification demos

Create and activate the environment:

```bash
cd /home/ameya/ChainCert_Demo/EDIL1
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If OCR is needed for upload verification demos:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

If `node_modules` is missing in `frontend/`, install only then:

```bash
cd /home/ameya/ChainCert_Demo/EDIL1/frontend
npm install
```

Do not run `npm install` unless dependencies are missing. The project’s package scripts are already defined and `npm run build` is known to work.

## 3. Start the backend

The backend is the Flask app in `app.py` and binds to port 5000 by default:

```bash
cd /home/ameya/ChainCert_Demo/EDIL1
source .venv/bin/activate
python app.py
```

Observation:
- the actual backend entrypoint is `if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=os.environ.get("FLASK_DEBUG", "0") == "1")`
- if a port is already in use, either stop the previous process or launch with a different port:

```bash
export PORT=5001
python app.py
```

Check backend health:

```bash
curl http://127.0.0.1:5000/api/v1/health
```

Expected response shape:

```json
{"success": true, "service": "ChainCert API", "api_version": "v1"}
```

If the backend fails:
- check terminal output for import errors, permission issues, or missing package installation
- confirm the environment is active
- confirm `requirements.txt` installed cleanly
- check `python -c "import flask; print(flask.__version__)"`

## 4. Start the frontend

Run the frontend in a second terminal:

```bash
cd /home/ameya/ChainCert_Demo/EDIL1/frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

The default Vite frontend URL is:
- `http://127.0.0.1:5173`

To confirm the frontend is running:
- open the browser to `http://127.0.0.1:5173`
- verify the landing page loads
- check the DevTools Console for JS errors

If port 5173 is occupied:

```bash
npm run dev -- --host 0.0.0.0 --port 4173
```

Then open `http://127.0.0.1:4173`.

## 5. Safe demo-data and database prep

This is the critical rule for the demo:
- the operational registry should remain empty and truthful
- do not run `python scripts/seed_demo.py`
- do not clear or overwrite the live `data/chain.json` or SQLite DBs just to create a demo
- do not silently insert demo credentials into the operational registry without being explicit

What to check before the demo:

```bash
cd /home/ameya/ChainCert_Demo/EDIL1
ls -l data
ls -l chaincert
```

Then inspect the live DBs only as a read-only check:

```bash
sqlite3 data/chaincert.db '.schema'
sqlite3 data/chaincert.db "SELECT certificate_id, student_name, status FROM certificates ORDER BY id DESC LIMIT 20;"
```

If you want to show a fictional certificate without touching production data, create one live through a proper institution log-in flow using a new unique ID and a fictional student. That keeps the demonstration truthful and does not rely on seeded fake records.

This repo’s `scripts/seed_demo.py` docs mention demo accounts for a fresh local setup, but the runbook deliberately does not rely on them because the objective is to keep the current operational registry empty.

## 6. Login and roles

The real login is implemented in the Flask API and the frontend calls it through `frontend/src/services/authService.ts`.

### Actual roles and permissions
From `chaincert/auth/models.py` and `chaincert/auth/policy.py`:
- `PLATFORM_ADMIN`
- `INSTITUTION_ADMIN`
- `ISSUER`
- `STUDENT`
- `PUBLIC_VERIFIER`

Permissions include:
- `PUBLIC_VERIFY`
- `ISSUE_CERTIFICATE`
- `CORRECT_CERTIFICATE`
- `BATCH_ADMINISTRATION`
- `REVOKE_CERTIFICATE`
- `MANAGE_INSTITUTION_USERS`
- `MANAGE_INSTITUTIONS`
- `CHANGE_ROLES`

The app route layer enforces auth using bearer tokens and checks `Permission.ISSUE_CERTIFICATE` and `Permission.REVOKE_CERTIFICATE`.

### UI routes
The actual frontend routes are defined in `frontend/src/routes/AppRoutes.tsx`:
- public landing page: `/`
- public verification page: `/verify`
- verification result page: `/verify/result`
- institution login: `/institution/login`
- institution dashboard: `/institution/dashboard`
- institution certificates: `/institution/certificates`
- bulk issuance page: `/institution/bulk-issuance`
- institution verification: `/institution/verification`
- institution audit: `/institution/audit`
- student login: `/student/login`
- student credentials: `/student/credentials`
- student credential detail: `/student/credentials/:id`

### Login forms and actual behavior
- Institution login form: `frontend/src/pages/auth/InstitutionLoginPage.tsx`
- Student login form: `frontend/src/pages/auth/StudentLoginPage.tsx`
- Both call `authService.loginInstitution(...)` and `authService.loginStudent(...)`
- The API endpoint is `POST /api/v1/auth/login`

The frontend stores the user and token in `localStorage` under `chaincert_auth_user`.

### Confirmed login flow
Use a browser form or a curl request:

```bash
curl -s http://127.0.0.1:5000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"<known-valid-email>","password":"<known-valid-password>"}'
```

The successful response includes:
- `access_token`
- `token_type`
- `user` (id, email, display_name, role, institution_id)

If the backend rejects credentials:
- confirm the user exists in the access DB
- confirm the institution and role are valid
- confirm the password is correct
- do not try to reset anything destructively in the live environment without a clear procedure

### Student-specific behavior
The API includes:
- `GET /students/me`
- `GET /students/me/certificates`
- `GET /students/me/certificates/<certificate_id>`

But in `student_certificates()` the app filters by `student_name` matching the student’s `display_name` exactly after case-folding. This is an important limitation.

In practice:
- a student can only see a certificate if the certificate record’s `student_name` matches the authenticated student display name
- if a record was issued under a different name or the student account was created with a different display name, the student will not see it
- the UI should show the correct empty state when the record is not associated with the current student

## 7. Main demo: institution issues a real certificate

This is the proof-based demo path.

Use one clearly fictional example throughout the live presentation. Example:
- `certificate_id`: `DEMO-CC-2026-ALICE-001`
- `student_name`: `Alice Example`
- `roll_number`: `DEMO-ROLL-ALICE-001`
- `course`: `Bachelor of Technology in Artificial Intelligence`
- `cgpa`: `9.80`
- `issue_date`: `2026-08-20`
- `institution_id`: use the institution name tied to the authenticated institution, for example `WESTMINSTER` or the exact value from the real institution setup

### 7.1 Actual institution form fields
The frontend page `frontend/src/pages/institution/CertificatesPage.tsx` creates a form with fields like:
- `id`
- `studentName`
- `studentRoll`
- `studentEmail`
- `course`
- `degreeType`
- `institution`
- `institutionId`
- `issueDate`
- `batch`
- `grade`
- `cgpa`

However, the real API payload includes only the canonical backend fields passed by the service:
- `certificate_id`
- `student_name`
- `roll_number`
- `course`
- `cgpa`
- `issue_date`
- `institution_id`

The service layer `frontend/src/services/credentialService.ts` does this exact payload mapping.

### 7.2 How to issue from the UI
1. Launch the frontend and log in as an institution user.
2. Navigate to `/institution/dashboard`.
3. Click `Register Certificate`.
4. Fill in a new fictional certificate record.
5. Submit the form.
6. The UI should show a success toast and refresh the list.

Expected visible outcome:
- the certificate appears in the institution certificate list
- the page updates with the newly created record
- there is no fake/mock fallback; the request goes through the real service layer and backend API

### 7.3 How to confirm it persisted
Use a read-only backend query:

```bash
curl -s -H "Authorization: Bearer <token>" \
  http://127.0.0.1:5000/api/v1/certificates/DEMO-CC-2026-ALICE-001
```

Expected result:
- `200 OK`
- JSON document containing the certificate record

Direct DB check (read only):

```bash
sqlite3 data/chaincert.db "SELECT certificate_id, student_name, batch_id, merkle_root, status FROM certificates WHERE certificate_id='DEMO-CC-2026-ALICE-001';"
```

### 7.4 What the backend actually does during issuance
The real issuance lifecycle is implemented in `chaincert/records/database.py`:
- `add_certificate()` validates and stores the record
- `issue_certificate()` creates a single-leaf Merkle tree
- `assign_batch_and_proofs()` stores the Merkle root and proof
- `chain.add_batch()` adds the block to the local persisted chain
- `update_batch_block_id()` marks the batch as `CHAINED`

This is the actual lifecycle to explain to a nontechnical audience:
- a record is created
- its fields are hashed with the canonical hash function
- a single-certificate batch is created
- the Merkle root is calculated
- a proof is generated and stored
- the batch is linked into the local chain
- the record is persisted in the registry

This is real code, but it is still local application data, not a public blockchain.

### 7.5 If the issue fails
Common causes:
- missing or invalid auth token
- institution mismatch
- duplicate certificate ID
- bad field values
- backend failed to create the chain block

The API returns JSON errors with `400` or `403` in those cases. The code catches `CertificateValidationError` and notably rolls back the certificate creation when chain creation fails.

## 8. Student demonstration

### 8.1 Student login
Open `http://127.0.0.1:5173/student/login`.

Login with a real student account that exists in the access-control DB, or create one through an authorized admin path if your environment already supports it.

A real student login flow is implemented in `frontend/src/pages/auth/StudentLoginPage.tsx` and the backend `/api/v1/auth/login` endpoint.

### 8.2 Student access page
Navigate to `/student/credentials`.

The student page loads records through `credentialService.getAll()` and displays credential cards.

### 8.3 Real ownership model
The actual backend route `GET /students/me/certificates` filters by comparing:
- `record['student_name']`
- to the authenticated user's `display_name`

This means:
- the certificate must be issued under the student’s name exactly in the registry
- if the student name or display name does not match, the certificate will not appear
- if no record matches, the empty state is shown rather than invented records

### 8.4 Student detail view
The student detail route is `frontend/src/pages/student/StudentCredentialDetailsPage.tsx`.

It can display a certificate detail page and a public verification link such as:

```text
http://127.0.0.1:5173/verify?id=DEMO-CC-2026-ALICE-001
```

Do not claim that every institution-issued certificate automatically appears in every student account. The app only exposes a record when the matching data model is satisfied.

## 9. Public verification demo

The public verification flow exists in the frontend and in the backend API.

### 9.1 Frontend public verification pages
- `http://127.0.0.1:5173/verify`
- `http://127.0.0.1:5173/verify/result?id=<CERT_ID>`

The frontend uses `verificationService.verifyById()` and `verificationService.verifyUploadedFile()` from `frontend/src/services/verificationService.ts`.

### 9.2 Backend verification routes
The backend defines actual API routes in `chaincert/api/routes.py`:
- `POST /api/v1/verify`
- `POST /api/v1/verification/verify`
- `POST /api/v1/verification/verify-upload`

The actual verification statuses are in `chaincert/verification/models.py` and are handled in `VerificationEngine.verify()`:
- `GENUINE`
- `TAMPERED`
- `REVOKED`
- `NOT_FOUND`
- `REVIEW_REQUIRED`

### 9.3 Identifier lookup verification
Example:

```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/verify \
  -H 'Content-Type: application/json' \
  -d '{"certificate_id":"DEMO-CC-2026-ALICE-001"}'
```

Expected result (after issue):
- `status: GENUINE`
- `explanation` tells the user the record matches the trusted DB record

### 9.4 Unknown document or unknown ID
Example:

```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/verify \
  -H 'Content-Type: application/json' \
  -d '{"certificate_id":"NO-SUCH-CERT"}'
```

Expected result:
- `status: NOT_FOUND`

### 9.5 Upload verification
The actual upload API uses multipart data and expects a field named `document` or `file`.

Supported upload formats from `chaincert/ingestion/extractor.py`:
- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`

Upload limits:
- maximum `10 MB`
- maximum `10` PDF pages

Example:

```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/verification/verify-upload \
  -F 'document=@/path/to/cert.pdf'
```

This endpoint extracts candidate fields and verifies them against the trusted record if one exists.

### 9.6 What to say during the demo
A truthful presenter script is:
- “This system checks the certificate against the institution’s trusted registry.”
- “It verifies the submitted fields against the stored hash.”
- “If the fields differ, the status is `TAMPERED`.”
- “If the record is not in the registry, it is `NOT_FOUND`.”
- “If extraction is incomplete or ambiguous, it is `REVIEW_REQUIRED`.”
- “If the institution revoked it, it is `REVOKED`.”

Do not say anything stronger than that. This project does not claim public or external blockchain provenance.

## 10. Tampering demonstration

A tampering demo is valid only if you do it in a controlled way and never alter live registry data.

### Safe method
1. Issue a real fictional certificate.
2. Copy the certificate fields from the issued record into a local JSON or text file.
3. Change a single field, like `cgpa` from `9.80` to `9.99`.
4. Submit the modified payload or upload a modified copy of the certificate.
5. Query the verification endpoint.

Example payload:

```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/verify \
  -H 'Content-Type: application/json' \
  -d '{"certificate_id":"DEMO-CC-2026-ALICE-001","student_name":"Alice Example","roll_number":"DEMO-ROLL-ALICE-001","course":"Bachelor of Technology in Artificial Intelligence","cgpa":"9.99","issue_date":"2026-08-20","institution_id":"<REAL_INSTITUTION_NAME>"}'
```

Expected result:
- `status: TAMPERED`
- field mismatch is detected by comparing the submitted hash to the trusted stored hash

Important:
- do not edit the registry record itself
- do not modify `data/chain.json` manually
- do not replace a valid record with a modified one in the DB

### If upload-based tampering is unreliable
The project supports document upload verification, but OCR extraction can produce `REVIEW_REQUIRED` if the document is incomplete, uncertain, or ambiguous. In those cases, do not force a tampering demonstration; instead, use the identifier-based verification with a modified JSON payload, which is a cleaner and more deterministic proof.

## 11. Revocation demo

Revocation is implemented in the API and is protected by `Permission.REVOKE_CERTIFICATE`.

### Real API route
`POST /api/v1/certificates/<certificate_id>/revoke`

Authorization:
- valid institution admin or platform admin token required

Body:

```json
{"reason": "Academic integrity review"}
```

Example:

```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/certificates/DEMO-CC-2026-ALICE-001/revoke \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"reason":"Academic integrity review"}'
```

Expected response:
- `200 OK`
- message says the certificate was revoked

Then verify again:

```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/verify \
  -H 'Content-Type: application/json' \
  -d '{"certificate_id":"DEMO-CC-2026-ALICE-001"}'
```

Expected result:
- `status: REVOKED`

Important:
- revocation is real in the database state
- a revoked certificate is not reported as genuine
- the app does not claim revocation changes the public blockchain state; it changes the trusted registry record status within this local application

## 12. Chain, Merkle proof, and audit demonstrations

### Real features that are genuinely implemented
1. Single-certificate issuance creates a Merkle root and proof.
2. `VerificationEngine.verify()` checks proof availability and includes `merkle_proof_valid` and `chain_valid` fields when the trusted record has proof data.
3. `Chain.validate_chain()` checks each block’s hash and `previous_root` linkage.
4. `GET /api/v1/verification/history` lists verification attempts.
5. `GET /api/v1/audit` returns access/verification audit events.
6. The certificate registry includes metadata like `batch_id`, `merkle_root`, and `merkle_proof`.

### What is not genuinely implemented as a backend feature
The frontend `Audit & Integrity` screen contains a simulated “Run Integrity Check” flow. The service `frontend/src/services/auditService.ts` does this:
- calls `GET /api/v1/health`
- returns a static `ALL_INTACT` result with a static Merkle root and count

This is a UI simulation, not a real chain audit endpoint. The real backend does not expose a dedicated `POST /api/v1/integrity/check` route.

### Honest way to explain the chain in front of an audience
Say:
- “This project maintains a local, tamper-evident chain of certificate batches in JSON, not a public blockchain.”
- “Each batch has a Merkle root; the chain validates previous-root linkage and the stored hash of each block.”
- “The verification layer checks those proofs where they exist.”
- “The UI shows the integrity concept visually, but the actual security model is local application integrity, not external consensus.”

## 13. API verification commands (copy-paste ready)

### Health check
```bash
curl http://127.0.0.1:5000/api/v1/health
```

### Login
```bash
curl -s http://127.0.0.1:5000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"<valid-email>","password":"<valid-password>"}'
```

### List certificates (institution only)
```bash
curl -s http://127.0.0.1:5000/api/v1/certificates \
  -H 'Authorization: Bearer <token>'
```

### Fetch one certificate
```bash
curl -s http://127.0.0.1:5000/api/v1/certificates/DEMO-CC-2026-ALICE-001 \
  -H 'Authorization: Bearer <token>'
```

### Register a certificate
```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/certificates \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "certificate": {
      "certificate_id": "DEMO-CC-2026-ALICE-001",
      "student_name": "Alice Example",
      "roll_number": "DEMO-ROLL-ALICE-001",
      "course": "Bachelor of Technology in Artificial Intelligence",
      "cgpa": "9.80",
      "issue_date": "2026-08-20",
      "institution_id": "<institution-name>"
    }
  }'
```

### Verify by ID
```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/verify \
  -H 'Content-Type: application/json' \
  -d '{"certificate_id":"DEMO-CC-2026-ALICE-001"}'
```

### Verify uploaded document
```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/verification/verify-upload \
  -F 'document=@/path/to/certificate.pdf'
```

### Revoke a certificate
```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/certificates/DEMO-CC-2026-ALICE-001/revoke \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"reason":"Academic integrity review"}'
```

### Verification history
```bash
curl -s http://127.0.0.1:5000/api/v1/verification/history?limit=20 \
  -H 'Authorization: Bearer <token>'
```

### Audit log
```bash
curl -s http://127.0.0.1:5000/api/v1/audit?limit=20 \
  -H 'Authorization: Bearer <token>'
```

## 14. Expected demo checklist

Use this checklist during the live presentation:

- [ ] Backend is running on `http://127.0.0.1:5000`
- [ ] Frontend is running on `http://127.0.0.1:5173`
- [ ] `/api/v1/health` returns success
- [ ] Institution login works for a valid account
- [ ] Institution certificate registration works for a fictional record
- [ ] The issued certificate is visible and retrievable from the API
- [ ] The certificate appears in the institution certificate list
- [ ] A student account can view the record only when the names match the actual model
- [ ] Public verification by certificate ID returns `GENUINE`
- [ ] A modified copy of the certificate returns `TAMPERED`
- [ ] An unknown ID returns `NOT_FOUND`
- [ ] A revoked record returns `REVOKED`
- [ ] An incomplete or uncertain upload can return `REVIEW_REQUIRED`
- [ ] The chain/Merkle metadata is attached to the record
- [ ] Any audit/history page is read-only and uses the live backend data or the documented front-end simulation

If any item fails, do not panic; follow the troubleshooting steps below.

## 15. Troubleshooting

### Backend fails to start
Symptoms:
- `ModuleNotFoundError`
- port already in use
- Flask errors in terminal

Fix:
```bash
cd /home/ameya/ChainCert_Demo/EDIL1
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Check if Tesseract is missing for document upload flows:
```bash
which tesseract
```

### Frontend fails to start
Fix:
```bash
cd /home/ameya/ChainCert_Demo/EDIL1/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

If nothing appears, check the terminal for Vite errors and the browser console for runtime errors.

### Port already occupied
Use a different port:

```bash
export PORT=5001
python app.py
```

or

```bash
npm run dev -- --host 0.0.0.0 --port 4173
```

### Login rejected
Possible causes:
- wrong email/password
- account missing or inactive
- role mismatch
- institution mismatch

Check via backend database or actual known account setup only. Do not create or reset the live registry simply to fix a login issue.

### API 401 or 403
- make sure Authorization header is present
- make sure the token is valid
- make sure the institution/account matches the route permission
- verify the current user role

### Certificate creation fails
Common causes:
- duplicate `certificate_id`
- wrong institution name or institution mismatch
- validation error from missing required fields
- chain batch failure

Use a unique fictional ID and ensure all required fields are present.

### Certificate issues but is not retrievable
Check:
```bash
curl -s -H "Authorization: Bearer <token>" http://127.0.0.1:5000/api/v1/certificates
```

Then inspect the record in SQLite:

```bash
sqlite3 data/chaincert.db "SELECT * FROM certificates WHERE certificate_id='<id>';"
```

### Student cannot see a certificate
This is often a naming mismatch. The student page filters by `student_name` matching `display_name`.

Fix by checking:
- the certificate was issued under the same student name
- the student account itself exists
- the student is logged in as the correct user

### Upload rejected
The extractor only accepts:
- PDF
- PNG
- JPG
- JPEG

Maximum upload is 10 MB and 10 pages for PDFs.

### Verification result is unexpectedly `REVIEW_REQUIRED`
This is normal when:
- OCR was incomplete or ambiguous
- required fields were missing from the document
- the date or CGPA could not be resolved cleanly

This is an intentional safety mechanism and not a false “failure” claim.

### Chain/proof validation fails
This can happen if:
- the chain file was manually edited
- a database record was tampered with
- the record has no proof data

Do not fix it manually in the live registry. If a failure occurs in a demo, treat it as a demonstration of integrity checks, not as a reason to reset the app.

### Browser cannot reach backend
Check:
- backend is actually running
- correct port is used
- CORS is allowed for local origin if needed
- DevTools Network tab shows API failure

## 16. Presentation script: 5-minute version

“Good morning. This is ChainCert, a local certificate registry and verification system. We’ll start by launching the backend and frontend, then log in as an institution user. We’ll issue a fictional certificate with a unique ID, show that it persists in the registry, and then verify it publicly using the certificate ID. Next, we’ll modify a field in a copied version and show that the system identifies it as tampered. We’ll then revoke the record and show that verification returns `REVOKED`. Finally, we’ll explain the Merkle root and local chain integrity model, while being careful to note that this is a local application chain, not an external public blockchain.”

## 17. Presentation script: full demo version

1. Show backend health endpoint.
2. Start frontend and show landing page.
3. Log in as an institution user.
4. Navigate to the certificates page.
5. Create a fictional certificate with a unique ID.
6. Show the success toast and record.
7. Query the backend by ID and show the returned JSON record.
8. Open the public verification page and verify the ID.
9. Create a modified copy and show a `TAMPERED` result.
10. Revoke the same certificate and show `REVOKED`.
11. Open the verification history or audit route and explain the recorded events.
12. Explain the local chain and Merkle root concept without overstating security claims.
13. Close by saying precisely what is implemented and what remains only a local application integrity model.

## 18. Questions an evaluator may ask

### Q1: Is this blockchain?
A: Not in the public/distributed sense. The project uses a local persisted Chain with block linkage, Merkle roots, and tamper-evidence checks. It is a local application integrity model, not an external blockchain consensus system.

### Q2: How do you prevent fake certificates?
A: The system compares submitted fields against the trusted registry record using canonical hashing and optionally checks Merkle proof and chain validity. It does not guarantee external trust beyond this local registry model.

### Q3: Why does the student page sometimes show no certificate?
A: Because the student access check is based on the matching `student_name` to the authenticated user’s display name. If the data does not match exactly, access is denied by design.

## 19. Known limitations to disclose honestly

- This is not a public blockchain and does not claim external consensus or decentralization.
- The frontend audit “integrity check” is partly simulated.
- Bulk issuance remains intentionally unavailable because there is no backend bulk-issuance endpoint.
- The student visibility model depends on matching names and institution ownership.
- OCR is a candidate-text extraction process and does not prove authenticity.
- The operational registry should remain empty; demo data should be created live and explicitly identified as fictional.

## 20. Final pre-demo checklist

- [ ] Backend started in the repo root with the active virtual environment
- [ ] Frontend started in `frontend/`
- [ ] `/api/v1/health` returns success
- [ ] Authenticated institution user exists and works
- [ ] Use a fictional certificate ID unique to this demo
- [ ] Never run `scripts/seed_demo.py` in this live environment
- [ ] Do not clean or overwrite `data/chain.json` or SQLite DBs
- [ ] Verify by ID works
- [ ] Tampering check works on a modified copy, not the real registry record
- [ ] Revocation check works and is explained honestly
- [ ] You are prepared to state the local-chain limitation clearly

## 21. Final note

This runbook is intentionally grounded in the code, not in assumptions. The live demo should be truthful, concise, and explicit about the technology being demonstrated. If you need a final fallback, use the real API-backed flow that issues, verifies, and revokes a single certificate, and explain each step as a local registry integrity check rather than a broad claim about a decentralized blockchain.

### Confirmed live accounts in this workspace
The current live access database contains these users:
- `demo.admin@chaincert.local` — role `PLATFORM_ADMIN` — confirmed usable login path in this environment
- `issuer@chaincert.local` — role `INSTITUTION_ADMIN` — confirmed usable login path in this environment
- `student@mmcoe.local` — role `STUDENT` — account exists, but no confirmed usable password was verified from the codebase or live DB; do not guess or invent a password during the demo

This means the runbook should not describe a student demo as already-ready unless the presenter has a verified student password from the environment or a freshly created student account with a confirmed password.

### Startup shell note
The command sequence is valid when run from the repository root, but this shell environment showed a startup issue caused by an external shell startup script (`/home/ameya/pico_ws/install/setup.bash`) not found in the active shell. If the shell fails before the app starts, bypass the shell init issue by running from the repo root and invoking the venv Python directly:

```bash
cd /home/ameya/ChainCert_Demo/EDIL1
/home/ameya/ChainCert_Demo/EDIL1/.venv/bin/python app.py
```

This avoids the failing shell bootstrap and still uses the project’s active virtual environment.

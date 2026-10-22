# End-to-End Audit of the Live ChainCert Application

## Scope and constraints
- Audit performed without mutating the live operational SQLite data or chain state.
- Focused on actual runtime behavior of the live Flask backend, auth DB, certificate registry DB, and frontend API integration.
- Evidence was collected from the running application code and live database state in `/home/ameya/ChainCert_Demo/EDIL1`.

## Executive summary
The project is not in a fake demo state at runtime anymore, but it is also not yet in a populated production state. The live backend is structurally valid and the auth stack is working, but the active operational registry is empty and there is no confirmed live issuance event in the current persisted data.

The strongest evidence from the current runtime state is:
- `data/access_control.db` contains only a real institutional auth model and a live student record: `student@mmcoe.local` with role `STUDENT` and institution `MMCOE`.
- `data/chaincert.db` has zero certificate rows, zero batch rows, and zero verification rows.
- `data/chain.json` is an empty list.
- The runtime verification API for an unknown ID returns `NOT_FOUND`, which is the correct result when the registry is empty.
- The live student login succeeds and returns a valid token, a real student profile, and an empty certificate list.

This means the app is currently in a truthful “empty registry / real auth” state rather than a populated certificate registry. That is a safer baseline than the earlier demo stage, but it also means certificate issuance, revocation, chain linkage, and batch integrity cannot be validated against real live records until a real institution admin issues records into the registry.

## Evidence from the live app state

### 1. Auth database state
Live query result from `data/access_control.db`:
- `institutions`: 1 row (`MMCOE`)
- `users`: 3 rows
  - `demo.admin@chaincert.local` — `PLATFORM_ADMIN`
  - `issuer@chaincert.local` — `INSTITUTION_ADMIN`
  - `student@mmcoe.local` — `STUDENT`

This confirms the app has a real auth model and a valid student record in the active auth database.

### 2. Registry database state
Live query result from `data/chaincert.db`:
- `batches`: 0
- `certificates`: 0
- `verification_attempts`: 0
- `users`: 0
- `audit_log`: 12

This means there are no persisted certificate records and no live issuance batch in the current application state.

### 3. Chain state
`data/chain.json` currently contains:
- `[]`

This is consistent with an empty chain and confirms there are no chain-linked certificate batches to check.

### 4. Student login and self-access endpoints
Real runtime validation using the Flask test client:
- `POST /api/v1/auth/login` with `student@mmcoe.local` and `StudentPass!2026` returned HTTP 200 and a valid bearer token.
- `GET /api/v1/auth/me` with that token returned HTTP 200 and a valid `STUDENT` user payload.
- `GET /api/v1/students/me/certificates` returned HTTP 200 with `count: 0` and an empty list.
- The response is correct for an empty registry and confirms the student route is active and safe.

### 5. Unknown certificate verification behavior
Runtime verification of an unknown ID:
- `POST /api/v1/verify` with `certificate_id = CC-9999-00000-FAKE`
- Result: HTTP 200, status `NOT_FOUND`
- Explanation: `No trusted certificate record was found for this ID.`

This is the expected result in an empty registry and confirms the verification engine is not fabricating a false certificate match.

## Workflow-by-workflow verdict

### A. Authentication and session validation
Status: Pass (for the live student account that exists in the DB)

Evidence:
- Student login successfully returned a token.
- `authenticate()` successfully returned the user object from the session token.
- `GET /api/v1/auth/me` succeeded on the same token.

Observations:
- The auth model is legitimate and functioning.
- The code path is protected by bearer tokens and session validation in `chaincert/auth/service.py`.
- No destructive changes were made to the auth layer during this audit.

### B. Student-scoped authorization
Status: Pass in principle; empty state prevents deeper live cross-user testing

Evidence:
- The route `/api/v1/students/me/certificates` existed and returned `success: true` with empty results for the logged-in student.
- The route enforces a `STUDENT` role and compares the record’s `student_name` to the authenticated user’s `display_name` before allowing detail access.

Limitations:
- There is only one real student in the current auth DB, so actual cross-student isolation testing is limited until more student accounts or records exist.

### C. Issuance persistence and registry writes
Status: Not validated against a live certificate record in the current operational state

Evidence:
- No certificate rows are present in `data/chaincert.db`.
- No batch rows are present in `batches`.
- The issue flow exists in the API (`POST /api/v1/certificates`), but there was no confirmed live institution-issued certificate to record during this audit.

This is not a code failure; it is a current empty-registry state. Without an actual institution admin issuance to the registry, we cannot truthfully verify live issuance persistence or chain linkage.

### D. Hashing, canonicalization, Merkle proofs, and chain linkage
Status: Code-level validated by the project test suite, but not live-data validated in the current empty registry

Evidence from the repository:
- `tests/test_hashing.py`
- `tests/test_proof.py`
- `tests/test_tree.py`
- `tests/test_chain.py`
- `tests/test_chain_validation.py`
- `tests/test_m1_m2_m3_m4_integration.py`

These tests exercise:
- canonical hash generation,
- Merkle root construction,
- proof generation and verification,
- chain batch linkage,
- tamper detection.

However, those are deterministic unit/integration tests without a populated live database. They do not prove the current operational DB contains real live chain data.

### E. Revocation
Status: Not validated against a live persistent certificate in the current app state

Evidence:
- The revoke endpoint exists in `chaincert/api/routes.py` and the DB schema contains `revocation_reason`, `revoked_at`, and `status='REVOKED'` logic.
- The engine also writes to verification history.

But the current `data/chaincert.db` is empty, so there is no live certificate subject to revocation in the active app right now.

### F. Public verification and upload verification
Status: Functionally implemented; current live run is empty registry, so only `NOT_FOUND` is expected

Evidence:
- `verify` routes exist and are wired to the verification engine.
- Upload verification and document extraction routes are present.
- Unknown ID verification returned `NOT_FOUND` rather than fabricated success.

This is the correct behavior for the present empty-state registry.

### G. Frontend runtime behavior
Status: Mostly fixed, but there are still stale demo placeholders in some UI fallback strings

Evidence:
- There are no current imports of `frontend/src/services/mockData.ts` in the active app tree.
- The service layer is now using live API responses rather than direct mock datasets for certificate and auth data.
- However, some components still contain fallback demo strings such as:
  - `currentUser?.name || 'Ananya Patil'`
  - `currentUser?.studentId || 'STU-2024-89042'`
  - `Westminster State University` in the student profile card

These strings are not active data sources in the current runtime if the app loads real user data, but they remain as passive placeholders and should be treated as stale demo copy until replaced with neutral and data-driven text.

### H. Bulk issuance and batch workflows
Status: Not implemented by the backend API and not live-tested

Evidence from `frontend/src/services/credentialService.ts`:
- `processBulkIssuance` throws: `Bulk issuance is not implemented by the backend API.`
- `BulkIssuancePage.tsx` is a static page with hardcoded records and progression UI, not connected to a real batch-creation backend.

This is a confirmed functional gap in the current application. It is not a hidden issue; it is explicitly represented as a placeholder.

## Confirmed issues and priorities

### High priority
1. The app currently has no live cert registry state. The system is truthful and empty, but it does not yet provide operational certificate issuance data for end users.
2. Bulk issuance is not implemented at the API layer and is represented only as a UI placeholder.
3. The live authorization state is real, but it is minimal and not yet backed by active institution certificate issuance records.

### Medium priority
1. Some fallback UI text still contains stale demo identities and names even in the cleaned app. These are not current data sources but remain misleading placeholders.
2. `frontend/src/services/mockData.ts` still exists in the repo and contains the old Westminster/Ananya dataset. It is not active in the current app, but it remains a potential source of confusion and should be isolated or removed in a future cleanup if this project is meant to remain demo-free.

### Low priority / cosmetic
1. Some static institutional labels and wording still reflect a Westminster demo environment rather than generalizable live institution naming. This is not a functional blocker, but it can still confuse users if left in place.

## Final assessment
The application is now in a safer and more truthful state than before:
- it no longer invents certificate records,
- it no longer presents fake verification history as truth,
- it uses a real auth database with a valid student account,
- and its verification engine correctly returns `NOT_FOUND` for an absent registry record.

However, this is still a partially operational system rather than a fully populated certificate registry. The remaining gaps are not hidden corruptions; they are either:
- actual empty live state,
- absent backend support for bulk issuance,
- or stale placeholder copy in the UI.

The app is ready for honest, real-world operations only after a real institution admin issues genuine records into the registry. Until then, the observed runtime behavior is correct for an empty certificate ledger, not a populated chain.

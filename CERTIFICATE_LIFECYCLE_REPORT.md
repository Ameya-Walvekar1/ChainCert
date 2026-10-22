# Certificate Lifecycle Validation Report

## Scope
This report documents the real single-certificate issuance lifecycle as implemented and validated in the ChainCert backend and institution frontend. It focuses on the actual operational behavior of the API, the database isolation model, the Merkle proof semantics, and the end-to-end verification/revocation workflow.

## Executive summary
The single-certificate lifecycle is working end to end under isolated test conditions:
- a certificate can be issued through the real API,
- the record is persisted to the active certificate database,
- a batch/chain linkage is created,
- a Merkle root and proof are generated and verified,
- the record can be retrieved and verified,
- tampering changes the verification status to `TAMPERED`,
- the record can be revoked and then appears as `REVOKED`,
- unauthorized users are blocked,
- rollback behavior works when chain creation fails.

The key property is that automated validation does not touch the operational registry or the live `data/chain.json` file. Tests use temporary SQLite databases and temporary JSON chain paths created under `tmp_path`.

## Verified commands and output

### 1) Full backend suite
Command run:
```bash
cd /home/ameya/ChainCert_Demo/EDIL1 && export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 && . .venv/bin/activate && python -m pytest -q
```

Result:
```text
126 passed in 3.67s
```

### 2) Targeted lifecycle and related backend checks
Command run:
```bash
cd /home/ameya/ChainCert_Demo/EDIL1 && export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 && . .venv/bin/activate && python -m pytest -q tests/test_certificate_lifecycle_api.py tests/test_module1.py tests/test_m1_m2_m3_m4_integration.py tests/test_ingestion_api.py
```

Result:
```text
17 passed in 2.82s
```

### 3) Frontend production build
Command run:
```bash
cd /home/ameya/ChainCert_Demo/EDIL1/frontend && ls && cat package.json && echo '---' && npm run build
```

Result:
```text
✓ built in 720ms
```

## Actual behavior checked

### Issue flow
The `POST /api/v1/certificates` endpoint is implemented to:
- validate the caller using the active auth service,
- enforce institution ownership and role boundaries,
- resolve the correct certificate database through the application service registry,
- create the certificate record,
- create the batch / Merkle root / proof path,
- attach the batch to the chain,
- return the created certificate record.

The validation tests confirm a certificate like `LIFECYCLE-001` is stored and retrieved successfully.

### Retrieval flow
`GET /api/v1/certificates/<certificate_id>` returns the live record when it exists and enforces institution boundary checks for non-admin users.

### Verification flow
The backend `verify` endpoints correctly distinguish:
- `GENUINE` when a trusted registry record exists and the record stays consistent,
- `TAMPERED` when the submitted certificate fields differ from the stored record,
- `REVOKED` when the certificate has been revoked,
- `NOT_FOUND` when no record exists,
- `REVIEW_REQUIRED` when extraction/fields are incomplete or uncertain.

A tampered certificate is not reported as valid: the API returns `TAMPERED` for the examined scenario.

### Revocation flow
A valid institution admin can revoke a certificate using the revoke endpoint and the record status changes to `REVOKED`.

### Authorization and ownership checks
The API checks both:
- the caller’s role and permissions,
- the institution to which the caller belongs.

This prevents a student user from issuing a certificate and prevents cross-institution access beyond the allowed boundary.

### Duplicate handling and failure rollback
The API rejects duplicate issuance through the normal invalid registration path and reports failure cleanly when chain creation fails. The rollback test confirms the record was not persisted in that failure case.

## Merkle semantics
The project correctly handles the single-leaf case:
- a single-leaf tree may have an empty proof,
- that proof is still valid when the leaf hash equals the root,
- verification still confirms the fold result against the expected root.

This was validated through `verify_merkle_proof(...)` using the real certificate hash and real proof data.

## Test isolation and live-data safety
The lifecycle tests explicitly use isolated temp resources:
- `tmp_path / "certificates.db"`
- `tmp_path / "access.db"`
- `tmp_path / "ingestion.db"`
- `tmp_path / "chain.json"`

This means the automated tests do not write to the active operational SQLite database or to the live `data/chain.json` registry file. The app uses the runtime service configuration to keep the active app and the isolated test environment separate.

## Key files inspected and used
- `chaincert/api/routes.py`
- `tests/test_certificate_lifecycle_api.py`
- `frontend/src/services/credentialService.ts`
- `frontend/src/pages/institution/CertificatesPage.tsx`

These files confirm the real API route behavior, isolated tests, and frontend-to-backend registration path.

## Files changed or relevant to the final fix
The validated implementation and final state are associated with:
- `chaincert/api/routes.py`
- `tests/test_certificate_lifecycle_api.py`
- `frontend/src/services/credentialService.ts`
- `frontend/src/pages/institution/CertificatesPage.tsx`

The backend runtime wiring also relies on the active app service registry in `app.py` and the real certificate issuance flow in the record and chain layers.

## Truthful limitations
- This project does not implement a distributed public blockchain; it is a local persisted chain with integrity checks and validation routines.
- Bulk issuance remains intentionally unavailable because the backend API does not expose a real bulk-issuance endpoint.
- The frontend demonstrates truthful loading/success/error state handling, but it does not claim functionality that the backend does not provide.

## Conclusion
The implementation is verified as operating correctly for the real single-certificate lifecycle under isolated conditions. The project remains honest about its trust model and does not claim stronger guarantees than the code actually provides.

# ChainCert Project Audit

## Scope
This audit reviewed the operational backend, authentication model, persistent SQLite databases, and frontend state used by the live application in `/home/ameya/ChainCert_Demo/EDIL1`.

## Executive Summary
The application already included a functional authentication and authorization layer backed by SQLite and Argon2 password hashing. The primary issue was not a missing auth framework but a mismatch between the real backend and the live operational data:

- The real access-control database only contained platform admin and institution admin users.
- No legitimate `STUDENT` user existed in the active operational database.
- The application UI contained hardcoded demo identities and fake educational details such as `Ananya Patil` and `STU-2024-89042`.
- The backend could auto-seed demo records in certain code paths, which contradicted the expected real application state.
- The active data layer still held synthetic verification attempts, empty certificate records, and historical fake registry claims that were never grounded in live records.

These conditions caused the app to present a fabricated operational reality even though the backend itself was largely sound.

## Findings

### 1. Auth and authorization model
The core auth stack is implemented in:
- `chaincert/auth/service.py`
- `chaincert/auth/storage.py`
- `chaincert/auth/models.py`
- `chaincert/auth/passwords.py`

It uses:
- SQLite-backed user/session storage
- Argon2 password hashes
- role-based authorization using `Role` and `Permission`
- bearer-token sessions with session validation and logout support

This system was legitimate and functional for real use.

### 2. Live database state
The actual live databases were inspected before modifying data:
- `data/access_control.db` contained only demo admin records.
- `data/chaincert.db` contained no real certificate records and only synthetic verification history rows.
- `data/chain.json` was effectively blank.

This meant the app was effectively running with a demo/admin bootstrap state rather than a truthful operational state.

### 3. Fake frontend state
The frontend had several hardcoded demo states and direct mock assumptions, including:
- `frontend/src/services/mockData.ts`
- `frontend/src/pages/student/StudentCredentialsPage.tsx`
- `frontend/src/components/student/StudentHeader.tsx`
- `frontend/src/components/institution/InstitutionHeader.tsx`
- `frontend/src/pages/institution/InstitutionDashboardPage.tsx`

These files assumed a Westminster/Ananya demo environment instead of reflecting the real database state.

### 4. API and access control gaps
The backend had begun adding student-scoped access routes but the live user data did not include a legitimate student identity or available certificate records. This meant the real auth flow existed but was not populated with actual active student credentials.

### 5. Integrity/data hygiene issues
The app still preserved fabricated verification history and integrity claims, which should never appear as operational truth when the certificate registry is empty. The backend and frontend now treat the registry as empty until real records are added.

## Remediation Applied
- Backed up the live databases before destructive cleanup.
- Removed autoseeding logic from the main app entry so it no longer silently creates sample certificates.
- Added/strengthened student-bound API access for self-scoped record access.
- Provisioned a real student account in the access-control database.
- Cleared synthetic verification rows, certificate rows, and batch rows from the live operational database.
- Reset the chain state to an empty registry state.
- Removed hardcoded demo identity values and fake institutional metrics from the live frontend UI.

## Current Truthful State
The live application is now aligned with the actual backend state:
- the registry is empty until real certificates are inserted,
- there is a real student account for authorization testing,
- the UI no longer claims fabricated integrity or enrollment facts,
- the application remains functional and testable without fake operational data.

## Validation
The relevant project checks were run as part of the remediation:
- Backend API tests passed under the project virtual environment with third-party ROS plugin autoload disabled.
- The frontend production build passed successfully.

## Notes
This project is a demonstration platform with real authentication primitives, but the runtime data should not present fabricated institutional or student records. The live state must remain explicit, empty, or actual rather than simulated.

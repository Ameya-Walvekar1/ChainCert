# ChainCert Frontend

ChainCert is an academic credential verification platform. This repository contains the complete frontend application built with **React 19**, **TypeScript**, **Vite**, and **Tailwind CSS**.

---

## 🚀 Quick Start (Running the App)

### Prerequisites
- **Node.js** (v18.0.0 or higher recommended)
- **npm** (comes with Node.js)

### 1. Install Dependencies
Run this command from inside the `chaincert_frontend` folder:
```bash
npm install
```

### 2. Start the Development Server
```bash
npm run dev
```

The application will start on:
👉 **`http://localhost:5173`**

### 3. Build for Production (Optional)
To verify or compile the production bundle:
```bash
npm run build
```

---

## 📦 What to Send / Exclude When Sharing

When zipping or sharing this folder with a teammate, **exclude**:
- ❌ `node_modules/` (Very large! Teammate can generate this using `npm install`)
- ❌ `dist/` (Build output)
- ❌ `.env.local` / `.env` (Personal configurations)

### ✅ What to include:
- `src/` (All source code, components, services, and pages)
- `public/` (Public assets)
- `index.html`
- `package.json` & `package-lock.json`
- `vite.config.ts`, `tsconfig*.json`
- `tailwind.config.js`, `postcss.config.js`
- `.env.example`
- `README.md`

---

## 🔌 Backend Integration Guide

The frontend is architected using a clean **Service Layer Pattern** located in `src/services/`. The UI components do **not** have hardcoded mock data embedded in them—they communicate exclusively through asynchronous service functions that return TypeScript-typed promises.

### 1. Configuring Backend URL

1. Copy `.env.example` to `.env.local` (or `.env`):
   ```bash
   cp .env.example .env.local
   ```
2. Set your backend URL:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

*Tip (Alternative to CORS):* You can also uncomment the `proxy` block inside `vite.config.ts` to automatically route `/api` calls to your backend port (e.g. `http://localhost:8000`).

---

### 2. Service Layer Files

All network operations are organized into 4 modular service files in `src/services/`:

| Service File | Responsibilities | Current State |
| :--- | :--- | :--- |
| `src/services/authService.ts` | Institution login, Student login, session management | Stores session in `localStorage` |
| `src/services/credentialService.ts` | List all credentials, fetch by ID, register new, update status, bulk issuance | Stored in `localStorage` with mock delay |
| `src/services/verificationService.ts` | Certificate ID lookup, file drag-and-drop hash verification, QR verification | Evaluates genuine/tampered/revoked/not-found states |
| `src/services/auditService.ts` | System audit logs, verification request history, Merkle integrity check | Stored in `localStorage` |

To connect to your backend, simply replace the local storage logic inside these methods with HTTP calls using `apiRequest()` (from `src/services/apiConfig.ts`) or `fetch`/`axios`.

---

### 3. Expected Backend Endpoints & Data Contracts

All data models and enums are defined in **`src/types/index.ts`**. Below is the REST endpoint contract expected by the frontend:

#### A. Authentication (`authService.ts`)
- **`POST /api/auth/institution/login`**
  - **Body:** `{ email: string, password: string }`
  - **Response:** `User` object (e.g., `{ id, name, email, role: 'institution', institutionId, institutionName }`)
- **`POST /api/auth/student/login`**
  - **Body:** `{ identifier: string, password: string }`
  - **Response:** `User` object (e.g., `{ id, name, email, role: 'student', studentId }`)

#### B. Credential Management (`credentialService.ts`)
- **`GET /api/credentials`**
  - **Response:** `Credential[]` (list of registered credentials)
- **`GET /api/credentials/:id`**
  - **Response:** `Credential` object
- **`POST /api/credentials`**
  - **Body:** `Omit<Credential, 'status' | 'sha256Hash' | 'merkleRoot' | 'qrCodeUrl'>`
  - **Response:** `Credential` (with computed cryptographic hash & status `'ACTIVE'`)
- **`PATCH /api/credentials/:id`**
  - **Body:** `Partial<Credential>` (e.g., `{ status: 'REVOKED', revocationReason: '...' }`)
  - **Response:** Updated `Credential`
- **`POST /api/credentials/bulk`**
  - **Body:** `BulkIssuanceBatch`
  - **Response:** Processed `BulkIssuanceBatch`

#### C. Verification (`verificationService.ts`)
- **`GET /api/verify/:id`**
  - **Response:** `VerificationResult` containing:
    - `state`: `'GENUINE' | 'TAMPERED' | 'REVIEW_REQUIRED' | 'NOT_FOUND' | 'REVOKED'`
    - `certificateId`: string
    - `credential`: `Credential` (if found)
    - `checks`: Array of `{ name, passed, message, details }`
    - `issuerVerification`: `{ institutionName, accreditationStatus, registryId, pkiKeyFingerprint }`
    - `integrityProof`: `{ sha256, merkleRoot, batchId, leafIndex }`
- **`POST /api/verify/upload`**
  - **Body:** `FormData` containing the certificate file (`file: File`)
  - **Response:** `VerificationResult`

#### D. Audit & Integrity (`auditService.ts`)
- **`GET /api/audit/events`**
  - **Response:** `AuditEvent[]`
- **`GET /api/audit/verification-history`**
  - **Response:** `VerificationHistoryItem[]`
- **`POST /api/audit/integrity-check`**
  - **Response:** `{ status: 'ALL_INTACT', verifiedCount: number, merkleRoot: string, timestamp: string, executionTimeMs: number }`

---

## 🧭 Page Routes & Navigation Flow

| Route | Page | Description |
| :--- | :--- | :--- |
| `/` | Landing Page | Hero section, features, role selection, public verification input |
| `/verify` | Public Verification | Dual-mode verification: Certificate ID lookup or Document Upload (drag & drop) |
| `/verify/result` | Verification Result | Deep result inspection showing all 5 verification states, cryptographic proofs, issuer details |
| `/institution/login` | Institution Sign-in | University / issuer administrative authentication |
| `/student/login` | Student Sign-in | Student credential portal login |
| `/institution/dashboard` | Issuer Dashboard | Real-time stats, quick actions, recent issuance table, verification health |
| `/institution/certificates` | Certificate Register | Search, filter, inspect, and revoke credentials |
| `/institution/bulk-issuance` | Bulk Issuance | 4-step wizard: Upload CSV/JSON, Validate records, Sign & Issue, Download report |
| `/institution/verification` | Verification Audit | Issuer verification log & request analysis |
| `/institution/audit` | Audit & Integrity | System audit trail, cryptographic integrity scanner, verification history |
| `/student/credentials` | Student Portal | Verified credentials grid & list, export, quick verify |
| `/student/credentials/:id`| Credential Detail | High-resolution verifiable certificate view with QR code, SHA-256 hash, and download options |

---

## 🛠️ Tech Stack & Libraries
- **React 19**
- **TypeScript**
- **Vite**
- **Tailwind CSS**
- **React Router v7**
- **Lucide Icons**

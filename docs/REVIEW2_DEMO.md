# ChainCert — Review 2 Examiner Demonstration Script

**Department:** Artificial Intelligence & Data Science  
**Institution:** MMCOE, Pune  
**Academic Year:** 2026–27  
**Module:** Review 2 Prototype Demonstration  

---

## Quick Launch Instructions

To launch the interactive Flask web dashboard:

```bash
cd EDIL1
python3 app.py
```

Open browser at: **`http://localhost:5000`** (or `http://127.0.0.1:5000`)

To run automated unit and integration test suites:

```bash
pytest tests/ -v
```

---

## Step-by-Step Examiner Viva Demonstration

### Step 1: System Overview & Architecture (Home Page)
1. Open `http://localhost:5000/`.
2. Point out the four **WORKING** module cards:
   - Module 1: Certificate & Record Management
   - Module 2: SHA-256 Hashing Engine
   - Module 3: Merkle Tree Builder
   - Module 4: Block Chaining
3. Highlight that Review 2 uses plain text `.txt` certificate input and that PDF/OCR are future scope (Modules 5–7).

---

### Step 2: Module 1 Demonstration — Registration & Ingestion
1. Navigate to **M1: Records** (`/module1`).
2. Click **"Load CC001"** or paste text from `test_certificates/certificate1.txt`:
   ```txt
   CERTIFICATE ID: CC001
   NAME: Rahul Sharma
   ROLL NUMBER: A101
   COURSE: AI & DS
   CGPA: 9.20
   ISSUE DATE: 2026-08-20
   INSTITUTION ID: MMCOE
   ```
3. Click **"REGISTER CERTIFICATE"**.
4. Show examiner:
   - Parsed field inspection table.
   - 64-character SHA-256 hash generated automatically by Module 2.
   - Record stored in SQLite database (`certificates` table).

---

### Step 3: Module 2 Demonstration — Deterministic SHA-256 & Tamper Test
1. Navigate to **M2: Hasher** (`/module2`).
2. Show the 4-step canonicalization pipeline: `Data` $\rightarrow$ `Canonicalization` $\rightarrow$ `SHA-256` $\rightarrow$ `64-Hex Hash`.
3. Select `CC001 — Rahul Sharma (CGPA: 9.20)`.
4. Set field to alter: `CGPA`, new value: `9.99`.
5. Click **"RUN MODULE 2 TAMPER TEST"**.
6. Show examiner:
   - Hash A (Original) vs Hash B (Tampered).
   - **Hash Changed: YES** $\rightarrow$ **PASS — CERTIFICATE ALTERATION DETECTED**.
   - Bitwise Avalanche Effect metrics: $\sim 50\%$ bit flip percentage and bitwise Hamming distance.

---

### Step 4: Module 3 Demonstration — Merkle Tree & Proof Verification
1. Navigate to **M3: Merkle** (`/module3`).
2. View batch `SEM1_2026` (4 certificates).
3. Show examiner:
   - Computed Merkle Root (single 64-character digest representing all 4 certificates).
   - Visual Merkle Tree Diagram displaying levels $0 \rightarrow 1 \rightarrow 2$ (Root).
   - Change batch to `ODD_BATCH_2026` (5 certificates) to demonstrate **odd-leaf promotion policy** (unpaired node promoted without duplication, avoiding CVE-2012-2459 vulnerability).
4. Select `CC001` under Proof Explorer and click **"GENERATE & VERIFY MERKLE PROOF"**.
5. Show examiner:
   - $O(\log N)$ proof path steps.
   - Result: **MERKLE PROOF: VALID (Membership Confirmed)**.

---

### Step 5: Module 4 Demonstration — Block Chaining & Linkage
1. Navigate to **M4: Blocks** (`/module4`).
2. Show examiner:
   - Block #1 (Genesis Block, `previous_root` = `None`).
   - Block #2 (`previous_root` = Block #1's `merkle_root`).
   - Block header SHA-256 digest over all fields.
   - Live **CHAIN STATUS: VALID** banner.
3. Click **"ADD BATCH BLOCK"** to append a new batch to the chain.

---

### Step 6: Empirical Tamper Suite
1. Navigate to **Tamper Test** (`/tamper-test`).
2. Click **"RUN CERTIFICATE TAMPER TEST"** $\rightarrow$ Demonstrates how 1 CGPA digit change propagates up the pipeline to invalidate Merkle root and proof.
3. Click **"RUN BLOCK TAMPER TEST"** $\rightarrow$ Forcibly corrupts `previous_root` in Block 2 copy and executes Module 4 `validate_chain()`, showing live **CHAIN STATUS: INVALID** with exact error traceback.

---

### Step 7: Automated End-to-End Complete Demo
1. Navigate to **Run Complete Demo** (`/demo`).
2. Click **"RUN COMPLETE DEMO"**.
3. Show examiner the 12-step timeline with green checkmarks (✓) executing live across M1 $\rightarrow$ M2 $\rightarrow$ M3 $\rightarrow$ M4.

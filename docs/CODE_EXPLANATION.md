# ChainCert — Comprehensive Code Explanation (Viva Reference)

**Department:** Artificial Intelligence & Data Science  
**Institution:** MMCOE, Pune  
**Academic Year:** 2026–27  

This document explains every major file, class, and function in simple, viva-friendly language.

---

## 1. Module 1 — Records & Certificate Management (`chaincert/records/`)

### FILE: `chaincert/records/parser.py`
**PURPOSE:** Parses plain text (`.txt`) certificate files into normalized python dictionaries matching Module 2's expected fields.

- **`parse_certificate_text(text_content)`**:
  - Reads line by line, splits by colon (`:`).
  - Maps key aliases (`STUDENT NAME`, `ROLL NO`, `INSTITUTION`) to canonical key names (`student_name`, `roll_number`, `institution_id`).
  - Invokes Module 2 `validate_certificate_data()` to validate required fields and types.

- **`parse_certificate_file(file_path)`**:
  - Utility helper to read file contents from disk and pass to `parse_certificate_text()`.

---

### FILE: `chaincert/records/database.py`
**PURPOSE:** Manages SQLite database persistence (`data/chaincert.db`).

- **`init_db(db_path)`**: Creates `certificates` and `batches` tables if they do not exist.
- **`add_certificate(cert_data, db_path)`**: Validates certificate data, inserts into SQLite, calls Module 2 `hash_certificate()` to generate SHA-256 fingerprint, and stores `certificate_hash` and `canonical_data`.
- **`get_certificate(certificate_id, db_path)`**: Fetches certificate record by ID and parses stored JSON Merkle proof.
- **`list_certificates(batch_id, db_path)`**: Retrieves list of certificates.
- **`update_certificate(certificate_id, updates, db_path)`**: Updates certificate attributes and automatically re-invokes Module 2 to update the hash.
- **`assign_batch_and_proofs(batch_id, merkle_root, proof_map, db_path)`**: Stores Merkle Root and JSON Merkle proofs for a batch.

---

## 2. Module 2 — SHA-256 Hashing Engine (`chaincert/hashing/`)

### FILE: `chaincert/hashing/canonicalizer.py`
**PURPOSE:** Converts structured certificate dictionaries into a single deterministic UTF-8 string.

- **`canonicalize_certificate(cert_input)`**: Processes fields in strict canonical order (`certificate_id`, `student_name`, `roll_number`, `course`, `cgpa`, `issue_date`, `institution_id`) and formats as pipe-delimited string `key1=val1|key2=val2...`.

---

### FILE: `chaincert/hashing/hasher.py`
**PURPOSE:** Generates 64-character SHA-256 hexadecimal digests.

- **`generate_sha256(canonical_data)`**: Encodes string to UTF-8 and computes `hashlib.sha256().hexdigest()`.
- **`hash_certificate(cert_input)`**: Full pipeline wrapper executing canonicalization followed by SHA-256 hashing.
- **`compare_hashes(hash_a, hash_b)`**: Case-insensitive string comparison for hash equality.

---

### FILE: `chaincert/hashing/avalanche.py`
**PURPOSE:** Calculates cryptographic Avalanche Effect metrics between two hashes.

- **`compute_avalanche_effect(hash_a, hash_b)`**: Converts hex hashes to binary bits, computes bitwise XOR ($\oplus$), and returns Hamming distance and bit flip percentage ($\approx 50\%$).

---

## 3. Module 3 — Merkle Tree Builder (`chaincert/merkle/`)

### FILE: `chaincert/merkle/tree.py`
**PURPOSE:** Builds binary Merkle tree from certificate leaf hashes.

- **`build_merkle_tree(leaf_hashes)`**: Takes list of 64-char hex leaf hashes, validates format, applies level-by-level reduction using `reduce_level()`, and returns `MerkleTree` object with `levels` and `merkle_root`.
- **`reduce_level(level)`**: Combines pairs of hashes using Module 2 SHA-256. If leaf count is odd, promotes the unpaired node unchanged to avoid duplicate-last collisions (CVE-2012-2459).

---

### FILE: `chaincert/merkle/proof.py`
**PURPOSE:** Generates and verifies $O(\log N)$ Merkle membership proofs.

- **`generate_proof_for_hash(tree, target_hash)`**: Traverses tree levels from leaf to root, recording sibling hash and position (`left`/`right`).
- **`verify_merkle_proof(leaf_hash, proof, expected_root)`**: Re-computes root by folding leaf hash upwards with sibling steps and compares against `expected_root`.

---

## 4. Module 4 — Block Chaining (`chaincert/chain/`)

### FILE: `chaincert/chain/chain.py`
**PURPOSE:** Manages an ordered chain of certificate batch blocks.

- **`Chain.add_batch(batch_id, merkle_root, certificate_count)`**: Creates a new block wrapping the Merkle root, automatically setting `previous_root` to the latest block's `merkle_root`.
- **`Chain.validate_chain()`**: Iterates through all blocks, checking:
  1. Root linkage: `block[i].previous_root == block[i-1].merkle_root`.
  2. Block header self-integrity: `recompute_hash() == stored block_hash`.
  Returns `ChainValidationResult(is_valid, errors)`.

"""Module 5 verification engine wired to ChainCert Modules 1–4.

Verification is based on trusted database records and the existing Module 2 hash
format. When a stored Merkle proof exists, it is checked with Module 3; the local
Module 4 chain is validated when the proof is available. This is not an external
blockchain anchor or consensus claim.
"""
from typing import Any
from chaincert.hashing import hash_certificate
from chaincert.hashing.validator import validate_certificate_data
from chaincert.hashing.exceptions import CertificateValidationError
from chaincert.merkle import verify_merkle_proof
from chaincert.chain import Chain
from .models import VerificationResult, VerificationStatus

FIELDS = ("certificate_id", "student_name", "roll_number", "course", "cgpa", "issue_date", "institution_id")

class VerificationEngine:
    def __init__(self, chain: Chain | None = None):
        self.chain = chain

    @staticmethod
    def _record_fields(record: dict[str, Any]) -> dict[str, Any]:
        return {key: record.get(key) for key in FIELDS}

    def verify(self, submitted: dict[str, Any], trusted_record: dict[str, Any] | None) -> VerificationResult:
        cid = submitted.get("certificate_id") if isinstance(submitted, dict) else None
        if not isinstance(submitted, dict) or not isinstance(cid, str) or not cid.strip():
            return VerificationResult(VerificationStatus.REVIEW_REQUIRED, None,
                "A certificate ID is required to verify the submitted fields.",
                {"input_valid": False, "reference_found": None}, [], integrity_details={})
        cid = cid.strip()
        if trusted_record is None:
            return VerificationResult(VerificationStatus.NOT_FOUND, cid,
                "No trusted certificate record was found for this ID.",
                {"input_valid": True, "reference_found": False}, [], integrity_details={})
        if str(trusted_record.get("status", "")).upper() == "REVOKED":
            return VerificationResult(VerificationStatus.REVOKED, cid,
                "This credential has been revoked by the issuing institution.",
                {"input_valid": True, "reference_found": True, "revoked": True}, [],
                trusted_fingerprint=trusted_record.get("certificate_hash"),
                integrity_details={"revocation_reason": trusted_record.get("revocation_reason")})
        missing = [f for f in FIELDS if submitted.get(f) is None or str(submitted.get(f)).strip() == ""]
        if missing:
            return VerificationResult(VerificationStatus.REVIEW_REQUIRED, cid,
                "One or more required fields could not be extracted reliably; manual review is required.",
                {"input_valid": False, "reference_found": True, "missing_fields": missing}, [],
                trusted_fingerprint=trusted_record.get("certificate_hash"), integrity_details={})
        try:
            submitted_hash = hash_certificate(self._record_fields(submitted)).certificate_hash
            trusted_hash_calc = hash_certificate(self._record_fields(trusted_record)).certificate_hash
        except (CertificateValidationError, ValueError, TypeError) as exc:
            return VerificationResult(VerificationStatus.REVIEW_REQUIRED, cid,
                f"The extracted fields could not be validated: {exc}",
                {"input_valid": False, "reference_found": True}, [],
                trusted_fingerprint=trusted_record.get("certificate_hash"), integrity_details={})
        trusted_hash_stored = trusted_record.get("certificate_hash")
        stored_record_consistent = bool(trusted_hash_stored and trusted_hash_calc == trusted_hash_stored)
        submitted_fields = self._record_fields(submitted)
        trusted_fields = self._record_fields(trusted_record)
        # Compare normalized fields using Module 2's own validation conventions
        # (e.g. 9.2 and 9.20 are equivalent CGPA representations).
        try:
            submitted_normalized, _ = validate_certificate_data(submitted_fields)
            trusted_normalized, _ = validate_certificate_data(trusted_fields)
            mismatches = sorted(f for f in FIELDS if str(submitted_normalized.get(f, "")) != str(trusted_normalized.get(f, "")))
        except Exception:
            mismatches = sorted(f for f in FIELDS if str(submitted_fields.get(f, "")).strip() != str(trusted_fields.get(f, "")).strip())
        hash_match = submitted_hash == trusted_hash_stored
        details: dict[str, Any] = {
            "stored_record_hash_consistent": stored_record_consistent,
            "merkle_proof_available": bool(trusted_record.get("merkle_proof") and trusted_record.get("merkle_root")),
            "merkle_proof_valid": None,
            "chain_valid": None,
            "chain_errors": [],
            "evidence_note": "Local application evidence only; no external blockchain anchoring is asserted."
        }
        proof_available = details["merkle_proof_available"]
        if proof_available:
            try:
                proof = trusted_record.get("merkle_proof_parsed") or trusted_record.get("merkle_proof")
                if isinstance(proof, str):
                    import json
                    proof = json.loads(proof)
                details["merkle_proof_valid"] = bool(verify_merkle_proof(trusted_hash_stored, proof, trusted_record["merkle_root"]))
                if self.chain is not None:
                    chain_result = self.chain.validate_chain()
                    batch_blocks = [b for b in self.chain.blocks if b.batch_id == trusted_record.get("batch_id")]
                    batch_root_matches = any(b.merkle_root == trusted_record.get("merkle_root") for b in batch_blocks)
                    details["batch_block_found"] = bool(batch_blocks)
                    details["batch_root_matches_block"] = bool(batch_root_matches) if batch_blocks else None
                    details["chain_valid"] = bool(chain_result.is_valid and batch_root_matches)
                    details["chain_errors"] = list(chain_result.errors)
                    if not batch_blocks:
                        details["chain_errors"].append("No chain block was found for the certificate batch.")
                    elif not batch_root_matches:
                        details["chain_errors"].append("Certificate Merkle root does not match its batch block.")
            except Exception as exc:
                details["merkle_proof_valid"] = False
                details["integrity_error"] = str(exc)
        checks = {
            "input_valid": True,
            "reference_found": True,
            "fields_match": not mismatches,
            "submitted_hash_matches_trusted_hash": hash_match,
            "stored_record_hash_consistent": stored_record_consistent,
            "merkle_proof_valid": details["merkle_proof_valid"],
            "chain_valid": details["chain_valid"],
        }
        if not stored_record_consistent:
            status = VerificationStatus.REVIEW_REQUIRED
            explanation = "The trusted record does not match its stored fingerprint. The institution must inspect the registry integrity."
        elif mismatches or not hash_match:
            status = VerificationStatus.TAMPERED
            explanation = "The submitted certificate fields differ from the trusted registered record."
        elif details["merkle_proof_valid"] is False or details["chain_valid"] is False:
            status = VerificationStatus.REVIEW_REQUIRED
            explanation = "The certificate fields match, but available batch integrity evidence failed validation."
        else:
            status = VerificationStatus.GENUINE
            explanation = "The submitted fields match the trusted certificate record and its stored SHA-256 fingerprint."
            if not proof_available:
                explanation += " No stored Merkle proof was available for this record."
        return VerificationResult(status, cid, explanation, checks, mismatches, submitted_hash,
                                 trusted_hash_stored, details)

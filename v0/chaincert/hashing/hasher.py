"""
Cryptographic Hashing Engine (SHA-256) for ChainCert.
Provides the authoritative single-source hashing interface for the complete system.
"""

import hashlib
import re
from typing import Dict, Any, Union
from chaincert.hashing.canonicalizer import canonicalize_certificate
from chaincert.hashing.models import HashResult, CertificateRecord, HASH_ALGORITHM, HASH_SPEC_VERSION
from chaincert.hashing.exceptions import HashingError


HEX_64_REGEX = re.compile(r'^[a-fA-F0-9]{64}$')


def generate_sha256(canonical_data: str) -> str:
    """
    Generate SHA-256 cryptographic fingerprint from canonical UTF-8 string.

    Args:
        canonical_data (str): Canonicalized string representation of certificate.

    Returns:
        str: 64-character hexadecimal SHA-256 digest.
    """
    if not isinstance(canonical_data, str):
        raise HashingError(f"Canonical data must be string, got {type(canonical_data).__name__}.")
    if not canonical_data:
        raise HashingError("Canonical data cannot be empty.")

    try:
        utf8_bytes = canonical_data.encode("utf-8")
        sha256_hash = hashlib.sha256(utf8_bytes).hexdigest()
        return sha256_hash.lower()
    except Exception as e:
        raise HashingError(f"SHA-256 calculation failed: {str(e)}") from e


def hash_certificate(cert_input: Union[Dict[str, Any], CertificateRecord]) -> HashResult:
    """
    Full Module 2 Pipeline: Certificate Input -> Canonicalization -> SHA-256 -> HashResult.

    Args:
        cert_input: Dict or CertificateRecord containing certificate fields.

    Returns:
        HashResult: Structured hash output contract containing canonical string and SHA-256 hash.
    """
    canonical_str = canonicalize_certificate(cert_input)
    cert_hash = generate_sha256(canonical_str)

    return HashResult(
        canonical_data=canonical_str,
        certificate_hash=cert_hash,
        hash_algorithm=HASH_ALGORITHM,
        canonicalization_version=HASH_SPEC_VERSION,
    )


def compare_hashes(hash_a: str, hash_b: str) -> bool:
    """
    Compare two certificate SHA-256 hashes.

    Args:
        hash_a (str): First 64-char hexadecimal hash string.
        hash_b (str): Second 64-char hexadecimal hash string.

    Returns:
        bool: True if hashes match exactly, False otherwise.
    """
    if not isinstance(hash_a, str) or not isinstance(hash_b, str):
        return False

    clean_a = hash_a.strip().lower()
    clean_b = hash_b.strip().lower()

    if not HEX_64_REGEX.match(clean_a) or not HEX_64_REGEX.match(clean_b):
        return False

    return clean_a == clean_b

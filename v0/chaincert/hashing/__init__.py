"""
ChainCert Module 2: Hashing Engine Package Exports.
"""

from chaincert.hashing.models import CertificateRecord, HashResult, HASH_ALGORITHM, HASH_SPEC_VERSION, CANONICAL_FIELD_ORDER
from chaincert.hashing.validator import validate_certificate_data, validate_cgpa, parse_and_validate_date
from chaincert.hashing.canonicalizer import canonicalize_certificate, normalize_whitespace, normalize_cgpa
from chaincert.hashing.hasher import generate_sha256, hash_certificate, compare_hashes
from chaincert.hashing.avalanche import compute_avalanche_effect, format_avalanche_report
from chaincert.hashing.exceptions import (
    ChainCertError,
    CertificateValidationError,
    CanonicalizationError,
    HashingError,
)

__all__ = [
    "CertificateRecord",
    "HashResult",
    "HASH_ALGORITHM",
    "HASH_SPEC_VERSION",
    "CANONICAL_FIELD_ORDER",
    "validate_certificate_data",
    "validate_cgpa",
    "parse_and_validate_date",
    "canonicalize_certificate",
    "normalize_whitespace",
    "normalize_cgpa",
    "generate_sha256",
    "hash_certificate",
    "compare_hashes",
    "compute_avalanche_effect",
    "format_avalanche_report",
    "ChainCertError",
    "CertificateValidationError",
    "CanonicalizationError",
    "HashingError",
]

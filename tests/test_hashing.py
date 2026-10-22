"""
Unit tests for Cryptographic Hashing Engine (TC01, TC12).
"""

import pytest
from chaincert.hashing import (
    hash_certificate,
    generate_sha256,
    compare_hashes,
    CertificateValidationError,
    CanonicalizationError,
)


@pytest.fixture
def base_certificate():
    return {
        "certificate_id": "CC001",
        "student_name": "Rahul Sharma",
        "roll_number": "A101",
        "course": "AI & DS",
        "cgpa": "9.20",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    }


def test_tc01_hashing_determinism(base_certificate):
    """TC01: Executing hash_certificate 100 times on the same input yields identical SHA-256 digests."""
    initial_hash = hash_certificate(base_certificate).certificate_hash

    assert len(initial_hash) == 64
    assert all(c in "0123456789abcdef" for c in initial_hash)

    for _ in range(100):
        current_hash = hash_certificate(base_certificate).certificate_hash
        assert current_hash == initial_hash


def test_tc12_missing_and_malformed_fields(base_certificate):
    """TC12: Missing fields, invalid dates, out-of-range CGPA raise CertificateValidationError."""
    # 1. Missing field
    incomplete_cert = base_certificate.copy()
    del incomplete_cert["student_name"]
    with pytest.raises(CertificateValidationError) as exc1:
        hash_certificate(incomplete_cert)
    assert "Missing mandatory certificate fields" in str(exc1.value)

    # 2. Blank whitespace string
    blank_name_cert = base_certificate.copy()
    blank_name_cert["student_name"] = "   "
    with pytest.raises(CertificateValidationError) as exc2:
        hash_certificate(blank_name_cert)
    assert "cannot be empty or blank whitespace" in str(exc2.value)

    # 3. Invalid CGPA string
    invalid_cgpa_cert = base_certificate.copy()
    invalid_cgpa_cert["cgpa"] = "nine point two"
    with pytest.raises(CertificateValidationError) as exc3:
        hash_certificate(invalid_cgpa_cert)
    assert "Invalid CGPA value" in str(exc3.value)

    # 4. Out of range CGPA
    out_of_range_cgpa = base_certificate.copy()
    out_of_range_cgpa["cgpa"] = "11.5"
    with pytest.raises(CertificateValidationError) as exc4:
        hash_certificate(out_of_range_cgpa)
    assert "out of valid academic range" in str(exc4.value)

    # 5. Invalid date
    invalid_date_cert = base_certificate.copy()
    invalid_date_cert["issue_date"] = "2026-13-45"
    with pytest.raises(CertificateValidationError) as exc5:
        hash_certificate(invalid_date_cert)
    assert "Invalid or unsupported date format" in str(exc5.value)


def test_compare_hashes_utility():
    """Verify hash comparison helper behavior."""
    hash1 = "a3f1" + "0" * 60
    hash2 = "A3F1" + "0" * 60
    hash3 = "b3f1" + "0" * 60

    assert compare_hashes(hash1, hash2) is True
    assert compare_hashes(hash1, hash3) is False
    assert compare_hashes(hash1, "invalid_hash") is False

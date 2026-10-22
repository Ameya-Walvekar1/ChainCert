"""
Unit tests for Certificate Canonicalization (TC08, TC09, TC10, TC11).
"""

import pytest
from chaincert.hashing import canonicalize_certificate, hash_certificate


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


def test_tc08_whitespace_normalization(base_certificate):
    """TC08: Leading/trailing and internal whitespace normalization produces identical canonical representation & hash."""
    cert_raw = base_certificate.copy()
    cert_padded = {
        "certificate_id": " CC001 ",
        "student_name": "  Rahul   Sharma  ",
        "roll_number": " A101 ",
        "course": " AI & DS ",
        "cgpa": " 9.20 ",
        "issue_date": " 2026-08-20 ",
        "institution_id": " MMCOE ",
    }

    canon1 = canonicalize_certificate(cert_raw)
    canon2 = canonicalize_certificate(cert_padded)

    assert canon1 == canon2
    assert hash_certificate(cert_raw).certificate_hash == hash_certificate(cert_padded).certificate_hash


def test_tc09_date_format_normalization(base_certificate):
    """TC09: Equivalent date representations (20/08/2026 vs 2026-08-20) normalize to YYYY-MM-DD."""
    cert1 = base_certificate.copy()
    cert2 = base_certificate.copy()
    cert2["issue_date"] = "20/08/2026"

    cert3 = base_certificate.copy()
    cert3["issue_date"] = "August 20, 2026"

    canon1 = canonicalize_certificate(cert1)
    canon2 = canonicalize_certificate(cert2)
    canon3 = canonicalize_certificate(cert3)

    assert canon1 == canon2 == canon3
    assert "issue_date=2026-08-20" in canon1
    assert hash_certificate(cert1).certificate_hash == hash_certificate(cert2).certificate_hash == hash_certificate(cert3).certificate_hash


def test_tc10_cgpa_format_normalization(base_certificate):
    """TC10: Equivalent CGPA formats (9.2 vs 9.20 vs 9.200) normalize to 2 decimal places."""
    cert1 = base_certificate.copy()  # "9.20"
    cert2 = base_certificate.copy()
    cert2["cgpa"] = "9.2"
    cert3 = base_certificate.copy()
    cert3["cgpa"] = 9.2
    cert4 = base_certificate.copy()
    cert4["cgpa"] = "9.200"

    canon1 = canonicalize_certificate(cert1)
    canon2 = canonicalize_certificate(cert2)
    canon3 = canonicalize_certificate(cert3)
    canon4 = canonicalize_certificate(cert4)

    assert canon1 == canon2 == canon3 == canon4
    assert "cgpa=9.20" in canon1
    assert hash_certificate(cert1).certificate_hash == hash_certificate(cert2).certificate_hash


def test_tc11_field_ordering_independence(base_certificate):
    """TC11: Input dictionary key ordering does not affect canonical output or hash."""
    cert_ordered = {
        "certificate_id": "CC001",
        "student_name": "Rahul Sharma",
        "roll_number": "A101",
        "course": "AI & DS",
        "cgpa": "9.20",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    }

    cert_scrambled = {
        "institution_id": "MMCOE",
        "cgpa": "9.20",
        "course": "AI & DS",
        "student_name": "Rahul Sharma",
        "issue_date": "2026-08-20",
        "roll_number": "A101",
        "certificate_id": "CC001",
    }

    canon1 = canonicalize_certificate(cert_ordered)
    canon2 = canonicalize_certificate(cert_scrambled)

    expected_canonical_start = "certificate_id=CC001|student_name=Rahul Sharma|roll_number=A101"
    assert canon1.startswith(expected_canonical_start)
    assert canon1 == canon2
    assert hash_certificate(cert_ordered).certificate_hash == hash_certificate(cert_scrambled).certificate_hash

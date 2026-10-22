"""
Unit tests for Tamper Detection & Single-Character Alterations (TC02–TC07).
Validates that modifying any single field alters the generated SHA-256 certificate hash.
"""

import pytest
from chaincert.hashing import hash_certificate, compare_hashes


@pytest.fixture
def original_certificate():
    return {
        "certificate_id": "CC001",
        "student_name": "Rahul Sharma",
        "roll_number": "A101",
        "course": "AI & DS",
        "cgpa": "9.20",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    }


def test_tc02_student_name_single_char_tampering(original_certificate):
    """TC02: Single-character alteration in student_name must generate a completely different hash."""
    orig_hash = hash_certificate(original_certificate).certificate_hash

    tampered_cert = original_certificate.copy()
    tampered_cert["student_name"] = "Rahul SharmA"  # 'a' -> 'A'

    tampered_hash = hash_certificate(tampered_cert).certificate_hash

    assert orig_hash != tampered_hash
    assert compare_hashes(orig_hash, tampered_hash) is False


def test_tc03_roll_number_tampering(original_certificate):
    """TC03: Single-character alteration in roll_number must generate a different hash."""
    orig_hash = hash_certificate(original_certificate).certificate_hash

    tampered_cert = original_certificate.copy()
    tampered_cert["roll_number"] = "A102"

    tampered_hash = hash_certificate(tampered_cert).certificate_hash

    assert orig_hash != tampered_hash


def test_tc04_course_tampering(original_certificate):
    """TC04: Alteration in course field must generate a different hash."""
    orig_hash = hash_certificate(original_certificate).certificate_hash

    tampered_cert = original_certificate.copy()
    tampered_cert["course"] = "AI & ML"

    tampered_hash = hash_certificate(tampered_cert).certificate_hash

    assert orig_hash != tampered_hash


def test_tc05_cgpa_tampering(original_certificate):
    """TC05: Alteration in CGPA (9.20 -> 9.21) must generate a different hash."""
    orig_hash = hash_certificate(original_certificate).certificate_hash

    tampered_cert = original_certificate.copy()
    tampered_cert["cgpa"] = "9.21"

    tampered_hash = hash_certificate(tampered_cert).certificate_hash

    assert orig_hash != tampered_hash


def test_tc06_issue_date_tampering(original_certificate):
    """TC06: Single-day alteration in issue_date must generate a different hash."""
    orig_hash = hash_certificate(original_certificate).certificate_hash

    tampered_cert = original_certificate.copy()
    tampered_cert["issue_date"] = "2026-08-21"

    tampered_hash = hash_certificate(tampered_cert).certificate_hash

    assert orig_hash != tampered_hash


def test_tc07_institution_id_tampering(original_certificate):
    """TC07: Alteration in institution_id must generate a different hash."""
    orig_hash = hash_certificate(original_certificate).certificate_hash

    tampered_cert = original_certificate.copy()
    tampered_cert["institution_id"] = "COEP"

    tampered_hash = hash_certificate(tampered_cert).certificate_hash

    assert orig_hash != tampered_hash


def test_certificate_id_tampering(original_certificate):
    """Alteration in certificate_id must generate a different hash."""
    orig_hash = hash_certificate(original_certificate).certificate_hash

    tampered_cert = original_certificate.copy()
    tampered_cert["certificate_id"] = "CC002"

    tampered_hash = hash_certificate(tampered_cert).certificate_hash

    assert orig_hash != tampered_hash

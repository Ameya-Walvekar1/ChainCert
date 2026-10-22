"""
Sample certificate records for Module 3 demonstration and integration tests.

These records are FIXED, not randomly generated, so that the Merkle root shown
in a review demonstration is reproducible and can be checked against a slide.
Module 2 already ships a synthetic ``data_generator`` for bulk/benchmark work;
this file exists only to give Module 3 a small, stable, human-readable batch.

Placement note: this package sits at the repository root rather than at
``chaincert/utils/``. Module 2 already defines ``chaincert.utils``, and because
the two repositories are merged as a pkgutil namespace package, a second
``chaincert/utils`` in Module 3 would shadow Module 2's. Keeping these helpers
outside the ``chaincert`` namespace avoids that collision entirely.

Field names follow the master specification, Section 13.
"""

from typing import Any, Dict, List

#: A small batch of academic certificates in the canonical field set that
#: Module 2 expects. Four records, so the tree is a clean power of two.
SAMPLE_CERTIFICATES: List[Dict[str, Any]] = [
    {
        "certificate_id": "CC001",
        "student_name": "Rahul Sharma",
        "roll_number": "A101",
        "course": "AI & DS",
        "cgpa": "9.20",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    },
    {
        "certificate_id": "CC002",
        "student_name": "Priya Deshmukh",
        "roll_number": "A102",
        "course": "AI & DS",
        "cgpa": "8.75",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    },
    {
        "certificate_id": "CC003",
        "student_name": "Aditya Kulkarni",
        "roll_number": "A103",
        "course": "AI & DS",
        "cgpa": "9.05",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    },
    {
        "certificate_id": "CC004",
        "student_name": "Sneha Patil",
        "roll_number": "A104",
        "course": "AI & DS",
        "cgpa": "8.40",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    },
]

#: A five-record batch, used to exercise the odd-leaf promotion policy at more
#: than one level (5 -> 3 -> 2 -> 1).
SAMPLE_CERTIFICATES_ODD: List[Dict[str, Any]] = SAMPLE_CERTIFICATES + [
    {
        "certificate_id": "CC005",
        "student_name": "Omkar Joshi",
        "roll_number": "A105",
        "course": "AI & DS",
        "cgpa": "7.95",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    },
]


def get_sample_certificates(count: int = 4) -> List[Dict[str, Any]]:
    """Return ``count`` sample certificates as fresh copies.

    Copies are returned so that a caller tampering with a record for a
    demonstration cannot mutate the shared module-level fixtures.

    Raises:
        ValueError: If ``count`` is outside the available range.
    """
    available = len(SAMPLE_CERTIFICATES_ODD)

    if count < 1 or count > available:
        raise ValueError(
            f"count must be between 1 and {available}, got {count}."
        )

    return [dict(record) for record in SAMPLE_CERTIFICATES_ODD[:count]]


def tamper_certificate(
    certificate: Dict[str, Any],
    field: str = "cgpa",
    new_value: Any = "8.20",
) -> Dict[str, Any]:
    """Return a copy of a certificate with one field altered.

    Used to demonstrate that a single-field change propagates through Module 2's
    hash and therefore changes Module 3's Merkle root.

    Raises:
        KeyError: If ``field`` is not present on the record.
    """
    if field not in certificate:
        raise KeyError(
            f"Field {field!r} is not present on this certificate record."
        )

    tampered = dict(certificate)
    tampered[field] = new_value
    return tampered


__all__ = [
    "SAMPLE_CERTIFICATES",
    "SAMPLE_CERTIFICATES_ODD",
    "get_sample_certificates",
    "tamper_certificate",
]

"""
Unit tests for Avalanche Effect & Cryptographic Fingerprinting Metrics.
"""

import pytest
from chaincert.hashing import hash_certificate, compute_avalanche_effect


def test_avalanche_effect_metrics():
    """Verify that a 1-character input change causes a significant bitwise avalanche effect (~50% bit flips)."""
    cert1 = {
        "certificate_id": "CC001",
        "student_name": "Rahul Sharma",
        "roll_number": "A101",
        "course": "AI & DS",
        "cgpa": "9.20",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    }

    cert2 = cert1.copy()
    cert2["student_name"] = "Rahul SharmA"  # 1 character changed

    hash1 = hash_certificate(cert1).certificate_hash
    hash2 = hash_certificate(cert2).certificate_hash

    metrics = compute_avalanche_effect(hash1, hash2)

    assert metrics["total_bits"] == 256
    # SHA-256 theoretical avalanche effect averages ~128 flipped bits out of 256.
    # We assert that at least 90 bits flip (ratio > 35%).
    assert metrics["hamming_distance"] >= 90
    assert metrics["bit_flip_ratio_percent"] >= 35.0
    assert metrics["is_avalanche_significant"] is True

"""
Synthetic Certificate Generator for ChainCert.
Generates deterministic synthetic academic certificate records for Review 2 testing and benchmarking.
"""

import random
from typing import List, Dict, Any
from chaincert.hashing.models import CertificateRecord

COURSES = [
    "AI & DS",
    "Computer Engineering",
    "Information Technology",
    "Electronics & Telecommunication",
    "Mechanical Engineering",
]

FIRST_NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Rohan", "Ananya", "Vikram", "Pooja", "Aditya", "Neha"]
LAST_NAMES = ["Sharma", "Patil", "Deshmukh", "Kulkarni", "Joshi", "Verma", "Gupta", "Mehta", "Chavan", "Pawar"]
INSTITUTION_ID = "MMCOE"


def generate_synthetic_certificates(count: int = 20, seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generate a list of synthetic certificate dictionaries.

    Args:
        count (int): Number of certificates to generate (default 20 for Review 2).
        seed (int): Random seed for reproducibility.

    Returns:
        List[Dict[str, Any]]: List of certificate field dictionaries.
    """
    rng = random.Random(seed)
    certificates = []

    for i in range(1, count + 1):
        cert_id = f"CC{i:04d}"
        fname = rng.choice(FIRST_NAMES)
        lname = rng.choice(LAST_NAMES)
        student_name = f"{fname} {lname}"
        roll_no = f"A{100 + i}"
        course = rng.choice(COURSES)
        cgpa = round(rng.uniform(6.5, 9.95), 2)
        day = rng.randint(1, 28)
        month = rng.randint(1, 12)
        issue_date = f"2026-{month:02d}-{day:02d}"

        cert_dict = {
            "certificate_id": cert_id,
            "student_name": student_name,
            "roll_number": roll_no,
            "course": course,
            "cgpa": f"{cgpa:.2f}",
            "issue_date": issue_date,
            "institution_id": INSTITUTION_ID,
        }
        certificates.append(cert_dict)

    return certificates

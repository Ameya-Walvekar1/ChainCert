"""
Plain text certificate parser for Module 1 (Certificate & Record Management).

Parses structured plain text (.txt) certificate input into a dictionary compatible
with Module 2's CANONICAL_FIELD_ORDER expected input.
"""

from typing import Dict, Any
from chaincert.hashing.validator import validate_certificate_data
from chaincert.hashing.exceptions import CertificateValidationError


# Key aliases mapping common labels to Module 2 canonical field names
KEY_ALIASES = {
    "CERTIFICATE ID": "certificate_id",
    "CERTIFICATE_ID": "certificate_id",
    "CERT ID": "certificate_id",
    "ID": "certificate_id",
    "NAME": "student_name",
    "STUDENT NAME": "student_name",
    "STUDENT_NAME": "student_name",
    "ROLL NUMBER": "roll_number",
    "ROLL NO": "roll_number",
    "ROLL_NUMBER": "roll_number",
    "COURSE": "course",
    "BRANCH": "course",
    "CGPA": "cgpa",
    "GRADE": "cgpa",
    "GPA": "cgpa",
    "ISSUE DATE": "issue_date",
    "ISSUE_DATE": "issue_date",
    "DATE": "issue_date",
    "INSTITUTION ID": "institution_id",
    "INSTITUTION_ID": "institution_id",
    "INSTITUTION": "institution_id",
    "COLLEGE": "institution_id",
}


def parse_certificate_text(text_content: str) -> Dict[str, Any]:
    """
    Parse text content containing key-value pairs separated by colon (:).

    Example text:
        CERTIFICATE ID: CC001
        NAME: Rahul Sharma
        ROLL NUMBER: A101
        COURSE: AI & DS
        CGPA: 9.20
        ISSUE DATE: 2026-08-20
        INSTITUTION ID: MMCOE

    Returns:
        Dict[str, Any]: Dictionary containing normalized certificate fields.

    Raises:
        CertificateValidationError: If text is missing mandatory fields or invalid.
    """
    if not text_content or not text_content.strip():
        raise CertificateValidationError("Empty certificate text file.")

    extracted: Dict[str, str] = {}

    for line in text_content.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" in line:
            raw_key, raw_val = line.split(":", 1)
            norm_key_upper = raw_key.strip().upper()
            val = raw_val.strip()

            if norm_key_upper in KEY_ALIASES:
                canonical_key = KEY_ALIASES[norm_key_upper]
                extracted[canonical_key] = val

    # Validate against Module 2 validator
    validated_fields, _ = validate_certificate_data(extracted)
    return validated_fields


def parse_certificate_file(file_path: str) -> Dict[str, Any]:
    """Read a .txt file and parse certificate content."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_certificate_text(content)

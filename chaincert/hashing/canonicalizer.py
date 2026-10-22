"""
Deterministic Certificate Canonicalization Engine.
Single Source of Truth for ChainCert Field Normalization & Formatting.
"""

import re
from typing import Dict, Any, Union
from chaincert.hashing.models import CANONICAL_FIELD_ORDER, CertificateRecord
from chaincert.hashing.validator import validate_certificate_data
from chaincert.hashing.exceptions import CanonicalizationError, CertificateValidationError


def normalize_whitespace(text: str) -> str:
    """
    Trim leading/trailing whitespace and collapse internal consecutive spaces.
    Example: "  Rahul   Sharma  " -> "Rahul Sharma"
    """
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r'\s+', ' ', text.strip())


def normalize_cgpa(cgpa_val: Union[float, int, str]) -> str:
    """
    Format CGPA to exactly 2 decimal places string.
    Example: 9.2 -> "9.20", 9 -> "9.00", "9.200" -> "9.20"
    """
    val = float(str(cgpa_val).strip())
    return f"{val:.2f}"


def canonicalize_certificate(cert_input: Union[Dict[str, Any], CertificateRecord]) -> str:
    """
    Transform certificate data into a deterministic, canonical UTF-8 string representation.

    Rules:
        1. Mandatory 7-field structure in fixed order.
        2. Field keys lowercase.
        3. Whitespace trimmed and internal whitespace collapsed.
        4. CGPA formatted to 2 decimal places.
        5. Date formatted to YYYY-MM-DD.
        6. Serialized as key=value pairs joined by '|'.

    Args:
        cert_input: Dict or CertificateRecord object.

    Returns:
        str: Deterministic canonical string serialization.

    Raises:
        CanonicalizationError: If input cannot be canonicalized.
    """
    try:
        if isinstance(cert_input, CertificateRecord):
            raw_dict = cert_input.to_dict()
        elif isinstance(cert_input, dict):
            raw_dict = cert_input
        else:
            raise CanonicalizationError(f"Unsupported certificate input type: {type(cert_input).__name__}")

        # Validate & parse input
        validated_dict, _ = validate_certificate_data(raw_dict)

        canonical_pairs = []

        for field_key in CANONICAL_FIELD_ORDER:
            raw_value = validated_dict[field_key]

            if field_key == "cgpa":
                formatted_value = normalize_cgpa(raw_value)
            elif field_key == "issue_date":
                # Already parsed to YYYY-MM-DD in validator
                formatted_value = raw_value
            else:
                formatted_value = normalize_whitespace(str(raw_value))

            canonical_pairs.append(f"{field_key}={formatted_value}")

        return "|".join(canonical_pairs)

    except Exception as e:
        if isinstance(e, (CanonicalizationError, CertificateValidationError)):
            raise e
        raise CanonicalizationError(f"Failed to canonicalize certificate: {str(e)}") from e

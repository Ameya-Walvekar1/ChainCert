"""
Data models for Certificate Records and Hash Output Contracts.
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, Any, Union


# Canonical Specification Metadata
HASH_ALGORITHM: str = "SHA-256"
HASH_SPEC_VERSION: str = "1.0"

# Canonical field order (Strict single source of truth)
CANONICAL_FIELD_ORDER = (
    "certificate_id",
    "student_name",
    "roll_number",
    "course",
    "cgpa",
    "issue_date",
    "institution_id",
)


@dataclass
class CertificateRecord:
    """
    Structured academic certificate model matching official ChainCert specifications.
    """
    certificate_id: str
    student_name: str
    roll_number: str
    course: str
    cgpa: Union[float, str]
    issue_date: str
    institution_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to Python dictionary."""
        return {
            "certificate_id": self.certificate_id,
            "student_name": self.student_name,
            "roll_number": self.roll_number,
            "course": self.course,
            "cgpa": self.cgpa,
            "issue_date": self.issue_date,
            "institution_id": self.institution_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CertificateRecord":
        """Instantiate record from a dictionary, ensuring keys are present."""
        missing = [f for f in CANONICAL_FIELD_ORDER if f not in data]
        if missing:
            raise ValueError(f"Missing mandatory certificate fields: {', '.join(missing)}")
        return cls(
            certificate_id=str(data["certificate_id"]),
            student_name=str(data["student_name"]),
            roll_number=str(data["roll_number"]),
            course=str(data["course"]),
            cgpa=data["cgpa"],
            issue_date=str(data["issue_date"]),
            institution_id=str(data["institution_id"]),
        )


@dataclass
class HashResult:
    """
    Output contract returned by Module 2 Hashing Engine.
    Consumable by Module 1 (Storage), Module 3 (Merkle Tree), Module 5 (Verification).
    """
    canonical_data: str
    certificate_hash: str
    hash_algorithm: str = HASH_ALGORITHM
    canonicalization_version: str = HASH_SPEC_VERSION
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Convert HashResult to dictionary for JSON serialization or module exchange."""
        return {
            "canonical_data": self.canonical_data,
            "hash_algorithm": self.hash_algorithm,
            "canonicalization_version": self.canonicalization_version,
            "certificate_hash": self.certificate_hash,
            "timestamp": self.timestamp,
        }

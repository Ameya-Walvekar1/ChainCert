"""
Certificate Record representation for Module 1.
Combines raw certificate attributes with Module 2 hash and Module 3/4 batch metadata.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import json


@dataclass
class ExtendedCertificateRecord:
    """
    Certificate model for Module 1, storing both canonical fields and chain metadata.
    """
    certificate_id: str
    student_name: str
    roll_number: str
    course: str
    cgpa: str
    issue_date: str
    institution_id: str
    status: str = "REGISTERED"
    certificate_hash: Optional[str] = None
    canonical_data: Optional[str] = None
    batch_id: Optional[str] = None
    merkle_root: Optional[str] = None
    merkle_proof: Optional[str] = None  # JSON string
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_canonical_dict(self) -> Dict[str, Any]:
        """Return raw dictionary expected by Module 2 canonicalizer."""
        return {
            "certificate_id": self.certificate_id,
            "student_name": self.student_name,
            "roll_number": self.roll_number,
            "course": self.course,
            "cgpa": self.cgpa,
            "issue_date": self.issue_date,
            "institution_id": self.institution_id,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Return full record dictionary including database/proof fields."""
        d = asdict(self)
        if self.merkle_proof and isinstance(self.merkle_proof, str):
            try:
                d["merkle_proof_parsed"] = json.loads(self.merkle_proof)
            except Exception:
                d["merkle_proof_parsed"] = None
        return d

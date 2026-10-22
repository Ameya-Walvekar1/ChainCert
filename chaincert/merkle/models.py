"""
Data models for ChainCert Module 3 — Merkle Tree Builder.

Style follows Module 2's ``chaincert/hashing/models.py``: plain dataclasses
with ``to_dict()`` / ``from_dict()`` helpers so that structures can cross
module boundaries as JSON.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from chaincert.merkle.exceptions import InvalidProofError
from chaincert.merkle.validator import validate_hash, validate_position

#: Specification metadata, mirroring Module 2's HASH_SPEC_VERSION convention.
MERKLE_SPEC_VERSION: str = "1.0"

#: Odd-leaf policy identifier, recorded in outputs so that a consumer can tell
#: which construction rule produced a given root.
ODD_LEAF_POLICY: str = "promote-unpaired"


@dataclass(frozen=True)
class ProofStep:
    """One step of a Merkle proof: a sibling digest and which side it sits on.

    ``position`` is the position of the SIBLING relative to the node currently
    being folded. This definition is stated explicitly because the opposite
    convention is equally plausible and mixing the two is the most common cause
    of proof-verification bugs.

        position == "right"  ->  parent = H(current + sibling)
        position == "left"   ->  parent = H(sibling + current)
    """

    hash: str
    position: str

    def __post_init__(self) -> None:
        # frozen=True, so assign through object.__setattr__ after validation.
        object.__setattr__(self, "hash", validate_hash(self.hash, label="ProofStep.hash"))
        object.__setattr__(self, "position", validate_position(self.position))

    @property
    def sibling_is_left(self) -> bool:
        """True when the sibling must be concatenated BEFORE the current node."""
        return self.position == "left"

    def to_dict(self) -> Dict[str, str]:
        """Serialize to the standardized proof-step mapping."""
        return {"hash": self.hash, "position": self.position}

    @classmethod
    def from_dict(cls, data: Any) -> "ProofStep":
        """Rebuild a proof step from a mapping.

        Raises:
            InvalidProofError: If the mapping is not a dict or is missing keys.
        """
        if not isinstance(data, dict):
            raise InvalidProofError(
                f"Proof step must be a dict, got {type(data).__name__}."
            )

        missing = [key for key in ("hash", "position") if key not in data]
        if missing:
            raise InvalidProofError(
                f"Proof step is missing required key(s): {', '.join(missing)}."
            )

        return cls(hash=data["hash"], position=data["position"])


@dataclass(frozen=True)
class MerkleTree:
    """A fully constructed Merkle tree over a batch of certificate hashes.

    The tree is stored as a list of levels rather than as linked node objects.
    Level 0 holds the leaves; the final level holds exactly one digest, the
    Merkle root. A level-based layout keeps proof generation to simple index
    arithmetic (parent index == child index // 2) and keeps the structure easy
    to print during a demonstration.

    Attributes:
        levels: ``levels[0]`` is the leaves; ``levels[-1] == [merkle_root]``.
        leaf_count: Number of certificates in the batch.
        height: Number of hashing levels above the leaves. A single-leaf tree
            has height 0; a four-leaf tree has height 2.
    """

    levels: List[List[str]] = field(default_factory=list)

    @property
    def leaves(self) -> List[str]:
        """The leaf digests, in the order Module 2 supplied them."""
        return list(self.levels[0])

    @property
    def merkle_root(self) -> str:
        """The single digest summarizing the whole batch."""
        return self.levels[-1][0]

    @property
    def leaf_count(self) -> int:
        """Number of certificate hashes in this batch."""
        return len(self.levels[0])

    @property
    def height(self) -> int:
        """Number of hashing levels above the leaf level."""
        return len(self.levels) - 1

    def level(self, index: int) -> List[str]:
        """Return a copy of one level of the tree."""
        return list(self.levels[index])

    def index_of(self, leaf_hash: str) -> int:
        """Return the index of a leaf digest, or -1 if absent.

        If the same digest appears more than once (only possible if two
        certificates canonicalize identically, which Module 1's unique
        ``certificate_id`` should prevent), the FIRST index is returned.
        """
        normalized = validate_hash(leaf_hash, label="leaf_hash")
        try:
            return self.levels[0].index(normalized)
        except ValueError:
            return -1

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the tree's summary for hand-off to the next module.

        Deliberately does not include the full level structure. The downstream
        consumer (Module 4, Block Chaining) needs the root and the certificate
        count, nothing more. Use ``levels`` directly for demonstration or
        debugging.
        """
        return {
            "merkle_root": self.merkle_root,
            "certificate_count": self.leaf_count,
            "height": self.height,
            "merkle_spec_version": MERKLE_SPEC_VERSION,
            "odd_leaf_policy": ODD_LEAF_POLICY,
        }


__all__ = [
    "MERKLE_SPEC_VERSION",
    "ODD_LEAF_POLICY",
    "ProofStep",
    "MerkleTree",
]

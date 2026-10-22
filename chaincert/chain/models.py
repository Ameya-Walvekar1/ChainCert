"""
Data models for ChainCert Module 4 — Block Chaining.

Style follows Module 3's ``chaincert/merkle/models.py``: a frozen dataclass
with ``to_dict()`` / ``from_dict()`` helpers so structures cross module
boundaries (and disk) as plain JSON.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from chaincert.chain.exceptions import InvalidBlockError
from chaincert.chain.hashing_backend import compute_block_hash
from chaincert.merkle.exceptions import InvalidHashError
from chaincert.merkle.validator import validate_hash

#: Specification metadata, mirroring Module 3's MERKLE_SPEC_VERSION convention.
CHAIN_SPEC_VERSION: str = "1.0"


def _validate_batch_id(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidBlockError(
            f"batch_id must be a non-empty string, got {value!r}."
        )
    return value.strip()


def _validate_certificate_count(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InvalidBlockError(
            f"certificate_count must be a positive integer, got {value!r}."
        )
    return value


def _validate_block_id(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InvalidBlockError(
            f"block_id must be a positive integer, got {value!r}."
        )
    return value


@dataclass(frozen=True)
class Block:
    """One certificate batch, chained to the batch that came before it.

    Attributes:
        block_id: 1-based position of this block in the chain.
        batch_id: Human-readable batch identifier (e.g. ``"SEM1_2026"``).
        timestamp: ISO-8601 UTC timestamp of block creation.
        certificate_count: Number of certificates summarized by ``merkle_root``.
        merkle_root: Module 3's Merkle root for this batch (64 lowercase hex).
        previous_root: The previous block's ``merkle_root``, or ``None`` for
            the first block in the chain. This is the field that links one
            batch's history to the next.
        block_hash: SHA-256 digest (via Module 2, see ``hashing_backend.py``)
            over every field above, computed once at creation time. It is NOT
            part of the previous/current root chain — it is a self-integrity
            fingerprint of this block alone. Its purpose: ``previous_root``
            only proves that a block's *merkle_root* wasn't swapped after the
            fact; it says nothing about ``batch_id``, ``certificate_count``,
            or ``timestamp`` being edited directly in storage. Recomputing
            ``block_hash`` from a block's current fields and comparing it to
            the stored value catches exactly that. See
            ``chain.py::Chain.validate_chain`` for how the two checks combine.
    """

    block_id: int
    batch_id: str
    timestamp: str
    certificate_count: int
    merkle_root: str
    previous_root: Optional[str]
    block_hash: str

    @classmethod
    def create(
        cls,
        *,
        block_id: int,
        batch_id: str,
        certificate_count: int,
        merkle_root: str,
        previous_root: Optional[str],
        timestamp: Optional[str] = None,
    ) -> "Block":
        """Validate inputs, compute ``block_hash``, and build a new Block.

        This is the ONLY normal way to create a Block. ``Block(...)`` (the
        dataclass constructor) is still used by ``from_dict`` and by
        ``dataclasses.replace`` when deliberately constructing a tampered
        block for a validation demonstration — see
        ``chaincert/tests/test_chain_tampering.py``.

        Args:
            block_id: 1-based position in the chain. Normally supplied by
                ``Chain.add_batch``, not chosen by the caller.
            batch_id: Human-readable batch identifier.
            certificate_count: Number of certificates in this batch. Must
                match the ``certificate_count`` Module 3 reported for the
                same ``merkle_root``.
            merkle_root: The Merkle root Module 3 computed for this batch.
                Validated with Module 3's own ``validate_hash`` so Module 4
                does not re-implement hash-format checking.
            previous_root: The previous block's ``merkle_root``, or ``None``
                for the first block.
            timestamp: ISO-8601 UTC timestamp. Defaults to "now" when omitted.

        Raises:
            InvalidBlockError: If ``batch_id``, ``certificate_count``, or
                ``block_id`` fail validation.
            InvalidHashError: If ``merkle_root`` or ``previous_root`` is not a
                valid 64-character hex digest (propagated from Module 3).
        """
        block_id = _validate_block_id(block_id)
        batch_id = _validate_batch_id(batch_id)
        certificate_count = _validate_certificate_count(certificate_count)
        merkle_root = validate_hash(merkle_root, label="merkle_root")

        if previous_root is not None:
            previous_root = validate_hash(previous_root, label="previous_root")

        timestamp = timestamp or datetime.now(timezone.utc).isoformat()

        block_hash = compute_block_hash(
            block_id=block_id,
            batch_id=batch_id,
            timestamp=timestamp,
            certificate_count=certificate_count,
            merkle_root=merkle_root,
            previous_root=previous_root,
        )

        return cls(
            block_id=block_id,
            batch_id=batch_id,
            timestamp=timestamp,
            certificate_count=certificate_count,
            merkle_root=merkle_root,
            previous_root=previous_root,
            block_hash=block_hash,
        )

    def recompute_hash(self) -> str:
        """Recompute ``block_hash`` from this block's CURRENT field values.

        Used by chain validation: if this differs from ``self.block_hash``,
        something in the block was changed after it was created.
        """
        return compute_block_hash(
            block_id=self.block_id,
            batch_id=self.batch_id,
            timestamp=self.timestamp,
            certificate_count=self.certificate_count,
            merkle_root=self.merkle_root,
            previous_root=self.previous_root,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for JSON storage or hand-off to another module."""
        return {
            "block_id": self.block_id,
            "batch_id": self.batch_id,
            "timestamp": self.timestamp,
            "certificate_count": self.certificate_count,
            "merkle_root": self.merkle_root,
            "previous_root": self.previous_root,
            "block_hash": self.block_hash,
            "chain_spec_version": CHAIN_SPEC_VERSION,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "Block":
        """Rebuild a Block exactly as stored, WITHOUT recomputing block_hash.

        This is deliberate and different from ``create()``. Loading from
        storage must reproduce exactly what was persisted, tampered or not —
        recomputing the hash on load would silently "heal" a tampered file
        instead of letting ``validate_chain()`` catch it.

        Raises:
            InvalidBlockError: If ``data`` is not a dict or is missing
                required keys.
        """
        if not isinstance(data, dict):
            raise InvalidBlockError(
                f"Block data must be a dict, got {type(data).__name__}."
            )

        required = (
            "block_id",
            "batch_id",
            "timestamp",
            "certificate_count",
            "merkle_root",
            "previous_root",
            "block_hash",
        )
        missing = [key for key in required if key not in data]
        if missing:
            raise InvalidBlockError(
                f"Block data is missing required key(s): {', '.join(missing)}."
            )

        try:
            return cls(
                block_id=data["block_id"],
                batch_id=data["batch_id"],
                timestamp=data["timestamp"],
                certificate_count=data["certificate_count"],
                merkle_root=data["merkle_root"],
                previous_root=data["previous_root"],
                block_hash=data["block_hash"],
            )
        except InvalidHashError:
            # from_dict must be able to load a block whose merkle_root/
            # previous_root field was corrupted, so validate_chain() can
            # report it as a tamper finding rather than the load crashing.
            return cls(
                block_id=data["block_id"],
                batch_id=data["batch_id"],
                timestamp=data["timestamp"],
                certificate_count=data["certificate_count"],
                merkle_root=str(data["merkle_root"]),
                previous_root=(
                    None
                    if data["previous_root"] is None
                    else str(data["previous_root"])
                ),
                block_hash=data["block_hash"],
            )


__all__ = ["CHAIN_SPEC_VERSION", "Block"]

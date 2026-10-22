"""
Hashing bridge for ChainCert Module 4 — Block Chaining.

The master specification (Section 22, Rule 1) requires ONE SHA-256
implementation across the whole project. Module 3 already built the single
bridge to Module 2's ``generate_sha256`` in ``chaincert/merkle/hashing_backend.py``
and documented why (Module 2 is the project's single source of truth for
hashing; nothing else may import ``hashlib``).

Module 4 does not open a second bridge to Module 2. It imports Module 3's
already-vetted ``generate_sha256`` directly. This is intentional reuse, not
duplication: Module 3's bridge already raises a clear, actionable error if
Module 2 is missing, so Module 4 gets that same guardrail for free.
"""

from typing import Optional

from chaincert.merkle.hashing_backend import generate_sha256

__all__ = ["generate_sha256", "compute_block_hash"]


def compute_block_hash(
    *,
    block_id: int,
    batch_id: str,
    timestamp: str,
    certificate_count: int,
    merkle_root: str,
    previous_root: Optional[str],
) -> str:
    """Compute a block's self-integrity fingerprint.

    All six fields are concatenated into one delimited string, in a fixed
    order, and passed to Module 2's ``generate_sha256`` — the same
    text-domain-concatenation approach Module 3 uses for internal Merkle
    nodes (see ``chaincert/merkle/hashing_backend.py::hash_pair``), applied
    here to a block's fields instead of two child hashes.

    ``previous_root`` is rendered as the literal string ``"None"`` when the
    block is the first in the chain, so that a first block's hash cannot
    collide with a later block that happens to share the same
    ``merkle_root`` as a genuine (but different) ``previous_root`` value.

    This is NOT the previous/current Merkle-root chain (that lives in
    ``Chain.validate_chain`` and only compares ``previous_root`` to the
    prior block's ``merkle_root``). This is a separate, per-block fingerprint
    that detects direct tampering with a block's own stored fields.

    Returns:
        A 64-character lowercase hexadecimal digest.
    """
    payload = "|".join(
        [
            str(block_id),
            batch_id,
            timestamp,
            str(certificate_count),
            merkle_root,
            str(previous_root),
        ]
    )
    return generate_sha256(payload)

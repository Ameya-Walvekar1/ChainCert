"""
Input validation for ChainCert Module 3 — Merkle Tree Builder.

Scope note (important for review): this module validates the STRUCTURE of a
hash string that has already been produced elsewhere. It does not hash
anything, does not canonicalize anything, and does not validate certificate
fields. Those belong to Module 2.

Module 2 does contain a ``HEX_64_REGEX`` in ``hashing/hasher.py``, but it is
module-private: it is not re-exported by ``chaincert/hashing/__init__.py`` and
is not listed in that package's ``__all__``. Module 2's public
``compare_hashes()`` validates internally but returns ``False`` on malformed
input rather than raising, so it cannot be used as a validator either.
Module 3 therefore defines its own structural check. This is not duplication of
Module 2's hashing responsibility.
"""

import re
from typing import Any, List, Sequence

from chaincert.merkle.exceptions import (
    EmptyLeafListError,
    InvalidHashError,
    InvalidProofError,
)

#: A SHA-256 digest rendered as hexadecimal: exactly 64 hex characters.
#: Accepted case-insensitively on input; normalized to lowercase immediately.
HEX_64_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")

#: Legal values for a proof step's ``position`` field.
VALID_POSITIONS = ("left", "right")


def validate_hash(value: Any, *, label: str = "hash") -> str:
    """Validate a single SHA-256 hex digest and normalize it to lowercase.

    Args:
        value: The candidate digest.
        label: Name used in the error message, for a clearer failure.

    Returns:
        The digest, stripped and lowercased.

    Raises:
        InvalidHashError: If the value is not a string, or is not exactly 64
            hexadecimal characters.
    """
    if not isinstance(value, str):
        raise InvalidHashError(
            f"{label} must be a string, got {type(value).__name__}."
        )

    cleaned = value.strip()

    if not cleaned:
        raise InvalidHashError(f"{label} cannot be empty or blank whitespace.")

    if not HEX_64_REGEX.match(cleaned):
        raise InvalidHashError(
            f"{label} must be exactly 64 hexadecimal characters "
            f"(got {len(cleaned)} characters: {cleaned[:16]!r}...)."
        )

    return cleaned.lower()


def validate_leaf_hashes(leaf_hashes: Any) -> List[str]:
    """Validate the list of certificate hashes handed over by Module 2.

    Order is preserved exactly as received. The list is never sorted: the
    ordering of certificates within a batch is semantically meaningful, and
    sorting would let an attacker rearrange a batch without changing the root.

    Args:
        leaf_hashes: A sequence of 64-character hex digests.

    Returns:
        A new list of lowercase digests, in the original order.

    Raises:
        EmptyLeafListError: If the sequence is empty.
        InvalidHashError: If the input is not a list/tuple, or any element is
            not a valid digest.
    """
    if isinstance(leaf_hashes, (str, bytes)):
        raise InvalidHashError(
            "leaf_hashes must be a list of hash strings, not a single string."
        )

    if not isinstance(leaf_hashes, Sequence):
        raise InvalidHashError(
            f"leaf_hashes must be a list or tuple, got {type(leaf_hashes).__name__}."
        )

    if len(leaf_hashes) == 0:
        raise EmptyLeafListError(
            "Cannot build a Merkle tree from an empty certificate batch. "
            "An empty batch has no Merkle root."
        )

    return [
        validate_hash(item, label=f"leaf_hashes[{index}]")
        for index, item in enumerate(leaf_hashes)
    ]


def validate_position(value: Any) -> str:
    """Validate a proof step's sibling position.

    Args:
        value: Candidate position.

    Returns:
        The position, stripped and lowercased.

    Raises:
        InvalidProofError: If the value is not exactly ``"left"`` or ``"right"``.
    """
    if not isinstance(value, str):
        raise InvalidProofError(
            f"Proof step position must be a string, got {type(value).__name__}."
        )

    cleaned = value.strip().lower()

    if cleaned not in VALID_POSITIONS:
        raise InvalidProofError(
            f"Proof step position must be one of {VALID_POSITIONS}, got {value!r}."
        )

    return cleaned


def validate_leaf_index(leaf_index: Any, leaf_count: int) -> int:
    """Validate a leaf index against the tree's leaf count.

    Raises:
        InvalidProofError: If the index is not an integer or is out of range.
    """
    if isinstance(leaf_index, bool) or not isinstance(leaf_index, int):
        raise InvalidProofError(
            f"leaf_index must be an integer, got {type(leaf_index).__name__}."
        )

    if leaf_index < 0 or leaf_index >= leaf_count:
        raise InvalidProofError(
            f"leaf_index {leaf_index} is out of range for a tree with "
            f"{leaf_count} leaves (valid range: 0 to {leaf_count - 1})."
        )

    return leaf_index


__all__ = [
    "HEX_64_REGEX",
    "VALID_POSITIONS",
    "validate_hash",
    "validate_leaf_hashes",
    "validate_position",
    "validate_leaf_index",
]

"""
Custom Exceptions for ChainCert Module 3 — Merkle Tree Builder.

Per the ChainCert master specification (Section 22, Rule 1: "Do not create
duplicate versions of the same function"), Module 3 does NOT define its own
root exception type. It inherits from Module 2's ``ChainCertError`` so that
the whole project shares a single exception hierarchy:

    ChainCertError                (defined in Module 2)
        └── MerkleError           (this module)
             ├── InvalidHashError
             ├── EmptyLeafListError
             ├── InvalidProofError
             └── LeafNotFoundError

If Module 2 is not importable (for example, a teammate has cloned Module 3
alone and has not yet placed Module 2 alongside it), we fall back to a local
base class so that Module 3 still imports cleanly and raises sensible errors.
The fallback affects the exception base class ONLY. It never substitutes for
Module 2's hashing: ``chaincert.merkle.hashing_backend`` raises a hard error
if the real ``generate_sha256`` is missing.
"""

try:  # pragma: no cover - trivial import branch
    from chaincert.hashing.exceptions import ChainCertError

    _INHERITS_FROM_MODULE2 = True
except ImportError:  # pragma: no cover - trivial import branch

    class ChainCertError(Exception):
        """Fallback base used only when Module 2 is not on the import path."""

    _INHERITS_FROM_MODULE2 = False


class MerkleError(ChainCertError):
    """Base exception for all Module 3 (Merkle Tree Builder) errors."""


class InvalidHashError(MerkleError):
    """Raised when a value is not a valid 64-character hexadecimal SHA-256 digest."""


class EmptyLeafListError(MerkleError):
    """Raised when Merkle tree construction is attempted with no leaves.

    An empty batch has no cryptographic meaning. Module 3 refuses to invent a
    placeholder root, because a fake root would be chained by Module 4 as if it
    were a real batch.
    """


class InvalidProofError(MerkleError):
    """Raised when a Merkle proof is structurally malformed."""


class LeafNotFoundError(MerkleError):
    """Raised when a requested leaf hash or leaf index is not present in the tree."""


__all__ = [
    "ChainCertError",
    "MerkleError",
    "InvalidHashError",
    "EmptyLeafListError",
    "InvalidProofError",
    "LeafNotFoundError",
]

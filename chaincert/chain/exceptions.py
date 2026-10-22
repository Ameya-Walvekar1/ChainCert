"""
Custom Exceptions for ChainCert Module 4 — Block Chaining.

Per the ChainCert master specification (Section 22, Rule 1: "Do not create
duplicate versions of the same function"), Module 4 does NOT define a second
root exception type or a second Module-2-fallback shim. Module 3 already
solved that problem in ``chaincert/merkle/exceptions.py``: it imports Module
2's ``ChainCertError`` when Module 2 is importable, and falls back to a local
base class when it is not, so that the whole project shares one exception
hierarchy no matter which repositories happen to be on the path.

Module 4 reuses that exact base by importing it from Module 3, rather than
re-implementing the same try/except fallback a third time:

    ChainCertError                (defined in Module 2, or Module 3's fallback)
        └── ChainError            (this module)
             ├── InvalidBlockError
             ├── EmptyChainError
             ├── BlockNotFoundError
             ├── ChainStorageError
             └── ChainTamperError
"""

from chaincert.merkle.exceptions import ChainCertError


class ChainError(ChainCertError):
    """Base exception for all Module 4 (Block Chaining) errors."""


class InvalidBlockError(ChainError):
    """Raised when a block's fields are missing, malformed, or out of range."""


class EmptyChainError(ChainError):
    """Raised when an operation requires at least one block but the chain is empty."""


class BlockNotFoundError(ChainError):
    """Raised when a requested block_id does not exist in the chain."""


class ChainStorageError(ChainError):
    """Raised when the chain cannot be saved to or loaded from disk."""


class ChainTamperError(ChainError):
    """Raised by strict validation helpers when a block fails its integrity check.

    ``Chain.validate_chain()`` itself does not raise this — it returns a
    :class:`~chaincert.chain.chain.ChainValidationResult` so a caller can
    inspect *every* problem in one pass, which is far more useful for a
    demonstration than an exception that stops at the first bad block.
    ``ChainTamperError`` exists for callers that want a hard failure instead,
    e.g. ``Chain.validate_chain(raise_on_failure=True)``.
    """


__all__ = [
    "ChainCertError",
    "ChainError",
    "InvalidBlockError",
    "EmptyChainError",
    "BlockNotFoundError",
    "ChainStorageError",
    "ChainTamperError",
]

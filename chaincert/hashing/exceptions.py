"""
Custom Exceptions for ChainCert Module 2 — Hashing Engine.
"""

class ChainCertError(Exception):
    """Base exception for all ChainCert errors."""
    pass


class CertificateValidationError(ChainCertError):
    """Raised when certificate data is missing required fields or has invalid formats."""
    pass


class CanonicalizationError(ChainCertError):
    """Raised when canonicalization of certificate data fails."""
    pass


class HashingError(ChainCertError):
    """Raised when SHA-256 hash generation encounters an error."""
    pass

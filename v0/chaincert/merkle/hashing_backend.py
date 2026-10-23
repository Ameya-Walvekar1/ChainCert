"""
Module 2 hashing bridge for ChainCert Module 3.

The ChainCert master specification (Section 22, Rules 1 and 3) requires that
SHA-256 generation be performed by ONE implementation across the whole project.
Module 2's ``MODULE2_SPECIFICATION.md`` Section 1 names Module 2 the Single
Source of Truth for hashing.

Module 3 therefore does NOT import ``hashlib``. Every internal Merkle node hash
is produced by Module 2's ``generate_sha256``.

This file exists so that the dependency is declared in exactly one place. If the
import fails, we raise immediately with an actionable message instead of
silently substituting ``hashlib`` — a silent substitution would be the exact
"two modules, two SHA-256 implementations" failure that Rule 1 exists to
prevent.
"""

from typing import Callable

_IMPORT_HELP = (
    "ChainCert Module 3 requires Module 2 (the Hashing Engine) to be importable.\n"
    "Module 2 is the project's single source of truth for SHA-256 and Module 3\n"
    "must not reimplement it.\n\n"
    "Fix this by placing Module 2 next to Module 3:\n\n"
    "    <workspace>/\n"
    "        ChainCert-module2/     <- git clone of the Module 2 repository\n"
    "        ChainCert-module3/     <- this repository\n\n"
    "    git clone https://github.com/Ameya-Walvekar1/ChainCert-module2.git\n\n"
    "or vendor it inside this repository:\n\n"
    "    git clone https://github.com/Ameya-Walvekar1/ChainCert-module2.git vendor/ChainCert-module2\n\n"
    "See README.md > Installation for details."
)

try:
    from chaincert.hashing import generate_sha256 as _generate_sha256
except ImportError as exc:  # pragma: no cover - environment-dependent branch
    raise ImportError(f"{_IMPORT_HELP}\n\nOriginal import error: {exc}") from exc


#: Module 2's SHA-256 function. Signature: ``(canonical_data: str) -> str``.
#: Returns a lowercase 64-character hexadecimal digest.
generate_sha256: Callable[[str], str] = _generate_sha256


def hash_pair(left: str, right: str) -> str:
    """Hash two child node digests into their parent digest.

    The two 64-character hexadecimal strings are concatenated into a single
    128-character string, which is then passed to Module 2's
    ``generate_sha256``. The concatenation is performed on the HEXADECIMAL
    TEXT, not on raw bytes.

    This is a deliberate design choice, documented here because it is a likely
    viva question. Module 2's public API accepts ``str`` and internally does
    ``canonical_data.encode("utf-8")``, so a text-domain combination is the only
    way to reuse it. Bitcoin, by contrast, concatenates 32 raw bytes and applies
    SHA-256 twice. Both constructions are deterministic and collision-resistant
    for our purposes; ours is simpler to inspect and debug, and it satisfies the
    master specification's requirement that all hashing flow through Module 2.

    Args:
        left: Left child digest, 64 lowercase hex characters.
        right: Right child digest, 64 lowercase hex characters.

    Returns:
        The parent digest, 64 lowercase hex characters.
    """
    return generate_sha256(left + right)


__all__ = ["generate_sha256", "hash_pair"]

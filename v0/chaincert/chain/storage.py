"""
JSON storage for ChainCert Module 4 — Block Chaining.

Review 2 scope keeps this deliberately simple: the whole chain is one JSON
array of block dicts, e.g. ``chain.json``. No database, no ORM, no schema
migrations. The project has no existing database convention to plug into
(Module 3 keeps no persistent state at all), so this is the smallest thing
that lets a chain survive across demo runs.
"""

import json
from pathlib import Path
from typing import List, Union

from chaincert.chain.exceptions import ChainStorageError
from chaincert.chain.models import Block

PathLike = Union[str, Path]


def save_chain(blocks: List[Block], path: PathLike) -> None:
    """Write a chain to disk as a JSON array of block dicts.

    Args:
        blocks: The chain's blocks, in order (block 1 first).
        path: Destination file, e.g. ``"chain.json"``.

    Raises:
        ChainStorageError: If the file cannot be written.
    """
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump([block.to_dict() for block in blocks], handle, indent=2)
    except OSError as exc:
        raise ChainStorageError(f"Could not write chain to {path}: {exc}") from exc


def load_chain(path: PathLike) -> List[Block]:
    """Load a chain from a JSON array of block dicts.

    Blocks are rebuilt with ``Block.from_dict``, which does NOT recompute
    ``block_hash`` — so a file that was hand-edited between runs loads
    exactly as-is, and ``Chain.validate_chain()`` can report the tampering
    instead of the load silently masking it.

    Args:
        path: Source file, e.g. ``"chain.json"``.

    Returns:
        The chain's blocks, in the order stored.

    Raises:
        ChainStorageError: If the file is missing, unreadable, or not valid
            JSON, or if its top-level shape is not a list.
    """
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise ChainStorageError(f"Could not read chain from {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ChainStorageError(f"{path} does not contain valid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise ChainStorageError(
            f"{path} must contain a JSON array of blocks, got {type(data).__name__}."
        )

    return [Block.from_dict(item) for item in data]


__all__ = ["save_chain", "load_chain"]

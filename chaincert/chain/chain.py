"""
Chain management for ChainCert Module 4 — Block Chaining.

Consumes the Merkle root Module 3 produces for a batch of certificates
(``MerkleTree.to_dict()["merkle_root"]``), wraps it in a :class:`Block`, and
links it to the batch that came before it. See
``docs/MODULE4_INTEGRATION_NOTES.md`` (or the accompanying chat response) for
exactly where Module 3's output is handed to ``Chain.add_batch``.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

from chaincert.chain.exceptions import BlockNotFoundError, ChainTamperError
from chaincert.chain.models import Block
from chaincert.chain.storage import load_chain, save_chain

PathLike = Union[str, Path]


@dataclass
class ChainValidationResult:
    """Outcome of :meth:`Chain.validate_chain`.

    Reports EVERY problem found, not just the first one — for a Review 2
    demonstration, "block 2's previous_root is wrong" is a much better thing
    to show on screen than a bare ``False``.

    Attributes:
        is_valid: True only if ``errors`` is empty.
        errors: Human-readable descriptions of each broken link or tampered
            block, in block order.
    """

    is_valid: bool
    errors: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid


class Chain:
    """An ordered, tamper-evident history of certificate-batch blocks.

    A ``Chain`` holds :class:`Block` instances in memory and, optionally,
    mirrors them to a JSON file (see ``chaincert/chain/storage.py``) so the
    history survives across separate demo/script runs.
    """

    def __init__(
        self,
        storage_path: Optional[PathLike] = None,
        *,
        autoload: bool = True,
    ) -> None:
        """Create a chain, optionally backed by a JSON file.

        Args:
            storage_path: Path to a JSON file such as ``"chain.json"``. If
                omitted, the chain exists only in memory for this process.
            autoload: If True (default) and ``storage_path`` already exists,
                load the existing chain from it immediately.
        """
        self._blocks: List[Block] = []
        self.storage_path = Path(storage_path) if storage_path else None

        if self.storage_path and autoload and self.storage_path.exists():
            self._blocks = load_chain(self.storage_path)

    # -- Reading ----------------------------------------------------------

    @property
    def blocks(self) -> List[Block]:
        """All blocks, in chain order (block 1 first). Returns a copy."""
        return list(self._blocks)

    @property
    def latest_block(self) -> Optional[Block]:
        """The most recently added block, or ``None`` for an empty chain."""
        return self._blocks[-1] if self._blocks else None

    def get_block(self, block_id: int) -> Block:
        """Look up a block by its 1-based ``block_id``.

        Raises:
            BlockNotFoundError: If no block with that id exists.
        """
        for block in self._blocks:
            if block.block_id == block_id:
                return block
        raise BlockNotFoundError(f"No block with block_id={block_id} in this chain.")

    def __len__(self) -> int:
        return len(self._blocks)

    def __iter__(self):
        return iter(self.blocks)

    # -- Writing ------------------------------------------------------------

    def add_batch(
        self,
        *,
        batch_id: str,
        merkle_root: str,
        certificate_count: int,
        timestamp: Optional[str] = None,
    ) -> Block:
        """Add a new batch to the chain as the next block.

        This is Module 4's primary entry point and the consumer of Module
        3's output. ``previous_root`` is determined automatically: it is
        ``None`` for the first block, or the current ``latest_block``'s
        ``merkle_root`` for every block after that. Callers never set
        ``previous_root`` themselves — that is exactly the field this method
        exists to get right automatically.

        Args:
            batch_id: Human-readable batch identifier, e.g. ``"SEM1_2026"``.
            merkle_root: The Merkle root Module 3 computed for this batch —
                typically ``build_merkle_tree(leaf_hashes).merkle_root`` or
                ``build_merkle_tree(leaf_hashes).to_dict()["merkle_root"]``.
            certificate_count: Number of certificates in this batch —
                typically the same tree's ``leaf_count`` /
                ``to_dict()["certificate_count"]``.
            timestamp: ISO-8601 UTC timestamp. Defaults to "now".

        Returns:
            The newly created :class:`Block`, already appended to the chain
            (and persisted, if this chain has a ``storage_path``).
        """
        previous_root = self.latest_block.merkle_root if self._blocks else None
        block = Block.create(
            block_id=len(self._blocks) + 1,
            batch_id=batch_id,
            certificate_count=certificate_count,
            merkle_root=merkle_root,
            previous_root=previous_root,
            timestamp=timestamp,
        )
        self._blocks.append(block)

        if self.storage_path:
            self.save()

        return block

    def replace_block(self, block_id: int, tampered_block: Block) -> None:
        """Overwrite one block in place — FOR TESTS AND DEMOS ONLY.

        Normal chain usage only ever appends via ``add_batch``; nothing in
        this class calls ``replace_block`` on its own. It exists so tamper
        detection can be demonstrated honestly: build a modified copy of a
        real block with ``dataclasses.replace(original, previous_root=...)``
        or ``dataclasses.replace(original, merkle_root=...)``, install it
        with this method, and then show ``validate_chain()`` catching it.

        Args:
            block_id: Which block to overwrite.
            tampered_block: Its replacement. Not validated against the rest
                of the chain — that is exactly what makes it "tampered".

        Raises:
            BlockNotFoundError: If ``block_id`` does not exist.
        """
        for index, block in enumerate(self._blocks):
            if block.block_id == block_id:
                self._blocks[index] = tampered_block
                if self.storage_path:
                    self.save()
                return
        raise BlockNotFoundError(f"No block with block_id={block_id} in this chain.")

    # -- Persistence --------------------------------------------------------

    def save(self, path: Optional[PathLike] = None) -> None:
        """Persist the chain to JSON.

        Args:
            path: Overrides ``self.storage_path`` for this call. If both are
                omitted, nothing is written.
        """
        target = Path(path) if path else self.storage_path
        if target is None:
            return
        save_chain(self._blocks, target)

    def load(self, path: Optional[PathLike] = None) -> None:
        """Replace this chain's in-memory blocks with what is stored on disk.

        Args:
            path: Overrides ``self.storage_path`` for this call.
        """
        target = Path(path) if path else self.storage_path
        if target is None:
            raise ValueError("No storage_path configured and none was given.")
        self._blocks = load_chain(target)

    # -- Validation -----------------------------------------------------

    def validate_chain(self, *, raise_on_failure: bool = False) -> ChainValidationResult:
        """Verify every block's integrity and its link to the block before it.

        Two independent checks run against every block:

        1. **Root linkage** — ``block[i].previous_root`` must equal
           ``block[i-1].merkle_root`` (and must be ``None`` for block 1).
           This is the check the module requirements describe: it catches a
           block whose ``previous_root`` was pointed at the wrong (or a
           fabricated) root.
        2. **Self-integrity** — each block's ``block_hash`` is recomputed
           from its CURRENT field values and compared to the stored
           ``block_hash``. This catches a block whose ``merkle_root``,
           ``batch_id``, ``certificate_count``, or ``timestamp`` was edited
           directly, which linkage alone would miss if the attacker also
           patched every following block's ``previous_root`` to match.

        Also checks that ``block_id`` values are exactly ``1, 2, 3, ...`` in
        order, which catches reordered or duplicated blocks.

        An empty chain is considered trivially valid.

        Args:
            raise_on_failure: If True, raise :class:`ChainTamperError`
                instead of returning a result with ``is_valid=False``.

        Returns:
            A :class:`ChainValidationResult` listing every problem found.

        Raises:
            ChainTamperError: Only if ``raise_on_failure=True`` and the chain
                is invalid.
        """
        errors: List[str] = []
        blocks = self._blocks

        for index, block in enumerate(blocks):
            expected_block_id = index + 1
            if block.block_id != expected_block_id:
                errors.append(
                    f"Position {index}: expected block_id={expected_block_id}, "
                    f"found block_id={block.block_id} (blocks out of order?)."
                )

            if block.recompute_hash() != block.block_hash:
                errors.append(
                    f"Block {block.block_id}: stored block_hash does not match "
                    f"its current fields (batch_id, timestamp, certificate_count, "
                    f"merkle_root, or previous_root was modified after creation)."
                )

            if index == 0:
                if block.previous_root is not None:
                    errors.append(
                        f"Block {block.block_id}: is the first block but "
                        f"previous_root={block.previous_root!r} (expected None)."
                    )
            else:
                previous_block = blocks[index - 1]
                if block.previous_root != previous_block.merkle_root:
                    errors.append(
                        f"Block {block.block_id}: previous_root="
                        f"{block.previous_root!r} does not match block "
                        f"{previous_block.block_id}'s merkle_root="
                        f"{previous_block.merkle_root!r}."
                    )

        result = ChainValidationResult(is_valid=not errors, errors=errors)

        if raise_on_failure and not result.is_valid:
            raise ChainTamperError("; ".join(errors))

        return result


__all__ = ["Chain", "ChainValidationResult"]

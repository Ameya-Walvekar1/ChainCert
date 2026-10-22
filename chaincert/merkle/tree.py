"""
Merkle Tree construction for ChainCert Module 3.

Implements the master specification (Section 6):

    Certificate Hashes -> Pair hashes -> Hash each pair
                       -> Repeat level-by-level -> Merkle Root

ODD-LEAF POLICY: PROMOTE THE UNPAIRED NODE UNCHANGED.

The master specification does not define odd-leaf handling, so this is a
documented engineering decision, applied identically at EVERY level.

    [H1, H2, H3]   ->   [H(H1+H2), H3]   ->   [H(H(H1+H2)+H3)]

The rejected alternative is duplicating the last node, which introduces a real
collision: under duplicate-last, the three-leaf batch ``[H1, H2, H3]`` and the
four-leaf batch ``[H1, H2, H3, H3]`` both reduce to ``H(H(H1+H2) + H(H3+H3))``
and therefore produce an IDENTICAL root from two different certificate sets.
This is the flaw recorded as CVE-2012-2459 in Bitcoin's Merkle implementation.
Promoting the unpaired node avoids it: the two batches above produce
``H(H12 + H3)`` and ``H(H12 + H33)`` respectively, which differ.
"""

from typing import List, Sequence

from chaincert.merkle.hashing_backend import hash_pair
from chaincert.merkle.models import MerkleTree
from chaincert.merkle.validator import validate_leaf_hashes


def reduce_level(level: Sequence[str]) -> List[str]:
    """Reduce one tree level to the level above it.

    Nodes are consumed left to right in pairs. If the level holds an odd number
    of nodes, the final unpaired node is carried up unchanged (promoted).

    Args:
        level: Digests at the current level. Must be non-empty.

    Returns:
        The digests at the next level up. Length is ``ceil(len(level) / 2)``.

    Raises:
        ValueError: If the level is empty.
    """
    if not level:
        raise ValueError("Cannot reduce an empty tree level.")

    parents: List[str] = []

    for index in range(0, len(level) - 1, 2):
        parents.append(hash_pair(level[index], level[index + 1]))

    # Odd count: the last node had no partner. Promote it unchanged.
    if len(level) % 2 == 1:
        parents.append(level[-1])

    return parents


def build_merkle_tree(leaf_hashes: Sequence[str]) -> MerkleTree:
    """Build a Merkle tree from a batch of certificate hashes.

    This is Module 3's primary entry point and the consumer of Module 2's
    output. Leaf order is preserved exactly as supplied; the list is never
    sorted.

    Single-leaf batches: the root IS the leaf digest, unhashed. There is no
    pair to combine, and hashing a lone leaf again would add a special case
    without adding integrity.

    Args:
        leaf_hashes: Certificate hashes from Module 2, each 64 hex characters.
            Accepted in any case; normalized to lowercase.

    Returns:
        A :class:`MerkleTree` exposing ``merkle_root``, ``leaves``, ``levels``,
        ``leaf_count`` and ``height``.

    Raises:
        EmptyLeafListError: If ``leaf_hashes`` is empty.
        InvalidHashError: If any element is not a valid SHA-256 hex digest.

    Example:
        >>> tree = build_merkle_tree([h1, h2, h3, h4])
        >>> tree.merkle_root
        '9f2c...'
        >>> tree.height
        2
    """
    leaves = validate_leaf_hashes(leaf_hashes)

    levels: List[List[str]] = [leaves]

    while len(levels[-1]) > 1:
        levels.append(reduce_level(levels[-1]))

    return MerkleTree(levels=levels)


def compute_merkle_root(leaf_hashes: Sequence[str]) -> str:
    """Convenience wrapper returning only the Merkle root.

    Equivalent to ``build_merkle_tree(leaf_hashes).merkle_root``. Provided for
    callers that need the batch fingerprint and nothing else.
    """
    return build_merkle_tree(leaf_hashes).merkle_root


__all__ = ["reduce_level", "build_merkle_tree", "compute_merkle_root"]

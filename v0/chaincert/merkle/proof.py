"""
Merkle Proof generation and verification for ChainCert Module 3.

A Merkle proof answers one question: "is this certificate hash a member of the
batch summarized by this Merkle root?" It answers it without revealing the
other certificates in the batch and without needing the tree.

Proof format (standardized per master specification Section 22, Rule 7):

    [
        {"hash": "<64 hex>", "position": "left" | "right"},
        ...
    ]

``position`` is the position of the SIBLING relative to the node being folded:

    "right" -> parent = SHA256(current + sibling)
    "left"  -> parent = SHA256(sibling + current)

Steps are ordered from the leaf level upward.
"""

from typing import Any, Dict, List, Sequence, Union

from chaincert.merkle.exceptions import InvalidProofError, LeafNotFoundError
from chaincert.merkle.hashing_backend import hash_pair
from chaincert.merkle.models import MerkleTree, ProofStep
from chaincert.merkle.validator import validate_hash, validate_leaf_index

#: A proof may be supplied either as ProofStep objects or as plain dicts
#: (for example, after a JSON round-trip through Module 1's database).
ProofInput = Sequence[Union[ProofStep, Dict[str, Any]]]


def generate_proof(tree: MerkleTree, leaf_index: int) -> List[ProofStep]:
    """Generate the Merkle proof for the leaf at ``leaf_index``.

    Walks from the leaf to the root. At each level the node's sibling is
    recorded, along with which side that sibling sits on. When a node was
    promoted (it was the unpaired last node at an odd-sized level) it has no
    sibling at that level, so no step is recorded and the walk simply continues
    upward. Proof length is therefore at most ``tree.height`` and may be shorter
    for promoted nodes.

    Args:
        tree: The tree the leaf belongs to.
        leaf_index: Zero-based position of the leaf.

    Returns:
        Ordered proof steps, leaf level first.

    Raises:
        InvalidProofError: If ``leaf_index`` is not an integer in range.
    """
    validate_leaf_index(leaf_index, tree.leaf_count)

    proof: List[ProofStep] = []
    index = leaf_index

    # Walk every level except the root level.
    for level in tree.levels[:-1]:
        is_last_and_unpaired = (index == len(level) - 1) and (len(level) % 2 == 1)

        if not is_last_and_unpaired:
            if index % 2 == 0:
                # Current node is a left child; its sibling is on the right.
                proof.append(ProofStep(hash=level[index + 1], position="right"))
            else:
                # Current node is a right child; its sibling is on the left.
                proof.append(ProofStep(hash=level[index - 1], position="left"))

        index //= 2

    return proof


def generate_proof_for_hash(tree: MerkleTree, leaf_hash: str) -> List[ProofStep]:
    """Generate a Merkle proof by leaf digest rather than by index.

    Module 5 (Verification Engine) will hold a recalculated certificate hash
    rather than a batch position, so this is the lookup it will use.

    If the same digest appears more than once in the batch, the FIRST matching
    leaf is used. Duplicates are possible in principle only if two certificates
    canonicalize identically, which Module 1's unique ``certificate_id`` is
    expected to prevent.

    Raises:
        InvalidHashError: If ``leaf_hash`` is not a valid digest.
        LeafNotFoundError: If the digest is not in this tree.
    """
    normalized = validate_hash(leaf_hash, label="leaf_hash")
    index = tree.index_of(normalized)

    if index == -1:
        raise LeafNotFoundError(
            f"Leaf hash {normalized[:16]}... is not present in this Merkle tree "
            f"({tree.leaf_count} leaves)."
        )

    return generate_proof(tree, index)


def _coerce_proof(proof: Any) -> List[ProofStep]:
    """Normalize a proof supplied as ProofStep objects and/or dicts."""
    if isinstance(proof, (str, bytes, dict)):
        raise InvalidProofError(
            f"proof must be a list of proof steps, got {type(proof).__name__}."
        )

    if not isinstance(proof, Sequence):
        raise InvalidProofError(
            f"proof must be a list or tuple, got {type(proof).__name__}."
        )

    steps: List[ProofStep] = []
    for position, raw in enumerate(proof):
        if isinstance(raw, ProofStep):
            steps.append(raw)
        elif isinstance(raw, dict):
            steps.append(ProofStep.from_dict(raw))
        else:
            raise InvalidProofError(
                f"proof[{position}] must be a ProofStep or dict, "
                f"got {type(raw).__name__}."
            )

    return steps


def verify_merkle_proof(
    leaf_hash: str,
    proof: ProofInput,
    expected_root: str,
) -> bool:
    """Verify that ``leaf_hash`` belongs to the batch summarized by ``expected_root``.

    This function does NOT take the tree. That is the whole point of a Merkle
    proof: a verifier who holds only the certificate hash, a short proof, and
    the published root can confirm membership without access to the other
    certificates or to the tree structure. Module 5 will call exactly this.

    Algorithm::

        current = leaf_hash
        for step in proof:
            if step.position == "right":  current = SHA256(current + step.hash)
            else:                         current = SHA256(step.hash + current)
        return current == expected_root

    An empty proof is legitimate for a single-leaf batch, where the leaf is
    itself the root.

    Args:
        leaf_hash: The certificate hash whose membership is claimed.
        proof: Ordered proof steps, leaf level first.
        expected_root: The trusted Merkle root to check against.

    Returns:
        True only if the fold reproduces ``expected_root`` exactly.

    Raises:
        InvalidHashError: If ``leaf_hash`` or ``expected_root`` is malformed.
        InvalidProofError: If the proof structure is malformed.

    Note:
        Malformed input raises rather than returning False, so that a broken
        proof is never mistaken for a genuine tamper finding. A well-formed
        proof that simply does not reconstruct the root returns False.
    """
    current = validate_hash(leaf_hash, label="leaf_hash")
    root = validate_hash(expected_root, label="expected_root")
    steps = _coerce_proof(proof)

    for step in steps:
        if step.sibling_is_left:
            current = hash_pair(step.hash, current)
        else:
            current = hash_pair(current, step.hash)

    return current == root


def proof_to_dicts(proof: Sequence[ProofStep]) -> List[Dict[str, str]]:
    """Serialize a proof for storage or transport (for example, as JSON)."""
    return [step.to_dict() for step in proof]


def proof_from_dicts(data: Sequence[Dict[str, Any]]) -> List[ProofStep]:
    """Rebuild a proof from its serialized form."""
    return _coerce_proof(data)


__all__ = [
    "generate_proof",
    "generate_proof_for_hash",
    "verify_merkle_proof",
    "proof_to_dicts",
    "proof_from_dicts",
]

"""
ChainCert Module 3: Merkle Tree Builder — Package Exports.
"""

from chaincert.merkle.models import (
    MerkleTree,
    ProofStep,
    MERKLE_SPEC_VERSION,
    ODD_LEAF_POLICY,
)
from chaincert.merkle.tree import (
    build_merkle_tree,
    compute_merkle_root,
    reduce_level,
)
from chaincert.merkle.proof import (
    generate_proof,
    generate_proof_for_hash,
    verify_merkle_proof,
    proof_to_dicts,
    proof_from_dicts,
)
from chaincert.merkle.validator import (
    validate_hash,
    validate_leaf_hashes,
    validate_position,
    validate_leaf_index,
    HEX_64_REGEX,
    VALID_POSITIONS,
)
from chaincert.merkle.exceptions import (
    ChainCertError,
    MerkleError,
    InvalidHashError,
    EmptyLeafListError,
    InvalidProofError,
    LeafNotFoundError,
)

__all__ = [
    "MerkleTree",
    "ProofStep",
    "MERKLE_SPEC_VERSION",
    "ODD_LEAF_POLICY",
    "build_merkle_tree",
    "compute_merkle_root",
    "reduce_level",
    "generate_proof",
    "generate_proof_for_hash",
    "verify_merkle_proof",
    "proof_to_dicts",
    "proof_from_dicts",
    "validate_hash",
    "validate_leaf_hashes",
    "validate_position",
    "validate_leaf_index",
    "HEX_64_REGEX",
    "VALID_POSITIONS",
    "ChainCertError",
    "MerkleError",
    "InvalidHashError",
    "EmptyLeafListError",
    "InvalidProofError",
    "LeafNotFoundError",
]

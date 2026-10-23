"""
ChainCert Module 4: Block Chaining — Package Exports.
"""

from chaincert.chain.models import Block, CHAIN_SPEC_VERSION
from chaincert.chain.chain import Chain, ChainValidationResult
from chaincert.chain.storage import save_chain, load_chain
from chaincert.chain.hashing_backend import compute_block_hash
from chaincert.chain.exceptions import (
    ChainCertError,
    ChainError,
    InvalidBlockError,
    EmptyChainError,
    BlockNotFoundError,
    ChainStorageError,
    ChainTamperError,
)

__all__ = [
    "Block",
    "CHAIN_SPEC_VERSION",
    "Chain",
    "ChainValidationResult",
    "save_chain",
    "load_chain",
    "compute_block_hash",
    "ChainCertError",
    "ChainError",
    "InvalidBlockError",
    "EmptyChainError",
    "BlockNotFoundError",
    "ChainStorageError",
    "ChainTamperError",
]

"""Shared fixtures for the Module 3 test suite."""

import sys
from pathlib import Path

import pytest

# Locate Module 2.
M2_ROOT = Path(__file__).resolve().parents[2].parent / "ChainCert-module2-main"
M2_CHAINCERT = M2_ROOT / "chaincert"

# Make Module 2's chaincert subpackages available alongside Module 3's.
import chaincert

if str(M2_CHAINCERT) not in chaincert.__path__:
    chaincert.__path__.append(str(M2_CHAINCERT))

from chaincert.hashing import generate_sha256


def make_hash(seed: str) -> str:
    """Produce a deterministic, real 64-hex digest via Module 2."""
    return generate_sha256(seed)


@pytest.fixture
def h():
    """Factory producing deterministic leaf hashes: h('a'), h('b'), ..."""
    return make_hash


@pytest.fixture
def leaves4(h):
    return [h("cert-1"), h("cert-2"), h("cert-3"), h("cert-4")]


@pytest.fixture
def leaves3(h):
    return [h("cert-1"), h("cert-2"), h("cert-3")]


@pytest.fixture
def leaves5(h):
    return [h(f"cert-{i}") for i in range(1, 6)]
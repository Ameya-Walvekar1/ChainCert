"""Tests for chaincert.chain.chain.Chain.validate_chain — tamper detection.

Every test here builds a genuine, valid chain first, then corrupts exactly
one thing about it using ``dataclasses.replace`` + ``Chain.replace_block``
(see ``Block.create`` and ``Chain.replace_block`` docstrings for why that is
the supported way to build a tamper-test fixture), and checks that
``validate_chain()`` reports it.
"""

import dataclasses

import pytest

from chaincert.chain import Chain, ChainTamperError


def _valid_three_block_chain(h) -> Chain:
    chain = Chain()
    chain.add_batch(batch_id="SEM1_2026", merkle_root=h("root-a"), certificate_count=10)
    chain.add_batch(batch_id="SEM2_2026", merkle_root=h("root-b"), certificate_count=10)
    chain.add_batch(batch_id="SEM3_2026", merkle_root=h("root-c"), certificate_count=10)
    return chain


def test_broken_previous_root_link_is_invalid(h):
    chain = _valid_three_block_chain(h)
    original_b2 = chain.get_block(2)

    fake_root = h("fake-root")
    tampered_b2 = dataclasses.replace(original_b2, previous_root=fake_root)
    chain.replace_block(2, tampered_b2)

    result = chain.validate_chain()

    assert not result.is_valid
    assert any("Block 2" in error for error in result.errors)


def test_modified_merkle_root_on_earlier_block_is_invalid(h):
    """Changing block 1's root should break block 2's linkage to it."""
    chain = _valid_three_block_chain(h)
    original_b1 = chain.get_block(1)

    tampered_b1 = dataclasses.replace(original_b1, merkle_root=h("swapped-root"))
    chain.replace_block(1, tampered_b1)

    result = chain.validate_chain()

    assert not result.is_valid
    # Block 1's own stored fields no longer match its block_hash...
    assert any("Block 1" in error for error in result.errors)
    # ...and block 2's previous_root no longer matches block 1's new root.
    assert any("Block 2" in error for error in result.errors)


def test_tampered_batch_information_is_caught_by_block_hash(h):
    """previous_root linkage alone would miss this; block_hash catches it."""
    chain = _valid_three_block_chain(h)
    original_b3 = chain.get_block(3)

    tampered_b3 = dataclasses.replace(original_b3, certificate_count=99999)
    chain.replace_block(3, tampered_b3)

    result = chain.validate_chain()

    assert not result.is_valid
    assert any("Block 3" in error and "block_hash" in error for error in result.errors)


def test_untampered_chain_remains_valid_after_unrelated_reads(h):
    """Sanity check: validation itself must not be destructive."""
    chain = _valid_three_block_chain(h)

    first = chain.validate_chain()
    second = chain.validate_chain()

    assert first.is_valid and second.is_valid


def test_raise_on_failure_raises_chain_tamper_error(h):
    chain = _valid_three_block_chain(h)
    original_b2 = chain.get_block(2)
    tampered_b2 = dataclasses.replace(original_b2, previous_root=h("fake-root"))
    chain.replace_block(2, tampered_b2)

    with pytest.raises(ChainTamperError):
        chain.validate_chain(raise_on_failure=True)

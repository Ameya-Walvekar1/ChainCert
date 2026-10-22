"""Tests for chaincert.chain.chain.Chain.validate_chain — the happy paths."""

from chaincert.chain import Chain


def test_empty_chain_is_valid():
    result = Chain().validate_chain()
    assert result.is_valid
    assert result.errors == []


def test_single_block_chain_is_valid(h):
    chain = Chain()
    chain.add_batch(batch_id="SEM1_2026", merkle_root=h("root-a"), certificate_count=10)

    result = chain.validate_chain()
    assert result.is_valid
    assert bool(result) is True


def test_three_block_chain_with_correct_linkage_is_valid(h):
    """Block 1 -> Root A; Block 2 -> Root B (prev A); Block 3 -> Root C (prev B)."""
    chain = Chain()
    chain.add_batch(batch_id="SEM1_2026", merkle_root=h("root-a"), certificate_count=10)
    chain.add_batch(batch_id="SEM2_2026", merkle_root=h("root-b"), certificate_count=10)
    chain.add_batch(batch_id="SEM3_2026", merkle_root=h("root-c"), certificate_count=10)

    result = chain.validate_chain()

    assert result.is_valid
    assert result.errors == []

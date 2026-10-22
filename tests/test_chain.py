"""Tests for chaincert.chain.chain.Chain — creation and linkage."""

from chaincert.chain import Chain, BlockNotFoundError
import pytest


def test_new_chain_is_empty():
    chain = Chain()
    assert len(chain) == 0
    assert chain.latest_block is None
    assert chain.blocks == []


def test_first_block_previous_root_is_none(h):
    chain = Chain()
    block = chain.add_batch(
        batch_id="SEM1_2026", merkle_root=h("root-a"), certificate_count=10
    )

    assert block.block_id == 1
    assert block.previous_root is None
    assert chain.latest_block == block
    assert len(chain) == 1


def test_second_block_previous_root_matches_first_root(h):
    chain = Chain()
    b1 = chain.add_batch(
        batch_id="SEM1_2026", merkle_root=h("root-a"), certificate_count=10
    )
    b2 = chain.add_batch(
        batch_id="SEM2_2026", merkle_root=h("root-b"), certificate_count=8
    )

    assert b2.block_id == 2
    assert b2.previous_root == b1.merkle_root


def test_multiple_batches_chain_correctly(h):
    """Root1 -> Block1; Root2 -> Block2.previous_root = Root1; etc."""
    chain = Chain()
    roots = [h(f"root-{i}") for i in range(3)]

    blocks = [
        chain.add_batch(
            batch_id=f"SEM{i + 1}_2026", merkle_root=root, certificate_count=10
        )
        for i, root in enumerate(roots)
    ]

    assert [b.merkle_root for b in blocks] == roots
    assert blocks[0].previous_root is None
    assert blocks[1].previous_root == roots[0]
    assert blocks[2].previous_root == roots[1]
    assert [b.block_id for b in blocks] == [1, 2, 3]


def test_get_block_by_id(h):
    chain = Chain()
    chain.add_batch(batch_id="SEM1_2026", merkle_root=h("root-a"), certificate_count=10)
    b2 = chain.add_batch(batch_id="SEM2_2026", merkle_root=h("root-b"), certificate_count=5)

    assert chain.get_block(2) == b2


def test_get_missing_block_raises():
    chain = Chain()
    with pytest.raises(BlockNotFoundError):
        chain.get_block(1)


def test_chain_is_iterable(h):
    chain = Chain()
    chain.add_batch(batch_id="SEM1_2026", merkle_root=h("root-a"), certificate_count=10)
    chain.add_batch(batch_id="SEM2_2026", merkle_root=h("root-b"), certificate_count=10)

    assert [b.block_id for b in chain] == [1, 2]


def test_chain_persists_to_and_loads_from_json(tmp_path, h):
    path = tmp_path / "chain.json"

    chain = Chain(storage_path=path)
    chain.add_batch(batch_id="SEM1_2026", merkle_root=h("root-a"), certificate_count=10)
    chain.add_batch(batch_id="SEM2_2026", merkle_root=h("root-b"), certificate_count=8)

    assert path.exists()

    reloaded = Chain(storage_path=path)
    assert len(reloaded) == 2
    assert reloaded.latest_block.batch_id == "SEM2_2026"
    assert reloaded.validate_chain().is_valid

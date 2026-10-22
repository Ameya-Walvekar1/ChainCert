"""Tests for chaincert.chain.models.Block."""

import dataclasses

import pytest

from chaincert.chain import Block, InvalidBlockError
from chaincert.merkle.exceptions import InvalidHashError


def test_first_block_has_no_previous_root(h):
    root = h("root-a")
    block = Block.create(
        block_id=1,
        batch_id="SEM1_2026",
        certificate_count=10,
        merkle_root=root,
        previous_root=None,
    )

    assert block.previous_root is None
    assert block.merkle_root == root
    assert block.block_id == 1
    assert block.certificate_count == 10


def test_block_hash_is_deterministic_for_same_fields(h):
    root = h("root-a")
    b1 = Block.create(
        block_id=1,
        batch_id="SEM1_2026",
        certificate_count=10,
        merkle_root=root,
        previous_root=None,
        timestamp="2026-01-01T00:00:00+00:00",
    )
    b2 = Block.create(
        block_id=1,
        batch_id="SEM1_2026",
        certificate_count=10,
        merkle_root=root,
        previous_root=None,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    assert b1.block_hash == b2.block_hash
    assert len(b1.block_hash) == 64


def test_block_hash_changes_if_any_field_changes(h):
    root = h("root-a")
    base = Block.create(
        block_id=1,
        batch_id="SEM1_2026",
        certificate_count=10,
        merkle_root=root,
        previous_root=None,
        timestamp="2026-01-01T00:00:00+00:00",
    )
    different_batch = Block.create(
        block_id=1,
        batch_id="SEM1_2026_RESIT",
        certificate_count=10,
        merkle_root=root,
        previous_root=None,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    assert base.block_hash != different_batch.block_hash


def test_invalid_merkle_root_is_rejected():
    with pytest.raises(InvalidHashError):
        Block.create(
            block_id=1,
            batch_id="SEM1_2026",
            certificate_count=10,
            merkle_root="not-a-real-hash",
            previous_root=None,
        )


def test_invalid_certificate_count_is_rejected(h):
    with pytest.raises(InvalidBlockError):
        Block.create(
            block_id=1,
            batch_id="SEM1_2026",
            certificate_count=0,
            merkle_root=h("root-a"),
            previous_root=None,
        )


def test_empty_batch_id_is_rejected(h):
    with pytest.raises(InvalidBlockError):
        Block.create(
            block_id=1,
            batch_id="   ",
            certificate_count=10,
            merkle_root=h("root-a"),
            previous_root=None,
        )


def test_to_dict_and_from_dict_round_trip(h):
    block = Block.create(
        block_id=2,
        batch_id="SEM2_2026",
        certificate_count=5,
        merkle_root=h("root-b"),
        previous_root=h("root-a"),
    )

    restored = Block.from_dict(block.to_dict())

    assert restored == block


def test_from_dict_does_not_recompute_hash(h):
    """from_dict must reproduce exactly what was stored, tampered or not."""
    block = Block.create(
        block_id=1,
        batch_id="SEM1_2026",
        certificate_count=10,
        merkle_root=h("root-a"),
        previous_root=None,
    )

    corrupted = block.to_dict()
    corrupted["certificate_count"] = 999  # edited directly, hash left stale

    restored = Block.from_dict(corrupted)

    assert restored.certificate_count == 999
    assert restored.block_hash == block.block_hash  # stale hash preserved
    assert restored.recompute_hash() != restored.block_hash  # now detectable


def test_dataclasses_replace_produces_a_tampered_block_with_stale_hash(h):
    """The documented pattern for building a tamper-test fixture."""
    original = Block.create(
        block_id=2,
        batch_id="SEM2_2026",
        certificate_count=10,
        merkle_root=h("root-b"),
        previous_root=h("root-a"),
    )

    tampered = dataclasses.replace(original, previous_root=h("fake-root"))

    assert tampered.block_hash == original.block_hash
    assert tampered.recompute_hash() != tampered.block_hash

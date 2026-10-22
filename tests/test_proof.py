"""Merkle proof generation and verification tests."""

import pytest

from chaincert.merkle import (
    InvalidHashError,
    InvalidProofError,
    LeafNotFoundError,
    ProofStep,
    build_merkle_tree,
    generate_proof,
    generate_proof_for_hash,
    proof_from_dicts,
    proof_to_dicts,
    verify_merkle_proof,
)


@pytest.mark.parametrize("index", [0, 1, 2, 3])
def test_proof_verifies_for_every_leaf(leaves4, index):
    tree = build_merkle_tree(leaves4)
    proof = generate_proof(tree, index)
    assert verify_merkle_proof(leaves4[index], proof, tree.merkle_root) is True


def test_proof_length_equals_height_for_power_of_two(leaves4):
    tree = build_merkle_tree(leaves4)
    assert len(generate_proof(tree, 0)) == tree.height == 2


def test_promoted_leaf_has_shorter_proof(leaves3):
    """The unpaired third leaf has no sibling at level 0, so one fewer step."""
    tree = build_merkle_tree(leaves3)
    assert len(generate_proof(tree, 2)) == 1
    assert len(generate_proof(tree, 0)) == 2
    assert verify_merkle_proof(leaves3[2], generate_proof(tree, 2), tree.merkle_root)


@pytest.mark.parametrize("index", [0, 1, 2, 3, 4])
def test_odd_tree_proofs_all_verify(leaves5, index):
    tree = build_merkle_tree(leaves5)
    proof = generate_proof(tree, index)
    assert verify_merkle_proof(leaves5[index], proof, tree.merkle_root) is True


def test_single_leaf_proof_is_empty(h):
    leaf = h("solo")
    tree = build_merkle_tree([leaf])
    proof = generate_proof(tree, 0)
    assert proof == []
    assert verify_merkle_proof(leaf, proof, tree.merkle_root) is True


def test_sibling_position_semantics(leaves4):
    """Leaf 0 is a left child, so its sibling must be recorded as 'right'."""
    tree = build_merkle_tree(leaves4)
    assert generate_proof(tree, 0)[0].position == "right"
    assert generate_proof(tree, 1)[0].position == "left"


def test_modified_leaf_fails(leaves4, h):
    tree = build_merkle_tree(leaves4)
    proof = generate_proof(tree, 1)
    assert verify_merkle_proof(h("forged"), proof, tree.merkle_root) is False


def test_modified_sibling_fails(leaves4, h):
    tree = build_merkle_tree(leaves4)
    proof = generate_proof(tree, 1)
    tampered = [ProofStep(hash=h("evil"), position=proof[0].position)] + proof[1:]
    assert verify_merkle_proof(leaves4[1], tampered, tree.merkle_root) is False


def test_flipped_position_fails(leaves4):
    tree = build_merkle_tree(leaves4)
    proof = generate_proof(tree, 1)
    flipped = [ProofStep(hash=proof[0].hash, position="right")] + proof[1:]
    assert verify_merkle_proof(leaves4[1], flipped, tree.merkle_root) is False


def test_wrong_root_fails(leaves4, h):
    tree = build_merkle_tree(leaves4)
    proof = generate_proof(tree, 0)
    assert verify_merkle_proof(leaves4[0], proof, h("wrong-root")) is False


def test_malformed_proof_raises(leaves4):
    tree = build_merkle_tree(leaves4)
    with pytest.raises(InvalidProofError):
        verify_merkle_proof(leaves4[0], [{"hash": "abc"}], tree.merkle_root)
    with pytest.raises(InvalidProofError):
        verify_merkle_proof(leaves4[0], ["garbage"], tree.merkle_root)
    with pytest.raises(InvalidProofError):
        verify_merkle_proof(leaves4[0], {"hash": "x"}, tree.merkle_root)


def test_malformed_root_raises(leaves4):
    tree = build_merkle_tree(leaves4)
    with pytest.raises(InvalidHashError):
        verify_merkle_proof(leaves4[0], generate_proof(tree, 0), "not-a-root")


def test_invalid_leaf_index_raises(leaves4):
    tree = build_merkle_tree(leaves4)
    with pytest.raises(InvalidProofError):
        generate_proof(tree, 99)


def test_proof_by_hash_matches_proof_by_index(leaves4):
    tree = build_merkle_tree(leaves4)
    assert generate_proof_for_hash(tree, leaves4[2]) == generate_proof(tree, 2)


def test_proof_for_absent_hash_raises(leaves4, h):
    tree = build_merkle_tree(leaves4)
    with pytest.raises(LeafNotFoundError):
        generate_proof_for_hash(tree, h("never-issued"))


def test_proof_survives_json_round_trip(leaves4):
    tree = build_merkle_tree(leaves4)
    proof = generate_proof(tree, 3)
    restored = proof_from_dicts(proof_to_dicts(proof))
    assert restored == proof
    assert verify_merkle_proof(leaves4[3], restored, tree.merkle_root) is True

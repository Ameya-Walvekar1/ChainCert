"""Tamper-detection tests at the Merkle layer."""

from chaincert.merkle import build_merkle_tree, generate_proof, verify_merkle_proof


def test_any_single_leaf_change_changes_the_root(leaves5, h):
    """Tampering with any position in the batch must surface in the root."""
    baseline = build_merkle_tree(leaves5).merkle_root

    for index in range(len(leaves5)):
        mutated = list(leaves5)
        mutated[index] = h(f"tampered-{index}")
        assert build_merkle_tree(mutated).merkle_root != baseline


def test_old_proof_fails_against_new_root(leaves4, h):
    """A proof issued before tampering must not validate against the new root."""
    original = build_merkle_tree(leaves4)
    proof = generate_proof(original, 1)

    tampered_leaves = list(leaves4)
    tampered_leaves[1] = h("altered-certificate")
    tampered_tree = build_merkle_tree(tampered_leaves)

    assert verify_merkle_proof(leaves4[1], proof, original.merkle_root) is True
    assert verify_merkle_proof(leaves4[1], proof, tampered_tree.merkle_root) is False


def test_tampering_propagates_up_every_level(leaves4, h):
    """A leaf change must alter its parent, not only the final root."""
    original = build_merkle_tree(leaves4)
    mutated = list(leaves4)
    mutated[0] = h("changed")
    tampered = build_merkle_tree(mutated)

    assert original.levels[1][0] != tampered.levels[1][0]
    assert original.levels[1][1] == tampered.levels[1][1]  # untouched subtree
    assert original.merkle_root != tampered.merkle_root


def test_removing_a_certificate_changes_the_root(leaves5):
    full = build_merkle_tree(leaves5).merkle_root
    short = build_merkle_tree(leaves5[:-1]).merkle_root
    assert full != short

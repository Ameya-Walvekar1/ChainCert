"""Merkle root property tests: determinism, format, sensitivity."""

from chaincert.merkle import HEX_64_REGEX, build_merkle_tree, compute_merkle_root


def test_root_is_deterministic_across_many_runs(leaves4):
    roots = {build_merkle_tree(leaves4).merkle_root for _ in range(100)}
    assert len(roots) == 1


def test_root_is_64_hex_characters(leaves5):
    root = build_merkle_tree(leaves5).merkle_root
    assert len(root) == 64
    assert HEX_64_REGEX.match(root)


def test_root_is_lowercase(leaves4):
    root = build_merkle_tree(leaves4).merkle_root
    assert root == root.lower()


def test_uppercase_input_produces_same_root(leaves4):
    lower = build_merkle_tree(leaves4).merkle_root
    upper = build_merkle_tree([x.upper() for x in leaves4]).merkle_root
    assert lower == upper


def test_changing_one_leaf_changes_root(leaves4, h):
    original = build_merkle_tree(leaves4).merkle_root
    modified = build_merkle_tree(leaves4[:3] + [h("different")]).merkle_root
    assert original != modified


def test_changing_leaf_order_changes_root(leaves4):
    original = build_merkle_tree(leaves4).merkle_root
    swapped = build_merkle_tree(
        [leaves4[1], leaves4[0], leaves4[2], leaves4[3]]
    ).merkle_root
    assert original != swapped


def test_compute_merkle_root_matches_tree(leaves5):
    assert compute_merkle_root(leaves5) == build_merkle_tree(leaves5).merkle_root


def test_to_dict_output_contract(leaves4):
    payload = build_merkle_tree(leaves4).to_dict()
    assert payload["certificate_count"] == 4
    assert payload["odd_leaf_policy"] == "promote-unpaired"
    assert len(payload["merkle_root"]) == 64

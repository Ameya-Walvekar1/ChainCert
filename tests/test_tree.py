"""Tree construction tests, including odd-leaf promotion at every level."""

import pytest

from chaincert.merkle import (
    EmptyLeafListError,
    InvalidHashError,
    build_merkle_tree,
    reduce_level,
)
from chaincert.merkle.hashing_backend import hash_pair


def test_single_leaf_root_is_the_leaf(h):
    leaf = h("only-cert")
    tree = build_merkle_tree([leaf])
    assert tree.merkle_root == leaf
    assert tree.leaf_count == 1
    assert tree.height == 0


def test_two_leaves(h):
    a, b = h("a"), h("b")
    tree = build_merkle_tree([a, b])
    assert tree.merkle_root == hash_pair(a, b)
    assert tree.height == 1


def test_four_leaves_structure(leaves4):
    tree = build_merkle_tree(leaves4)
    h1, h2, h3, h4 = leaves4
    expected = hash_pair(hash_pair(h1, h2), hash_pair(h3, h4))
    assert tree.merkle_root == expected
    assert tree.height == 2
    assert [len(level) for level in tree.levels] == [4, 2, 1]


def test_eight_leaves_height(h):
    tree = build_merkle_tree([h(f"c{i}") for i in range(8)])
    assert tree.height == 3
    assert [len(level) for level in tree.levels] == [8, 4, 2, 1]


def test_three_leaves_promotes_unpaired_node(leaves3):
    """Odd leaf count: H3 is carried up unchanged, not duplicated."""
    tree = build_merkle_tree(leaves3)
    h1, h2, h3 = leaves3
    assert tree.levels[1] == [hash_pair(h1, h2), h3]
    assert tree.merkle_root == hash_pair(hash_pair(h1, h2), h3)


def test_five_leaves_hits_odd_count_at_two_levels(leaves5):
    """5 -> 3 -> 2 -> 1: promotion must apply at level 0 AND level 1."""
    tree = build_merkle_tree(leaves5)
    assert [len(level) for level in tree.levels] == [5, 3, 2, 1]


def test_larger_odd_count(h):
    tree = build_merkle_tree([h(f"c{i}") for i in range(13)])
    assert [len(level) for level in tree.levels] == [13, 7, 4, 2, 1]
    assert len(tree.merkle_root) == 64


def test_promotion_avoids_duplicate_last_collision(leaves3):
    """The CVE-2012-2459 case.

    Under a duplicate-last policy, [H1,H2,H3] and [H1,H2,H3,H3] would produce
    the same root from two different certificate sets. Promotion must keep them
    distinct.
    """
    h1, h2, h3 = leaves3
    root_three = build_merkle_tree([h1, h2, h3]).merkle_root
    root_four = build_merkle_tree([h1, h2, h3, h3]).merkle_root
    assert root_three != root_four


def test_empty_list_raises(leaves4):
    with pytest.raises(EmptyLeafListError):
        build_merkle_tree([])


def test_invalid_leaf_raises(leaves4):
    with pytest.raises(InvalidHashError):
        build_merkle_tree(leaves4[:3] + ["not-a-hash"])


def test_reduce_empty_level_raises():
    with pytest.raises(ValueError):
        reduce_level([])

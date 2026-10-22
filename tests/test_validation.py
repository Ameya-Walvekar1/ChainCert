"""Validation layer tests: hash structure, leaf lists, positions, indices."""

import pytest

from chaincert.merkle import (
    EmptyLeafListError,
    InvalidHashError,
    InvalidProofError,
    validate_hash,
    validate_leaf_hashes,
    validate_leaf_index,
    validate_position,
)


def test_valid_64_char_hash_accepted(h):
    digest = h("anything")
    assert validate_hash(digest) == digest


def test_short_hash_rejected():
    with pytest.raises(InvalidHashError):
        validate_hash("a" * 63)


def test_long_hash_rejected():
    with pytest.raises(InvalidHashError):
        validate_hash("a" * 65)


def test_non_hex_hash_rejected():
    with pytest.raises(InvalidHashError):
        validate_hash("z" * 64)


def test_non_string_hash_rejected():
    with pytest.raises(InvalidHashError):
        validate_hash(12345)


def test_uppercase_hash_normalized_to_lowercase(h):
    digest = h("cert-1")
    assert validate_hash(digest.upper()) == digest


def test_surrounding_whitespace_stripped(h):
    digest = h("cert-1")
    assert validate_hash(f"  {digest}  ") == digest


def test_empty_leaf_list_rejected():
    with pytest.raises(EmptyLeafListError):
        validate_leaf_hashes([])


def test_single_string_is_not_a_leaf_list(h):
    with pytest.raises(InvalidHashError):
        validate_leaf_hashes(h("cert-1"))


def test_leaf_list_preserves_order(leaves4):
    assert validate_leaf_hashes(leaves4) == leaves4


def test_position_must_be_left_or_right():
    assert validate_position("LEFT") == "left"
    with pytest.raises(InvalidProofError):
        validate_position("middle")


def test_leaf_index_bounds():
    assert validate_leaf_index(0, 4) == 0
    with pytest.raises(InvalidProofError):
        validate_leaf_index(4, 4)
    with pytest.raises(InvalidProofError):
        validate_leaf_index(-1, 4)
    with pytest.raises(InvalidProofError):
        validate_leaf_index("2", 4)

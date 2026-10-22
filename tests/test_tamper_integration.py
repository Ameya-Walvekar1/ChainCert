"""
Integration test verifying tamper detection across certificate data and block headers.
"""

import pytest
import os
import tempfile
import dataclasses
from pathlib import Path

from chaincert.records import (
    init_db,
    add_certificate,
    get_certificate,
    update_certificate,
    parse_certificate_file,
)
from chaincert.hashing import hash_certificate, compare_hashes
from chaincert.merkle import (
    build_merkle_tree,
    verify_merkle_proof,
    generate_proof_for_hash,
)
from chaincert.chain import Chain, ChainTamperError


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_certificate_data_tamper_detection(temp_db):
    test_cert_dir = Path(__file__).resolve().parent.parent / "test_certificates"
    cert_1 = parse_certificate_file(str(test_cert_dir / "certificate1.txt"))
    cert_2 = parse_certificate_file(str(test_cert_dir / "certificate2.txt"))

    # Original certificates registered
    rec1 = add_certificate(cert_1, db_path=temp_db)
    rec2 = add_certificate(cert_2, db_path=temp_db)

    orig_hashes = [rec1["certificate_hash"], rec2["certificate_hash"]]
    orig_tree = build_merkle_tree(orig_hashes)

    proof1 = generate_proof_for_hash(orig_tree, rec1["certificate_hash"])
    assert verify_merkle_proof(rec1["certificate_hash"], proof1, orig_tree.merkle_root) is True

    # TAMPER: Alter CGPA of Certificate 1 in database (9.20 -> 9.99)
    tampered_rec1 = update_certificate("CC001", {"cgpa": "9.99"}, db_path=temp_db)

    # Re-calculate hash
    new_hash = tampered_rec1["certificate_hash"]
    assert new_hash != rec1["certificate_hash"]
    assert compare_hashes(new_hash, rec1["certificate_hash"]) is False

    # Proof against original root MUST FAIL
    assert verify_merkle_proof(new_hash, proof1, orig_tree.merkle_root) is False

    # Rebuilding tree with tampered hash produces DIFFERENT Merkle root
    new_tree = build_merkle_tree([new_hash, rec2["certificate_hash"]])
    assert new_tree.merkle_root != orig_tree.merkle_root


def test_block_chain_tamper_detection():
    # Setup chain with 2 blocks
    tree_1 = build_merkle_tree(["a" * 64, "b" * 64])
    tree_2 = build_merkle_tree(["c" * 64, "d" * 64])

    chain = Chain()
    block_1 = chain.add_batch(batch_id="BATCH_1", merkle_root=tree_1.merkle_root, certificate_count=2)
    block_2 = chain.add_batch(batch_id="BATCH_2", merkle_root=tree_2.merkle_root, certificate_count=2)

    # Initial chain is valid
    val_orig = chain.validate_chain()
    assert val_orig.is_valid is True

    # TAMPER: Forcibly overwrite previous_root in Block 2
    fake_prev_root = "f" * 64
    tampered_block_2 = dataclasses.replace(block_2, previous_root=fake_prev_root)
    chain.replace_block(2, tampered_block_2)

    # Validate chain after tampering
    val_tampered = chain.validate_chain()
    assert val_tampered.is_valid is False
    assert len(val_tampered.errors) > 0
    assert "previous_root" in val_tampered.errors[0] or "stored block_hash" in val_tampered.errors[0]

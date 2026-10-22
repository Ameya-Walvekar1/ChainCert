"""
Integration test verifying the end-to-end pipeline across Modules 1, 2, 3, and 4.
"""

import pytest
import os
import tempfile
from pathlib import Path

from chaincert.records import (
    init_db,
    add_certificate,
    get_certificate,
    list_certificates,
    assign_batch_and_proofs,
    update_batch_block_id,
    parse_certificate_file,
)
from chaincert.hashing import hash_certificate
from chaincert.merkle import (
    build_merkle_tree,
    generate_proof_for_hash,
    verify_merkle_proof,
    proof_to_dicts,
)
from chaincert.chain import Chain


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_full_pipeline_m1_m2_m3_m4(temp_db):
    test_cert_dir = Path(__file__).resolve().parent.parent / "test_certificates"
    cert_files = [
        test_cert_dir / "certificate1.txt",
        test_cert_dir / "certificate2.txt",
        test_cert_dir / "certificate3.txt",
        test_cert_dir / "certificate4.txt",
    ]

    # STEP 1: Module 1 loads text files and stores certificates in SQLite
    # STEP 2: Module 1 automatically calls Module 2 to compute SHA-256 hashes
    added_certs = []
    for file_path in cert_files:
        cert_dict = parse_certificate_file(str(file_path))
        stored = add_certificate(cert_dict, db_path=temp_db)
        added_certs.append(stored)

    assert len(added_certs) == 4
    for cert in added_certs:
        assert cert["certificate_hash"] is not None
        assert len(cert["certificate_hash"]) == 64

    # STEP 3: Module 3 receives certificate hashes from Module 1 / Module 2
    leaf_hashes = [c["certificate_hash"] for c in added_certs]
    tree = build_merkle_tree(leaf_hashes)

    assert tree.leaf_count == 4
    assert len(tree.merkle_root) == 64

    # STEP 4: Module 3 generates Merkle proofs for each certificate
    proof_map = {}
    for cert in added_certs:
        proof = generate_proof_for_hash(tree, cert["certificate_hash"])
        # Verify proof against Merkle root
        assert verify_merkle_proof(cert["certificate_hash"], proof, tree.merkle_root) is True
        proof_map[cert["certificate_id"]] = proof_to_dicts(proof)

    # Save batch and Merkle proofs into Module 1 DB
    batch_id = "SEM1_2026"
    assign_batch_and_proofs(batch_id, tree.merkle_root, proof_map, db_path=temp_db)

    # STEP 5: Module 4 receives Merkle Root and builds Block
    chain = Chain()
    block = chain.add_batch(
        batch_id=batch_id,
        merkle_root=tree.merkle_root,
        certificate_count=tree.leaf_count,
    )

    update_batch_block_id(batch_id, block.block_id, db_path=temp_db)

    assert block.block_id == 1
    assert block.batch_id == batch_id
    assert block.merkle_root == tree.merkle_root
    assert block.previous_root is None

    # STEP 6: Module 4 Chain Validation
    validation_res = chain.validate_chain()
    assert validation_res.is_valid is True
    assert len(validation_res.errors) == 0

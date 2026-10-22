"""End-to-end tests against the REAL Module 2 hashing engine.

No stubs, no fakes: these call Module 2's actual hash_certificate() pipeline.
"""

from chaincert.hashing import hash_certificate
from chaincert.merkle import (
    build_merkle_tree,
    generate_proof_for_hash,
    verify_merkle_proof,
)
from utils.sample_data import get_sample_certificates, tamper_certificate


def leaf_hashes_for(certificates):
    """Exactly the call shape Module 2's INTEGRATION_GUIDE.md prescribes."""
    return [hash_certificate(cert).certificate_hash for cert in certificates]


def test_real_certificates_produce_a_merkle_root():
    certificates = get_sample_certificates(4)
    tree = build_merkle_tree(leaf_hashes_for(certificates))

    assert tree.leaf_count == 4
    assert len(tree.merkle_root) == 64


def test_modifying_a_certificate_changes_the_root():
    """The headline integration test: M2 hash change propagates to M3 root."""
    certificates = get_sample_certificates(4)
    original_root = build_merkle_tree(leaf_hashes_for(certificates)).merkle_root

    tampered = list(certificates)
    tampered[1] = tamper_certificate(tampered[1], field="cgpa", new_value="8.20")
    new_root = build_merkle_tree(leaf_hashes_for(tampered)).merkle_root

    assert original_root != new_root


def test_m2_normalization_does_not_change_the_root():
    """Equivalent-but-differently-formatted input must give an identical root.

    This proves Module 3 inherits Module 2's canonicalization guarantees rather
    than reimplementing them.
    """
    certificates = get_sample_certificates(4)
    original_root = build_merkle_tree(leaf_hashes_for(certificates)).merkle_root

    reformatted = [dict(cert) for cert in certificates]
    reformatted[0]["student_name"] = "  Rahul   Sharma  "
    reformatted[0]["cgpa"] = 9.2
    reformatted[0]["issue_date"] = "20/08/2026"

    assert build_merkle_tree(leaf_hashes_for(reformatted)).merkle_root == original_root


def test_proof_round_trip_with_real_certificate():
    certificates = get_sample_certificates(5)
    hashes = leaf_hashes_for(certificates)
    tree = build_merkle_tree(hashes)

    target = hash_certificate(certificates[2]).certificate_hash
    proof = generate_proof_for_hash(tree, target)

    assert verify_merkle_proof(target, proof, tree.merkle_root) is True


def test_module3_uses_module2_hashing_not_hashlib():
    """Guard against a teammate reintroducing a second SHA-256 implementation."""
    import chaincert.merkle.tree as tree_module
    import chaincert.merkle.proof as proof_module
    import chaincert.merkle.hashing_backend as backend

    assert not hasattr(tree_module, "hashlib")
    assert not hasattr(proof_module, "hashlib")

    from chaincert.hashing import generate_sha256

    assert backend.generate_sha256 is generate_sha256

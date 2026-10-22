"""End-to-end tests: real Module 3 Merkle roots feeding real Module 4 blocks.

No stubs: certificate hashes come from the real Module 2 hashing engine (via
the ``h`` / sample-certificate fixtures already used by Module 3's own
test_m2_integration.py), and Merkle roots come from Module 3's real
``build_merkle_tree``. This is the exact hand-off described in
docs/INTEGRATION_GUIDE.md §3.
"""

from chaincert.hashing import hash_certificate
from chaincert.merkle import build_merkle_tree
from chaincert.chain import Chain
from utils.sample_data import get_sample_certificates, tamper_certificate


def leaf_hashes_for(certificates):
    """Exactly the call shape Module 2's INTEGRATION_GUIDE.md prescribes."""
    return [hash_certificate(cert).certificate_hash for cert in certificates]


def test_module3_root_flows_into_a_module4_block():
    certificates = get_sample_certificates(4)
    tree = build_merkle_tree(leaf_hashes_for(certificates))

    chain = Chain()
    block = chain.add_batch(
        batch_id="SEM1_2026",
        merkle_root=tree.merkle_root,
        certificate_count=tree.leaf_count,
    )

    assert block.merkle_root == tree.merkle_root
    assert block.certificate_count == tree.leaf_count
    assert block.previous_root is None


def test_module3_to_dict_contract_is_accepted_directly():
    """Chain.add_batch should accept tree.to_dict()'s exact field names."""
    certificates = get_sample_certificates(4)
    tree_summary = build_merkle_tree(leaf_hashes_for(certificates)).to_dict()

    chain = Chain()
    block = chain.add_batch(
        batch_id="SEM1_2026",
        merkle_root=tree_summary["merkle_root"],
        certificate_count=tree_summary["certificate_count"],
    )

    assert block.merkle_root == tree_summary["merkle_root"]
    assert block.certificate_count == tree_summary["certificate_count"]


def test_multiple_real_batches_chain_together():
    batch_1 = get_sample_certificates(3)
    batch_2 = get_sample_certificates(5)  # includes the odd-leaf record

    root_1 = build_merkle_tree(leaf_hashes_for(batch_1)).merkle_root
    root_2 = build_merkle_tree(leaf_hashes_for(batch_2)).merkle_root
    assert root_1 != root_2  # different batches, different roots

    chain = Chain()
    block_1 = chain.add_batch(batch_id="SEM1_2026", merkle_root=root_1, certificate_count=3)
    block_2 = chain.add_batch(batch_id="SEM2_2026", merkle_root=root_2, certificate_count=5)

    assert block_2.previous_root == block_1.merkle_root
    assert chain.validate_chain().is_valid


def test_tampering_a_certificate_changes_the_root_and_would_break_a_stored_chain():
    """Ties Module 3's tamper detection to Module 4's: a changed certificate
    produces a different root, so re-deriving it later and comparing against
    the root stored in a Module 4 block reveals the tamper — exactly what
    Module 5 (Verification) will eventually automate.
    """
    certificates = get_sample_certificates(4)
    original_root = build_merkle_tree(leaf_hashes_for(certificates)).merkle_root

    chain = Chain()
    chain.add_batch(batch_id="SEM1_2026", merkle_root=original_root, certificate_count=4)

    tampered = list(certificates)
    tampered[1] = tamper_certificate(tampered[1], field="cgpa", new_value="8.20")
    recomputed_root = build_merkle_tree(leaf_hashes_for(tampered)).merkle_root

    assert recomputed_root != chain.get_block(1).merkle_root

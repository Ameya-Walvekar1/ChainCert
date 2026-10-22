"""Seed a local ChainCert demo account and synthetic certificate fixtures.

Demo credentials are for local demonstration only. Change all secrets before any
public deployment. This script never clears existing certificate or chain data.
"""
import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, ensure_sample_certificates, chain_instance
from chaincert.auth import Role
from chaincert.records import add_certificate, get_certificate, parse_certificate_file, list_certificates, assign_batch_and_proofs, update_batch_block_id
from chaincert.merkle import build_merkle_tree, generate_proof_for_hash, proof_to_dicts

EMAIL = os.environ.get("CHAINCERT_DEMO_EMAIL", "demo.admin@chaincert.local")
PASSWORD = os.environ.get("CHAINCERT_DEMO_PASSWORD", "ChainCertDemo!2026")

with app.app_context():
    services = app.extensions["chaincert_services"]
    access = services["access"]
    with access.store.connect() as con:
        existing = con.execute("SELECT id FROM users WHERE email=? COLLATE NOCASE", (EMAIL,)).fetchone()
        user_count = con.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
        institution = con.execute("SELECT id,name FROM institutions WHERE name='MMCOE'").fetchone()
    if existing:
        print(f"Demo account already exists: {EMAIL}. Password is unchanged.")
    elif user_count:
        print("Access-control database already contains users; refusing unsafe bootstrap.")
        print("Sign in as a platform admin and provision a demo user, or use a fresh local data directory.")
    else:
        institution_id = access.create_institution("MMCOE")
        access.provision_user(email=EMAIL, display_name="ChainCert Demo Admin", password=PASSWORD,
                              role=Role.PLATFORM_ADMIN, institution_id=None)
        token = access.login(EMAIL, PASSWORD)
        actor = access.authenticate(token)
        access.provision_user(email="issuer@chaincert.local", display_name="Demo Issuer", password="IssuerDemo!2026",
                              role=Role.INSTITUTION_ADMIN, institution_id=institution_id, actor=actor)
        access.logout(token)
        print(f"Created demo platform admin: {EMAIL}")
        print("Created institution admin: issuer@chaincert.local / IssuerDemo!2026")

    # Seed existing synthetic .txt examples without clearing records.
    sample_dir = ROOT / "test_certificates"
    for idx in range(1, 6):
        cert_path = sample_dir / f"certificate{idx}.txt"
        if cert_path.exists() and not get_certificate(f"CC{idx:03d}"):
            try: add_certificate(parse_certificate_file(str(cert_path)))
            except Exception as exc: print(f"Skipped {cert_path.name}: {exc}")

    # A separate OCR-friendly synthetic credential whose identifiers avoid common
    # O/0 and I/1 OCR confusions. Its PDF is scanned/image-only.
    if not get_certificate("CERT-A1"):
        add_certificate({"certificate_id": "CERT-A1", "student_name": "Demo Student", "roll_number": "R-101",
                         "course": "Data Science", "cgpa": "8.75", "issue_date": "2026-08-20", "institution_id": "MMCOE"})

    certs = [get_certificate(cid) for cid in ("CC001", "CC002", "CC003", "CC004")]
    certs = [c for c in certs if c]
    if certs:
        tree = build_merkle_tree([c["certificate_hash"] for c in certs])
        matching_block = next((b for b in chain_instance.blocks if b.batch_id == "SEM1_2026" and b.merkle_root == tree.merkle_root), None)
        target_batch = "SEM1_2026" if matching_block else "DEMO_SEM1_2026"
        proof_map = {c["certificate_id"]: proof_to_dicts(generate_proof_for_hash(tree, c["certificate_hash"])) for c in certs}
        assign_batch_and_proofs(target_batch, tree.merkle_root, proof_map)
        matching_demo_block = next((b for b in chain_instance.blocks if b.batch_id == target_batch and b.merkle_root == tree.merkle_root), None)
        if not matching_demo_block:
            block = chain_instance.add_batch(batch_id=target_batch, merkle_root=tree.merkle_root, certificate_count=len(certs))
            update_batch_block_id(target_batch, block.block_id)
        print(f"Prepared {len(certs)} sample certificates and Merkle proofs in batch {target_batch}.")

    ocr_cert = get_certificate("CERT-A1")
    if ocr_cert:
        ocr_tree = build_merkle_tree([ocr_cert["certificate_hash"]])
        ocr_batch = "DEMO_OCR_2026"
        ocr_proof = {"CERT-A1": proof_to_dicts(generate_proof_for_hash(ocr_tree, ocr_cert["certificate_hash"]))}
        assign_batch_and_proofs(ocr_batch, ocr_tree.merkle_root, ocr_proof)
        if not any(b.batch_id == ocr_batch and b.merkle_root == ocr_tree.merkle_root for b in chain_instance.blocks):
            ocr_block = chain_instance.add_batch(batch_id=ocr_batch, merkle_root=ocr_tree.merkle_root, certificate_count=1)
            update_batch_block_id(ocr_batch, ocr_block.block_id)
        print("Prepared OCR-only sample credential CERT-A1 in batch DEMO_OCR_2026.")

print("Demo seed complete. See README.md for startup and API commands.")

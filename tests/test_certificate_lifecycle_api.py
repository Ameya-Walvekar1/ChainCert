import json

import pytest

from app import app
from chaincert.auth import AccessControlService, Role
from chaincert.hashing import hash_certificate
from chaincert.ingestion import ExtractionService
from chaincert.merkle import verify_merkle_proof
from chaincert.records import get_certificate
from chaincert.verification import VerificationEngine, VerificationHistory
from chaincert.chain import Chain


@pytest.fixture
def lifecycle_app(tmp_path, monkeypatch):
    cert_db = tmp_path / "certificates.db"
    access_db = tmp_path / "access.db"
    ingestion_db = tmp_path / "ingestion.db"
    chain_path = tmp_path / "chain.json"

    access = AccessControlService(str(access_db), "test-secret-that-is-long-enough-for-tests-123456")
    access.create_institution("TEST-LAB")
    admin_id = access.provision_user(
        email="issuer@chaincert.local",
        display_name="Issuer User",
        password="TestIssuer!2026",
        role=Role.INSTITUTION_ADMIN,
        institution_id=1,
        actor=None,
    )
    admin = access.authenticate(access.login("issuer@chaincert.local", "TestIssuer!2026"))
    access.provision_user(
        email="student@chaincert.local",
        display_name="Student User",
        password="TestStudent!2026",
        role=Role.STUDENT,
        institution_id=1,
        actor=admin,
    )

    chain = Chain(storage_path=chain_path, autoload=True)
    app.extensions["chaincert_services"] = {
        "access": access,
        "extractor": ExtractionService(str(ingestion_db)),
        "verification": VerificationEngine(chain),
        "history": VerificationHistory(str(tmp_path / "verification_history.db")),
        "certificate_db": str(cert_db),
        "max_upload_bytes": 10 * 1024 * 1024,
        "chain": chain,
    }

    issuer_token = access.login("issuer@chaincert.local", "TestIssuer!2026")
    student_token = access.login("student@chaincert.local", "TestStudent!2026")

    return app.test_client(), {"Authorization": "Bearer " + issuer_token}, {"Authorization": "Bearer " + student_token}, cert_db, chain_path


def test_single_certificate_lifecycle_works_and_isolated(lifecycle_app):
    client, issuer_headers, student_headers, cert_db, chain_path = lifecycle_app

    payload = {
        "certificate": {
            "certificate_id": "LIFECYCLE-001",
            "student_name": "Ada Example",
            "roll_number": "ADA-001",
            "course": "B.Tech in Computer Science",
            "cgpa": "9.80",
            "issue_date": "2026-08-20",
            "institution_id": "TEST-LAB",
        }
    }

    response = client.post("/api/v1/certificates", headers=issuer_headers, json=payload)
    assert response.status_code == 201, response.json
    body = response.json
    assert body["certificate"]["certificate_id"] == "LIFECYCLE-001"

    record = get_certificate("LIFECYCLE-001", db_path=str(cert_db))
    assert record is not None
    assert record["certificate_id"] == "LIFECYCLE-001"
    assert record["batch_id"]
    assert record["merkle_root"]
    assert isinstance(record["merkle_proof_parsed"], list)
    assert record["status"] in {"BATCHED", "CHAINED"}

    expected_hash = hash_certificate({
        "certificate_id": record["certificate_id"],
        "student_name": record["student_name"],
        "roll_number": record["roll_number"],
        "course": record["course"],
        "cgpa": record["cgpa"],
        "issue_date": record["issue_date"],
        "institution_id": record["institution_id"],
    }).certificate_hash
    assert record["certificate_hash"] == expected_hash
    assert verify_merkle_proof(record["certificate_hash"], record["merkle_proof_parsed"], record["merkle_root"]) is True

    chain = app.extensions["chaincert_services"]["chain"]
    assert len(chain.blocks) >= 1
    assert chain.validate_chain().is_valid is True

    fetched = client.get("/api/v1/certificates/LIFECYCLE-001", headers=issuer_headers)
    assert fetched.status_code == 200
    assert fetched.json["certificate"]["certificate_id"] == "LIFECYCLE-001"

    tampered = client.post("/api/v1/verify", json={**payload["certificate"], "cgpa": "9.99"})
    assert tampered.status_code == 200
    assert tampered.json["status"] == "TAMPERED"

    revoke = client.post("/api/v1/certificates/LIFECYCLE-001/revoke", headers=issuer_headers, json={"reason": "Academic integrity review"})
    assert revoke.status_code == 200, revoke.json
    revoked_check = client.post("/api/v1/verify", json={"certificate_id": "LIFECYCLE-001"})
    assert revoked_check.status_code == 200
    assert revoked_check.json["status"] == "REVOKED"

    unknown = client.post("/api/v1/verify", json={"certificate_id": "NO-SUCH-CERT"})
    assert unknown.status_code == 200
    assert unknown.json["status"] == "NOT_FOUND"

    unauthorized = client.post("/api/v1/certificates", headers=student_headers, json=payload)
    assert unauthorized.status_code == 403


def test_single_certificate_rolls_back_on_chain_failure(tmp_path):
    cert_db = tmp_path / "certificates.db"
    access_db = tmp_path / "access.db"
    chain_path = tmp_path / "chain.json"

    access = AccessControlService(str(access_db), "test-secret-that-is-long-enough-for-tests-123456")
    access.create_institution("ROLLBACK-LAB")
    access.provision_user(
        email="issuer@rollback.local",
        display_name="Rollback Issuer",
        password="Rollback!2026",
        role=Role.INSTITUTION_ADMIN,
        institution_id=1,
        actor=None,
    )

    chain = Chain(storage_path=chain_path, autoload=True)
    app.extensions["chaincert_services"] = {
        "access": access,
        "extractor": ExtractionService(str(tmp_path / "ingestion.db")),
        "verification": VerificationEngine(chain),
        "history": VerificationHistory(str(tmp_path / "verification_history.db")),
        "certificate_db": str(cert_db),
        "max_upload_bytes": 10 * 1024 * 1024,
        "chain": chain,
    }

    client = app.test_client()
    token = access.login("issuer@rollback.local", "Rollback!2026")
    headers = {"Authorization": "Bearer " + token}

    original_add_batch = chain.add_batch

    def fail_add_batch(*args, **kwargs):
        raise RuntimeError("simulated batch failure")

    chain.add_batch = fail_add_batch
    try:
        response = client.post(
            "/api/v1/certificates",
            headers=headers,
            json={
                "certificate": {
                    "certificate_id": "ROLLBACK-001",
                    "student_name": "Rollback Example",
                    "roll_number": "RB-001",
                    "course": "B.Tech in Data Science",
                    "cgpa": "9.10",
                    "issue_date": "2026-08-20",
                    "institution_id": "ROLLBACK-LAB",
                }
            },
        )
        assert response.status_code == 400, response.json
        assert get_certificate("ROLLBACK-001", db_path=str(cert_db)) is None
    finally:
        chain.add_batch = original_add_batch

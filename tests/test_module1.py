"""
Unit tests for Module 1: Certificate & Record Management.
"""

import pytest
import os
import tempfile
from pathlib import Path

from chaincert.records.parser import parse_certificate_text, parse_certificate_file
from chaincert.records.database import (
    init_db,
    add_certificate,
    get_certificate,
    list_certificates,
    update_certificate,
    assign_batch_and_proofs,
    delete_certificate,
    clear_database,
)
from chaincert.hashing.exceptions import CertificateValidationError


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_parse_certificate_text_valid():
    text = """
    CERTIFICATE ID: CC001
    NAME: Rahul Sharma
    ROLL NUMBER: A101
    COURSE: AI & DS
    CGPA: 9.20
    ISSUE DATE: 2026-08-20
    INSTITUTION ID: MMCOE
    """
    cert = parse_certificate_text(text)
    assert cert["certificate_id"] == "CC001"
    assert cert["student_name"] == "Rahul Sharma"
    assert cert["roll_number"] == "A101"
    assert cert["course"] == "AI & DS"
    assert float(cert["cgpa"]) == 9.2
    assert cert["issue_date"] == "2026-08-20"
    assert cert["institution_id"] == "MMCOE"


def test_parse_certificate_text_missing_field():
    text = """
    CERTIFICATE ID: CC001
    NAME: Rahul Sharma
    CGPA: 9.20
    """
    with pytest.raises(CertificateValidationError):
        parse_certificate_text(text)


def test_add_and_retrieve_certificate(temp_db):
    data = {
        "certificate_id": "CC001",
        "student_name": "Rahul Sharma",
        "roll_number": "A101",
        "course": "AI & DS",
        "cgpa": "9.20",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    }
    res = add_certificate(data, db_path=temp_db)
    assert res["certificate_id"] == "CC001"
    assert res["certificate_hash"] is not None
    assert len(res["certificate_hash"]) == 64

    retrieved = get_certificate("CC001", db_path=temp_db)
    assert retrieved is not None
    assert retrieved["certificate_hash"] == res["certificate_hash"]


def test_duplicate_certificate_id_rejection(temp_db):
    data = {
        "certificate_id": "CC001",
        "student_name": "Rahul Sharma",
        "roll_number": "A101",
        "course": "AI & DS",
        "cgpa": "9.20",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    }
    add_certificate(data, db_path=temp_db)
    with pytest.raises(CertificateValidationError):
        add_certificate(data, db_path=temp_db)


def test_update_certificate_recomputes_hash(temp_db):
    data = {
        "certificate_id": "CC001",
        "student_name": "Rahul Sharma",
        "roll_number": "A101",
        "course": "AI & DS",
        "cgpa": "9.20",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    }
    orig = add_certificate(data, db_path=temp_db)
    orig_hash = orig["certificate_hash"]

    updated = update_certificate("CC001", {"cgpa": "9.99"}, db_path=temp_db)
    assert updated["cgpa"] == "9.99"
    assert updated["certificate_hash"] != orig_hash


def test_assign_batch_and_proofs(temp_db):
    data = {
        "certificate_id": "CC001",
        "student_name": "Rahul Sharma",
        "roll_number": "A101",
        "course": "AI & DS",
        "cgpa": "9.20",
        "issue_date": "2026-08-20",
        "institution_id": "MMCOE",
    }
    add_certificate(data, db_path=temp_db)

    proof_map = {
        "CC001": [{"hash": "a" * 64, "position": "right"}]
    }
    assign_batch_and_proofs("SEM1_2026", "b" * 64, proof_map, db_path=temp_db)

    cert = get_certificate("CC001", db_path=temp_db)
    assert cert["batch_id"] == "SEM1_2026"
    assert cert["merkle_root"] == "b" * 64
    assert cert["status"] == "BATCHED"
    assert cert["merkle_proof_parsed"] == proof_map["CC001"]

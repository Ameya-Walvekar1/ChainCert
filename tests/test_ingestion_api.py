from __future__ import annotations
import io, shutil
from pathlib import Path

import fitz
import pytest
from PIL import Image, ImageDraw, ImageFont

import chaincert.records.database as record_db
from chaincert.auth import AccessControlService, Role
from chaincert.hashing import hash_certificate
from chaincert.ingestion import ExtractionService, extract_fields
from chaincert.verification import VerificationEngine, VerificationHistory
from app import app, chain_instance

FIELDS = {
    "certificate_id": "TST-DEMO-001",
    "student_name": "Demo Student",
    "roll_number": "T-001",
    "course": "AI & DS",
    "cgpa": "9.20",
    "issue_date": "2026-08-20",
    "institution_id": "TEST-UNI",
}


def make_text_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    y = 100
    for line in text.splitlines():
        page.insert_text((60, y), line, fontsize=16, fontname="helv")
        y += 35
    data = doc.tobytes()
    doc.close()
    return data


def test_native_pdf_extraction_and_ambiguous_date(tmp_path):
    service = ExtractionService(tmp_path / "uploads.db")
    text = "\n".join(["Certificate ID: TST-DEMO-001", "Student Name: Demo Student",
        "Registration Number: T-001", "Programme: AI & DS", "CGPA: 9.20",
        "Issue Date: 2026-08-20", "Institution ID: TEST-UNI"])
    result = service.extract("synthetic.pdf", make_text_pdf(text))
    assert result["source_type"] == "text_pdf"
    assert result["fields"]["certificate_id"]["value"] == "TST-DEMO-001"
    assert result["fields"]["roll_number"]["value"] == "T-001"
    assert result["fields"]["cgpa"]["value"] == "9.20"
    assert result["fields"]["issue_date"]["confidence"] is None
    assert service.get(result["upload_id"])["upload_id"] == result["upload_id"]

    fields, warnings = extract_fields("Issue Date: 01/02/2026")
    assert fields["issue_date"]["value"] is None
    assert any("Ambiguous" in warning for warning in warnings)


def test_rejects_unsupported_and_oversized_documents(tmp_path):
    service = ExtractionService(tmp_path / "uploads.db", max_upload_bytes=8)
    with pytest.raises(ValueError):
        service.extract("doc.exe", b"hello")
    with pytest.raises(ValueError):
        service.extract("doc.pdf", b"%PDF-" + b"x" * 20)


def test_scanned_pdf_uses_ocr_when_tesseract_available(tmp_path):
    if not shutil.which("tesseract"):
        pytest.skip("Tesseract executable is not installed")
    image = Image.new("RGB", (1600, 1800), "white")
    draw = ImageDraw.Draw(image)
    lines = ["CHAINCERT DEMO", "Certificate ID: TST-DEMO-001", "Student Name: Demo Student",
             "Roll Number: T-001", "Course: AI and DS", "CGPA: 9.20",
             "Issue Date: 2026-08-20", "Institution ID: TEST-UNI"]
    y = 100
    for line in lines:
        draw.text((100, y), line, fill="black", font=ImageFont.load_default(size=42))
        y += 180
    image_bytes = io.BytesIO(); image.save(image_bytes, format="PNG")
    doc = fitz.open(); page = doc.new_page(width=595, height=842)
    page.insert_image(page.rect, stream=image_bytes.getvalue())
    pdf_bytes = doc.tobytes(); doc.close()
    result = ExtractionService(tmp_path / "uploads.db").extract("scan.pdf", pdf_bytes)
    assert result["source_type"] == "scanned_pdf"
    assert result["fields"]["certificate_id"]["value"] == "TST-DEMO-001"
    assert result["fields"]["certificate_id"]["confidence_method"] == "mean_tesseract_token_score_proxy"


@pytest.mark.parametrize("fmt,extension", [("PNG", ".png"), ("JPEG", ".jpg")])
def test_png_and_jpeg_ocr(tmp_path, fmt, extension):
    if not shutil.which("tesseract"):
        pytest.skip("Tesseract executable is not installed")
    image = Image.new("RGB", (1600, 1200), "white")
    draw = ImageDraw.Draw(image)
    lines = ["Certificate ID: TST-IMAGE-003", "Student Name: Image Student", "Roll Number: IMG-003",
             "Course: AI and DS", "CGPA: 8.80", "Issue Date: 2026-08-20", "Institution ID: TEST-UNI"]
    y = 70
    for line in lines:
        draw.text((80, y), line, fill="black", font=ImageFont.load_default(size=40)); y += 150
    buffer = io.BytesIO(); image.save(buffer, format=fmt)
    result = ExtractionService(tmp_path / "uploads.db").extract("sample" + extension, buffer.getvalue())
    assert result["source_type"] == "image"
    assert result["fields"]["certificate_id"]["value"] == "TST-IMAGE-003"
    assert result["fields"]["certificate_id"]["confidence"] is not None


def test_missing_fields_and_invalid_cgpa_are_reviewable():
    fields, warnings = extract_fields("Certificate ID: X-1\nCGPA: 15.5\nIssue Date: 2026-08-20")
    assert fields["student_name"]["value"] is None
    assert fields["cgpa"]["value"] is None
    assert any("Invalid CGPA" in warning for warning in warnings)


def _setup_api(tmp_path, monkeypatch):
    db_path = tmp_path / "certificates.db"
    monkeypatch.setattr(record_db, "DEFAULT_DB_PATH", db_path)
    access = AccessControlService(str(tmp_path / "access.db"), "test-secret-that-is-long-enough-for-tests-123456")
    access.create_institution("TEST-UNI")
    access.provision_user(email="test-admin@chaincert.local", display_name="Test Admin",
                          password="TestAdmin!2026", role=Role.PLATFORM_ADMIN, institution_id=None)
    token = access.login("test-admin@chaincert.local", "TestAdmin!2026")
    actor = access.authenticate(token)
    access.provision_user(email="test-university@chaincert.local", display_name="Test University",
                          password="TestUniversity!2026", role=Role.INSTITUTION_ADMIN, institution_id=1, actor=actor)
    university_token = access.login("test-university@chaincert.local", "TestUniversity!2026")
    app.extensions["chaincert_services"] = {
        "access": access,
        "extractor": ExtractionService(tmp_path / "uploads.db"),
        "verification": VerificationEngine(chain_instance),
        "history": VerificationHistory(db_path),
        "certificate_db": str(db_path),
        "max_upload_bytes": 10 * 1024 * 1024,
    }
    return app.test_client(), {"Authorization": "Bearer " + token}, {"Authorization": "Bearer " + university_token}


def test_api_register_verify_tamper_review_not_found_and_revoke(tmp_path, monkeypatch):
    client, headers, university_headers = _setup_api(tmp_path, monkeypatch)
    response = client.post("/api/v1/certificates", headers=headers, json=FIELDS)
    assert response.status_code == 201, response.json
    assert response.json["certificate"]["certificate_id"] == FIELDS["certificate_id"]

    genuine = client.post("/api/v1/verify", json=FIELDS)
    assert genuine.status_code == 200 and genuine.json["status"] == "GENUINE", genuine.json

    original_pdf = make_text_pdf("\n".join(["Certificate ID: TST-DEMO-001", "Student Name: Demo Student",
        "Roll Number: T-001", "Course: AI & DS", "CGPA: 9.20", "Issue Date: 2026-08-20", "Institution ID: TEST-UNI"]))
    upload_genuine = client.post("/api/v1/verification/verify-upload", data={"document": (io.BytesIO(original_pdf), "original.pdf")}, content_type="multipart/form-data")
    assert upload_genuine.json["status"] == "GENUINE", upload_genuine.json

    modified_pdf = make_text_pdf("\n".join(["Certificate ID: TST-DEMO-001", "Student Name: Demo Student",
        "Roll Number: T-001", "Course: AI & DS", "CGPA: 9.99", "Issue Date: 2026-08-20", "Institution ID: TEST-UNI"]))
    upload_tampered = client.post("/api/v1/verification/verify-upload", data={"document": (io.BytesIO(modified_pdf), "modified.pdf")}, content_type="multipart/form-data")
    assert upload_tampered.json["status"] == "TAMPERED", upload_tampered.json

    modified = dict(FIELDS, cgpa="9.99")
    tampered = client.post("/api/v1/verify", json=modified)
    assert tampered.json["status"] == "TAMPERED", tampered.json
    assert "cgpa" in tampered.json["mismatched_fields"]

    unknown = client.post("/api/v1/verify", json=dict(FIELDS, certificate_id="UNKNOWN-ID"))
    assert unknown.json["status"] == "NOT_FOUND", unknown.json

    review = client.post("/api/v1/verify", json={"certificate_id": FIELDS["certificate_id"], "student_name": "Demo Student"})
    assert review.json["status"] == "REVIEW_REQUIRED", review.json

    revoke = client.post(f"/api/v1/certificates/{FIELDS['certificate_id']}/revoke", headers=headers, json={"reason": "Demo revocation"})
    assert revoke.status_code == 200, revoke.json
    after = client.post("/api/v1/verify", json={"certificate_id": FIELDS["certificate_id"]})
    assert after.json["status"] == "REVOKED", after.json

    history = client.get("/api/v1/verification/history", headers=headers)
    assert history.status_code == 200 and history.json["count"] >= 4
    university_history = client.get("/api/v1/verification/history", headers=university_headers)
    assert university_history.status_code == 200
    assert any(item["certificate_id"] == FIELDS["certificate_id"] and item["status"] == "TAMPERED" for item in university_history.json["attempts"])


def test_extract_endpoint_and_upload_result_endpoint(tmp_path, monkeypatch):
    client, _headers, _university_headers = _setup_api(tmp_path, monkeypatch)
    text = "\n".join(["Certificate ID: TST-UP-002", "Student Name: Upload Student",
        "Roll Number: U-002", "Course: Data Science", "CGPA: 8.75",
        "Issue Date: 2026-08-20", "Institution ID: TEST-UNI"])
    data = make_text_pdf(text)
    response = client.post("/api/v1/certificates/extract", data={"document": (io.BytesIO(data), "upload.pdf")}, content_type="multipart/form-data")
    assert response.status_code == 200, response.json
    upload_id = response.json["upload_id"]
    retrieved = client.get(f"/api/v1/uploads/{upload_id}")
    assert retrieved.status_code == 200
    assert retrieved.json["fields"]["certificate_id"]["value"] == "TST-UP-002"

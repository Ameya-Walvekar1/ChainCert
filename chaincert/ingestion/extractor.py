"""PDF/image ingestion and candidate academic-field extraction.

Tesseract word confidence is exposed as a normalized mean token-confidence proxy,
not as a calibrated probability. Native PDF text extraction has no field-level
confidence, so confidence is null rather than fabricated.
"""
from __future__ import annotations
import io, re, uuid, json, sqlite3, time
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import fitz  # PyMuPDF
from PIL import Image, ImageOps, ImageSequence
import pytesseract
from pytesseract import Output

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_PAGES = 10
RETENTION_SECONDS = 24 * 60 * 60

FIELD_ALIASES = {
    "certificate_id": ["certificate id", "certificate number", "certificate no", "cert id", "cert no", "credential id"],
    "student_name": ["student name", "name of candidate", "candidate name", "name of student", "student", "name"],
    "roll_number": ["roll number", "roll no", "roll #", "registration number", "registration no", "enrollment number", "enrolment number", "student number", "student id"],
    "course": ["course", "programme", "program", "degree", "qualification", "branch", "course name"],
    "cgpa": ["cumulative grade point average", "grade point average", "cgpa", "sgpa", "gpa", "grade"],
    "issue_date": ["date of issue", "issue date", "date issued", "date of award", "award date"],
    "institution_id": ["institution id", "institution code", "university id", "college id", "institution", "university", "college", "issued by"],
}

class DocumentError(ValueError):
    """Raised for unsupported, malformed, or over-limit documents."""

class ExtractionService:
    def __init__(self, database_path: str | Path, *, max_upload_bytes=MAX_UPLOAD_BYTES,
                 max_pages=MAX_PAGES, retention_seconds=RETENTION_SECONDS):
        self.database_path = str(database_path)
        self.max_upload_bytes = int(max_upload_bytes)
        self.max_pages = int(max_pages)
        self.retention_seconds = int(retention_seconds)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.execute('''CREATE TABLE IF NOT EXISTS upload_results (
                upload_id TEXT PRIMARY KEY, result_json TEXT NOT NULL,
                created_at INTEGER NOT NULL, expires_at INTEGER NOT NULL
            )''')

    def connect(self):
        con = sqlite3.connect(self.database_path, timeout=10)
        con.row_factory = sqlite3.Row
        return con

    def _cleanup(self):
        now = int(time.time())
        with self.connect() as con:
            con.execute("DELETE FROM upload_results WHERE expires_at < ?", (now,))

    def get(self, upload_id: str):
        self._cleanup()
        with self.connect() as con:
            row = con.execute("SELECT result_json FROM upload_results WHERE upload_id=? AND expires_at>=?", (upload_id, int(time.time()))).fetchone()
        return json.loads(row["result_json"]) if row else None

    def extract(self, filename: str, data: bytes) -> dict[str, Any]:
        self._cleanup()
        if not data:
            raise DocumentError("The uploaded document is empty.")
        if len(data) > self.max_upload_bytes:
            raise DocumentError(f"File exceeds the {self.max_upload_bytes // (1024*1024)} MB upload limit.")
        suffix = Path(filename or "").suffix.lower()
        if suffix not in {".pdf", ".png", ".jpg", ".jpeg"}:
            raise DocumentError("Unsupported file type. Upload PDF, PNG, JPG, or JPEG.")
        pages: list[tuple[str, str, float | None]] = []
        methods: list[str] = []
        if suffix == ".pdf":
            if not data.startswith(b"%PDF-"):
                raise DocumentError("The file extension says PDF, but the file signature is invalid.")
            try:
                document = fitz.open(stream=data, filetype="pdf")
            except Exception:
                raise DocumentError("The PDF is malformed or encrypted and could not be opened.") from None
            try:
                if document.page_count < 1:
                    raise DocumentError("The PDF contains no pages.")
                if document.page_count > self.max_pages:
                    raise DocumentError(f"PDF has {document.page_count} pages; the limit is {self.max_pages}.")
                for page in document:
                    # Avoid pathological page sizes causing excessive raster allocation.
                    rect = page.rect
                    if rect.width > 2000 or rect.height > 3000 or rect.width * rect.height > 3_000_000:
                        raise DocumentError("A PDF page has unsafe dimensions and cannot be rendered.")
                    native_text = page.get_text("text") or ""
                    usable = len(re.sub(r"\W", "", native_text, flags=re.UNICODE)) >= 20
                    if usable:
                        pages.append((native_text, "native_pdf_text", None)); methods.append("native")
                    else:
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                        image = Image.open(io.BytesIO(pix.tobytes("png")))
                        text, confidence_map = self._ocr(image)
                        pages.append((text, "ocr", confidence_map)); methods.append("ocr")
            finally:
                document.close()
            source_type = "text_pdf" if methods and all(m == "native" for m in methods) else ("scanned_pdf" if methods and all(m == "ocr" for m in methods) else "mixed_pdf")
        else:
            try:
                image = Image.open(io.BytesIO(data))
                if image.format not in {"PNG", "JPEG"}:
                    raise DocumentError("Image content must be PNG or JPEG.")
                image.verify()
                image = Image.open(io.BytesIO(data))
                if image.width * image.height > 40_000_000:
                    raise DocumentError("Image dimensions are too large to process safely.")
                text, confidence_map = self._ocr(ImageOps.exif_transpose(image).convert("RGB"))
            except DocumentError:
                raise
            except Exception:
                raise DocumentError("The image is malformed or unsupported.") from None
            pages.append((text, "ocr", confidence_map)); methods.append("ocr"); source_type = "image"
        full_text = "\n".join(p[0] for p in pages)
        line_conf: dict[str, float] = {}
        for text, method, confidence_map in pages:
            if method == "ocr" and confidence_map:
                line_conf.update(confidence_map)
        fields, warnings = extract_fields(full_text, line_confidence=line_conf,
                                           native_text_used=any(p[1] == "native_pdf_text" for p in pages))
        if any(value["value"] is None for value in fields.values()):
            warnings.append("Some required fields could not be extracted reliably. Review the document before verification.")
        requires_review = any(value["value"] is None for value in fields.values()) or any("ambiguous" in w.lower() or "invalid" in w.lower() for w in warnings)
        result = {
            "upload_id": str(uuid.uuid4()), "source_type": source_type,
            "pages_processed": len(pages), "fields": fields, "warnings": list(dict.fromkeys(warnings)),
            "requires_review": bool(requires_review),
            "extraction_note": "OCR extracts visible text but does not establish authenticity or detect every visual manipulation."
        }
        now = int(time.time())
        with self.connect() as con:
            con.execute("INSERT INTO upload_results(upload_id,result_json,created_at,expires_at) VALUES(?,?,?,?)",
                        (result["upload_id"], json.dumps(result, ensure_ascii=False), now, now + self.retention_seconds))
        return result

    @staticmethod
    def _ocr(image: Image.Image) -> tuple[str, dict[str, float]]:
        # Tesseract confidence is a token-level engine score, not a calibrated
        # probability that a field is correct. Aggregate scores per OCR line.
        try:
            data = pytesseract.image_to_data(image, output_type=Output.DICT, config="--psm 6")
        except Exception as exc:
            raise DocumentError("OCR is unavailable. Install Tesseract OCR and pytesseract.") from exc
        grouped: dict[tuple[str, str, str], list[str]] = {}
        scores: dict[tuple[str, str, str], list[float]] = {}
        for i, token in enumerate(data.get("text", [])):
            token = str(token).strip()
            if not token:
                continue
            key = (str(data["block_num"][i]), str(data["par_num"][i]), str(data["line_num"][i]))
            grouped.setdefault(key, []).append(token)
            try:
                value = float(data["conf"][i])
                if value >= 0: scores.setdefault(key, []).append(max(0.0, min(100.0, value)) / 100.0)
            except (ValueError, TypeError, IndexError):
                pass
        text_lines = []
        confidence_map: dict[str, float] = {}
        for key, tokens in grouped.items():
            line = " ".join(tokens)
            text_lines.append(line)
            values = scores.get(key, [])
            if values: confidence_map[line] = sum(values) / len(values)
        return "\n".join(text_lines), confidence_map


def _field_label_match(line: str):
    stripped = line.strip()
    for field, aliases in FIELD_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            pattern = r"^\s*" + re.escape(alias).replace(r"\ ", r"\s+") + r"\s*(?:[:：\-–—]\s*|\s{1,})(.*?)\s*$"
            match = re.match(pattern, stripped, flags=re.IGNORECASE)
            if match:
                return field, match.group(1).strip()
            # Allow a label alone; its value may be on the next line.
            if re.fullmatch(r"\s*" + re.escape(alias).replace(r"\ ", r"\s+") + r"\s*[:：]?\s*", stripped, flags=re.IGNORECASE):
                return field, ""
    return None, None


def _normalize_date(value: str) -> tuple[str | None, str | None]:
    value = value.strip().replace(",", "")
    iso = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", value)
    if iso:
        try: return datetime(int(iso.group(1)), int(iso.group(2)), int(iso.group(3))).strftime("%Y-%m-%d"), None
        except ValueError: return None, f"Invalid issue date: {value}"
    month_names = {m.lower(): i for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}
    named = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", value)
    if named:
        month = month_names.get(named.group(2).lower())
        if month:
            try: return datetime(int(named.group(3)), month, int(named.group(1))).strftime("%Y-%m-%d"), None
            except ValueError: return None, f"Invalid issue date: {value}"
    slash = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", value)
    if slash:
        a, b, y = map(int, slash.groups())
        if a > 12 and 1 <= b <= 12: day, month = a, b
        elif b > 12 and 1 <= a <= 12: month, day = a, b
        elif a <= 12 and b <= 12:
            return None, f"Ambiguous issue date '{value}'; review day/month order."
        else: return None, f"Invalid issue date: {value}"
        try: return datetime(y, month, day).strftime("%Y-%m-%d"), None
        except ValueError: return None, f"Invalid issue date: {value}"
    return None, f"Unrecognized issue date: {value}"


def _normalize_cgpa(value: str) -> tuple[str | None, str | None]:
    cleaned = value.strip().replace(",", ".")
    match = re.search(r"(?<!\d)(\d{1,2}(?:\.\d{1,3})?)(?!\d)", cleaned)
    if not match:
        return None, f"Invalid CGPA/grade value '{value}'; expected a numeric CGPA from 0 to 10."
    try: score = Decimal(match.group(1))
    except InvalidOperation: return None, f"Invalid CGPA value '{value}'."
    if not score.is_finite() or score < 0 or score > 10:
        return None, f"Invalid CGPA value '{value}'; expected 0 to 10."
    return f"{score:.2f}", None


def extract_fields(text: str, *, line_confidence: dict[str, float] | None = None,
                   native_text_used: bool = False) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Extract candidates. Missing/ambiguous values remain null; no guessing."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in (text or "").splitlines()]
    lines = [line for line in lines if line]
    candidates: dict[str, tuple[str, str, float | None]] = {}
    warnings: list[str] = []
    for idx, line in enumerate(lines):
        field, value = _field_label_match(line)
        if not field or field in candidates:
            continue
        source = line
        confidence_line = line
        if not value:
            for next_line in lines[idx+1:idx+3]:
                if _field_label_match(next_line)[0]: break
                value = next_line
                source = f"{line} | {next_line}"
                confidence_line = next_line
                break
        if value:
            conf = (line_confidence or {}).get(confidence_line)
            candidates[field] = (value.strip(), source, conf)
    output: dict[str, dict[str, Any]] = {}
    for field in FIELD_ALIASES:
        candidate = candidates.get(field)
        if not candidate:
            output[field] = {"value": None, "confidence": None, "confidence_method": "unavailable", "source_text": None}
            warnings.append(f"Field '{field}' was not found.")
            continue
        value, source, conf = candidate
        normalized = value.strip()
        warning = None
        if field == "cgpa": normalized, warning = _normalize_cgpa(value)
        elif field == "issue_date": normalized, warning = _normalize_date(value)
        # Native text extraction does not provide confidence; OCR confidence is the
        # average Tesseract token score for the page proxy, explicitly not calibrated.
        method = "mean_tesseract_token_score_proxy" if conf is not None else "not_provided_by_extractor"
        if field == "cgpa" and normalized is None: pass
        output[field] = {"value": normalized, "confidence": round(conf, 4) if conf is not None else None,
                         "confidence_method": method, "source_text": source}
        if warning: warnings.append(warning)
    if native_text_used:
        warnings.append("Native PDF text extraction does not provide calibrated field-level confidence; confidence is null where no OCR score is available.")
    return output, warnings

"""Persistent verification-attempt history in the existing certificate database."""
import json, sqlite3
from pathlib import Path
from datetime import datetime, timezone

class VerificationHistory:
    def __init__(self, database_path: str | Path):
        self.path = str(database_path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.execute('''CREATE TABLE IF NOT EXISTS verification_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id TEXT,
                certificate_id TEXT,
                status TEXT NOT NULL,
                explanation TEXT NOT NULL,
                mismatched_fields TEXT NOT NULL,
                source_type TEXT,
                actor_user_id INTEGER,
                institution_id TEXT,
                created_at TEXT NOT NULL
            )''')
            con.execute('''CREATE INDEX IF NOT EXISTS idx_verification_attempts_created
                           ON verification_attempts(created_at DESC)''')

    def connect(self):
        con = sqlite3.connect(self.path, timeout=10)
        con.row_factory = sqlite3.Row
        return con

    def record(self, result: dict, upload_id=None, source_type=None, actor_user_id=None, institution_id=None):
        with self.connect() as con:
            cur = con.execute('''INSERT INTO verification_attempts
                (upload_id, certificate_id, status, explanation, mismatched_fields, source_type, actor_user_id, institution_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                upload_id, result.get("certificate_id"), result.get("status", "REVIEW_REQUIRED"),
                result.get("explanation", ""), json.dumps(result.get("mismatched_fields", [])),
                source_type, actor_user_id, str(institution_id) if institution_id is not None else None,
                datetime.now(timezone.utc).isoformat()))
            return int(cur.lastrowid)

    def list(self, limit=100, institution_id=None):
        limit = max(1, min(int(limit), 500))
        with self.connect() as con:
            if institution_id is None:
                rows = con.execute('SELECT * FROM verification_attempts ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
            else:
                rows = con.execute('SELECT * FROM verification_attempts WHERE institution_id=? ORDER BY id DESC LIMIT ?', (str(institution_id), limit)).fetchall()
        out = []
        for row in rows:
            item = dict(row)
            try: item["mismatched_fields"] = json.loads(item["mismatched_fields"])
            except Exception: item["mismatched_fields"] = []
            out.append(item)
        return out

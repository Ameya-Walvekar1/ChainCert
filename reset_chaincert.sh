#!/usr/bin/env bash
set -Eeuo pipefail

cd "$HOME/ChainCert_Demo/EDIL1"
ROOT="$PWD"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$ROOT/backups/full-reset-$STAMP"

echo "ChainCert full certificate reset"
echo "Project: $ROOT"
echo "Backup:  $BACKUP"
echo
echo "This will DELETE all certificate records, batch records, and the current chain history."
echo "Admin accounts, institutions, source PDFs, and source code will be preserved."
read -r -p 'Type RESET-CERTIFICATES to continue: ' CONFIRM
if [[ "$CONFIRM" != "RESET-CERTIFICATES" ]]; then
  echo "Cancelled. No data changed."
  exit 1
fi

mkdir -p "$BACKUP/data"
for f in data/chaincert.db data/access_control.db data/ingestion.db data/chain.json; do
  if [[ -f "$f" ]]; then cp -a "$f" "$BACKUP/data/"; fi
done
if [[ -d frontend/src ]]; then
  cp -a frontend/src "$BACKUP/frontend-src"
fi

echo
echo "1/5 Backups created."

echo "2/5 Clearing certificate and batch records..."
.venv/bin/python - <<'PY'
import sqlite3
from pathlib import Path

db_path = Path("data/chaincert.db")
if not db_path.exists():
    raise SystemExit(f"Missing database: {db_path}")

con = sqlite3.connect(db_path)
try:
    tables = {
        row[0] for row in
        con.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    if "certificates" not in tables or "batches" not in tables:
        raise RuntimeError("Expected certificates/batches tables not found; refusing reset.")

    con.execute("BEGIN IMMEDIATE")
    before_certificates = con.execute("SELECT COUNT(*) FROM certificates").fetchone()[0]
    before_batches = con.execute("SELECT COUNT(*) FROM batches").fetchone()[0]
    con.execute("DELETE FROM certificates")
    con.execute("DELETE FROM batches")
    con.commit()

    after_certificates = con.execute("SELECT COUNT(*) FROM certificates").fetchone()[0]
    after_batches = con.execute("SELECT COUNT(*) FROM batches").fetchone()[0]
    print(f"Certificates: {before_certificates} -> {after_certificates}")
    print(f"Batches:      {before_batches} -> {after_batches}")
    if after_certificates or after_batches:
        raise RuntimeError("Reset verification failed.")
except Exception:
    con.rollback()
    raise
finally:
    con.close()
PY

echo "3/5 Resetting chain history..."
# chain.json is a JSON array of blocks in this project.
printf '[]\n' > data/chain.json

echo "4/5 Fixing frontend executable permissions..."
if [[ -d frontend/node_modules/.bin ]]; then
  chmod +x frontend/node_modules/.bin/tsc 
           frontend/node_modules/.bin/vite 2>/dev/null || true
fi

echo "5/5 Running checks..."
BUILD_STATUS=skipped
TEST_STATUS=skipped

if [[ -f frontend/package.json && -d frontend/node_modules ]]; then
  (
    cd frontend
    npm run build
  ) && BUILD_STATUS=PASS || BUILD_STATUS=FAIL
else
  echo "Frontend build skipped: dependencies or package.json missing."
fi

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 
  .venv/bin/python -m pytest --collect-only -q 
  && TEST_STATUS=PASS || TEST_STATUS=FAIL

echo
echo "========== FINAL RESET CHECK =========="
.venv/bin/python - <<'PY'
import json, sqlite3
from pathlib import Path

con = sqlite3.connect("data/chaincert.db")
print("Certificates remaining:", con.execute("SELECT COUNT(*) FROM certificates").fetchone()[0])
print("Batches remaining:", con.execute("SELECT COUNT(*) FROM batches").fetchone()[0])
con.close()

blocks = json.loads(Path("data/chain.json").read_text())
print("Chain blocks remaining:", len(blocks))

con = sqlite3.connect("data/access_control.db")
print("Admin accounts preserved:")
for row in con.execute(
    "SELECT email, role, active FROM users "
    "WHERE role IN ('PLATFORM_ADMIN','INSTITUTION_ADMIN')"
):
    print(" ", row)
con.close()
PY

echo
echo "Build result: $BUILD_STATUS"
echo "Test discovery: $TEST_STATUS"
echo "Backup: $BACKUP"
echo
echo "Reset finished. Review build/test results above before launching the app."

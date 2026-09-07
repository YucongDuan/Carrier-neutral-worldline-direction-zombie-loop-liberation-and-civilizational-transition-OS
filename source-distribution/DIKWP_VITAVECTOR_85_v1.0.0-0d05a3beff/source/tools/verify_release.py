from pathlib import Path
import hashlib
import json
import zipfile

archive = Path(__file__).resolve().parents[2] / "DIKWP_VITAVECTOR_85_v1.0.0.zip"
report = {"archive": str(archive), "checks": {}}
report["checks"]["exists"] = archive.is_file()
if archive.is_file():
    report["sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as zf:
        bad = zf.testzip()
        names = zf.namelist()
    report["checks"]["zip_integrity"] = bad is None
    report["checks"]["single_top_level"] = len({n.split("/")[0] for n in names if n}) == 1
    report["checks"]["no_runtime_db"] = not any(n.endswith((".db", ".db-wal", ".db-shm", ".pyc")) or "__pycache__" in n for n in names)
report["passed"] = all(report["checks"].values())
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["passed"] else 1)

from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {"MANIFEST.sha256"}
rows = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel in EXCLUDE or rel.startswith(("var/", "outputs/", ".git/", "dist/", "build/")) or "__pycache__" in rel or rel.endswith((".pyc", ".pyo")):
        continue
    rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
(ROOT / "MANIFEST.sha256").write_text("\n".join(rows) + "\n", encoding="utf-8")
print(len(rows))

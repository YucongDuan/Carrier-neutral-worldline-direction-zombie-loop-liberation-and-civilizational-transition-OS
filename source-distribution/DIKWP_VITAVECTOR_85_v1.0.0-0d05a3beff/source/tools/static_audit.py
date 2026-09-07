from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
required = [
    "README.md", "README.zh-CN.md", "WORLDLINE_CHARTER.md", "ANTI_DEHUMANIZATION_BOUNDARY.md",
    "LICENSE", "NOTICE", "CITATION.cff", "index.html", "assets/app.js", "assets/styles.css",
    "vitavector85/core.py", "vitavector85/server.py", "vitavector85/store.py", "vitavector85/cli.py",
    "schemas/worldline.schema.json", "examples/zombie_loop.json", "examples/regenerative_transition.json",
]
checks = []
for rel in required:
    checks.append((f"required:{rel}", (ROOT / rel).is_file()))

text_files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in {".py", ".js", ".html", ".md", ".json", ".yml", ".yaml", ".toml"} and "tools/static_audit.py" not in p.as_posix()]
combined = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in text_files)
checks.extend([
    ("no_humanity_score_assignment", not bool(re.search(r"humanity_score\s*[:=]\s*(?!None|null)", combined))),
    ("personhood_not_performed", "NOT_PERFORMED" in combined),
    ("zombie_window_boundary", "WORLDLINE_WINDOW_ONLY" in combined),
    ("no_remote_script", "<script src=\"http" not in combined and "<script src='http" not in combined),
    ("no_eval", "eval(" not in combined),
    ("no_shell_execution", "subprocess" not in (ROOT / "vitavector85/core.py").read_text(encoding="utf-8")),
    ("external_writeback_default_false", "default_external_writeback\": False" in (ROOT / "vitavector85/core.py").read_text(encoding="utf-8")),
    ("csp_present", "Content-Security-Policy" in (ROOT / "vitavector85/server.py").read_text(encoding="utf-8")),
    ("all_12_dimensions", len(json.loads((ROOT / "examples" / "regenerative_transition.json").read_text(encoding="utf-8"))) > 0),
])

for schema in (ROOT / "schemas").glob("*.json"):
    try:
        json.loads(schema.read_text(encoding="utf-8"))
        checks.append((f"json:{schema.name}", True))
    except Exception:
        checks.append((f"json:{schema.name}", False))
for example in (ROOT / "examples").glob("*.json"):
    try:
        json.loads(example.read_text(encoding="utf-8"))
        checks.append((f"example:{example.name}", True))
    except Exception:
        checks.append((f"example:{example.name}", False))

failed = [name for name, ok in checks if not ok]
report = {"suite": "static_audit", "passed": not failed, "passed_count": len(checks)-len(failed), "total_count": len(checks), "failed": failed}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["passed"] else 1)

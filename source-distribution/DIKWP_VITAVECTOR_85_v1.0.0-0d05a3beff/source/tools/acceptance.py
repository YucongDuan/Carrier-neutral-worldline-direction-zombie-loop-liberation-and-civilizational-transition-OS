from pathlib import Path
import sys
import json
import threading
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vitavector85.server import VitaVectorServer

def call(url, method="GET", payload=None):
    raw = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=raw, method=method, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8")), dict(resp.headers)

server = VitaVectorServer(("127.0.0.1", 0), ROOT, ROOT / "var" / "acceptance.db", quiet=True)
thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start(); time.sleep(.05)
base = f"http://127.0.0.1:{server.server_port}"
checks = []
try:
    status, health, headers = call(base + "/api/health")
    checks += [("health", status == 200), ("non_personhood", health.get("non_personhood_classifier") is True), ("csp", "Content-Security-Policy" in headers)]
    payload = json.loads((ROOT / "examples" / "zombie_loop.json").read_text(encoding="utf-8"))
    status, created, _ = call(base + "/api/worldlines", "POST", payload)
    wl = created.get("worldline", {}); wid = wl.get("worldline_id")
    checks += [("create", status == 201), ("zombie", wl.get("loop_diagnostics", {}).get("state") == "ZOMBIE_CLOSURE"), ("no_humanity_score", wl.get("carrier", {}).get("humanity_score") is None)]
    intervention = json.loads((ROOT / "examples" / "zombie_intervention.json").read_text(encoding="utf-8"))
    status, ir, _ = call(base + f"/api/worldlines/{wid}/intervention", "POST", intervention)
    checks.append(("intervention", status == 200 and ir.get("worldline", {}).get("mesh85", {}).get("closure") == "AWAITING_WORLD_EFFECT"))
    outcome = json.loads((ROOT / "examples" / "zombie_outcome.json").read_text(encoding="utf-8"))
    status, orr, _ = call(base + f"/api/worldlines/{wid}/outcome", "POST", outcome)
    checks.append(("outcome", status == 200 and orr.get("worldline", {}).get("mesh85", {}).get("closure") == "FULL_GENERATIVE_WORLDLINE_CLOSURE"))
    status, pub, _ = call(base + f"/api/worldlines/{wid}/public")
    checks.append(("public_boundary", status == 200 and pub.get("personhood_assessment") == "NOT_PERFORMED"))
    status, audit, _ = call(base + "/api/audit/verify")
    checks.append(("audit", status == 200 and audit.get("valid") is True))
    status, dash, _ = call(base + "/api/dashboard")
    checks.append(("dashboard_no_scores", status == 200 and dash.get("personhood_score_count") == 0))
finally:
    server.shutdown(); server.server_close(); thread.join(timeout=2)
    for suffix in ("", "-wal", "-shm"):
        p = ROOT / "var" / f"acceptance.db{suffix}"
        if p.exists(): p.unlink()
failed = [n for n, ok in checks if not ok]
report = {"suite": "http_acceptance", "passed": not failed, "passed_count": len(checks)-len(failed), "total_count": len(checks), "failed": failed}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["passed"] else 1)

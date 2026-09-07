import json
from pathlib import Path
import threading
import time
from urllib.request import Request, urlopen

from vitavector85.server import VitaVectorServer

ROOT = Path(__file__).resolve().parents[1]


def request_json(url, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8")), dict(resp.headers)


def test_server_endpoints(tmp_path):
    server = VitaVectorServer(("127.0.0.1", 0), ROOT, tmp_path / "server.db", quiet=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        status, health, headers = request_json(base + "/api/health")
        assert status == 200
        assert health["non_personhood_classifier"] is True
        assert headers.get("X-Content-Type-Options") == "nosniff"
        payload = json.loads((ROOT / "examples" / "zombie_loop.json").read_text(encoding="utf-8"))
        status, created, _ = request_json(base + "/api/worldlines", "POST", payload)
        assert status == 201
        wid = created["worldline"]["worldline_id"]
        status, got, _ = request_json(base + f"/api/worldlines/{wid}")
        assert got["worldline"]["carrier"]["humanity_score"] is None
        status, public, _ = request_json(base + f"/api/worldlines/{wid}/public")
        assert public["personhood_assessment"] == "NOT_PERFORMED"
        status, audit, _ = request_json(base + "/api/audit/verify")
        assert audit["valid"] is True
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)

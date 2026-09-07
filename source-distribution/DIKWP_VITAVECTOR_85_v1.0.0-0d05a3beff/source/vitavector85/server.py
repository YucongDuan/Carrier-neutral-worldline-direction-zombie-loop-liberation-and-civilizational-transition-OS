from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse

from .core import VERSION, compile_worldline, record_intervention, record_outcome, generate_successor, public_summary, system_summary
from .store import WorldlineStore


class VitaVectorHandler(SimpleHTTPRequestHandler):
    server_version = f"VITAVECTOR85/{VERSION}"

    @property
    def app(self) -> "VitaVectorServer":
        return self.server  # type: ignore[return-value]

    def log_message(self, fmt: str, *args: Any) -> None:
        if not self.app.quiet:
            super().log_message(fmt, *args)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'")
        super().end_headers()

    def _json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 2_000_000:
            raise ValueError("request too large")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid JSON") from exc
        if not isinstance(value, dict):
            raise ValueError("JSON object required")
        return value

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/api/health", "/api/summary"}:
            self._json(200, system_summary())
            return
        if path == "/api/dashboard":
            self._json(200, self.app.store.dashboard())
            return
        if path == "/api/worldlines":
            self._json(200, {"worldlines": self.app.store.list()})
            return
        if path == "/api/audit":
            self._json(200, {"events": self.app.store.audit()})
            return
        if path == "/api/audit/verify":
            self._json(200, self.app.store.verify_audit())
            return
        match = re.fullmatch(r"/api/worldlines/([^/]+)", path)
        if match:
            record = self.app.store.get(match.group(1))
            self._json(200, record) if record else self._json(404, {"error": "worldline not found"})
            return
        match = re.fullmatch(r"/api/worldlines/([^/]+)/public", path)
        if match:
            record = self.app.store.get(match.group(1))
            self._json(200, public_summary(record["worldline"])) if record else self._json(404, {"error": "worldline not found"})
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            payload = self._body()
            if path == "/api/worldlines":
                wl = compile_worldline(payload)
                self._json(201, self.app.store.save(wl, event_type="WORLDLINE_COMPILE"))
                return
            match = re.fullmatch(r"/api/worldlines/([^/]+)/intervention", path)
            if match:
                record = self.app.store.get(match.group(1))
                if not record:
                    self._json(404, {"error": "worldline not found"}); return
                wl = record_intervention(record["worldline"], payload)
                self._json(200, self.app.store.save(wl, expected_revision=record["revision"], event_type="WORLDLINE_INTERVENTION"))
                return
            match = re.fullmatch(r"/api/worldlines/([^/]+)/outcome", path)
            if match:
                record = self.app.store.get(match.group(1))
                if not record:
                    self._json(404, {"error": "worldline not found"}); return
                wl = record_outcome(record["worldline"], payload)
                self._json(200, self.app.store.save(wl, expected_revision=record["revision"], event_type="WORLDLINE_OUTCOME"))
                return
            match = re.fullmatch(r"/api/worldlines/([^/]+)/successor", path)
            if match:
                record = self.app.store.get(match.group(1))
                if not record:
                    self._json(404, {"error": "worldline not found"}); return
                successor = generate_successor(record["worldline"], payload)
                self._json(201, self.app.store.save(successor, event_type="WORLDLINE_SUCCESSOR"))
                return
            self._json(404, {"error": "unknown endpoint"})
        except RuntimeError as exc:
            self._json(409, {"error": str(exc)})
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
        except Exception as exc:  # pragma: no cover
            self._json(500, {"error": f"internal error: {type(exc).__name__}"})


class VitaVectorServer(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], root: Path, db_path: Path, quiet: bool = False):
        handler = partial(VitaVectorHandler, directory=str(root))
        super().__init__(address, handler)
        self.store = WorldlineStore(db_path)
        self.root = root
        self.quiet = quiet


def serve(root: str | Path, db_path: str | Path, host: str = "127.0.0.1", port: int = 8781, quiet: bool = False) -> None:
    server = VitaVectorServer((host, int(port)), Path(root), Path(db_path), quiet=quiet)
    print(f"VITAVECTOR-85 running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import threading
from typing import Any, Iterator

from .core import canonical


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _hash_event(previous_hash: str, payload: dict[str, Any]) -> str:
    return hashlib.sha256((previous_hash + canonical(payload)).encode("utf-8")).hexdigest()


class WorldlineStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self.path, timeout=10)
        con.row_factory = sqlite3.Row
        try:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("PRAGMA foreign_keys=ON")
            yield con
            con.commit()
        finally:
            con.close()

    def _init_db(self) -> None:
        with self._connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS worldlines (
                    worldline_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    state TEXT NOT NULL,
                    closure TEXT NOT NULL,
                    body TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    digest TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    worldline_id TEXT,
                    revision INTEGER,
                    payload TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE
                );
                CREATE INDEX IF NOT EXISTS idx_worldlines_updated ON worldlines(updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_worldline ON audit_events(worldline_id, event_id);
                """
            )

    def _append_event(self, con: sqlite3.Connection, event_type: str, worldline_id: str | None, revision: int | None, payload: dict[str, Any]) -> None:
        row = con.execute("SELECT event_hash FROM audit_events ORDER BY event_id DESC LIMIT 1").fetchone()
        previous_hash = row["event_hash"] if row else "GENESIS"
        event = {
            "created_at": _now(),
            "event_type": event_type,
            "worldline_id": worldline_id,
            "revision": revision,
            "payload": payload,
        }
        event_hash = _hash_event(previous_hash, event)
        con.execute(
            "INSERT INTO audit_events(created_at,event_type,worldline_id,revision,payload,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?)",
            (event["created_at"], event_type, worldline_id, revision, json.dumps(payload, ensure_ascii=False, sort_keys=True), previous_hash, event_hash),
        )

    def save(self, worldline: dict[str, Any], expected_revision: int | None = None, event_type: str = "WORLDLINE_SAVE") -> dict[str, Any]:
        wid = str(worldline.get("worldline_id") or "")
        if not wid:
            raise ValueError("worldline_id is required")
        body = json.dumps(worldline, ensure_ascii=False, sort_keys=True)
        dig = hashlib.sha256(body.encode("utf-8")).hexdigest()
        state = str(worldline.get("loop_diagnostics", {}).get("state") or "UNKNOWN")
        closure = str(worldline.get("mesh85", {}).get("closure") or "UNKNOWN")
        now = _now()
        with self._lock, self._connect() as con:
            row = con.execute("SELECT revision, created_at FROM worldlines WHERE worldline_id=?", (wid,)).fetchone()
            if row:
                current = int(row["revision"])
                if expected_revision is not None and expected_revision != current:
                    raise RuntimeError(f"revision conflict: expected {expected_revision}, current {current}")
                revision = current + 1
                created_at = row["created_at"]
                con.execute(
                    "UPDATE worldlines SET title=?,state=?,closure=?,body=?,revision=?,digest=?,updated_at=? WHERE worldline_id=?",
                    (worldline.get("title", ""), state, closure, body, revision, dig, now, wid),
                )
            else:
                if expected_revision not in (None, 0):
                    raise RuntimeError("revision conflict: worldline does not exist")
                revision = 1
                created_at = now
                con.execute(
                    "INSERT INTO worldlines(worldline_id,title,state,closure,body,revision,digest,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                    (wid, worldline.get("title", ""), state, closure, body, revision, dig, created_at, now),
                )
            self._append_event(con, event_type, wid, revision, {"worldline_digest": dig, "state": state, "closure": closure})
        return {"worldline": worldline, "revision": revision, "digest": dig, "created_at": created_at, "updated_at": now}

    def get(self, worldline_id: str) -> dict[str, Any] | None:
        with self._connect() as con:
            row = con.execute("SELECT * FROM worldlines WHERE worldline_id=?", (worldline_id,)).fetchone()
        if not row:
            return None
        return {"worldline": json.loads(row["body"]), "revision": row["revision"], "digest": row["digest"], "created_at": row["created_at"], "updated_at": row["updated_at"]}

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT worldline_id,title,state,closure,revision,digest,created_at,updated_at FROM worldlines ORDER BY updated_at DESC LIMIT ?",
                (max(1, min(limit, 500)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def dashboard(self) -> dict[str, Any]:
        with self._connect() as con:
            rows = con.execute("SELECT state,closure,body FROM worldlines").fetchall()
        states: dict[str, int] = {}
        closures: dict[str, int] = {}
        flags: dict[str, int] = {}
        seeds = 0
        personhood_scores = 0
        for row in rows:
            states[row["state"]] = states.get(row["state"], 0) + 1
            closures[row["closure"]] = closures.get(row["closure"], 0) + 1
            wl = json.loads(row["body"])
            for flag in wl.get("loop_diagnostics", {}).get("flags", []):
                flags[flag] = flags.get(flag, 0) + 1
            seeds += len(wl.get("commons_seeds", []))
            if wl.get("carrier", {}).get("humanity_score") is not None:
                personhood_scores += 1
        return {
            "worldline_count": len(rows),
            "states": states,
            "closures": closures,
            "flag_counts": flags,
            "commons_seed_count": seeds,
            "personhood_score_count": personhood_scores,
            "personhood_scoring_forbidden": True,
        }

    def audit(self, limit: int = 200) -> list[dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute("SELECT * FROM audit_events ORDER BY event_id DESC LIMIT ?", (max(1, min(limit, 1000)),)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item["payload"])
            result.append(item)
        return result

    def verify_audit(self) -> dict[str, Any]:
        with self._connect() as con:
            rows = con.execute("SELECT * FROM audit_events ORDER BY event_id ASC").fetchall()
        previous = "GENESIS"
        errors: list[dict[str, Any]] = []
        head = "GENESIS"
        for row in rows:
            event = {
                "created_at": row["created_at"],
                "event_type": row["event_type"],
                "worldline_id": row["worldline_id"],
                "revision": row["revision"],
                "payload": json.loads(row["payload"]),
            }
            expected = _hash_event(previous, event)
            if row["previous_hash"] != previous or row["event_hash"] != expected:
                errors.append({"event_id": row["event_id"], "expected_previous": previous, "actual_previous": row["previous_hash"], "expected_hash": expected, "actual_hash": row["event_hash"]})
            previous = row["event_hash"]
            head = row["event_hash"]
        return {"valid": not errors, "event_count": len(rows), "errors": errors, "head_hash": head}

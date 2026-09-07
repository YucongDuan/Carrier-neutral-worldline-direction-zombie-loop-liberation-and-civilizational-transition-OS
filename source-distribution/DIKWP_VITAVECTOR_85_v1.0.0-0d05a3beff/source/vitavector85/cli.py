from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .core import VERSION, compile_worldline, record_intervention, record_outcome, generate_successor, public_summary, system_summary
from .server import serve
from .store import WorldlineStore


def _read(path: str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON object required")
    return data


def _write(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)


def _root() -> Path:
    source = Path(__file__).resolve().parent.parent
    resources = Path(__file__).resolve().parent / "resources"
    if (source / "index.html").is_file():
        return source
    if (resources / "index.html").is_file():
        return resources
    return source


def _runtime_root() -> Path:
    root = _root()
    return Path.cwd() / ".vitavector85" if root.name == "resources" else root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vitavector85", description="Carrier-neutral worldline direction and zombie-loop liberation")
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("summary")

    p = sub.add_parser("compile", help="compile a bounded worldline from JSON")
    p.add_argument("input"); p.add_argument("--out", required=True)
    p = sub.add_parser("intervene", help="record one selected intervention")
    p.add_argument("worldline"); p.add_argument("intervention"); p.add_argument("--out", required=True)
    p = sub.add_parser("outcome", help="record observed world effect")
    p.add_argument("worldline"); p.add_argument("outcome"); p.add_argument("--out", required=True)
    p = sub.add_parser("successor", help="generate a successor worldline")
    p.add_argument("worldline"); p.add_argument("--input"); p.add_argument("--out", required=True)
    p = sub.add_parser("public", help="emit public safe summary")
    p.add_argument("worldline"); p.add_argument("--out", required=True)
    p = sub.add_parser("demo", help="compile all bundled examples")
    p.add_argument("--out-dir", default="outputs/demo")
    p = sub.add_parser("verify-audit")
    p.add_argument("--db", default=str(_runtime_root() / "var" / "vitavector85.db"))
    p = sub.add_parser("serve")
    p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8781)
    p.add_argument("--db", default=str(_runtime_root() / "var" / "vitavector85.db")); p.add_argument("--quiet", action="store_true")
    sub.add_parser("selftest")
    return parser


def selftest() -> dict[str, Any]:
    root = _root()
    zombie = compile_worldline(_read(str(root / "examples" / "zombie_loop.json")))
    regen = compile_worldline(_read(str(root / "examples" / "regenerative_transition.json")))
    checks = {
        "no_humanity_score": zombie["carrier"]["humanity_score"] is None,
        "no_personhood_assessment": zombie["carrier"]["personhood_assessment"] == "NOT_PERFORMED",
        "zombie_detected": zombie["loop_diagnostics"]["state"] == "ZOMBIE_CLOSURE",
        "regenerative_detected": regen["loop_diagnostics"]["state"] == "REGENERATIVE_ASCENT",
        "semantic_11111": zombie["semantic_continuity"]["vector"] == "11111",
        "one_primary_transition": bool(zombie["primary_transition"]["code"]),
        "non_core_authority_zero": zombie["mesh85"]["non_core_semantic_authority"] == 0,
    }
    return {"passed": all(checks.values()), "checks": checks}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = _root()
    if args.command == "summary":
        print(json.dumps(system_summary(), ensure_ascii=False, indent=2)); return 0
    if args.command == "compile":
        _write(args.out, compile_worldline(_read(args.input))); return 0
    if args.command == "intervene":
        _write(args.out, record_intervention(_read(args.worldline), _read(args.intervention))); return 0
    if args.command == "outcome":
        _write(args.out, record_outcome(_read(args.worldline), _read(args.outcome))); return 0
    if args.command == "successor":
        payload = _read(args.input) if args.input else {}
        _write(args.out, generate_successor(_read(args.worldline), payload)); return 0
    if args.command == "public":
        _write(args.out, public_summary(_read(args.worldline))); return 0
    if args.command == "demo":
        out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
        for example in sorted((root / "examples").glob("*.json")):
            if example.stem.endswith(("_intervention", "_outcome")):
                continue
            _write(out / f"{example.stem}.worldline.json", compile_worldline(_read(str(example))))
        return 0
    if args.command == "verify-audit":
        print(json.dumps(WorldlineStore(args.db).verify_audit(), ensure_ascii=False, indent=2)); return 0
    if args.command == "serve":
        serve(root, args.db, args.host, args.port, args.quiet); return 0
    if args.command == "selftest":
        result = selftest(); print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if result["passed"] else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

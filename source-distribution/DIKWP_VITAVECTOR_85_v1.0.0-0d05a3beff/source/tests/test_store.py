import json
from pathlib import Path

from vitavector85.core import compile_worldline
from vitavector85.store import WorldlineStore

ROOT = Path(__file__).resolve().parents[1]


def test_store_save_get_audit(tmp_path):
    payload = json.loads((ROOT / "examples" / "zombie_loop.json").read_text(encoding="utf-8"))
    wl = compile_worldline(payload)
    store = WorldlineStore(tmp_path / "test.db")
    saved = store.save(wl)
    assert saved["revision"] == 1
    got = store.get(wl["worldline_id"])
    assert got and got["worldline"]["loop_diagnostics"]["state"] == "ZOMBIE_CLOSURE"
    assert store.verify_audit()["valid"] is True


def test_dashboard_has_no_personhood_scores(tmp_path):
    payload = json.loads((ROOT / "examples" / "regenerative_transition.json").read_text(encoding="utf-8"))
    wl = compile_worldline(payload)
    store = WorldlineStore(tmp_path / "test.db")
    store.save(wl)
    dash = store.dashboard()
    assert dash["personhood_score_count"] == 0
    assert dash["personhood_scoring_forbidden"] is True


def test_revision_conflict(tmp_path):
    payload = json.loads((ROOT / "examples" / "zombie_loop.json").read_text(encoding="utf-8"))
    wl = compile_worldline(payload)
    store = WorldlineStore(tmp_path / "test.db")
    store.save(wl)
    try:
        store.save(wl, expected_revision=0)
    except RuntimeError as exc:
        assert "revision conflict" in str(exc)
    else:
        raise AssertionError("expected conflict")

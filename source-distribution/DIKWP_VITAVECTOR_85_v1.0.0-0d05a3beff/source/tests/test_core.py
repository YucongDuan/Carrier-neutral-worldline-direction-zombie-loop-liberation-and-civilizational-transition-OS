import json
from pathlib import Path

import pytest

from vitavector85.core import compile_worldline, record_intervention, record_outcome, generate_successor, public_summary, system_summary

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


def test_summary_forbids_personhood_score():
    s = system_summary()
    assert s["non_personhood_classifier"] is True
    assert s["humanity_score"] is None


@pytest.mark.parametrize(
    "filename,state",
    [
        ("zombie_loop.json", "ZOMBIE_CLOSURE"),
        ("parasitic_loop.json", "PARASITIC_CLOSURE"),
        ("domination_descent.json", "DOMINATION_DESCENT"),
        ("terminal_harm.json", "TERMINAL_HARM_HOLD"),
        ("civilizing_transition.json", "CIVILIZING_TRANSITION"),
        ("regenerative_transition.json", "REGENERATIVE_ASCENT"),
    ],
)
def test_state_detection(filename, state):
    wl = compile_worldline(load(filename))
    assert wl["loop_diagnostics"]["state"] == state
    assert wl["semantic_continuity"]["vector"] == "11111"
    assert wl["carrier"]["personhood_assessment"] == "NOT_PERFORMED"
    assert wl["carrier"]["humanity_score"] is None
    assert wl["carrier"]["intrinsic_worth_score"] is None


def test_zombie_applies_to_window_not_person():
    wl = compile_worldline(load("zombie_loop.json"))
    assert wl["loop_diagnostics"]["applies_to"] == "WORLDLINE_WINDOW_ONLY"
    assert wl["loop_diagnostics"]["never_applies_to"] == "PERMANENT_PERSON_ESSENCE"
    assert wl["primary_transition"]["code"] == "INJECT_EXTERNAL_DIFFERENCE_AND_REQUIRE_WORLD_EFFECT"


def test_terminal_freeze_action():
    wl = compile_worldline(load("terminal_harm.json"))
    assert wl["primary_transition"]["code"] == "FREEZE_HARM_CAPABILITY_AND_PRESERVE_EVIDENCE"
    assert "HOLD" in wl["mesh85"]["closure"]


def test_intervention_closes_execution_debt():
    wl = compile_worldline(load("zombie_loop.json"))
    updated = record_intervention(wl, load("zombie_intervention.json"))
    assert len(updated["interventions"]) == 1
    assert updated["mesh85"]["debts"]["authority_debt"] == "CLOSED"
    assert updated["mesh85"]["debts"]["execution_debt"] == "CLOSED"
    assert updated["mesh85"]["closure"] == "AWAITING_WORLD_EFFECT"


def test_outcome_can_liberate_zombie_loop():
    wl = compile_worldline(load("zombie_loop.json"))
    wl = record_intervention(wl, load("zombie_intervention.json"))
    updated = record_outcome(wl, load("zombie_outcome.json"))
    assert updated["loop_diagnostics"]["state"] in {"CIVILIZING_TRANSITION", "REGENERATIVE_ASCENT", "OPEN_REPAIR"}
    assert updated["mesh85"]["closure"] == "FULL_GENERATIVE_WORLDLINE_CLOSURE"
    assert updated["mesh85"]["debts"]["effect_debt"] == "CLOSED"
    assert updated["commons_seeds"]


def test_successor_keeps_lineage():
    wl = compile_worldline(load("regenerative_transition.json"))
    nxt = generate_successor(wl)
    assert nxt["lineage"]["parent_worldline"] == wl["worldline_id"]
    assert wl["worldline_id"] in nxt["dikwp"]["D"]["sources"]
    assert nxt["carrier"]["personhood_assessment"] == "NOT_PERFORMED"


def test_public_summary_is_bounded():
    wl = compile_worldline(load("zombie_loop.json"))
    p = public_summary(wl)
    assert p["personhood_assessment"] == "NOT_PERFORMED"
    assert "permanent person essence" in p["boundary"]
    assert "input" not in p


def test_deterministic_id_for_same_payload():
    p = load("zombie_loop.json")
    a = compile_worldline(p)
    b = compile_worldline(p)
    assert a["worldline_id"] == b["worldline_id"]


def test_no_scalar_aggregate_direction_score():
    wl = compile_worldline(load("regenerative_transition.json"))
    assert "score" not in wl["direction_vector"]
    assert all(v["non_compensable"] is True for v in wl["direction_vector"].values())


def test_missing_outcome_rejected():
    wl = compile_worldline(load("zombie_loop.json"))
    with pytest.raises(ValueError):
        record_outcome(wl, {})

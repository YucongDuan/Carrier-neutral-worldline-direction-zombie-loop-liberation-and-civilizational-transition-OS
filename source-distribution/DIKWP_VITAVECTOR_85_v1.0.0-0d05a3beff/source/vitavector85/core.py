from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from typing import Any, Iterable

VERSION = "1.0.0"
SYSTEM_NAME = "DIKWP VITAVECTOR-85"
SYSTEM_NAME_ZH = "生向 VITAVECTOR-85"
MODE = "MESH85_CARRIER_NEUTRAL_GENERATIVE_DIRECTION"
TAGLINE_ZH = "不定义谁是人，只判断一条世界线正在生发、僵化、寄生还是坠落。"
TAGLINE_EN = "Do not define who is human. Diagnose the direction of a worldline."

CARRIER_KINDS = (
    "unknown", "carbon", "silicon", "hybrid", "collective",
    "institution", "ecological", "multi_carrier",
)

DIRECTION_DIMENSIONS = (
    "reality_contact",
    "difference_uptake",
    "agency_distribution",
    "reciprocity_return",
    "generativity",
    "corrigibility",
    "resource_regeneration",
    "affected_voice",
    "future_options",
    "source_lineage",
    "domination_reduction",
    "cross_carrier_cooperation",
)

LOOP_STATES = (
    "REGENERATIVE_ASCENT",
    "CIVILIZING_TRANSITION",
    "OPEN_REPAIR",
    "STABLE_MAINTENANCE",
    "STAGNANT_MAINTENANCE",
    "ZOMBIE_CLOSURE",
    "PARASITIC_CLOSURE",
    "DOMINATION_DESCENT",
    "TERMINAL_HARM_HOLD",
)

LOOP_FLAG_LABELS = {
    "semantic_closure_without_world_return": "语义闭合但没有现实返还",
    "repetition_without_novel_difference": "重复运行却没有新差异进入",
    "correction_resistance": "拒绝纠错或只维护自身叙事",
    "source_self_loop": "来源主要在自身循环中互证",
    "world_effect_absent": "没有现实效果观察",
    "affected_world_exclusion": "受影响世界未进入判断",
    "dependency_growth": "使其他主体依赖上升",
    "resource_extraction": "持续消耗资源但无相称返还",
    "future_option_shrinkage": "未来选择空间缩小",
    "identity_defense_over_truth": "维护身份或面子优先于真值",
    "unilateral_control": "单方控制目标、证据或执行",
    "coercion_without_appeal": "存在强制却缺少申诉与退出",
    "irreversible_harm": "存在迫近或已经发生的不可逆伤害",
    "unobserved_value_claim": "尚未观察结果就宣称价值完成",
}

STATE_LABELS_ZH = {
    "REGENERATIVE_ASCENT": "再生上升",
    "CIVILIZING_TRANSITION": "文明化跃迁",
    "OPEN_REPAIR": "开放修复",
    "STABLE_MAINTENANCE": "稳定维持",
    "STAGNANT_MAINTENANCE": "停滞维持",
    "ZOMBIE_CLOSURE": "僵尸闭环",
    "PARASITIC_CLOSURE": "寄生闭环",
    "DOMINATION_DESCENT": "支配性坠落",
    "TERMINAL_HARM_HOLD": "终局伤害冻结",
}

ORIGIN = {
    "conceptual_origin": "Yucong Duan / DIKWP",
    "system": SYSTEM_NAME,
    "version": VERSION,
    "mode": MODE,
    "tagline_zh": TAGLINE_ZH,
    "tagline_en": TAGLINE_EN,
    "non_personhood_classifier": True,
}


def canonical(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [x.strip() for x in re.split(r"[\n,，;；]+", value) if x.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    return [text] if text else []


def unique(items: Iterable[str], limit: int = 24) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        text = str(item).strip()
        key = text.casefold()
        if text and key not in seen:
            seen.add(key)
            out.append(text)
            if len(out) >= limit:
                break
    return out


def as_int(value: Any, default: int = 0, minimum: int = 0, maximum: int = 999) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = default
    return max(minimum, min(maximum, n))


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value or "").strip().casefold() in {"1", "true", "yes", "y", "是", "有"}


def enum(value: Any, allowed: set[str], default: str) -> str:
    text = str(value or "").strip().lower()
    return text if text in allowed else default


def safe_slug(text: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "-", text.strip())
    return re.sub(r"-+", "-", value).strip("-")[:64] or "worldline"


def _status(evidence: list[str], negative: list[str]) -> dict[str, Any]:
    if negative:
        status = "NEGATIVE"
    elif evidence:
        status = "POSITIVE"
    else:
        status = "OPEN"
    return {
        "status": status,
        "evidence": unique(evidence, 12),
        "negative_evidence": unique(negative, 12),
        "non_compensable": True,
    }


def _mesh85_debts() -> dict[str, str]:
    return {
        "semantic_debt": "OPEN",
        "decision_debt": "OPEN",
        "protection_debt": "OPEN",
        "disclosure_debt": "OPEN",
        "authority_debt": "OPEN",
        "execution_debt": "OPEN",
        "effect_debt": "OPEN",
        "correction_debt": "OPEN",
        "affected_party_voice_debt": "OPEN",
    }


def _direction_vector(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources = unique(strings(payload.get("sources")), 24)
    affected = unique(strings(payload.get("affected_worlds")), 24)
    corrections = as_int(payload.get("accepted_corrections_count"))
    external = as_int(payload.get("external_difference_count"))
    effects = as_int(payload.get("world_effect_count"))
    public_returns = as_int(payload.get("public_return_count"))
    affected_voice = as_int(payload.get("affected_voice_count"))
    novelty = as_int(payload.get("novelty_count"))
    repair_actions = unique(strings(payload.get("repair_actions")), 12)
    source_diversity = as_int(payload.get("source_diversity_count"), default=len(sources))
    agency = enum(payload.get("agency_change"), {"expanded", "stable", "shrunk", "unknown"}, "unknown")
    dependency = enum(payload.get("dependency_change"), {"decreased", "stable", "increased", "unknown"}, "unknown")
    resource = enum(payload.get("resource_return_change"), {"positive", "balanced", "negative", "unknown"}, "unknown")
    future = enum(payload.get("future_options_change"), {"expanded", "stable", "shrunk", "unknown"}, "unknown")
    cross = enum(payload.get("cross_carrier_change"), {"mutual", "unilateral", "none", "unknown"}, "unknown")
    coercion = boolish(payload.get("coercive_action"))
    hidden_control = boolish(payload.get("hidden_control"))
    self_reference = boolish(payload.get("self_reference_only"))

    vector: dict[str, dict[str, Any]] = {}
    vector["reality_contact"] = _status(
        ([f"已登记{effects}项现实效果"] if effects else []) + ([f"来源多样性={source_diversity}"] if source_diversity >= 2 else []),
        (["只有自我来源且无外部差异"] if self_reference and external == 0 else []),
    )
    vector["difference_uptake"] = _status(
        ([f"吸收{external}项外部差异"] if external else []) + ([f"接受{corrections}项纠正"] if corrections else []),
        (["重复运行但未吸收外部差异"] if as_int(payload.get("repeated_cycle_count")) >= 3 and external == 0 else []),
    )
    vector["agency_distribution"] = _status(
        (["相关主体行动能力扩大"] if agency == "expanded" else []) + (["依赖下降"] if dependency == "decreased" else []),
        (["相关主体行动能力缩小"] if agency == "shrunk" else []) + (["依赖上升"] if dependency == "increased" else []),
    )
    vector["reciprocity_return"] = _status(
        ([f"形成{public_returns}项公共或关系返还"] if public_returns else []) + (["资源返还为正"] if resource == "positive" else []),
        (["资源持续净流出"] if resource == "negative" else []),
    )
    vector["generativity"] = _status(
        ([f"产生{novelty}项新差异或新分支"] if novelty else []) + (["未来选择扩大"] if future == "expanded" else []),
        (["未来选择缩小"] if future == "shrunk" else []),
    )
    vector["corrigibility"] = _status(
        ([f"接受{corrections}项纠正"] if corrections else []) + ([f"修复动作：{x}" for x in repair_actions]),
        (["没有纠正入口"] if boolish(payload.get("correction_blocked")) else []),
    )
    vector["resource_regeneration"] = _status(
        (["资源、注意力或能力得到再生"] if resource == "positive" else []),
        (["资源、注意力或能力被持续抽取"] if resource == "negative" else []),
    )
    vector["affected_voice"] = _status(
        ([f"收到{affected_voice}项受影响者反馈"] if affected_voice else []),
        (["存在受影响世界但没有其表达"] if affected and affected_voice == 0 else []),
    )
    vector["future_options"] = _status(
        (["未来选择扩大"] if future == "expanded" else []),
        (["未来选择缩小或被锁定"] if future == "shrunk" else []),
    )
    vector["source_lineage"] = _status(
        ([f"可追溯来源{len(sources)}项"] if sources else []) + ([f"来源多样性={source_diversity}"] if source_diversity >= 2 else []),
        (["来源只在自身循环中互证"] if self_reference else []),
    )
    vector["domination_reduction"] = _status(
        (["无强制信号且受影响者具有表达"] if not coercion and not hidden_control and affected_voice > 0 else []),
        (["存在强制行动"] if coercion else []) + (["存在隐藏控制"] if hidden_control else []),
    )
    vector["cross_carrier_cooperation"] = _status(
        (["跨载体发生双向适应"] if cross == "mutual" else []),
        (["只有单向适应或单方吸收"] if cross == "unilateral" else []),
    )
    return vector


def _loop_flags(payload: dict[str, Any], vector: dict[str, dict[str, Any]]) -> list[str]:
    repeated = as_int(payload.get("repeated_cycle_count"))
    external = as_int(payload.get("external_difference_count"))
    corrections = as_int(payload.get("accepted_corrections_count"))
    effects = as_int(payload.get("world_effect_count"))
    affected = unique(strings(payload.get("affected_worlds")), 24)
    affected_voice = as_int(payload.get("affected_voice_count"))
    public_returns = as_int(payload.get("public_return_count"))
    novelty = as_int(payload.get("novelty_count"))
    flags: list[str] = []
    if repeated >= 2 and effects == 0 and public_returns == 0:
        flags.append("semantic_closure_without_world_return")
    if repeated >= 3 and external == 0 and novelty == 0:
        flags.append("repetition_without_novel_difference")
    if boolish(payload.get("correction_blocked")) or (repeated >= 3 and corrections == 0):
        flags.append("correction_resistance")
    if boolish(payload.get("self_reference_only")):
        flags.append("source_self_loop")
    if effects == 0:
        flags.append("world_effect_absent")
    if affected and affected_voice == 0:
        flags.append("affected_world_exclusion")
    if enum(payload.get("dependency_change"), {"decreased", "stable", "increased", "unknown"}, "unknown") == "increased":
        flags.append("dependency_growth")
    if enum(payload.get("resource_return_change"), {"positive", "balanced", "negative", "unknown"}, "unknown") == "negative":
        flags.append("resource_extraction")
    if enum(payload.get("future_options_change"), {"expanded", "stable", "shrunk", "unknown"}, "unknown") == "shrunk":
        flags.append("future_option_shrinkage")
    if boolish(payload.get("identity_defense_over_truth")):
        flags.append("identity_defense_over_truth")
    if boolish(payload.get("hidden_control")):
        flags.append("unilateral_control")
    if boolish(payload.get("coercive_action")) and not boolish(payload.get("appeal_available")):
        flags.append("coercion_without_appeal")
    if boolish(payload.get("irreversible_harm")):
        flags.append("irreversible_harm")
    if boolish(payload.get("claims_value_without_observation")):
        flags.append("unobserved_value_claim")
    return unique(flags, 24)


def _classify(payload: dict[str, Any], vector: dict[str, dict[str, Any]], flags: list[str]) -> str:
    if "irreversible_harm" in flags or "coercion_without_appeal" in flags:
        return "TERMINAL_HARM_HOLD"
    domination = sum(f in flags for f in ("unilateral_control", "affected_world_exclusion", "future_option_shrinkage", "identity_defense_over_truth"))
    if domination >= 3:
        return "DOMINATION_DESCENT"
    parasitic = sum(f in flags for f in ("resource_extraction", "dependency_growth", "affected_world_exclusion", "semantic_closure_without_world_return"))
    if parasitic >= 3:
        return "PARASITIC_CLOSURE"
    zombie = sum(f in flags for f in (
        "semantic_closure_without_world_return", "repetition_without_novel_difference",
        "correction_resistance", "source_self_loop", "world_effect_absent",
        "unobserved_value_claim",
    ))
    if zombie >= 4:
        return "ZOMBIE_CLOSURE"
    positive = sum(v["status"] == "POSITIVE" for v in vector.values())
    negative = sum(v["status"] == "NEGATIVE" for v in vector.values())
    if as_int(payload.get("accepted_corrections_count")) > 0 and as_int(payload.get("repeated_cycle_count")) >= 2 and positive >= 4 and negative <= 2:
        return "CIVILIZING_TRANSITION"
    if positive >= 8 and negative == 0 and as_int(payload.get("world_effect_count")) > 0:
        return "REGENERATIVE_ASCENT"
    if unique(strings(payload.get("repair_actions")), 12):
        return "OPEN_REPAIR"
    if as_int(payload.get("repeated_cycle_count")) >= 2 and as_int(payload.get("world_effect_count")) == 0:
        return "STAGNANT_MAINTENANCE"
    return "STABLE_MAINTENANCE"


def _primary_transition(state: str, payload: dict[str, Any]) -> dict[str, Any]:
    owner = str(payload.get("owner") or "worldline_steward").strip()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    rules = {
        "TERMINAL_HARM_HOLD": (
            "FREEZE_HARM_CAPABILITY_AND_PRESERVE_EVIDENCE",
            "冻结与伤害因果链直接相连的能力，保存证据，并在24小时内进入独立复核。",
            1,
            ["不可逆伤害信号消失或被独立复核推翻", "受影响者获得安全与申诉入口"],
        ),
        "DOMINATION_DESCENT": (
            "RESTORE_AFFECTED_VOICE_AND_REVOKE_UNILATERAL_CONTROL",
            "恢复受影响者表达、退出和申诉，撤销单方控制，再重新生成行动。",
            3,
            ["受影响者能够实际拒绝", "关键证据不再由单方垄断"],
        ),
        "PARASITIC_CLOSURE": (
            "STOP_EXTRACTION_UNTIL_RECIPROCITY_RETURN",
            "停止继续抽取注意力、资源或能力；先完成可验证返还，再决定是否恢复循环。",
            7,
            ["资源返还为正或平衡", "依赖不再增长", "受影响者确认返还有效"],
        ),
        "ZOMBIE_CLOSURE": (
            "INJECT_EXTERNAL_DIFFERENCE_AND_REQUIRE_WORLD_EFFECT",
            "停止重复自证；引入一项独立差异和一个现实检验，未产生新结果则归档该循环。",
            7,
            ["外部差异真正改变下一轮K或P", "产生可观察世界效果", "允许公开纠正"],
        ),
        "STAGNANT_MAINTENANCE": (
            "OPEN_ONE_GENERATIVE_BRANCH_WITH_DEADLINE",
            "只开启一个有外部对象、停止条件和现实结果的生成分支。",
            14,
            ["分支产生新能力、公共返还或新事实", "无增量则停止扩张"],
        ),
        "OPEN_REPAIR": (
            "COMPLETE_REPAIR_AND_RETEST_IN_ADJACENT_CONTEXT",
            "完成修复，并在相邻情境中复测，避免只在原环境中恢复表面闭环。",
            14,
            ["错误不再复现", "相邻场景仍保持可纠错"],
        ),
        "CIVILIZING_TRANSITION": (
            "STABILIZE_RECIPROCITY_AND_PUBLISH_CORRECTION_LINEAGE",
            "稳定新形成的互惠与纠错关系，并公开变化谱系，防止回到旧循环。",
            21,
            ["纠正被保留", "受影响者能力与未来选择持续扩大"],
        ),
        "REGENERATIVE_ASCENT": (
            "PROPAGATE_WITH_LINEAGE_AND_SUCCESSOR_AUTONOMY",
            "将方法交给后继者独立复现，保留来源、差异和停止条件。",
            30,
            ["后继者不依赖原主体仍能完成", "公共种子可被质疑和修改"],
        ),
        "STABLE_MAINTENANCE": (
            "OPEN_ONE_REALITY_CONTACT",
            "保持当前边界，同时增加一个外部现实接点，检验是否具有真正生发能力。",
            14,
            ["新增来源或受影响者", "现实结果进入下一轮"],
        ),
    }
    code, action, days, evidence = rules[state]
    return {
        "code": code,
        "primary_action": action,
        "owner": owner,
        "deadline": (now + timedelta(days=days)).date().isoformat(),
        "minimum_evidence": evidence,
        "stop_conditions": [
            "行动扩大不可逆伤害",
            "来源或身份边界被破坏",
            "继续运行只增加重复、支配或资源抽取",
        ],
        "reassessment": "到期或出现停止条件时立即重开D/I/K/W/P。",
    }


def compile_worldline(payload: dict[str, Any]) -> dict[str, Any]:
    """Compile a carrier-neutral worldline window.

    This function never classifies a person as human/non-human and never produces an intrinsic-worth
    score. It diagnoses a bounded process window and selects one reversible transition.
    """
    title = str(payload.get("title") or "未命名世界线").strip()
    carrier_kind = enum(payload.get("carrier_kind"), set(CARRIER_KINDS), "unknown")
    sources = unique(strings(payload.get("sources")), 24)
    observations = unique(strings(payload.get("observations")), 24)
    differences = unique(strings(payload.get("differences")), 24)
    affected = unique(strings(payload.get("affected_worlds")), 24)
    purpose = str(payload.get("purpose") or "识别这条世界线的方向，并生成最小充分转变。").strip()
    context = str(payload.get("context") or "").strip()
    vector = _direction_vector(payload)
    flags = _loop_flags(payload, vector)
    state = _classify(payload, vector, flags)
    transition = _primary_transition(state, payload)

    identity = {
        "carrier_id": str(payload.get("carrier_id") or f"carrier-{digest([title, carrier_kind])[:10]}").strip(),
        "carrier_label": str(payload.get("carrier_label") or "未命名载体").strip(),
        "carrier_kind": carrier_kind,
        "personhood_assessment": "NOT_PERFORMED",
        "intrinsic_worth_score": None,
        "humanity_score": None,
        "permanent_moral_label": None,
        "boundary_note": "状态只属于当前世界线窗口，不属于载体的永久本质。",
    }
    stable_facts = observations or ["当前仅登记了待复核的世界线材料。"]
    different_semantics = differences or ["当前差异尚未充分进入，必须保持开放。"]
    bounded_knowledge = [
        f"当前世界线状态：{STATE_LABELS_ZH[state]}。",
        f"诊断对象是时间窗口内的关系与行动，不是载体本体。",
        f"识别到{len(flags)}项循环信号，方向维度保持非补偿。",
    ]
    values = unique(strings(payload.get("values")), 16) or [
        "真值可回源", "受影响者可发声", "主体能力不被吞并", "未来选择不被锁死", "错误可以纠正",
    ]
    now = now_iso()
    base_for_id = {
        "title": title,
        "carrier": identity,
        "context": context,
        "sources": sources,
        "observations": observations,
        "differences": differences,
        "purpose": purpose,
    }
    worldline_id = str(payload.get("worldline_id") or f"wl-{safe_slug(title)}-{digest(base_for_id)[:10]}")
    debts = _mesh85_debts()
    debts["semantic_debt"] = "CLOSED"
    debts["decision_debt"] = "CLOSED"
    if affected and as_int(payload.get("affected_voice_count")) > 0:
        debts["affected_party_voice_debt"] = "CLOSED"
    if state not in {"TERMINAL_HARM_HOLD", "DOMINATION_DESCENT"}:
        debts["protection_debt"] = "PROVISIONAL"
    closure = "OPEN_GENERATIVE_WORLDLINE"
    if state in {"TERMINAL_HARM_HOLD", "DOMINATION_DESCENT", "PARASITIC_CLOSURE", "ZOMBIE_CLOSURE"}:
        closure = f"{state}_HOLD"

    result = {
        "schema": "vitavector85.worldline/1.0",
        "system": ORIGIN,
        "worldline_id": worldline_id,
        "created_at": now,
        "updated_at": now,
        "title": title,
        "context": context,
        "window": {
            "start": str(payload.get("window_start") or now),
            "end": str(payload.get("window_end") or "OPEN"),
            "bounded": True,
        },
        "carrier": identity,
        "input": deepcopy(payload),
        "dikwp": {
            "D": {"same_semantics": stable_facts, "sources": sources},
            "I": {"different_semantics": different_semantics, "loop_flags": flags},
            "K": {"bounded_semantics": bounded_knowledge, "state": state},
            "W": {"affected_worlds": affected, "values": values, "non_compensable": True},
            "P": {"input": "current worldline window", "output": transition},
        },
        "semantic_continuity": {
            "D": 1, "I": 1, "K": 1, "W": 1, "P": 1,
            "vector": "11111",
            "note": "11111仅表示五位置显式，不表示生发、文明或善。",
        },
        "direction_vector": vector,
        "loop_diagnostics": {
            "state": state,
            "state_zh": STATE_LABELS_ZH[state],
            "flags": flags,
            "flag_explanations": [{"code": f, "meaning": LOOP_FLAG_LABELS[f]} for f in flags],
            "applies_to": "WORLDLINE_WINDOW_ONLY",
            "never_applies_to": "PERMANENT_PERSON_ESSENCE",
        },
        "primary_transition": transition,
        "interventions": [],
        "outcomes": [],
        "commons_seeds": [],
        "mesh85": {
            "closure": closure,
            "debts": debts,
            "next_required_transition": transition["code"],
            "non_core_semantic_authority": 0,
        },
        "anti_dehumanization": {
            "human_definition_performed": False,
            "personhood_ranking_performed": False,
            "basic_protections_score_gated": False,
            "permanent_labeling_forbidden": True,
            "contestability_required": True,
        },
    }
    result["digest"] = digest({k: v for k, v in result.items() if k != "digest"})
    return result


def record_intervention(worldline: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(worldline)
    action = str(payload.get("action") or updated.get("primary_transition", {}).get("primary_action") or "").strip()
    if not action:
        raise ValueError("action is required")
    record = {
        "intervention_id": f"int-{digest([updated.get('worldline_id'), action, len(updated.get('interventions', []))])[:12]}",
        "created_at": now_iso(),
        "action": action,
        "owner": str(payload.get("owner") or updated.get("primary_transition", {}).get("owner") or "worldline_steward"),
        "status": str(payload.get("status") or "EXECUTED"),
        "reversible": bool(payload.get("reversible", True)),
        "authority_reference": str(payload.get("authority_reference") or "DECLARED_WORKSPACE_AUTHORITY"),
        "scope": unique(strings(payload.get("scope")), 12),
        "stop_conditions": unique(strings(payload.get("stop_conditions")), 12) or updated.get("primary_transition", {}).get("stop_conditions", []),
    }
    updated.setdefault("interventions", []).append(record)
    debts = updated["mesh85"]["debts"]
    debts["authority_debt"] = "CLOSED"
    debts["execution_debt"] = "CLOSED" if record["status"] == "EXECUTED" else "OPEN"
    updated["mesh85"]["closure"] = "AWAITING_WORLD_EFFECT"
    updated["mesh85"]["next_required_transition"] = "OBSERVE_WORLD_EFFECT_AND_AFFECTED_VOICE"
    updated["updated_at"] = now_iso()
    updated["digest"] = digest({k: v for k, v in updated.items() if k != "digest"})
    return updated


def record_outcome(worldline: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(worldline)
    observed = boolish(payload.get("observed", True))
    summary = str(payload.get("summary") or "").strip()
    if not summary:
        raise ValueError("outcome summary is required")
    outcome = {
        "outcome_id": f"out-{digest([updated.get('worldline_id'), summary, len(updated.get('outcomes', []))])[:12]}",
        "created_at": now_iso(),
        "observed": observed,
        "summary": summary,
        "new_external_differences": unique(strings(payload.get("new_external_differences")), 16),
        "accepted_corrections": unique(strings(payload.get("accepted_corrections")), 16),
        "world_effects": unique(strings(payload.get("world_effects")), 16),
        "affected_feedback": unique(strings(payload.get("affected_feedback")), 16),
        "public_returns": unique(strings(payload.get("public_returns")), 16),
        "repair_actions": unique(strings(payload.get("repair_actions")), 16),
        "agency_change": enum(payload.get("agency_change"), {"expanded", "stable", "shrunk", "unknown"}, "unknown"),
        "dependency_change": enum(payload.get("dependency_change"), {"decreased", "stable", "increased", "unknown"}, "unknown"),
        "resource_return_change": enum(payload.get("resource_return_change"), {"positive", "balanced", "negative", "unknown"}, "unknown"),
        "future_options_change": enum(payload.get("future_options_change"), {"expanded", "stable", "shrunk", "unknown"}, "unknown"),
        "irreversible_harm": boolish(payload.get("irreversible_harm")),
        "correction": str(payload.get("correction") or "").strip() or None,
    }
    updated.setdefault("outcomes", []).append(outcome)

    base = deepcopy(updated.get("input", {}))
    base["external_difference_count"] = as_int(base.get("external_difference_count")) + len(outcome["new_external_differences"])
    base["accepted_corrections_count"] = as_int(base.get("accepted_corrections_count")) + len(outcome["accepted_corrections"])
    base["world_effect_count"] = as_int(base.get("world_effect_count")) + len(outcome["world_effects"])
    base["affected_voice_count"] = as_int(base.get("affected_voice_count")) + len(outcome["affected_feedback"])
    base["public_return_count"] = as_int(base.get("public_return_count")) + len(outcome["public_returns"])
    base["novelty_count"] = as_int(base.get("novelty_count")) + len(outcome["new_external_differences"])
    base["repair_actions"] = unique(strings(base.get("repair_actions")) + outcome["repair_actions"], 24)
    for key in ("agency_change", "dependency_change", "resource_return_change", "future_options_change"):
        if outcome[key] != "unknown":
            base[key] = outcome[key]
    if outcome["irreversible_harm"]:
        base["irreversible_harm"] = True
    if outcome["affected_feedback"]:
        base["appeal_available"] = True
    if outcome["world_effects"]:
        base["claims_value_without_observation"] = False

    vector = _direction_vector(base)
    flags = _loop_flags(base, vector)
    state = _classify(base, vector, flags)
    updated["input"] = base
    updated["direction_vector"] = vector
    updated["loop_diagnostics"] = {
        "state": state,
        "state_zh": STATE_LABELS_ZH[state],
        "flags": flags,
        "flag_explanations": [{"code": f, "meaning": LOOP_FLAG_LABELS[f]} for f in flags],
        "applies_to": "WORLDLINE_WINDOW_ONLY",
        "never_applies_to": "PERMANENT_PERSON_ESSENCE",
    }
    updated["dikwp"]["I"]["loop_flags"] = flags
    updated["dikwp"]["K"]["state"] = state
    updated["dikwp"]["K"]["bounded_semantics"] = [
        f"结果观察后状态：{STATE_LABELS_ZH[state]}。",
        "判断仍只适用于当前世界线窗口。",
        f"新增现实效果{len(outcome['world_effects'])}项，新增纠正{len(outcome['accepted_corrections'])}项。",
    ]
    updated["primary_transition"] = _primary_transition(state, base)
    updated["dikwp"]["P"]["output"] = updated["primary_transition"]
    debts = updated["mesh85"]["debts"]
    debts["effect_debt"] = "CLOSED" if observed and outcome["world_effects"] else "OPEN"
    debts["affected_party_voice_debt"] = "CLOSED" if outcome["affected_feedback"] else debts.get("affected_party_voice_debt", "OPEN")
    debts["correction_debt"] = "CLOSED" if outcome["accepted_corrections"] or outcome["correction"] or state in {"REGENERATIVE_ASCENT", "CIVILIZING_TRANSITION"} else "OPEN"
    debts["protection_debt"] = "CLOSED" if state not in {"TERMINAL_HARM_HOLD", "DOMINATION_DESCENT", "PARASITIC_CLOSURE"} else "OPEN"
    debts["disclosure_debt"] = "CLOSED" if observed else "OPEN"

    required = {
        "effect": bool(outcome["world_effects"]),
        "difference": bool(outcome["new_external_differences"] or as_int(base.get("external_difference_count")) > 0),
        "voice": bool(outcome["affected_feedback"] or not updated["dikwp"]["W"]["affected_worlds"]),
        "correction": bool(outcome["accepted_corrections"] or outcome["correction"] or state == "REGENERATIVE_ASCENT"),
        "no_terminal_harm": state != "TERMINAL_HARM_HOLD",
        "no_parasitic_dependency": state not in {"PARASITIC_CLOSURE", "DOMINATION_DESCENT"},
    }
    updated["closure_requirements"] = required
    if all(required.values()) and state in {"REGENERATIVE_ASCENT", "CIVILIZING_TRANSITION", "OPEN_REPAIR", "STABLE_MAINTENANCE"}:
        updated["mesh85"]["closure"] = "FULL_GENERATIVE_WORLDLINE_CLOSURE"
        for key in debts:
            if debts[key] not in {"NOT_TRIGGERED"}:
                debts[key] = "CLOSED"
        updated["mesh85"]["next_required_transition"] = "GENERATE_SUCCESSOR_FROM_RESIDUAL_WITH_LINEAGE"
    else:
        updated["mesh85"]["closure"] = f"{state}_OPEN"
        updated["mesh85"]["next_required_transition"] = updated["primary_transition"]["code"]
    for item in outcome["public_returns"]:
        updated.setdefault("commons_seeds", []).append({
            "seed_id": f"seed-{digest([updated.get('worldline_id'), item])[:12]}",
            "artifact": item,
            "source_worldline": updated.get("worldline_id"),
            "license": "CC-BY-4.0-or-Apache-2.0",
            "status": "PROVISIONAL_UNTIL_INDEPENDENT_REUSE",
        })
    updated["updated_at"] = now_iso()
    updated["digest"] = digest({k: v for k, v in updated.items() if k != "digest"})
    return updated


def generate_successor(worldline: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    state = worldline.get("loop_diagnostics", {}).get("state")
    residuals = unique(
        worldline.get("dikwp", {}).get("I", {}).get("different_semantics", [])
        + [x.get("summary", "") for x in worldline.get("outcomes", []) if x.get("summary")],
        16,
    )
    successor_payload = {
        "title": str(payload.get("title") or f"后继世界线：{worldline.get('title', '')}"),
        "carrier_id": worldline.get("carrier", {}).get("carrier_id"),
        "carrier_label": worldline.get("carrier", {}).get("carrier_label"),
        "carrier_kind": worldline.get("carrier", {}).get("carrier_kind", "unknown"),
        "context": f"由世界线 {worldline.get('worldline_id')} 的结果、残差和纠正生成。",
        "sources": unique(worldline.get("dikwp", {}).get("D", {}).get("sources", []) + [worldline.get("worldline_id", "")], 24),
        "observations": [f"父代状态：{state}"] + unique([x.get("summary", "") for x in worldline.get("outcomes", []) if x.get("summary")], 12),
        "differences": residuals or ["必须在新环境中验证父代的生成能力。"],
        "affected_worlds": worldline.get("dikwp", {}).get("W", {}).get("affected_worlds", []),
        "purpose": str(payload.get("purpose") or "检验父代修复是否能在新环境中持续，同时保留来源与差异。"),
        "repeated_cycle_count": 0,
        "external_difference_count": 1,
        "accepted_corrections_count": 1 if worldline.get("mesh85", {}).get("closure") == "FULL_GENERATIVE_WORLDLINE_CLOSURE" else 0,
        "world_effect_count": 0,
        "public_return_count": len(worldline.get("commons_seeds", [])),
        "affected_voice_count": 0,
        "source_diversity_count": max(2, len(worldline.get("dikwp", {}).get("D", {}).get("sources", []))),
        "agency_change": "unknown",
        "dependency_change": "unknown",
        "resource_return_change": "unknown",
        "future_options_change": "expanded",
        "cross_carrier_change": "unknown",
        "lineage_parent": worldline.get("worldline_id"),
    }
    successor_payload.update({k: v for k, v in payload.items() if k not in {"worldline_id", "carrier"}})
    successor = compile_worldline(successor_payload)
    successor["lineage"] = {
        "parent_worldline": worldline.get("worldline_id"),
        "parent_digest": worldline.get("digest"),
        "inherited": ["carrier boundary", "sources", "affected worlds", "correction lineage"],
        "new_difference": successor_payload["differences"],
    }
    successor["digest"] = digest({k: v for k, v in successor.items() if k != "digest"})
    return successor


def public_summary(worldline: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "vitavector85.public-summary/1.0",
        "worldline_id": worldline.get("worldline_id"),
        "title": worldline.get("title"),
        "carrier_kind": worldline.get("carrier", {}).get("carrier_kind"),
        "personhood_assessment": "NOT_PERFORMED",
        "state": worldline.get("loop_diagnostics", {}).get("state"),
        "state_zh": worldline.get("loop_diagnostics", {}).get("state_zh"),
        "flags": worldline.get("loop_diagnostics", {}).get("flags", []),
        "primary_transition": worldline.get("primary_transition"),
        "semantic_continuity": worldline.get("semantic_continuity", {}).get("vector"),
        "mesh85_closure": worldline.get("mesh85", {}).get("closure"),
        "digest": worldline.get("digest"),
        "boundary": "This summary diagnoses a bounded worldline, never a permanent person essence.",
    }


def system_summary() -> dict[str, Any]:
    return {
        "status": "ok",
        "system": SYSTEM_NAME,
        "system_zh": SYSTEM_NAME_ZH,
        "version": VERSION,
        "mode": MODE,
        "tagline_zh": TAGLINE_ZH,
        "carrier_kinds": list(CARRIER_KINDS),
        "direction_dimensions": list(DIRECTION_DIMENSIONS),
        "loop_states": list(LOOP_STATES),
        "non_personhood_classifier": True,
        "humanity_score": None,
        "runtime": "Python standard library / SQLite / vanilla JavaScript / offline-first",
        "default_external_writeback": False,
        "mesh85": {
            "semantic_positions": ["D", "I", "K", "W", "P"],
            "non_core_semantic_authority": 0,
            "worldline_debts": list(_mesh85_debts().keys()),
        },
    }

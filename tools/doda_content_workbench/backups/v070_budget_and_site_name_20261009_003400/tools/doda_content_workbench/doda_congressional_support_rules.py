"""DoDA Congressional Support authoring: scored inputs and discrete hidden levels.

Authoring data only. Congressional Support behavior is not implemented in the runtime.
"""
import csv
import math

import doda_network_rules as net

INPUTS_FILE = "congressional_support_inputs.csv"
LEVELS_FILE = "congressional_support_levels.csv"
METRICS_FILE = "metrics.csv"

INPUT_COLUMNS = ["input_id", "display_name", "source_type", "metric_id", "scale", "floor_value",
                 "cap_value", "weight", "source_reference", "description", "sort_order", "active"]
LEVEL_COLUMNS = ["level_id", "display_name", "min_score", "grant_funding", "grant_territories",
                 "source_reference", "description", "sort_order", "active"]
SOURCE_TYPES = ("LIFETIME_EVIDENCE", "METRIC", "MISSION_SUCCESS_RATE")
SCALES = ("LINEAR", "LOG10")

RULES = {
    "scoring": "COMPENSATORY_WEIGHTED_AVERAGE",
    "componentRange": [0, 100],
    "levels": "DISCRETE_HIDDEN_FROM_PLAYER",
    "levelSelection": "HIGHEST_LEVEL_AT_OR_BELOW_SCORE",
    "grants": ["DEPARTMENT_FUNDING", "OPERATIONAL_TERRITORIES"],
    "fundingUnit": "FUNDING_UNITS",
    "departmentFundingIsMetric": False,
}


def component_score(value, floor, cap, scale="LINEAR"):
    """Return a 0 to 100 component score, or None when an input is undecided."""
    if value is None or floor is None or cap is None:
        return None
    if cap <= floor:
        raise ValueError("cap must be above floor")
    if scale not in SCALES:
        raise ValueError("scale must be LINEAR or LOG10")
    if scale == "LOG10" and floor < 1:
        raise ValueError("LOG10 floor must be at least 1")
    if value <= floor:
        return 0.0
    if value >= cap:
        return 100.0
    if scale == "LOG10":
        return 100.0 * (math.log10(value) - math.log10(floor)) / (math.log10(cap) - math.log10(floor))
    return 100.0 * (value - floor) / (cap - floor)


def combined_score(scores, weights):
    """Weighted average. A strong component can make up for a weak one."""
    total = 0.0
    weight_sum = 0
    for key, score in scores.items():
        weight = weights.get(key)
        if score is None or not weight:
            continue
        total += score * weight
        weight_sum += weight
    return total / weight_sum if weight_sum else None


def level_for_score(score, levels):
    """Highest level whose min_score is at or below the score, else None."""
    if score is None:
        return None
    best = None
    for level in sorted((lv for lv in levels if lv.get("minScore") is not None), key=lambda lv: lv["minScore"]):
        if level["minScore"] <= score:
            best = level
    return best


def _opt_int(raw, ctx, field, res, minimum, maximum=None):
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        res.errors.append(f"{ctx}: {field} must be a whole number")
        return None
    if value < minimum or (maximum is not None and value > maximum):
        limit = f"at least {minimum}" if maximum is None else f"between {minimum} and {maximum}"
        res.errors.append(f"{ctx}: {field} must be {limit}")
        return None
    return value


def _metric_ids(src):
    path = src / METRICS_FILE
    if not path.is_file():
        return None
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {row["metric_id"] for row in csv.DictReader(fh)}


def _validate_inputs(src, res):
    path = src / INPUTS_FILE
    if not path.is_file():
        return []
    rows = net.read_table(path, INPUT_COLUMNS, "congressional_support_inputs", res) or []
    metric_ids = _metric_ids(src)
    seen, pairs, items = set(), set(), []
    for r in rows:
        ctx = f"[congressional_support_inputs] Line {r['_line']}"
        iid = r["input_id"]
        if not iid or iid in seen:
            res.errors.append(f"{ctx}: blank or duplicate input_id '{iid}'")
            continue
        seen.add(iid)
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        source = r["source_type"].upper()
        if source not in SOURCE_TYPES:
            res.errors.append(f"{ctx}: source_type must be one of {', '.join(SOURCE_TYPES)}")
        metric = r["metric_id"]
        if source == "METRIC":
            if not metric:
                res.errors.append(f"{ctx}: a METRIC input needs a metric_id")
            elif metric_ids is not None and metric not in metric_ids:
                res.errors.append(f"{ctx}: metric_id '{metric}' is not a known metric")
        elif metric:
            res.errors.append(f"{ctx}: metric_id is only for METRIC inputs")
        scale = (r["scale"] or "LINEAR").upper()
        if scale not in SCALES:
            res.errors.append(f"{ctx}: scale must be one of {', '.join(SCALES)}")
        elif scale == "LOG10" and source != "LIFETIME_EVIDENCE":
            res.errors.append(f"{ctx}: LOG10 scale only applies to LIFETIME_EVIDENCE inputs")
        floor = _opt_int(r["floor_value"], ctx, "floor_value", res, 0)
        cap = _opt_int(r["cap_value"], ctx, "cap_value", res, 0, 100 if source == "MISSION_SUCCESS_RATE" else None)
        weight = _opt_int(r["weight"], ctx, "weight", res, 1)
        if floor is not None and cap is not None and cap <= floor:
            res.errors.append(f"{ctx}: cap_value must be above floor_value")
        if scale == "LOG10" and floor is not None and floor < 1:
            res.errors.append(f"{ctx}: a LOG10 floor_value must be at least 1")
        pair = (source, metric)
        if pair in pairs:
            res.errors.append(f"{ctx}: duplicate input for source '{source}' {metric}".rstrip())
        pairs.add(pair)
        active = net._bool(r["active"], ctx, res)
        if active and (floor is None or cap is None or weight is None):
            res.warnings.append(f"{ctx}: active input '{iid}' is missing floor, cap or weight")
        items.append({"inputId": iid, "displayName": r["display_name"], "sourceType": source,
                      "metricId": metric or None, "scale": scale, "floorValue": floor, "capValue": cap,
                      "weight": weight, "sourceReference": r["source_reference"] or None,
                      "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active})
    return sorted(items, key=lambda x: (x["sortOrder"] or 0, x["inputId"]))


def _validate_levels(src, res):
    path = src / LEVELS_FILE
    if not path.is_file():
        return []
    rows = net.read_table(path, LEVEL_COLUMNS, "congressional_support_levels", res) or []
    seen, items = set(), []
    for r in rows:
        ctx = f"[congressional_support_levels] Line {r['_line']}"
        lid = r["level_id"]
        if not lid or lid in seen:
            res.errors.append(f"{ctx}: blank or duplicate level_id '{lid}'")
            continue
        seen.add(lid)
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        minimum = _opt_int(r["min_score"], ctx, "min_score", res, 0, 100)
        funding = _opt_int(r["grant_funding"], ctx, "grant_funding", res, 0)
        territories = _opt_int(r["grant_territories"], ctx, "grant_territories", res, 0)
        active = net._bool(r["active"], ctx, res)
        if active and (minimum is None or (funding is None and territories is None)):
            res.warnings.append(f"{ctx}: active level '{lid}' is missing a score threshold or grants")
        items.append({"levelId": lid, "displayName": r["display_name"], "minScore": minimum,
                      "grantFunding": funding, "grantTerritories": territories,
                      "sourceReference": r["source_reference"] or None, "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active,
                      "_ctx": ctx})
    ordered = sorted(items, key=lambda x: (x["sortOrder"] or 0, x["levelId"]))
    valued = [item for item in ordered if item["minScore"] is not None]
    for a, b in zip(valued, valued[1:]):
        if not a["minScore"] < b["minScore"]:
            res.errors.append(f"{b['_ctx']}: min_score must strictly increase ({b['levelId']} is not above {a['levelId']})")
    return [{k: v for k, v in item.items() if not k.startswith("_")} for item in ordered]


def validate_congressional_support(root, res):
    src = root / "data_authoring" / "source"
    return {"inputs": _validate_inputs(src, res), "levels": _validate_levels(src, res),
            "rules": RULES, "implemented": False}

#!/usr/bin/env python3
r"""
DoDA Content Workbench - Personnel condition catalog (authoring slice).

Authored definitions only: which per-agent condition stats exist, their
ranges, and the severity bands that name each range. Current values belong to
the native simulation and campaign/save state, never to this catalog.

Settled decisions encoded here (2026-10-07):
  * PERS-03: The catalog holds per-agent stats only. Department scores stay in
    metrics.csv; world-pressure stats wait for their own slice.
  * PERS-04: Health is an at-a-glance summary, not an exact measure. It averages
    the contributing condition values (NEGATIVE stats are inverted first) and
    shows a colour-coded "Condition: ..." label. Health bands are therefore
    presentation only: no assignment effects and no forced off duty.
  * PERS-05: A band may suggest a care service where one exists; other actions
    stay as text until personal-care services are authored.
  * PERS-06: Any agent stat may count toward the Health average, chosen per stat
    with a formula: NORMALIZED (position within the stat's min-max range) or
    PERCENT_OF_REFERENCE (value as a percent of another stat, e.g. Current HP
    of Base HP). NEGATIVE stats are inverted before averaging. Loyalty does not
    count.
  * PERS-07: Death happens when Current HP drops to zero or below (killed in
    action): from NPC damage, or from severe illness when Nutrition, Stress, or
    Fatigue drive HP very low. That simulation is not implemented yet.

Source files:
  data_authoring/source/condition_stats.csv
  data_authoring/source/condition_bands.csv
  (condition_bands.suggested_care_service_id references care_services.csv)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import doda_network_rules as net
import doda_care_rules as care

TOOL_VERSION = "0.2.0"

STATS_FILE = "condition_stats.csv"
BANDS_FILE = "condition_bands.csv"

STAT_COLUMNS = ["stat_id", "display_name", "stat_category", "minimum_value", "maximum_value",
                "default_value", "direction", "storage_model", "derivation", "contributes_to_health",
                "health_formula", "health_reference_stat_id", "player_visibility", "high_value_meaning", "low_value_meaning", "source_reference",
                "description", "sort_order", "active"]
BAND_COLUMNS = ["band_id", "stat_id", "minimum_value", "maximum_value", "display_name", "severity",
                "assignment_effect", "forced_off_duty", "suggested_action", "suggested_care_service_id",
                "foims_warning", "ui_color", "source_reference", "description", "sort_order", "active"]

STAT_CATEGORIES = ("SUMMARY", "CONDITION", "PHYSICAL", "OPERATIONAL", "RELATIONSHIP")
DIRECTIONS = ("POSITIVE", "NEGATIVE")
STORAGE_MODELS = ("DIRECT", "DERIVED")
DERIVATIONS = ("AVERAGE_OF_CONTRIBUTORS", "FROM_ASSIGNMENTS")
HEALTH_FORMULAS = ("NORMALIZED", "PERCENT_OF_REFERENCE")
DEATH_STAT = "CURRENT_HP"
DEATH_RULE = {"statId": DEATH_STAT, "atOrBelow": 0, "outcome": "KILLED_IN_ACTION",
              "causes": ["NPC_DAMAGE", "SEVERE_ILLNESS"]}
VISIBILITIES = ("VISIBLE_BOTH", "DETAIL_ONLY", "HIDDEN_WITH_WARNINGS")
SEVERITIES = ("NONE", "LOW", "MODERATE", "HIGH", "CRITICAL", "TERMINAL")
ASSIGNMENT_EFFECTS = ("NONE", "MINOR_PENALTY", "MAJOR_PENALTY", "HIGH_RISK_TASK_BLOCK",
                      "NEW_TASK_BLOCK", "HARD_BLOCK")
COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

OPEN_ITEMS = {
    "PERS-OPEN-02": "Base/Current HP ranges and defaults.",
    "PERS-OPEN-04": "How Nutrition, Stress, and Fatigue reduce HP (severe illness), and incapacity rules.",
    "PERS-OPEN-05": "Tick rates, decay, and event effects (CondRules/EventsCat).",
    "PERS-OPEN-06": "Whether the Dead label follows the death state rather than the Health average.",
}


def _opt_int(value: str, ctx: str, field: str, res: net.Result) -> int | None:
    return net._int(value, ctx, field, res) if value else None


def _care_ids(src: Path) -> set[str]:
    path = src / care.CARE_FILE
    if not path.is_file():
        return set()
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return {(r.get("care_service_id") or "").strip() for r in csv.DictReader(fh)}


def validate_conditions(root: Path, res: net.Result) -> dict[str, Any]:
    src = root / "data_authoring" / "source"
    stat_rows = net.read_table(src / STATS_FILE, STAT_COLUMNS, "condition_stats", res)
    if stat_rows is None:
        return {"stats": [], "bands": []}
    stats: dict[str, dict[str, Any]] = {}
    for r in stat_rows:
        ctx = f"[condition_stats] Line {r['_line']}"
        sid = r["stat_id"]
        if not sid or sid in stats:
            res.errors.append(f"{ctx}: blank or duplicate stat_id '{sid}'")
            continue
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        for field, allowed in (("stat_category", STAT_CATEGORIES), ("direction", DIRECTIONS),
                               ("storage_model", STORAGE_MODELS), ("player_visibility", VISIBILITIES)):
            if r[field].upper() not in allowed:
                res.errors.append(f"{ctx}: {field} must be one of {', '.join(allowed)}")
        storage, derivation = r["storage_model"].upper(), r["derivation"].upper()
        if storage == "DERIVED" and derivation not in DERIVATIONS:
            res.errors.append(f"{ctx}: DERIVED stats need a derivation ({', '.join(DERIVATIONS)})")
        if storage == "DIRECT" and derivation:
            res.errors.append(f"{ctx}: DIRECT stats have no derivation")
        lo = _opt_int(r["minimum_value"], ctx, "minimum_value", res)
        hi = _opt_int(r["maximum_value"], ctx, "maximum_value", res)
        default = _opt_int(r["default_value"], ctx, "default_value", res)
        if lo is None:
            res.errors.append(f"{ctx}: minimum_value is required")
        if lo is not None and hi is not None and lo >= hi:
            res.errors.append(f"{ctx}: minimum_value must be below maximum_value")
        if default is not None and ((lo is not None and default < lo) or (hi is not None and default > hi)):
            res.errors.append(f"{ctx}: default_value is outside the stat range")
        contributes = net._bool(r["contributes_to_health"], ctx, res)
        formula, ref = r["health_formula"].upper(), r["health_reference_stat_id"]
        if contributes:
            if formula not in HEALTH_FORMULAS:
                res.errors.append(f"{ctx}: a Health contributor needs a health_formula "
                                  f"({', '.join(HEALTH_FORMULAS)})")
            if formula == "NORMALIZED" and (hi is None or lo is None):
                res.errors.append(f"{ctx}: NORMALIZED needs a known minimum and maximum")
            if formula == "PERCENT_OF_REFERENCE" and not ref:
                res.errors.append(f"{ctx}: PERCENT_OF_REFERENCE needs health_reference_stat_id")
            if formula != "PERCENT_OF_REFERENCE" and ref:
                res.errors.append(f"{ctx}: health_reference_stat_id is only used by PERCENT_OF_REFERENCE")
        elif formula or ref:
            res.errors.append(f"{ctx}: health_formula and reference are only set when the stat counts toward Health")
        if contributes and derivation == "AVERAGE_OF_CONTRIBUTORS":
            res.errors.append(f"{ctx}: the Health summary cannot contribute to itself")
        stats[sid] = {"statId": sid, "displayName": r["display_name"],
                      "statCategory": r["stat_category"].upper(), "minimumValue": lo, "maximumValue": hi,
                      "defaultValue": default, "direction": r["direction"].upper(), "storageModel": storage,
                      "derivation": derivation or None, "contributesToHealth": contributes,
                      "healthFormula": formula or None, "healthReferenceStatId": ref or None,
                      "playerVisibility": r["player_visibility"].upper(),
                      "highValueMeaning": r["high_value_meaning"], "lowValueMeaning": r["low_value_meaning"],
                      "sourceReference": r["source_reference"] or None, "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                      "active": net._bool(r["active"], ctx, res), "_ctx": ctx}

    for s in stats.values():
        ref = s["healthReferenceStatId"]
        if not s["contributesToHealth"] or s["healthFormula"] != "PERCENT_OF_REFERENCE" or not ref:
            continue
        target = stats.get(ref)
        if target is None:
            res.errors.append(f"{s['_ctx']}: unknown health_reference_stat_id '{ref}'")
        elif ref == s["statId"]:
            res.errors.append(f"{s['_ctx']}: a stat cannot be its own Health reference")
        else:
            if target["minimumValue"] is None or target["minimumValue"] < 1:
                res.errors.append(f"{s['_ctx']}: reference '{ref}' needs a minimum of at least 1 "
                                  "(it is divided by)")
            if s["active"] and not target["active"]:
                res.errors.append(f"{s['_ctx']}: active stat uses inactive Health reference '{ref}'")

    death = stats.get(DEATH_STAT)
    if death is not None and (death["minimumValue"] is None or death["minimumValue"] > 0):
        res.errors.append(f"{death['_ctx']}: {DEATH_STAT} must be able to reach 0 (death rule PERS-07)")

    summaries = [s for s in stats.values() if s["derivation"] == "AVERAGE_OF_CONTRIBUTORS"]
    if len(summaries) > 1:
        res.errors.append("[condition_stats] Only one stat may be the Health summary (AVERAGE_OF_CONTRIBUTORS)")
    for s in summaries:
        if s["active"] and not any(c["contributesToHealth"] and c["active"] for c in stats.values()):
            res.errors.append(f"{s['_ctx']}: active Health summary has no active contributors")

    bands = _validate_bands(src, stats, res)
    clean = lambda d: {k: v for k, v in d.items() if k != "_ctx"}
    return {"stats": sorted((clean(s) for s in stats.values()), key=lambda x: (x["sortOrder"] or 0, x["statId"])),
            "bands": [clean(b) for b in bands]}


def _validate_bands(src: Path, stats: dict[str, dict[str, Any]], res: net.Result) -> list[dict[str, Any]]:
    rows = net.read_table(src / BANDS_FILE, BAND_COLUMNS, "condition_bands", res) or []
    care_ids = _care_ids(src)
    bands: dict[str, dict[str, Any]] = {}
    for r in rows:
        ctx = f"[condition_bands] Line {r['_line']}"
        bid = r["band_id"]
        if not bid or bid in bands:
            res.errors.append(f"{ctx}: blank or duplicate band_id '{bid}'")
            continue
        stat = stats.get(r["stat_id"])
        if stat is None:
            res.errors.append(f"{ctx}: unknown stat_id '{r['stat_id']}'")
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        severity, effect = r["severity"].upper(), r["assignment_effect"].upper()
        if severity not in SEVERITIES:
            res.errors.append(f"{ctx}: severity must be one of {', '.join(SEVERITIES)}")
        if effect not in ASSIGNMENT_EFFECTS:
            res.errors.append(f"{ctx}: assignment_effect must be one of {', '.join(ASSIGNMENT_EFFECTS)}")
        lo = net._int(r["minimum_value"], ctx, "minimum_value", res)
        hi = net._int(r["maximum_value"], ctx, "maximum_value", res)
        if lo is not None and hi is not None and lo > hi:
            res.errors.append(f"{ctx}: minimum_value is above maximum_value")
        off_duty = net._bool(r["forced_off_duty"], ctx, res)
        active = net._bool(r["active"], ctx, res)
        care_id = r["suggested_care_service_id"]
        if care_id and care_id not in care_ids:
            res.errors.append(f"{ctx}: unknown suggested_care_service_id '{care_id}'")
        if r["ui_color"] and not COLOR_RE.match(r["ui_color"]):
            res.errors.append(f"{ctx}: ui_color must be #RRGGBB or blank")
        if stat is not None:
            if stat["derivation"] == "AVERAGE_OF_CONTRIBUTORS" and (effect != "NONE" or off_duty):
                res.errors.append(f"{ctx}: Health bands are presentation only (PERS-04): "
                                  "assignment_effect must be NONE and forced_off_duty false")
            if active and not stat["active"]:
                res.errors.append(f"{ctx}: active band belongs to inactive stat '{stat['statId']}'")
        bands[bid] = {"bandId": bid, "statId": r["stat_id"], "minimumValue": lo, "maximumValue": hi,
                      "displayName": r["display_name"], "severity": severity, "assignmentEffect": effect,
                      "forcedOffDuty": off_duty, "suggestedAction": r["suggested_action"] or None,
                      "suggestedCareServiceId": care_id or None, "foimsWarning": r["foims_warning"] or None,
                      "uiColor": r["ui_color"] or None, "sourceReference": r["source_reference"] or None,
                      "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active,
                      "_ctx": ctx}

    # Each stat's bands must tile its range: no gaps, no overlaps.
    for sid, stat in stats.items():
        own = sorted((b for b in bands.values() if b["statId"] == sid and b["minimumValue"] is not None
                      and b["maximumValue"] is not None), key=lambda b: b["minimumValue"])
        if not own:
            continue
        expected = stat["minimumValue"]
        for b in own:
            if expected is not None and b["minimumValue"] > expected:
                res.errors.append(f"[condition_bands] {sid}: gap before {b['bandId']} "
                                  f"({expected}-{b['minimumValue'] - 1} has no band)")
            elif expected is not None and b["minimumValue"] < expected:
                res.errors.append(f"[condition_bands] {sid}: {b['bandId']} overlaps the previous band")
            expected = b["maximumValue"] + 1
        if stat["maximumValue"] is not None:
            if expected - 1 < stat["maximumValue"]:
                res.errors.append(f"[condition_bands] {sid}: no band covers {expected}-{stat['maximumValue']}")
            elif expected - 1 > stat["maximumValue"]:
                res.errors.append(f"[condition_bands] {sid}: bands extend past maximum {stat['maximumValue']}")
    return sorted(bands.values(), key=lambda b: (b["statId"], b["minimumValue"] or 0))


def export(root: Path) -> tuple[net.Result, Path | None]:
    res = net.Result()
    data = validate_conditions(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "personnel_conditions_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "doda.personnel_conditions_catalog", "toolVersion": TOOL_VERSION,
               "generatedAtUtc": datetime.now(timezone.utc).isoformat(), **data,
               "healthSummary": {"method": "AVERAGE_OF_CONTRIBUTORS", "invertNegativeStats": True,
                                 "presentationOnly": True, "formulas": list(HEALTH_FORMULAS)},
               "deathRule": DEATH_RULE,
               "openItems": OPEN_ITEMS, "runtimeImplemented": False}
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="DoDA personnel condition catalog: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else net.find_project_root(Path(__file__).parent)
    if a.command == "validate":
        res = net.Result(); validate_conditions(root, res); out = None
    else:
        res, out = export(root)
    for w in res.warnings: print("WARNING:", w)
    for e in res.errors: print("ERROR:", e)
    print("Rows:", res.stats)
    if out: print("Exported:", out, "sha256", hashlib.sha256(out.read_bytes()).hexdigest())
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1


if __name__ == "__main__":
    sys.exit(main())

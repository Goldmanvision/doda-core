#!/usr/bin/env python3
r"""DoDA Content Workbench - territory and mission foundations (authoring only, no runtime).
Decisions: DESIGN_DECISIONS_2026-10-08.md (TERR-01 to TERR-26). Blank value means undecided."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import doda_network_rules as net

TOOL_VERSION = "0.1.0"
TERRITORIES_FILE = "territories.csv"
SETTINGS_FILE = "territory_settings.csv"
TIERS_FILE = "mission_tiers.csv"
FORMATS_FILE = "map_formats.csv"
MAPS_FILE = "maps.csv"

TERRITORY_COLUMNS = ["territory_id", "display_name", "locality", "region", "kind", "hq_name", "agents_allowed",
                     "population", "source_reference", "description", "sort_order", "active"]
SETTING_COLUMNS = ["setting_id", "display_name", "value", "unit", "source_reference", "description",
                   "sort_order", "active"]
TIER_COLUMNS = ["tier_id", "display_name", "min_lifetime_evidence", "authored_content", "source_reference",
                "description", "sort_order", "active"]
FORMAT_COLUMNS = ["format_id", "display_name", "role", "source_reference", "description", "sort_order", "active"]
MAP_COLUMNS = ["map_id", "format_id", "display_name", "has_objective", "agent_deployable", "source_reference",
               "description", "sort_order", "active"]

KINDS = ("STARTING", "PLOT", "PLAYER_ONLY")
KIND_UNLOCK = {"STARTING": "AT_START", "PLOT": "PLOT_EVENT", "PLAYER_ONLY": "PLOT_EVENT"}
FORMAT_ROLES = ("MISSION", "HUB", "TRANSIT")
SETTING_UNITS = {"TEAM_SIZE_LIMIT": "AGENTS", "OPEN_MISSION_AREA_CAP": "COUNT",
                 "MISSION_PERSISTENCE_MINUTES": "STRATEGIC_MINUTES",
                 "MAX_AGENT_SHARE_PER_HOUSING_PLACE": "PERCENT"}
PERCENT_SETTING = "MAX_AGENT_SHARE_PER_HOUSING_PLACE"
SCALE = 10000
MAX_DECIMAL_PLACES = 4

RULES = {
    "territories": {"mostAreGenerated": True, "authoredKinds": list(KINDS), "unlockByKind": KIND_UNLOCK,
                    "generatedUnlock": "EXPANSION_POINTS_EARNED_FROM_CONGRESSIONAL_SUPPORT",
                    "unlockIsPermanent": True},
    "evidence": {"counters": ["LIFETIME_EVIDENCE", "SPENDABLE_EVIDENCE"], "spendingLowersLifetime": False,
                 "missionTiers": "BANDS_OF_LIFETIME_EVIDENCE"},
    "leads": {"tiedToMissionAreaOrTerritory": False,
              "purchaseCreates": "MISSION_AREA_IN_RANDOM_ACCESSIBLE_TERRITORY", "mapPin": "VISUAL_ONLY"},
    "missionAreas": {"deployedAgentsAreNotSpawned": True, "agentsRunOnStatsAndDice": True,
                     "persistenceAfterDeployment": "GLOBAL_SETTING_TEMPLATE_MAY_OVERRIDE",
                     "openAreaCap": "DEPARTMENT_WIDE_UPGRADES_CAN_RAISE", "teamLimitSetting": "TEAM_SIZE_LIMIT"},
    "housing": {"capacityLimitsAgents": True, "spreadResidenceOut": True,
                "housingOutsideTerritoryAddsCommute": True, "tooManyAgentsHurtsPublicPerception": True},
}
OPEN_ITEMS = {
    "TERR-OPEN-01": "Mission tier names, count and thresholds; gating rules for the final authored tier.",
    "TERR-OPEN-02": "Values for the open mission area cap, persistence time and housing share limit; whether team size varies.",
    "TERR-OPEN-03": "Populations, housing capacity ranges, commute ranges and Public Perception bands for agent share.",
    "TERR-OPEN-04": "Territory Expansion points: earning rule from Congressional Support; generated-territory template.",
    "TERR-OPEN-05": "Mission area templates, hostile catalog, and how loadout weights the dice.",
    "TERR-OPEN-06": "Objective for MAP04; HQ names for Rosewell (if any).",
}


def _opt_int(raw, ctx, field, res, minimum):
    if not raw:
        return None
    try:
        n = int(raw)
    except ValueError:
        res.errors.append(f"{ctx}: {field} must be a whole number")
        return None
    if n < minimum:
        res.errors.append(f"{ctx}: {field} must be at least {minimum}")
        return None
    return n


def _percent(raw, ctx, res):
    try:
        d = Decimal(raw)
    except InvalidOperation:
        res.errors.append(f"{ctx}: value must be a number")
        return None
    if not d.is_finite() or not 0 < d <= 100:
        res.errors.append(f"{ctx}: value must be above 0 and at most 100 (percent)")
        return None
    exponent = d.normalize().as_tuple().exponent
    if isinstance(exponent, int) and exponent < -MAX_DECIMAL_PLACES:
        res.errors.append(f"{ctx}: value may have at most {MAX_DECIMAL_PLACES} decimal places")
        return None
    return d


def _strip(item):
    return {k: v for k, v in item.items() if not k.startswith("_")}


def _validate_territories(src, res):
    rows = net.read_table(src / TERRITORIES_FILE, TERRITORY_COLUMNS, "territories", res) or []
    seen, items = set(), []
    for r in rows:
        ctx = f"[territories] Line {r['_line']}"
        tid = r["territory_id"]
        if not tid or tid in seen:
            res.errors.append(f"{ctx}: blank or duplicate territory_id '{tid}'")
            continue
        seen.add(tid)
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        kind = r["kind"].upper()
        if kind not in KINDS:
            res.errors.append(f"{ctx}: kind must be one of {', '.join(KINDS)}")
        agents = net._bool(r["agents_allowed"], ctx, res)
        if kind == "PLAYER_ONLY" and agents:
            res.errors.append(f"{ctx}: a PLAYER_ONLY territory must set agents_allowed to false")
        if kind in ("STARTING", "PLOT") and not agents:
            res.errors.append(f"{ctx}: only a PLAYER_ONLY territory can set agents_allowed to false")
        if kind == "STARTING" and not r["hq_name"]:
            res.errors.append(f"{ctx}: the STARTING territory needs an hq_name")
        if kind == "PLOT" and not r["hq_name"]:
            res.warnings.append(f"{ctx}: plot territory '{tid}' has no hq_name yet")
        items.append({"territoryId": tid, "displayName": r["display_name"], "locality": r["locality"] or None,
                      "region": r["region"] or None, "kind": kind, "unlockMethod": KIND_UNLOCK.get(kind),
                      "hqName": r["hq_name"] or None, "agentsAllowed": agents,
                      "population": _opt_int(r["population"], ctx, "population", res, 1),
                      "sourceReference": r["source_reference"] or None, "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                      "active": net._bool(r["active"], ctx, res)})
    n_start = len([i for i in items if i["kind"] == "STARTING"])
    if n_start != 1:
        res.errors.append(f"[territories] exactly one territory must have kind STARTING (found {n_start})")
    return sorted(items, key=lambda x: (x["sortOrder"] or 0, x["territoryId"]))


def _validate_settings(src, res):
    rows = net.read_table(src / SETTINGS_FILE, SETTING_COLUMNS, "territory_settings", res) or []
    settings = {}
    for r in rows:
        ctx = f"[territory_settings] Line {r['_line']}"
        sid = r["setting_id"]
        if not sid or sid in settings:
            res.errors.append(f"{ctx}: blank or duplicate setting_id '{sid}'")
            continue
        if sid not in SETTING_UNITS:
            res.errors.append(f"{ctx}: unknown setting_id '{sid}' (expected {', '.join(SETTING_UNITS)})")
        elif r["unit"].upper() != SETTING_UNITS[sid]:
            res.errors.append(f"{ctx}: {sid} must use unit {SETTING_UNITS[sid]}")
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        value = None
        if r["value"]:
            if sid == PERCENT_SETTING:
                value = _percent(r["value"], ctx, res)
            else:
                n = _opt_int(r["value"], ctx, "value", res, 1)
                value = Decimal(n) if n is not None else None
        settings[sid] = {"settingId": sid, "displayName": r["display_name"], "unit": r["unit"].upper(),
                         "value": format(value.normalize(), "f") if value is not None else None,
                         "valueScaled": int((value * SCALE).to_integral_value()) if value is not None else None,
                         "sourceReference": r["source_reference"] or None, "description": r["description"],
                         "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                         "active": net._bool(r["active"], ctx, res)}
    for sid in SETTING_UNITS:
        if sid not in settings:
            res.errors.append(f"[territory_settings] Required setting '{sid}' is missing")
    return sorted(settings.values(), key=lambda x: (x["sortOrder"] or 0, x["settingId"]))


def _validate_tiers(src, res):
    rows = net.read_table(src / TIERS_FILE, TIER_COLUMNS, "mission_tiers", res) or []
    seen, items = set(), []
    for r in rows:
        ctx = f"[mission_tiers] Line {r['_line']}"
        tid = r["tier_id"]
        if not tid or tid in seen:
            res.errors.append(f"{ctx}: blank or duplicate tier_id '{tid}'")
            continue
        seen.add(tid)
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        items.append({"tierId": tid, "displayName": r["display_name"],
                      "minLifetimeEvidence": _opt_int(r["min_lifetime_evidence"], ctx, "min_lifetime_evidence", res, 0),
                      "authoredContent": net._bool(r["authored_content"], ctx, res),
                      "sourceReference": r["source_reference"] or None, "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                      "active": net._bool(r["active"], ctx, res), "_ctx": ctx})
    ordered = sorted(items, key=lambda x: (x["sortOrder"] or 0, x["tierId"]))
    if ordered and ordered[0]["minLifetimeEvidence"] not in (None, 0):
        res.errors.append(f"{ordered[0]['_ctx']}: the first tier must start at 0 lifetime Evidence")
    valued = [i for i in ordered if i["minLifetimeEvidence"] is not None]
    for a, b in zip(valued, valued[1:]):
        if not a["minLifetimeEvidence"] < b["minLifetimeEvidence"]:
            res.errors.append(f"{b['_ctx']}: min_lifetime_evidence must strictly increase "
                              f"({b['tierId']} is not above {a['tierId']})")
    authored = [i for i in ordered if i["authoredContent"]]
    if len(authored) > 1:
        res.errors.append("[mission_tiers] only one tier can be marked authored_content")
    elif authored and authored[0] is not ordered[-1]:
        res.errors.append(f"{authored[0]['_ctx']}: only the last tier can be authored_content (the final tier)")
    if ordered and not authored:
        res.warnings.append("[mission_tiers] no tier is marked authored_content; the final tier is authored end-game content")
    return [_strip(i) for i in ordered]


def _validate_formats(src, res):
    rows = net.read_table(src / FORMATS_FILE, FORMAT_COLUMNS, "map_formats", res) or []
    formats = {}
    for r in rows:
        ctx = f"[map_formats] Line {r['_line']}"
        fid = r["format_id"]
        if not fid or fid in formats:
            res.errors.append(f"{ctx}: blank or duplicate format_id '{fid}'")
            continue
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        role = r["role"].upper()
        if role not in FORMAT_ROLES:
            res.errors.append(f"{ctx}: role must be one of {', '.join(FORMAT_ROLES)}")
        formats[fid] = {"formatId": fid, "displayName": r["display_name"], "role": role,
                        "sourceReference": r["source_reference"] or None, "description": r["description"],
                        "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                        "active": net._bool(r["active"], ctx, res)}
    return formats


def _validate_maps(src, formats, res):
    rows = net.read_table(src / MAPS_FILE, MAP_COLUMNS, "maps", res) or []
    seen, items = set(), []
    for r in rows:
        ctx = f"[maps] Line {r['_line']}"
        mid = r["map_id"]
        if not mid or mid in seen:
            res.errors.append(f"{ctx}: blank or duplicate map_id '{mid}'")
            continue
        seen.add(mid)
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        fmt = formats.get(r["format_id"])
        has_objective = net._bool(r["has_objective"], ctx, res)
        deployable = net._bool(r["agent_deployable"], ctx, res)
        active = net._bool(r["active"], ctx, res)
        if fmt is None:
            res.errors.append(f"{ctx}: unknown format_id '{r['format_id']}'")
        else:
            if active and not fmt["active"]:
                res.errors.append(f"{ctx}: active map uses inactive format '{r['format_id']}'")
            if fmt["role"] == "MISSION":
                if not has_objective:
                    res.warnings.append(f"{ctx}: map '{mid}' has no objective yet, so its level cannot end")
            elif deployable:
                res.errors.append(f"{ctx}: a {fmt['role']} map cannot be agent_deployable")
        items.append({"mapId": mid, "formatId": r["format_id"], "displayName": r["display_name"],
                      "hasObjective": has_objective, "agentDeployable": deployable,
                      "sourceReference": r["source_reference"] or None, "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active})
    return sorted(items, key=lambda x: (x["sortOrder"] or 0, x["mapId"]))


def validate_territory(root, res):
    src = root / "data_authoring" / "source"
    formats = _validate_formats(src, res)
    return {"territories": _validate_territories(src, res), "settings": _validate_settings(src, res),
            "missionTiers": _validate_tiers(src, res),
            "mapFormats": sorted(formats.values(), key=lambda x: (x["sortOrder"] or 0, x["formatId"])),
            "maps": _validate_maps(src, formats, res)}


def export(root):
    res = net.Result()
    data = validate_territory(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "territory_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "doda.territory_catalog", "toolVersion": TOOL_VERSION,
               "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
               "decimalPlaces": MAX_DECIMAL_PLACES, "scale": SCALE, **data,
               "rules": RULES, "openItems": OPEN_ITEMS, "runtimeImplemented": False}
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv=None):
    p = argparse.ArgumentParser(description="DoDA territory foundations: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else net.find_project_root(Path(__file__).parent)
    out = None
    if a.command == "validate":
        res = net.Result()
        validate_territory(root, res)
    else:
        res, out = export(root)
    for w in res.warnings:
        print("WARNING:", w)
    for e in res.errors:
        print("ERROR:", e)
    print("Rows:", res.stats)
    if out:
        print("Exported:", out, "sha256", hashlib.sha256(out.read_bytes()).hexdigest())
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1


if __name__ == "__main__":
    sys.exit(main())
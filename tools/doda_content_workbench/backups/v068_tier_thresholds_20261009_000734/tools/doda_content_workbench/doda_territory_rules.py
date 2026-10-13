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
import doda_progression_identity_rules as progression_identity_rules
import doda_authored_mission_rules as authored_mission_rules

TOOL_VERSION = "0.1.0"
TERRITORIES_FILE = "territories.csv"
GREATER_TERRITORIES_FILE = "greater_territories.csv"
GREATER_TERRITORY_COLUMNS = ["greater_territory_id", "display_name", "source_reference", "description",
                             "sort_order", "active"]
TAGS_FILE = "greater_territory_tags.csv"
TAG_LINKS_FILE = "greater_territory_tag_links.csv"
TAG_COLUMNS = ["tag_id", "category", "display_name", "source_reference", "description",
               "sort_order", "active"]
TAG_LINK_COLUMNS = ["link_id", "greater_territory_id", "tag_id", "source_reference", "sort_order", "active"]
TAG_CATEGORIES = ("TERRAIN", "CLIMATE", "SETTLEMENT", "INSTITUTION", "THEME")
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
PERCENT_SETTINGS = {PERCENT_SETTING, "LEAD_COST_GROWTH_PERCENT"}
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

REQUIRED_SETTINGS = tuple(SETTING_UNITS)
PROGRESSION_SETTING_UNITS = {
    "LEAD_BASE_COST": "EVIDENCE_POINTS",
    "LEAD_COST_GROWTH_PERCENT": "PERCENT",
    "FINAL_GATE_CHECK_MINUTES": "STRATEGIC_MINUTES",
    "CAPSTONE_LEAD_COST": "EVIDENCE_POINTS",
    "FINAL_MIN_AVAILABLE_FUNDING": "FUNDING_UNITS",
    "FINAL_MIN_PREPAREDNESS": "METRIC_UNITS",
    "FINAL_MIN_OPERATIONAL_TERRITORIES": "COUNT",
}
SETTING_UNITS.update(PROGRESSION_SETTING_UNITS)

RULES["missionProgression"] = {
    "lowerTiersRemainAvailable": True,
    "ordinaryLeadPricing": {
        "model": "COMPOUND_PERCENT",
        "scope": "DEPARTMENT_WIDE",
        "counter": "SUCCESSFUL_ORDINARY_PAID_LEAD_PURCHASES",
        "formula": "ROUND_HALF_UP(BASE_COST * (1 + GROWTH_PERCENT / 100) ^ PRIOR_SUCCESSFUL_PURCHASES)",
        "rounding": "ROUND_HALF_UP_WHOLE_EVIDENCE_POINTS_PROPOSED",
        "excluded": ["FREE_TUTORIAL", "FAILED_PURCHASE", "REDEPLOYMENT"],
        "resetsOnTerritoryOrTierChange": False,
    },
    "finalGate": {
        "checksBeginAfterTier": "TIER_5",
        "evaluation": "PERIODIC",
        "requirementsCombine": "ALL",
        "readinessMetricId": "PREPAREDNESS",
        "fundingBasis": "CURRENT_AVAILABLE_DEPARTMENT_FUNDING",
        "requiredUpgradeReferencesSource": "missionProgression.finalGate.requiredUpgradeReferences",
        "requiredPlotMilestoneOrItemReferencesSource": "missionProgression.finalGate.requiredPlotMilestoneOrItemReferences",
        "capstoneMissionReferenceSource": "missionProgression.finalGate.capstoneMissionReference",
    },
    "capstone": {
        "tierId": "TIER_5",
        "priceModel": "SPECIAL_SEPARATE_PRICE",
        "offerRequiresAllFinalGateRequirements": True,
        "expires": False,
        "redeploymentRequiresRepurchase": False,
        "retainsMissionState": True,
        "completion": "AUTHORED_OBJECTIVES",
        "unlocksTierId": "TIER_6",
        "unlockIsPermanent": True,
        "advancesOrdinaryPurchaseCounter": False,
        "eligibilityRechecksAfterPurchase": False,
    },
}


def ordinary_lead_cost(base_cost, growth_percent_scaled, prior_purchases):
    values = (base_cost, growth_percent_scaled, prior_purchases)
    if any(value is None for value in values):
        return None
    if any(type(value) is not int for value in values):
        raise ValueError("Lead pricing inputs must be whole integers")
    full = 100 * SCALE
    if base_cost < 1 or not 0 < growth_percent_scaled <= full or prior_purchases < 0:
        raise ValueError("Base cost and growth must be positive, growth at most 100 percent, purchases nonnegative")
    numerator = base_cost * (full + growth_percent_scaled) ** prior_purchases
    denominator = full ** prior_purchases
    return (2 * numerator + denominator) // (2 * denominator)


def build_mission_progression(data):
    index = {row["settingId"]: row for row in data["settings"]}

    def usable(setting_id):
        row = index.get(setting_id)
        if row is None or not row["active"] or row["value"] is None:
            return None
        return row["valueScaled"] if row["unit"] == "PERCENT" else int(row["value"])

    missing_pricing = [
        sid for sid in ("LEAD_BASE_COST", "LEAD_COST_GROWTH_PERCENT")
        if usable(sid) is None
    ]
    gate_ids = [
        "FINAL_GATE_CHECK_MINUTES", "CAPSTONE_LEAD_COST",
        "FINAL_MIN_AVAILABLE_FUNDING", "FINAL_MIN_PREPAREDNESS",
        "FINAL_MIN_OPERATIONAL_TERRITORIES",
    ]
    missing_gate = [sid for sid in gate_ids if usable(sid) is None]
    tiers = {row["tierId"]: row for row in data["missionTiers"]}
    for tier_id in ("TIER_5", "TIER_6"):
        row = tiers.get(tier_id)
        if row is None or not row["active"] or row["minLifetimeEvidence"] is None:
            missing_gate.append(tier_id + "_ACTIVE_WITH_THRESHOLD")
    identities = data.get("progressionIdentities")
    if identities is None:
        reference_status = {
            "configured": False,
            "missingConfiguration": [
                "REQUIRED_UPGRADE_REFERENCES",
                "REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES",
            ],
        }
        requirements = []
    else:
        reference_status = identities["finalGateReferenceStatus"]
        requirements = [
            row for row in identities["missionTierRequirements"]
            if row["active"] and row["tierId"] == "TIER_6"
        ]
    missing_gate.extend(reference_status["missingConfiguration"])
    capstone_status = (data.get("authoredMissions") or {}).get("capstoneStatus")
    if capstone_status is None:
        missing_gate.append("CAPSTONE_MISSION_REFERENCE")
        capstone_chain = None
    else:
        missing_gate.extend(capstone_status["missingConfiguration"])
        capstone_chain = capstone_status["chainId"]
    upgrade_references = [
        row["referenceId"] for row in requirements
        if row["requirementType"] == "UPGRADE_ACQUIRED"
    ]
    plot_references = [
        {"requirementType": row["requirementType"], "referenceId": row["referenceId"]}
        for row in requirements
        if row["requirementType"] in ("MILESTONE_COMPLETED", "PLOT_ITEM_HELD")
    ]
    return {
        "contractVersion": "2026-10-08.4",
        "ordinaryPricing": {
            "baseCost": usable("LEAD_BASE_COST"),
            "growthPercentScaled": usable("LEAD_COST_GROWTH_PERCENT"),
            "scale": SCALE,
            "configured": not missing_pricing,
            "missingConfiguration": missing_pricing,
        },
        "finalGate": {
            "requiredUpgradeReferences": upgrade_references or None,
            "requiredPlotMilestoneOrItemReferences": plot_references or None,
            "requirements": requirements,
            "referenceConfigurationReady": reference_status["configured"],
            "capstoneMissionReference": capstone_chain,
            "capstoneStatus": capstone_status,
            "isCampaignEligibilityResult": False,
            "numericSettings": {sid: usable(sid) for sid in gate_ids},
            "configured": not missing_gate,
            "missingConfiguration": missing_gate,
        },
        "unconfiguredPolicy": "DO_NOT_PURCHASE_OR_AUTO_UNLOCK",
        "runtimeImplemented": False,
    }


OPEN_ITEMS = {
    "TERR-OPEN-01": "Six mission tiers settled; thresholds, concrete final-gate references and values remain open.",
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


def _validate_greater_territories(src, res):
    path = src / GREATER_TERRITORIES_FILE
    if not path.is_file():
        return [], None
    rows = net.read_table(path, GREATER_TERRITORY_COLUMNS, "greater_territories", res) or []
    seen, names, items = set(), set(), []
    for r in rows:
        ctx = f"[greater_territories] Line {r['_line']}"
        gid = r["greater_territory_id"]
        if not gid or gid in seen:
            res.errors.append(f"{ctx}: blank or duplicate greater_territory_id '{gid}'")
            continue
        seen.add(gid)
        name = r["display_name"]
        if not name:
            res.errors.append(f"{ctx}: display_name is required")
        elif name.casefold() in names:
            res.errors.append(f"{ctx}: duplicate display_name '{name}'")
        else:
            names.add(name.casefold())
        items.append({"greaterTerritoryId": gid, "displayName": name,
                      "sourceReference": r["source_reference"] or None, "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                      "active": net._bool(r["active"], ctx, res)})
    return sorted(items, key=lambda x: (x["sortOrder"] or 0, x["greaterTerritoryId"])), seen


def _validate_greater_territory_tags(src, res, greater_ids):
    import re as _re
    tags_path = src / TAGS_FILE
    links_path = src / TAG_LINKS_FILE
    if not tags_path.is_file():
        return None, []
    tag_rows = net.read_table(tags_path, TAG_COLUMNS, "greater_territory_tags", res) or []
    seen, names, tags = set(), set(), []
    for r in tag_rows:
        ctx = f"[greater_territory_tags] Line {r['_line']}"
        tid = r["tag_id"]
        if not tid or tid in seen:
            res.errors.append(f"{ctx}: blank or duplicate tag_id '{tid}'")
            continue
        seen.add(tid)
        if not _re.fullmatch(r"[a-z][a-z0-9_]*", tid):
            res.errors.append(f"{ctx}: tag_id must be lowercase letters, digits and underscores, starting with a letter")
        category = r["category"].upper()
        if category not in TAG_CATEGORIES:
            res.errors.append(f"{ctx}: category must be one of {', '.join(TAG_CATEGORIES)}")
        name = r["display_name"]
        if not name:
            res.errors.append(f"{ctx}: display_name is required")
        elif name.casefold() in names:
            res.errors.append(f"{ctx}: duplicate display_name '{name}'")
        else:
            names.add(name.casefold())
        tags.append({"tagId": tid, "category": category, "displayName": name,
                     "sourceReference": r["source_reference"] or None, "description": r["description"],
                     "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                     "active": net._bool(r["active"], ctx, res)})
    link_rows = (net.read_table(links_path, TAG_LINK_COLUMNS, "greater_territory_tag_links", res)
                 if links_path.is_file() else []) or []
    link_ids, pairs, links = set(), set(), []
    for r in link_rows:
        ctx = f"[greater_territory_tag_links] Line {r['_line']}"
        lid = r["link_id"]
        if not lid or lid in link_ids:
            res.errors.append(f"{ctx}: blank or duplicate link_id '{lid}'")
            continue
        link_ids.add(lid)
        gid, tid = r["greater_territory_id"], r["tag_id"]
        if greater_ids is not None and gid not in greater_ids:
            res.errors.append(f"{ctx}: greater_territory_id '{gid}' is not a known greater_territory_id")
        if tid not in seen:
            res.errors.append(f"{ctx}: tag_id '{tid}' is not a known tag_id")
        if (gid, tid) in pairs:
            res.errors.append(f"{ctx}: duplicate link for '{gid}' and '{tid}'")
        pairs.add((gid, tid))
        links.append({"linkId": lid, "greaterTerritoryId": gid, "tagId": tid,
                      "sourceReference": r["source_reference"] or None,
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                      "active": net._bool(r["active"], ctx, res)})
    if greater_ids is not None:
        linked = {link["greaterTerritoryId"] for link in links}
        for gid in sorted(greater_ids - linked):
            res.warnings.append(f"[greater_territory_tag_links] Greater Territory '{gid}' has no tags yet")
    tags.sort(key=lambda x: (x["sortOrder"] or 0, x["tagId"]))
    links.sort(key=lambda x: (x["sortOrder"] or 0, x["linkId"]))
    return tags, links


def _validate_territories(src, res, greater_ids=None):
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
        if r["hq_name"] and kind != "PLAYER_ONLY" and r["locality"] \
                and r["hq_name"] != f"{r['locality']} DoDA Office":
            res.warnings.append(f"{ctx}: hq_name '{r['hq_name']}' does not follow '<locality> DoDA Office'")
        if greater_ids is not None and r["region"] and r["region"] not in greater_ids:
            res.errors.append(f"{ctx}: region '{r['region']}' is not a known greater_territory_id")
        if greater_ids is not None and not r["region"]:
            res.warnings.append(f"{ctx}: territory '{tid}' has no Greater Territory yet")
        items.append({"territoryId": tid, "displayName": r["display_name"], "locality": r["locality"] or None,
                      "region": r["region"] or None, "greaterTerritoryId": r["region"] or None, "kind": kind, "unlockMethod": KIND_UNLOCK.get(kind),
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
            if sid in PERCENT_SETTINGS:
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
    for sid in REQUIRED_SETTINGS:
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
    greater_items, greater_ids = _validate_greater_territories(src, res)
    tag_items, tag_link_items = _validate_greater_territory_tags(src, res, greater_ids)
    data = {"territories": _validate_territories(src, res, greater_ids), "settings": _validate_settings(src, res),
            "missionTiers": _validate_tiers(src, res),
            "mapFormats": sorted(formats.values(), key=lambda x: (x["sortOrder"] or 0, x["formatId"])),
            "maps": _validate_maps(src, formats, res)}

    if greater_ids is not None:
        if tag_items is not None:
            by_greater = {}
            for link in tag_link_items:
                by_greater.setdefault(link["greaterTerritoryId"], []).append(link["tagId"])
            for item in greater_items:
                item["tags"] = sorted(by_greater.get(item["greaterTerritoryId"], []))
            data["greaterTerritoryTags"] = tag_items
            data["greaterTerritoryTagLinks"] = tag_link_items
        data["greaterTerritories"] = greater_items

    identity_files = (
        progression_identity_rules.UPGRADES_FILE,
        progression_identity_rules.MILESTONES_FILE,
        progression_identity_rules.ITEMS_FILE,
        progression_identity_rules.REQUIREMENTS_FILE,
    )
    identity_scope_present = (
        any((src / filename).is_file() for filename in identity_files)
        or (root / "tools" / "doda_content_workbench").is_dir()
    )
    if identity_scope_present:
        data["progressionIdentities"] = progression_identity_rules.validate_identities(root, res)
    authored_files = (authored_mission_rules.MISSIONS_FILE, authored_mission_rules.OBJECTIVES_FILE)
    if any((src / name).is_file() for name in authored_files):
        data["authoredMissions"] = authored_mission_rules.validate_authored_missions(root, res)
    if res.valid:
        data["missionProgression"] = build_mission_progression(data)
    return data


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
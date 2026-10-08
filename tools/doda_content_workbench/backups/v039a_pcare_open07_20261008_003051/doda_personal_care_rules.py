#!/usr/bin/env python3
r"""
DoDA Content Workbench - Personal-care actions (authoring slice).

Authored definitions only. When agents eat, rest, or go off duty is
simulation state owned by the native simulation.

Settled decisions encoded here (2026-10-07):
  * CARE-06: The care-services catalog holds medical and therapy services
    only, so personal care is its own catalog.
  * PCARE-01: Personal-care actions are Off Duty, Eating, Resting, and
    Decompression (v107 RemedyCat rows 11-14).
  * PCARE-02: Places where personal care can happen are personal-care location
    features (Food Access, Rest Facility, Safe Housing), following CARE-08.
    CAP_FOOD moves out of capabilities.csv with its ID unchanged. An action can
    happen at a place with ANY of its linked features.
  * PERS-18: An agent or analyst trained in a linked training can perform the
    action without being at a linked place.
  * PCARE-03: Place types are the kinds of real places (restaurant, agent home,
    hotel, car or van, ...). Each offers features. Food: restaurant, agent
    home, FBI safe house, office kitchen, cult mess hall, gas station. Rest is
    exclusively home (agent home, safe house), hotel, and car or van.
  * PCARE-04: A safe house serves as a home but belongs to no agent. Its
    occupancy depends on its beds. CAP_SAFE_HOUSING is deprecated in favour
    of the PLACE_SAFE_HOUSE place type.
  * PCARE-10: Energy is the inverse of Fatigue (energy = Fatigue maximum -
    Fatigue). An agent can start an activity only when energy is at or above
    the activity's energy_required_to_start.
  * PCARE-09: Agents and analysts have no tracked money. Personal care,
    food, and recreation are free: the player pays nothing and the agent
    pays nothing. (Salaried payroll on hire is separate. Medical and therapy
    costs in CARE-07 are unaffected.)
  * PCARE-05: Rest happens at a hospital only while an agent is in recovery
    from illness or injury; agents are also fed there during recovery. Which
    personal-care actions a care service provides is authored in
    personal_care_during_care.csv (REMED_RECOVERY -> Resting, Eating).
  * PCARE-06: Recreation (workbook FUN_CAPABLE) is a feature of recreation
    place types. Recreation places are randomized throughout operational
    territory; agents may travel to other territories or outside territory
    to reach one (territory authoring, deferred).
  * PCARE-07: Each recreation place type has a list of activities. Each
    activity has a place (dropdown), description, one duration, company
    options (alone, friends, strangers), a stress reduction per tick, and an
    fatigue cost per tick (energy used), energy required to start, and a
    hunger reduction per tick
    (some activities involve eating). Duration is the activity's time cost.
    Variants with different durations are separate
    activities (e.g. camp overnight / three days / one week).

Source files:
  data_authoring/source/personal_care_actions.csv
  data_authoring/source/personal_care_features.csv
  data_authoring/source/personal_care_locations.csv  (action -> feature)
  data_authoring/source/personal_care_trainings.csv  (action -> training)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import doda_network_rules as net
import doda_agent_attribute_rules as attribute_rules

TOOL_VERSION = "0.5.0"

ACTIONS_FILE = "personal_care_actions.csv"
FEATURES_FILE = "personal_care_features.csv"
LOCATIONS_FILE = "personal_care_locations.csv"
TRAININGS_FILE = "personal_care_trainings.csv"
PLACE_TYPES_FILE = "personal_care_place_types.csv"
PLACE_TYPE_FEATURES_FILE = "personal_care_place_type_features.csv"
ACTIVITIES_FILE = "recreation_activities.csv"
DURING_CARE_FILE = "personal_care_during_care.csv"

ACTION_COLUMNS = ["action_id", "display_name", "initiation", "off_duty_required",
                  "follow_up_action_id", "workbook_status", "source_reference", "description",
                  "sort_order", "active"]
FEATURE_COLUMNS = ["feature_id", "display_name", "description", "source_reference", "sort_order", "active"]
LOCATION_COLUMNS = ["action_id", "feature_id", "sort_order", "active"]
TRAINING_LINK_COLUMNS = ["action_id", "training_id", "sort_order", "active"]

PLACE_TYPE_COLUMNS = ["place_type_id", "display_name", "serves_as_home", "agent_owned", "occupancy_rule",
                      "source_reference", "description", "sort_order", "active"]
PLACE_TYPE_FEATURE_COLUMNS = ["place_type_id", "feature_id", "sort_order", "active"]
ACTIVITY_COLUMNS = ["activity_id", "place_type_id", "display_name", "description", "duration_minutes",
                    "duration_label", "company_options", "stress_reduction_per_tick", "fatigue_cost_per_tick",
                    "energy_required_to_start", "hunger_reduction_per_tick",
                    "source_reference", "sort_order", "active"]
DURING_CARE_COLUMNS = ["care_service_id", "action_id", "sort_order", "active"]

INITIATIONS = ("AGENT_INITIATED", "PLAYER_SCHEDULED")
OCCUPANCY_RULES = ("UNSPECIFIED", "BEDS")
COMPANY_OPTIONS = ("ALONE", "FRIENDS", "STRANGERS")
REST_FEATURE = "CAP_REST"
RECREATION_FEATURE = "CAP_RECREATION"
FATIGUE_STAT = "FATIGUE"

OPEN_ITEMS = {
    "PCARE-OPEN-01": "Durations, effects (fatigue, nutrition, stress recovery), and cost amounts.",
    "PCARE-OPEN-02": "Activities for the other recreation places; durations for Overnight, All day, and bowling; stress, fatigue, and hunger rates.",
    "PCARE-OPEN-07": "Tick length and how per-tick rates apply (with PERS-11 HP drain).",
    "PCARE-OPEN-03": "Whether Emergency Hospitalization also counts as recovery rest (PCARE-05).",
    "PCARE-OPEN-06": "Actual places, safe-house bed counts, and recreation placement and travel (territory authoring).",
    "PCARE-OPEN-04": "Accommodations (personal residence, rental, hotel, vehicle), location conditions (safe, hostile), undercover routes, and compliance rules.",
    "PCARE-OPEN-05": "CAP_REST and CAP_SAFE_HOUSING access booleans (workbook row shift).",
}


def _read_ids(path: Path, column: str | None = None) -> set[str]:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8-sig", newline="") as f:
        if column:
            return {(r.get(column) or "").strip() for r in csv.DictReader(f)}
        return {(r.get("capability_id") or r.get("feature_id") or "").strip() for r in csv.DictReader(f)}


def _validate_actions(src: Path, res: net.Result) -> dict[str, dict[str, Any]]:
    rows = net.read_table(src / ACTIONS_FILE, ACTION_COLUMNS, "personal_care_actions", res) or []
    actions: dict[str, dict[str, Any]] = {}
    for r in rows:
        ctx = f"[personal_care_actions] Line {r['_line']}"
        aid = r["action_id"]
        if not aid or aid in actions:
            res.errors.append(f"{ctx}: blank or duplicate action_id '{aid}'")
            continue
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        initiation = r["initiation"].upper()
        if initiation not in INITIATIONS:
            res.errors.append(f"{ctx}: initiation must be one of {', '.join(INITIATIONS)}")
        actions[aid] = {"actionId": aid, "displayName": r["display_name"], "initiation": initiation,
                        "offDutyRequired": net._bool(r["off_duty_required"], ctx, res),
                        "followUpActionId": r["follow_up_action_id"] or None,
                        "workbookStatus": r["workbook_status"] or None,
                        "sourceReference": r["source_reference"] or None, "description": r["description"],
                        "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                        "active": net._bool(r["active"], ctx, res), "_ctx": ctx}
    for a in actions.values():
        fu = a["followUpActionId"]
        if not fu:
            continue
        target = actions.get(fu)
        if target is None:
            res.errors.append(f"{a['_ctx']}: unknown follow_up_action_id '{fu}'")
        elif fu == a["actionId"]:
            res.errors.append(f"{a['_ctx']}: an action cannot follow itself")
        elif a["active"] and not target["active"]:
            res.errors.append(f"{a['_ctx']}: active action follows up with inactive '{fu}'")
    return actions


def _validate_features(src: Path, res: net.Result) -> dict[str, dict[str, Any]]:
    rows = net.read_table(src / FEATURES_FILE, FEATURE_COLUMNS, "personal_care_features", res) or []
    taken = {"capabilities.csv": _read_ids(src / "capabilities.csv"),
             "care_location_features.csv": _read_ids(src / "care_location_features.csv")}
    features: dict[str, dict[str, Any]] = {}
    for r in rows:
        ctx = f"[personal_care_features] Line {r['_line']}"
        fid = r["feature_id"]
        if not fid or fid in features:
            res.errors.append(f"{ctx}: blank or duplicate feature_id '{fid}'")
            continue
        for name, ids in taken.items():
            if fid in ids:
                res.errors.append(f"{ctx}: feature_id '{fid}' is also defined in {name}")
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        features[fid] = {"featureId": fid, "displayName": r["display_name"], "description": r["description"],
                         "sourceReference": r["source_reference"] or None,
                         "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                         "active": net._bool(r["active"], ctx, res), "_ctx": ctx}
    return features


def _validate_links(src: Path, filename: str, table: str, columns: list[str], target_col: str,
                    target_label: str, actions: dict[str, dict[str, Any]], targets: dict[str, bool],
                    res: net.Result) -> list[dict[str, Any]]:
    rows = net.read_table(src / filename, columns, table, res) or []
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for r in rows:
        ctx = f"[{table}] Line {r['_line']}"
        aid, tid = r["action_id"], r[target_col]
        if (aid, tid) in seen:
            res.errors.append(f"{ctx}: duplicate link {aid} -> {tid}")
            continue
        seen.add((aid, tid))
        active = net._bool(r["active"], ctx, res)
        action = actions.get(aid)
        if action is None:
            res.errors.append(f"{ctx}: unknown action_id '{aid}'")
        if tid not in targets:
            res.errors.append(f"{ctx}: unknown {target_col} '{tid}'")
        if active and action is not None and not action["active"]:
            res.errors.append(f"{ctx}: active link uses inactive action '{aid}'")
        if active and tid in targets and not targets[tid]:
            res.errors.append(f"{ctx}: active link uses inactive {target_label} '{tid}'")
        out.append({"actionId": aid, "featureId" if target_col == "feature_id" else "trainingId": tid,
                    "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active})
    return sorted(out, key=lambda x: (x["sortOrder"] or 0, x["actionId"]))


def _number(value: str, ctx: str, field: str, res: net.Result) -> float | None:
    if not value:
        return None
    try:
        n = float(value)
    except ValueError:
        res.errors.append(f"{ctx}: {field} must be a number")
        return None
    if n != n or n in (float("inf"), float("-inf")):
        res.errors.append(f"{ctx}: {field} must be a finite number")
        return None
    return int(n) if n.is_integer() else n


def _validate_during_care(src: Path, actions: dict[str, dict[str, Any]], res: net.Result
                          ) -> list[dict[str, Any]]:
    rows = net.read_table(src / DURING_CARE_FILE, DURING_CARE_COLUMNS, "personal_care_during_care", res) or []
    care_file = src / "care_services.csv"
    care_ids = _read_ids(care_file, "care_service_id")
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for r in rows:
        ctx = f"[personal_care_during_care] Line {r['_line']}"
        cid, aid = r["care_service_id"], r["action_id"]
        if (cid, aid) in seen:
            res.errors.append(f"{ctx}: duplicate link {cid} -> {aid}")
            continue
        seen.add((cid, aid))
        active = net._bool(r["active"], ctx, res)
        if care_file.exists() and cid not in care_ids:
            res.errors.append(f"{ctx}: unknown care_service_id '{cid}'")
        if aid not in actions:
            res.errors.append(f"{ctx}: unknown action_id '{aid}'")
        elif active and not actions[aid]["active"]:
            res.errors.append(f"{ctx}: active link uses inactive action '{aid}'")
        out.append({"careServiceId": cid, "actionId": aid,
                    "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active})
    return sorted(out, key=lambda x: (x["sortOrder"] or 0, x["careServiceId"]))


def _fatigue_max(src: Path) -> int:
    path = src / "condition_stats.csv"
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("stat_id") or "").strip() == FATIGUE_STAT:
                    try:
                        return int(r.get("maximum_value") or 100)
                    except ValueError:
                        break
    return 100


def _split(value: str) -> list[str]:
    return [x.strip() for x in value.split(";") if x.strip()]


def _validate_place_types(src: Path, features: dict[str, dict[str, Any]], res: net.Result
                          ) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    rows = net.read_table(src / PLACE_TYPES_FILE, PLACE_TYPE_COLUMNS, "personal_care_place_types", res) or []
    types: dict[str, dict[str, Any]] = {}
    for r in rows:
        ctx = f"[personal_care_place_types] Line {r['_line']}"
        pid = r["place_type_id"]
        if not pid or pid in types:
            res.errors.append(f"{ctx}: blank or duplicate place_type_id '{pid}'")
            continue
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        home = net._bool(r["serves_as_home"], ctx, res)
        owned = net._bool(r["agent_owned"], ctx, res)
        if owned and not home:
            res.errors.append(f"{ctx}: only a home can be agent-owned")
        occ = r["occupancy_rule"].upper()
        if occ not in OCCUPANCY_RULES:
            res.errors.append(f"{ctx}: occupancy_rule must be one of {', '.join(OCCUPANCY_RULES)}")
        types[pid] = {"placeTypeId": pid, "displayName": r["display_name"], "servesAsHome": home,
                      "agentOwned": owned, "occupancyRule": occ,
                      "sourceReference": r["source_reference"] or None, "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                      "active": net._bool(r["active"], ctx, res), "_ctx": ctx}
    rows = net.read_table(src / PLACE_TYPE_FEATURES_FILE, PLACE_TYPE_FEATURE_COLUMNS,
                          "personal_care_place_type_features", res) or []
    seen: set[tuple[str, str]] = set()
    links: list[dict[str, Any]] = []
    for r in rows:
        ctx = f"[personal_care_place_type_features] Line {r['_line']}"
        pid, fid = r["place_type_id"], r["feature_id"]
        if (pid, fid) in seen:
            res.errors.append(f"{ctx}: duplicate link {pid} -> {fid}")
            continue
        seen.add((pid, fid))
        active = net._bool(r["active"], ctx, res)
        if pid not in types:
            res.errors.append(f"{ctx}: unknown place_type_id '{pid}'")
        if fid not in features:
            res.errors.append(f"{ctx}: unknown feature_id '{fid}'")
        if active and pid in types and not types[pid]["active"]:
            res.errors.append(f"{ctx}: active link uses inactive place type '{pid}'")
        if active and fid in features and not features[fid]["active"]:
            res.errors.append(f"{ctx}: active link uses inactive feature '{fid}'")
        links.append({"placeTypeId": pid, "featureId": fid,
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active})
    for t in types.values():
        if t["servesAsHome"] and not any(l["placeTypeId"] == t["placeTypeId"] and l["featureId"] == REST_FEATURE
                                         for l in links):
            res.warnings.append(f"{t['_ctx']}: home place type '{t['placeTypeId']}' does not offer {REST_FEATURE}")
    return types, sorted(links, key=lambda x: (x["sortOrder"] or 0, x["placeTypeId"]))


def _validate_activities(src: Path, types: dict[str, dict[str, Any]], type_links: list[dict[str, Any]],
                         res: net.Result) -> list[dict[str, Any]]:
    rows = net.read_table(src / ACTIVITIES_FILE, ACTIVITY_COLUMNS, "recreation_activities", res) or []
    recreational = {l["placeTypeId"] for l in type_links if l["featureId"] == RECREATION_FEATURE}
    fatigue_max = _fatigue_max(src)
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        ctx = f"[recreation_activities] Line {r['_line']}"
        aid, pid = r["activity_id"], r["place_type_id"]
        if not aid or aid in out:
            res.errors.append(f"{ctx}: blank or duplicate activity_id '{aid}'")
            continue
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        active = net._bool(r["active"], ctx, res)
        if pid not in types:
            res.errors.append(f"{ctx}: unknown place_type_id '{pid}'")
        elif pid not in recreational:
            res.errors.append(f"{ctx}: place type '{pid}' does not offer {RECREATION_FEATURE}")
        elif active and not types[pid]["active"]:
            res.errors.append(f"{ctx}: active activity uses inactive place type '{pid}'")
        minutes = net._int(r["duration_minutes"], ctx, "duration_minutes", res) if r["duration_minutes"] else None
        if minutes is not None and minutes <= 0:
            res.errors.append(f"{ctx}: duration_minutes must be above 0")
        if active and minutes is None:
            res.errors.append(f"{ctx}: an active activity needs duration_minutes")
        rates = {}
        for field in ("stress_reduction_per_tick", "fatigue_cost_per_tick", "hunger_reduction_per_tick"):
            rates[field] = _number(r[field], ctx, field, res)
        energy = _number(r["energy_required_to_start"], ctx, "energy_required_to_start", res)
        if energy is not None and not 0 <= energy <= fatigue_max:
            res.errors.append(f"{ctx}: energy_required_to_start must be 0 to {fatigue_max} (the Fatigue range)")
        company = [c.upper() for c in _split(r["company_options"])]
        bad = [c for c in company if c not in COMPANY_OPTIONS]
        if bad:
            res.errors.append(f"{ctx}: company_options must be from {', '.join(COMPANY_OPTIONS)} (got {', '.join(bad)})")
        if len(set(company)) != len(company):
            res.errors.append(f"{ctx}: company_options has repeats")
        out[aid] = {"activityId": aid, "placeTypeId": pid, "displayName": r["display_name"],
                    "description": r["description"], "durationMinutes": minutes,
                    "durationLabel": r["duration_label"] or None, "companyOptions": company,
                    "stressReductionPerTick": rates["stress_reduction_per_tick"],
                    "fatigueCostPerTick": rates["fatigue_cost_per_tick"],
                    "energyRequiredToStart": energy,
                    "hungerReductionPerTick": rates["hunger_reduction_per_tick"],
                    "sourceReference": r["source_reference"] or None,
                    "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active}
    return sorted(out.values(), key=lambda x: (x["sortOrder"] or 0, x["activityId"]))


def validate_personal_care(root: Path, res: net.Result) -> dict[str, Any]:
    src = root / "data_authoring" / "source"
    actions = _validate_actions(src, res)
    features = _validate_features(src, res)
    scratch = net.Result()
    trainings = {t["id"]: bool(t["active"]) for t in attribute_rules.validate_attributes(root, scratch)["training"]}
    locations = _validate_links(src, LOCATIONS_FILE, "personal_care_locations", LOCATION_COLUMNS, "feature_id",
                                "location feature", actions,
                                {k: bool(v["active"]) for k, v in features.items()}, res)
    training_links = _validate_links(src, TRAININGS_FILE, "personal_care_trainings", TRAINING_LINK_COLUMNS,
                                     "training_id", "training", actions, trainings, res)
    for a in actions.values():
        if a["active"] and not any(l["actionId"] == a["actionId"] and l["active"]
                                   for l in locations + training_links):
            res.warnings.append(f"{a['_ctx']}: active action '{a['actionId']}' has no active place or training")
    for f in features.values():
        if f["active"] and not any(l["featureId"] == f["featureId"] and l["active"] for l in locations):
            res.warnings.append(f"{f['_ctx']}: active feature '{f['featureId']}' hosts no active actions")
    place_types, type_links = _validate_place_types(src, features, res)
    activities = _validate_activities(src, place_types, type_links, res)
    during_care = _validate_during_care(src, actions, res)
    strip = lambda d: [{k: v for k, v in x.items() if k != "_ctx"} for x in d.values()]
    return {"placeTypes": sorted(strip(place_types), key=lambda x: (x["sortOrder"] or 0, x["placeTypeId"])),
            "placeTypeFeatures": type_links, "recreationActivities": activities,
            "duringCare": during_care,"actions": sorted(strip(actions), key=lambda x: (x["sortOrder"] or 0, x["actionId"])),
            "features": sorted(strip(features), key=lambda x: (x["sortOrder"] or 0, x["featureId"])),
            "actionLocations": locations, "actionTrainings": training_links}


def export(root: Path) -> tuple[net.Result, Path | None]:
    res = net.Result()
    data = validate_personal_care(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "personal_care_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "doda.personal_care_catalog", "toolVersion": TOOL_VERSION,
               "generatedAtUtc": datetime.now(timezone.utc).isoformat(), **data,
               "placeRule": {"locationMatch": "ANY_LINKED_FEATURE",
                             "trainingBypassesLocation": True,
                             "placeTypesOfferFeatures": True,
                             "duringCare": "CARE_SERVICE_PROVIDES_LINKED_ACTIONS",
                             "cost": "FREE_NO_AGENT_FINANCES",
                             "energy": {"definition": "FATIGUE_MAX_MINUS_FATIGUE", "fatigueStatId": FATIGUE_STAT,
                                        "startRule": "ENERGY_AT_OR_ABOVE_REQUIRED"},
                             "safeHouseOccupancy": "BEDS",
                             "recreationPlacement": "RANDOMIZED_IN_TERRITORY_TRAVEL_MAY_BE_REQUIRED"},
               "openItems": OPEN_ITEMS, "runtimeImplemented": False}
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="DoDA personal-care actions: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else net.find_project_root(Path(__file__).parent)
    if a.command == "validate":
        res = net.Result(); validate_personal_care(root, res); out = None
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

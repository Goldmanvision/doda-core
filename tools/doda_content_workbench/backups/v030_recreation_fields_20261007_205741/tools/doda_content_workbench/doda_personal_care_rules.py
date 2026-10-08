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
  * PCARE-05: Rest happens at a hospital only while an agent is in recovery
    from illness or injury (care service REMED_RECOVERY).
  * PCARE-06: Recreation (workbook FUN_CAPABLE) is a feature of recreation
    place types. Recreation places are randomized throughout operational
    territory; agents may travel to other territories or outside territory
    to reach one (territory authoring, deferred).
  * PCARE-07: Each recreation place type has a list of activities, each with
    company options (alone, friends, strangers) and duration options.

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

TOOL_VERSION = "0.2.0"

ACTIONS_FILE = "personal_care_actions.csv"
FEATURES_FILE = "personal_care_features.csv"
LOCATIONS_FILE = "personal_care_locations.csv"
TRAININGS_FILE = "personal_care_trainings.csv"
PLACE_TYPES_FILE = "personal_care_place_types.csv"
PLACE_TYPE_FEATURES_FILE = "personal_care_place_type_features.csv"
ACTIVITIES_FILE = "recreation_activities.csv"

ACTION_COLUMNS = ["action_id", "display_name", "initiation", "off_duty_required", "cost_policy_reference",
                  "follow_up_action_id", "workbook_status", "source_reference", "description",
                  "sort_order", "active"]
FEATURE_COLUMNS = ["feature_id", "display_name", "description", "source_reference", "sort_order", "active"]
LOCATION_COLUMNS = ["action_id", "feature_id", "sort_order", "active"]
TRAINING_LINK_COLUMNS = ["action_id", "training_id", "sort_order", "active"]

PLACE_TYPE_COLUMNS = ["place_type_id", "display_name", "serves_as_home", "agent_owned", "occupancy_rule",
                      "source_reference", "description", "sort_order", "active"]
PLACE_TYPE_FEATURE_COLUMNS = ["place_type_id", "feature_id", "sort_order", "active"]
ACTIVITY_COLUMNS = ["activity_id", "place_type_id", "display_name", "company_options", "duration_options",
                    "source_reference", "description", "sort_order", "active"]

INITIATIONS = ("AGENT_INITIATED", "PLAYER_SCHEDULED")
OCCUPANCY_RULES = ("UNSPECIFIED", "BEDS")
COMPANY_OPTIONS = ("ALONE", "FRIENDS", "STRANGERS")
REST_FEATURE = "CAP_REST"
RECREATION_FEATURE = "CAP_RECREATION"
HOSPITAL_REST = {"actionId": "REMED_RESTING", "duringCareServiceIds": ["REMED_RECOVERY"]}

OPEN_ITEMS = {
    "PCARE-OPEN-01": "Durations, effects (fatigue, nutrition, stress recovery), and cost amounts.",
    "PCARE-OPEN-02": "Activities for recreation places without examples yet, and activity durations in minutes.",
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
                        "costPolicyReference": r["cost_policy_reference"] or None,
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
        company = [c.upper() for c in _split(r["company_options"])]
        bad = [c for c in company if c not in COMPANY_OPTIONS]
        if bad:
            res.errors.append(f"{ctx}: company_options must be from {', '.join(COMPANY_OPTIONS)} (got {', '.join(bad)})")
        if len(set(company)) != len(company):
            res.errors.append(f"{ctx}: company_options has repeats")
        durations = _split(r["duration_options"])
        if len(set(d.lower() for d in durations)) != len(durations):
            res.errors.append(f"{ctx}: duration_options has repeats")
        out[aid] = {"activityId": aid, "placeTypeId": pid, "displayName": r["display_name"],
                    "companyOptions": company, "durationOptions": durations,
                    "sourceReference": r["source_reference"] or None, "description": r["description"],
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
    if actions or place_types:
        care_ids = _read_ids(src / "care_services.csv", "care_service_id")
        care_present = (src / "care_services.csv").exists()
        if HOSPITAL_REST["actionId"] not in actions:
            res.errors.append(f"[personal_care_actions] hospital rest action '{HOSPITAL_REST['actionId']}' is missing (PCARE-05)")
        for cid in HOSPITAL_REST["duringCareServiceIds"]:
            if care_present and cid not in care_ids:
                res.errors.append(f"[care_services] hospital rest care service '{cid}' is missing (PCARE-05)")
    strip = lambda d: [{k: v for k, v in x.items() if k != "_ctx"} for x in d.values()]
    return {"placeTypes": sorted(strip(place_types), key=lambda x: (x["sortOrder"] or 0, x["placeTypeId"])),
            "placeTypeFeatures": type_links, "recreationActivities": activities,"actions": sorted(strip(actions), key=lambda x: (x["sortOrder"] or 0, x["actionId"])),
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
                             "hospitalRest": HOSPITAL_REST,
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

"""Authored missions: plot missions and the Tier 5 capstone chain.
Authoring/export only. Campaign progress and completion are native state."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import doda_network_rules as net

TOOL_VERSION = "0.1.0"
MISSIONS_FILE = "authored_missions.csv"
OBJECTIVES_FILE = "authored_mission_objectives.csv"
MISSION_COLUMNS = [
    "mission_id", "display_name", "kind", "chain_id", "chain_position", "tier_id",
    "unlocks_tier_id", "territory_id", "map_id", "player_only", "source_reference",
    "description", "sort_order", "active",
]
OBJECTIVE_COLUMNS = [
    "objective_id", "mission_id", "display_name", "required", "source_reference",
    "description", "sort_order", "active",
]
KINDS = ("PLOT_MISSION", "TIER_CAPSTONE")
RULES = {
    "sharedTableForPlotMissionsAndCapstone": True,
    "plotMissionsPlayerOnly": True,
    "capstoneIsMissionChain": True,
    "chainPositionsContiguousFromOne": True,
    "capstoneRequiresRequiredObjectivePerMission": True,
    "tier6UnlockTrigger": "UNDECIDED",
    "oneLeadPurchaseUnlocksWholeChain": "UNDECIDED_LEANING_NO_LEADS_STILL_OPEN_MISSION_AREAS",
    "campaignProgressIsNativeState": True,
}
OPEN_ITEMS = {
    "CAP-OPEN-01": "Legal review of using the real Savannah River Site name before release; fallback is an evocative fictional name.",
    "CAP-OPEN-02": "Capstone territory HQ name and the qualification agents need to deploy there.",
    "CAP-OPEN-03": "Chain mission names, maps and authored objectives.",
    "CAP-OPEN-04": "Tier 6 unlock trigger (undecided) and whether one capstone Lead opens the whole chain (leaning no: Leads still open mission areas).",
}


def _lookup(src, filename, columns, key, label, res):
    path = src / filename
    if not path.is_file():
        return {}
    scratch = net.Result()
    rows = net.read_table(path, columns, label, scratch) or []
    res.errors.extend(scratch.errors)
    return {row[key]: row for row in rows if row[key]}


def _flag(row, field="active"):
    return row.get(field, "").strip().lower() in ("true", "1", "yes")


def _order(row):
    try:
        return int(row["sort_order"])
    except (KeyError, ValueError):
        return 0


def _capstone_status(missions, objectives):
    caps = [m for m in missions if m["kind"] == "TIER_CAPSTONE"]
    if not caps:
        return {"chainId": None, "missionIds": [], "unlocksTierId": None,
                "configured": False, "missingConfiguration": ["CAPSTONE_MISSION_REFERENCE"]}
    caps.sort(key=lambda m: (m["chainPosition"] or 0, m["missionId"]))
    missing = []
    if any(not m["active"] for m in caps):
        missing.append("CAPSTONE_MISSIONS_INACTIVE")
    if any(not m["mapId"] for m in caps):
        missing.append("CAPSTONE_MAPS")
    if any(not m["territoryId"] for m in caps):
        missing.append("CAPSTONE_TERRITORY")
    covered = {o["missionId"] for o in objectives if o["required"] and o["active"]}
    if any(m["missionId"] not in covered for m in caps):
        missing.append("CAPSTONE_REQUIRED_OBJECTIVES")
    return {"chainId": caps[0]["chainId"], "missionIds": [m["missionId"] for m in caps],
            "unlocksTierId": caps[-1]["unlocksTierId"],
            "configured": not missing, "missingConfiguration": missing}


def validate_authored_missions(root, res):
    src = root / "data_authoring/source"
    tiers = _lookup(src, "mission_tiers.csv", ["tier_id", "active", "sort_order"],
                    "tier_id", "mission_tiers", res)
    territories = _lookup(src, "territories.csv", ["territory_id", "active"],
                          "territory_id", "territories", res)
    maps = _lookup(src, "maps.csv", ["map_id", "active"], "map_id", "maps", res)
    missions, ids = [], set()
    for path, label in ((src / MISSIONS_FILE, "authored_missions"),
                        (src / OBJECTIVES_FILE, "authored_mission_objectives")):
        if not path.is_file():
            res.errors.append(f"[{label}] Required source file missing: {path.name}")
    mission_rows = (net.read_table(src / MISSIONS_FILE, MISSION_COLUMNS, "authored_missions", res)
                    if (src / MISSIONS_FILE).is_file() else []) or []
    objective_rows = (net.read_table(src / OBJECTIVES_FILE, OBJECTIVE_COLUMNS,
                                     "authored_mission_objectives", res)
                      if (src / OBJECTIVES_FILE).is_file() else []) or []

    for row in mission_rows:
        ctx = f"[authored_missions] Line {row['_line']}"
        mid = row["mission_id"]
        if not mid or mid in ids:
            res.errors.append(f"{ctx}: blank or duplicate mission_id '{mid}'")
            continue
        ids.add(mid)
        if not row["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        kind = row["kind"].upper()
        if kind not in KINDS:
            res.errors.append(f"{ctx}: kind must be one of {', '.join(KINDS)}")
        if not row["chain_id"]:
            res.errors.append(f"{ctx}: chain_id is required")
        position = net._int(row["chain_position"], ctx, "chain_position", res)
        if position is not None and position < 1:
            res.errors.append(f"{ctx}: chain_position must be at least 1")
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(f"{ctx}: sort_order must be nonnegative")
        active = net._bool(row["active"], ctx, res)
        player_only = net._bool(row["player_only"], ctx, res)
        if kind == "PLOT_MISSION" and not player_only:
            res.errors.append(f"{ctx}: plot missions must be player_only")
        tier, unlocks = row["tier_id"], row["unlocks_tier_id"]
        if kind == "TIER_CAPSTONE" and not tier:
            res.errors.append(f"{ctx}: a capstone mission needs tier_id")
        if tier:
            if tier not in tiers:
                res.errors.append(f"{ctx}: unknown tier_id '{tier}'")
            elif active and not _flag(tiers[tier]):
                res.errors.append(f"{ctx}: active mission uses inactive tier '{tier}'")
        if unlocks:
            if kind != "TIER_CAPSTONE":
                res.errors.append(f"{ctx}: only a capstone mission can unlock a tier")
            elif unlocks not in tiers:
                res.errors.append(f"{ctx}: unknown unlocks_tier_id '{unlocks}'")
            elif tier in tiers and _order(tiers[unlocks]) <= _order(tiers[tier]):
                res.errors.append(f"{ctx}: unlocks_tier_id must come after tier_id")
        for field, index, label in (("territory_id", territories, "territory"),
                                    ("map_id", maps, "map")):
            value = row[field]
            if not value:
                continue
            if value not in index:
                res.errors.append(f"{ctx}: unknown {field} '{value}'")
            elif active and not _flag(index[value]):
                res.errors.append(f"{ctx}: active mission uses inactive {label} '{value}'")
        if kind == "TIER_CAPSTONE" and not row["map_id"]:
            res.warnings.append(f"{ctx}: capstone mission '{mid}' has no map yet")
        missions.append({
            "missionId": mid, "displayName": row["display_name"], "kind": kind,
            "chainId": row["chain_id"], "chainPosition": position,
            "tierId": tier or None, "unlocksTierId": unlocks or None,
            "territoryId": row["territory_id"] or None, "mapId": row["map_id"] or None,
            "playerOnly": player_only, "sourceReference": row["source_reference"] or None,
            "description": row["description"], "sortOrder": order, "active": active,
        })

    chains = {}
    for mission in missions:
        chains.setdefault(mission["chainId"], []).append(mission)
    capstone_chains = [cid for cid, items in chains.items()
                       if any(m["kind"] == "TIER_CAPSTONE" for m in items)]
    if len(capstone_chains) > 1:
        res.errors.append("[authored_missions] only one capstone chain is allowed")
    for chain_id, items in chains.items():
        label = f"[authored_missions] Chain '{chain_id}'"
        if len({m["kind"] for m in items}) > 1:
            res.errors.append(f"{label}: missions in one chain must share a kind")
        positions = sorted(m["chainPosition"] for m in items if m["chainPosition"])
        if len(positions) != len(set(positions)):
            res.errors.append(f"{label}: duplicate chain_position")
        elif positions != list(range(1, len(positions) + 1)):
            res.errors.append(f"{label}: chain positions must be contiguous from 1")
        if any(m["kind"] == "TIER_CAPSTONE" for m in items):
            if len({m["tierId"] for m in items}) > 1:
                res.errors.append(f"{label}: capstone missions must share one tier_id")
            final = max((m["chainPosition"] or 0) for m in items)
            with_unlock = [m for m in items if m["unlocksTierId"]]
            if len(with_unlock) != 1 or with_unlock[0]["chainPosition"] != final:
                res.errors.append(f"{label}: exactly the final mission must set unlocks_tier_id")

    mission_index = {m["missionId"]: m for m in missions}
    objectives, objective_ids = [], set()
    for row in objective_rows:
        ctx = f"[authored_mission_objectives] Line {row['_line']}"
        oid = row["objective_id"]
        if not oid or oid in objective_ids:
            res.errors.append(f"{ctx}: blank or duplicate objective_id '{oid}'")
            continue
        objective_ids.add(oid)
        if not row["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        active = net._bool(row["active"], ctx, res)
        required = net._bool(row["required"], ctx, res)
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(f"{ctx}: sort_order must be nonnegative")
        parent = mission_index.get(row["mission_id"])
        if parent is None:
            res.errors.append(f"{ctx}: unknown mission_id '{row['mission_id']}'")
        elif active and not parent["active"]:
            res.errors.append(f"{ctx}: active objective belongs to inactive mission")
        objectives.append({
            "objectiveId": oid, "missionId": row["mission_id"],
            "displayName": row["display_name"], "required": required,
            "sourceReference": row["source_reference"] or None,
            "description": row["description"], "sortOrder": order, "active": active,
        })
    return {
        "missions": sorted(missions, key=lambda m: (m["chainId"], m["chainPosition"] or 0, m["missionId"])),
        "objectives": sorted(objectives, key=lambda o: (o["missionId"], o["sortOrder"] or 0, o["objectiveId"])),
        "capstoneStatus": _capstone_status(missions, objectives),
    }


def export(root):
    res = net.Result()
    data = validate_authored_missions(root, res)
    if not res.valid:
        return res, None
    out = root / "generated/data/authored_mission_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.authored_mission_catalog", "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data, "rules": RULES, "openItems": OPEN_ITEMS, "runtimeImplemented": False,
    }
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "export"])
    parser.add_argument("--root", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else net.find_project_root(Path(__file__).parent)
    out = None
    if args.command == "export":
        res, out = export(root)
    else:
        res = net.Result()
        validate_authored_missions(root, res)
    for message in res.warnings:
        print("WARNING:", message)
    for message in res.errors:
        print("ERROR:", message)
    print("Rows:", res.stats)
    if out:
        print("Exported:", out)
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1


if __name__ == "__main__":
    sys.exit(main())

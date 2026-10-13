"""Progression identities and mission-tier requirements.
Authoring/export only. Campaign ownership, completion and inventory are native state.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import doda_network_rules as net

TOOL_VERSION = "0.1.0"
UPGRADES_FILE = "upgrades.csv"
MILESTONES_FILE = "plot_milestones.csv"
ITEMS_FILE = "plot_items.csv"
REQUIREMENTS_FILE = "mission_tier_requirements.csv"

COMMON_COLUMNS = ["source_reference", "description", "sort_order", "active"]
UPGRADE_COLUMNS = ["upgrade_id", "display_name", "track_id"] + COMMON_COLUMNS
MILESTONE_COLUMNS = ["milestone_id", "display_name"] + COMMON_COLUMNS
ITEM_COLUMNS = ["plot_item_id", "display_name"] + COMMON_COLUMNS
REQUIREMENT_COLUMNS = [
    "requirement_id", "tier_id", "upgrade_id", "milestone_id", "plot_item_id"
] + COMMON_COLUMNS

REFERENCE_TYPES = {
    "upgrade_id": "UPGRADE_ACQUIRED",
    "milestone_id": "MILESTONE_COMPLETED",
    "plot_item_id": "PLOT_ITEM_HELD",
}
RULES = {
    "upgradeMeaning": "PURCHASED_OR_UNLOCKED_BENEFIT_ABILITY_STATS_OR_ACCESS",
    "upgradeDefinitionIsNotEquipmentOwnership": True,
    "milestoneCheck": "COMPLETED_PERSISTENT_RECORD",
    "plotItemCheck": "CURRENTLY_HELD_AT_CAPSTONE_PURCHASE",
    "requirementsCombine": "ALL_ACTIVE_REQUIREMENTS",
    "definitionActiveIsNotCampaignAcquired": True,
    "emptyRequiredReferenceSet": "UNCONFIGURED_NOT_AUTOMATICALLY_SATISFIED",
}
OPEN_ITEMS = {
    "PID-OPEN-01": "Actual upgrade, milestone and plot-item definitions.",
    "PID-OPEN-02": "Which major upgrades and plot requirements gate Tier 6.",
    "PID-OPEN-03": "Upgrade acquisition costs, prerequisites and benefits.",
    "PID-OPEN-04": "Capstone mission definition and its stable mission reference.",
}


def _read(src, filename, columns, label, res):
    path = src / filename
    if not path.is_file():
        res.errors.append(f"[{label}] Required source file missing: {filename}")
        return []
    return net.read_table(path, columns, label, res) or []


def _external(src, filename, key, res):
    rows = _read(src, filename, [key, "active"], filename, res)
    index = {}
    for row in rows:
        value = row[key]
        ctx = f"[{filename}] Line {row['_line']}"
        if not value or value in index:
            res.errors.append(f"{ctx}: blank or duplicate {key} '{value}'")
            continue
        index[value] = net._bool(row["active"], ctx, res)
    return index


def _definitions(src, filename, columns, key, label, res, tracks=None):
    rows = _read(src, filename, columns, label, res)
    index = {}
    for row in rows:
        ctx = f"[{label}] Line {row['_line']}"
        value = row[key]
        if not value or value in index:
            res.errors.append(f"{ctx}: blank or duplicate {key} '{value}'")
            continue
        active = net._bool(row["active"], ctx, res)
        if not row["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(f"{ctx}: sort_order must be nonnegative")
        item = {
            "id": value, "displayName": row["display_name"],
            "sourceReference": row["source_reference"] or None,
            "description": row["description"], "sortOrder": order, "active": active,
        }
        if key == "upgrade_id":
            track = row["track_id"]
            if track:
                if tracks is None or track not in tracks:
                    res.errors.append(f"{ctx}: unknown track_id '{track}'")
                elif active and not tracks[track]:
                    res.errors.append(f"{ctx}: active upgrade uses inactive track '{track}'")
            item["trackId"] = track or None
        index[value] = item
    return index


def validate_identities(root, res):
    src = root / "data_authoring/source"
    tracks = None
    track_path = src / "department_tracks.csv"
    if track_path.is_file():
        tracks = _external(src, "department_tracks.csv", "track_id", res)

    upgrades = _definitions(src, UPGRADES_FILE, UPGRADE_COLUMNS,
                            "upgrade_id", "upgrades", res, tracks)
    milestones = _definitions(src, MILESTONES_FILE, MILESTONE_COLUMNS,
                              "milestone_id", "plot_milestones", res)
    items = _definitions(src, ITEMS_FILE, ITEM_COLUMNS,
                         "plot_item_id", "plot_items", res)
    rows = _read(src, REQUIREMENTS_FILE, REQUIREMENT_COLUMNS,
                 "mission_tier_requirements", res)
    tiers = _external(src, "mission_tiers.csv", "tier_id", res) if rows else {}
    catalogs = {"upgrade_id": upgrades, "milestone_id": milestones, "plot_item_id": items}
    requirements, seen, logical = [], set(), set()

    for row in rows:
        ctx = f"[mission_tier_requirements] Line {row['_line']}"
        rid = row["requirement_id"]
        if not rid or rid in seen:
            res.errors.append(f"{ctx}: blank or duplicate requirement_id '{rid}'")
            continue
        seen.add(rid)
        active = net._bool(row["active"], ctx, res)
        tier = row["tier_id"]
        if tier not in tiers:
            res.errors.append(f"{ctx}: unknown tier_id '{tier}'")
        elif active and not tiers[tier]:
            res.errors.append(f"{ctx}: active requirement uses inactive tier '{tier}'")
        references = [key for key in REFERENCE_TYPES if row[key]]
        if len(references) != 1:
            res.errors.append(f"{ctx}: exactly one upgrade, milestone or plot-item reference is required")
            continue
        field = references[0]
        target_id = row[field]
        target = catalogs[field].get(target_id)
        if target is None:
            res.errors.append(f"{ctx}: unknown {field} '{target_id}'")
        elif active and not target["active"]:
            res.errors.append(f"{ctx}: active requirement uses inactive target '{target_id}'")
        combination = (tier, field, target_id)
        if combination in logical:
            res.errors.append(f"{ctx}: duplicate logical requirement for '{target_id}' in '{tier}'")
        logical.add(combination)
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(f"{ctx}: sort_order must be nonnegative")
        requirements.append({
            "requirementId": rid, "tierId": tier,
            "requirementType": REFERENCE_TYPES[field], "referenceId": target_id,
            "sourceReference": row["source_reference"] or None,
            "description": row["description"], "sortOrder": order, "active": active,
        })

    def ordered(index):
        return sorted(index.values(), key=lambda item: (item["sortOrder"] or 0, item["id"]))

    active_final = [row for row in requirements if row["active"] and row["tierId"] == "TIER_6"]
    missing = []
    if not any(row["requirementType"] == "UPGRADE_ACQUIRED" for row in active_final):
        missing.append("REQUIRED_UPGRADE_REFERENCES")
    if not any(row["requirementType"] in ("MILESTONE_COMPLETED", "PLOT_ITEM_HELD")
               for row in active_final):
        missing.append("REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES")
    return {
        "upgrades": ordered(upgrades),
        "plotMilestones": ordered(milestones),
        "plotItems": ordered(items),
        "missionTierRequirements": sorted(
            requirements, key=lambda row: (row["sortOrder"] or 0, row["requirementId"])
        ),
        "finalGateReferenceStatus": {
            "configured": res.valid and not missing,
            "missingConfiguration": missing,
            "isCampaignEligibilityResult": False,
        },
    }


def export(root):
    res = net.Result()
    data = validate_identities(root, res)
    if not res.valid:
        return res, None
    out = root / "generated/data/progression_identity_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.progression_identity_catalog", "toolVersion": TOOL_VERSION,
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
    if args.command == "export":
        res, out = export(root)
    else:
        res = net.Result()
        validate_identities(root, res)
        out = None
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

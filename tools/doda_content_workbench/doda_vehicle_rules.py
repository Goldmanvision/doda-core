"""Generic vehicle types and team capacities; no inventory or allocation."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import doda_network_rules as net
from doda_task_staffing_rules import read_rows

VEHICLE_TYPES_FILE = "vehicle_types.csv"
COLUMNS = [
    "vehicle_type_id", "display_name", "max_team_members",
    "description", "sort_order", "active",
]


def validate_vehicles(root, result):
    path = Path(root) / "data_authoring/source" / VEHICLE_TYPES_FILE
    rows = read_rows(path, COLUMNS, result)
    result.stats["vehicle_types"] = len(rows)
    items, seen = [], set()
    for row in rows:
        ctx = "[vehicle_types] Line " + str(row["_line"])
        vid = row["vehicle_type_id"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", vid) or vid in seen:
            result.errors.append(ctx + ": invalid or duplicate vehicle_type_id")
        seen.add(vid)
        for field in ("display_name", "description"):
            if not row[field]:
                result.errors.append(ctx + ": " + field + " is required")
        capacity = None
        raw = row["max_team_members"]
        if not re.fullmatch(r"[0-9]+", raw) or int(raw) < 1:
            result.errors.append(ctx + ": max_team_members must be a positive whole number")
        else:
            capacity = int(raw)
        order = None
        if not re.fullmatch(r"[0-9]+", row["sort_order"]):
            result.errors.append(ctx + ": sort_order must be a nonnegative whole number")
        else:
            order = int(row["sort_order"])
        state = row["active"].upper()
        if state not in ("TRUE", "FALSE"):
            result.errors.append(ctx + ": active must be true or false")
        items.append({
            "vehicleTypeId": vid, "displayName": row["display_name"],
            "maxTeamMembers": capacity, "description": row["description"],
            "sortOrder": order, "active": state == "TRUE",
        })
    return {"vehicleTypes": sorted(
        items, key=lambda item: (item["sortOrder"] or 0, item["vehicleTypeId"])
    )}


def export(root):
    root = Path(root)
    result = net.Result()
    data = validate_vehicles(root, result)
    if not result.valid:
        return result, None
    path = root / "generated/data/vehicle_catalog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.vehicle_catalog", "toolVersion": "0.1.0",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data, "runtimeImplemented": False,
        "rules": {
            "catalogScope": "GENERIC_VEHICLE_TYPES",
            "capacityUnit": "TEAM_MEMBERS_PER_VEHICLE",
            "capacityIsNotVehicleQuantity": True,
            "capacityDoesNotChangeTaskStaffingLimits": True,
            "definitionsCreateNoInventory": True,
            "personalDeviceSlotAccountingApplies": False,
            "runtimeCapacityChecksImplemented": False,
            "allocationImplemented": False,
        },
        "openItems": {
            "VEH-01": "Vehicle brands/models and ownership catalog.",
            "VEH-02": "Multiple vehicles, oversized teams and allocation policy.",
            "VEH-03": "Travel, cargo, upgrades, prices and runtime inventory.",
        },
    }
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return result, path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "export"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "export":
        result, path = export(args.root)
    else:
        result = net.Result()
        validate_vehicles(args.root, result)
        path = None
    for message in result.warnings:
        print("WARNING:", message)
    for message in result.errors:
        print("ERROR:", message)
    if path:
        print("Exported:", path)
    print("RESULT:", "PASS" if result.valid else "FAIL")
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())

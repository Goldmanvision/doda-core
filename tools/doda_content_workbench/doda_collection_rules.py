"""Collection receptacle catalog only; no inventory or collection execution."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import doda_network_rules as net

RECEPTACLES_FILE = "collection_receptacles.csv"
COLUMNS = ["receptacle_id", "display_name", "description", "sort_order", "active"]
TOOL_VERSION = "0.1.0"


def validate_collection(root, result):
    root = Path(root)
    rows = net.read_table(
        root / "data_authoring/source" / RECEPTACLES_FILE,
        COLUMNS, "collection_receptacles", result,
    )
    items, seen = [], set()
    for row in rows or []:
        ctx = "[collection_receptacles] Line " + str(row.get("_line", "?"))
        rid = row["receptacle_id"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", rid) or rid in seen:
            result.errors.append(ctx + ": invalid or duplicate receptacle_id " + rid)
        seen.add(rid)
        for name in ("display_name", "description"):
            if not row[name]:
                result.errors.append(ctx + ": " + name + " is required")
        order = net._int(row["sort_order"], ctx, "sort_order", result)
        if order is not None and order < 0:
            result.errors.append(ctx + ": sort_order must be nonnegative")
        active = net._bool(row["active"], ctx, result)
        items.append({
            "receptacleId": rid, "displayName": row["display_name"],
            "description": row["description"], "sortOrder": order,
            "active": active,
        })
    return {"receptacles": sorted(
        items, key=lambda item: (item["sortOrder"] or 0, item["receptacleId"])
    )}


def export(root):
    root = Path(root)
    result = net.Result()
    data = validate_collection(root, result)
    if not result.valid:
        return result, None
    path = root / "generated/data/collection_receptacles.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.collection_receptacles",
        "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "runtimeImplemented": False,
        **data,
        "rules": {
            "definitionsCreateNoInventory": True,
            "collectionMappingsImplemented": False,
            "consumptionImplemented": False,
            "personalDeviceSlotAccountingApplies": False,
            "receptacleDoesNotReclassifyEvidence": True,
        },
        "openItems": {
            "COLLECT-01": "Authored evidence-type eligibility mappings.",
            "COLLECT-02": "Quantities, capacity, reuse and consumption.",
            "COLLECT-03": "Missing-receptacle weighted-selection behavior.",
            "COLLECT-04": "Task prerequisites and runtime inventory integration.",
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
        validate_collection(args.root, result)
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

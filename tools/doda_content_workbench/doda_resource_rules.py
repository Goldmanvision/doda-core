"""Resource definitions only. Balances and entity counts are runtime state."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import doda_network_rules as net

TOOL_VERSION = "0.1.0"
RESOURCES_FILE = "resources.csv"
RESOURCE_COLUMNS = [
    "resource_id", "display_name", "description", "resource_kind",
    "tracks_lifetime", "sort_order", "active",
]
RESOURCE_KINDS = ("STOCKPILE", "HOLDING", "HEADCOUNT")

def validate_resources(root, res):
    path = Path(root) / "data_authoring/source" / RESOURCES_FILE
    rows = net.read_table(path, RESOURCE_COLUMNS, "resources", res)
    if rows is None:
        return {"resources": []}
    items, seen = [], set()
    for row in rows:
        ctx = "[resources] Line " + str(row.get("_line", "?"))
        rid = row["resource_id"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", rid) or rid in seen:
            res.errors.append(ctx + ": invalid or duplicate resource_id " + rid)
        seen.add(rid)
        for field in ("display_name", "description"):
            if not row[field]:
                res.errors.append(ctx + ": " + field + " is required")
        kind = row["resource_kind"].upper()
        if kind not in RESOURCE_KINDS:
            res.errors.append(ctx + ": invalid resource_kind " + kind)
        lifetime = net._bool(row["tracks_lifetime"], ctx, res)
        active = net._bool(row["active"], ctx, res)
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(ctx + ": sort_order must be nonnegative")
        if kind != "STOCKPILE" and lifetime:
            res.errors.append(ctx + ": lifetime tracking applies only to STOCKPILE")
        items.append({
            "resourceId": rid,
            "displayName": row["display_name"],
            "description": row["description"],
            "resourceKind": kind,
            "tracksLifetime": lifetime,
            "sortOrder": order,
            "active": active,
        })
    return {"resources": sorted(
        items, key=lambda r: (r["sortOrder"] or 0, r["resourceId"])
    )}

def export(root):
    root = Path(root)
    res = net.Result()
    data = validate_resources(root, res)
    if not res.valid:
        return res, None
    path = root / "generated/data/resource_catalog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.resource_catalog",
        "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data,
        "runtimeImplemented": False,
        "rules": {
            "stockpilesAreBalances": True,
            "holdingsCountOwnedEntities": True,
            "headcountsDerivedFromPersonnel": True,
            "catalogStoresNoCurrentValues": True,
            "lifetimeCountsCreditsNotCurrentBalance": True,
        },
    }
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return res, path

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "export"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "export":
        res, path = export(args.root)
    else:
        res = net.Result()
        validate_resources(args.root, res)
        path = None
    for message in res.errors:
        print("ERROR:", message)
    for message in res.warnings:
        print("WARNING:", message)
    if path:
        print("Exported:", path)
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1

if __name__ == "__main__":
    raise SystemExit(main())

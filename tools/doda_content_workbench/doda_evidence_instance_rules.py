"""Evidence instance definitions; no live pieces, random sampling or credits."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as resources

INSTANCES_FILE = "evidence_type_instances.csv"
COLUMNS = [
    "evidence_instance_id", "display_name", "evidence_resource_id",
    "base_value_min", "base_value_max", "description", "sort_order", "active",
]
EVIDENCE_RESOURCES = (
    "EVIDENCE_PAPER", "EVIDENCE_PHOTOGRAPHIC", "EVIDENCE_DIGITAL",
    "EVIDENCE_AUDIO", "EVIDENCE_VIDEO", "EVIDENCE_CHEMICAL", "EVIDENCE_PHYSICAL",
)


def whole_value(raw):
    text = str(raw).strip()
    if not re.fullmatch(r"[0-9]+", text):
        raise ValueError("Base value must be a nonnegative whole number")
    return int(text)


def validate_instances(root, result):
    root = Path(root)
    resource_data = resources.validate_resources(root, result)["resources"]
    eligible = {
        item["resourceId"]: item["active"] for item in resource_data
        if item["resourceId"] in EVIDENCE_RESOURCES
        and item["resourceKind"] == "STOCKPILE"
    }
    rows = net.read_table(
        root / "data_authoring/source" / INSTANCES_FILE,
        COLUMNS, "evidence_type_instances", result,
    )
    items, seen = [], set()
    for row in rows or []:
        ctx = "[evidence_type_instances] Line " + str(row.get("_line", "?"))
        iid = row["evidence_instance_id"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", iid) or iid in seen:
            result.errors.append(ctx + ": invalid or duplicate evidence_instance_id")
        seen.add(iid)
        for field in ("display_name", "description"):
            if not row[field]:
                result.errors.append(ctx + ": " + field + " is required")
        active = net._bool(row["active"], ctx, result)
        rid = row["evidence_resource_id"]
        if rid not in eligible:
            result.errors.append(ctx + ": not an authored evidence stockpile: " + rid)
        elif active and not eligible[rid]:
            result.errors.append(ctx + ": active definition references inactive evidence")
        bounds = []
        for field in ("base_value_min", "base_value_max"):
            try:
                bounds.append(whole_value(row[field]))
            except ValueError as error:
                bounds.append(None)
                result.errors.append(ctx + ": " + field + ": " + str(error))
        low, high = bounds
        if low is not None and high is not None and low > high:
            result.errors.append(ctx + ": base_value_min must not exceed base_value_max")
        order = net._int(row["sort_order"], ctx, "sort_order", result)
        if order is not None and order < 0:
            result.errors.append(ctx + ": sort_order must be nonnegative")
        items.append({
            "evidenceInstanceId": iid, "displayName": row["display_name"],
            "evidenceResourceId": rid, "baseValueMin": low, "baseValueMax": high,
            "description": row["description"], "sortOrder": order, "active": active,
        })
    return {"definitions": sorted(
        items, key=lambda item: (item["sortOrder"] or 0, item["evidenceInstanceId"])
    )}


def export(root):
    root = Path(root)
    result = net.Result()
    data = validate_instances(root, result)
    if not result.valid:
        return result, None
    path = root / "generated/data/evidence_type_instances.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.evidence_type_instances", "toolVersion": "0.1.0",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data, "runtimeImplemented": False,
        "rules": {
            "catalogStoresDefinitionsNotLivePieces": True,
            "baseValueUnit": "EVIDENCE_VALUE_POINTS_NOT_PIECE_COUNT",
            "rangeEndpoints": "INCLUSIVE_NONNEGATIVE_INTEGERS",
            "equalEndpointsMeanFixedValue": True,
            "exportSamplesNoValues": True,
            "randomSamplingImplemented": False,
            "collectionMultiplierOwner": "COLLECTION_MODEL",
            "rounding": "ROUND_HALF_UP_PER_PIECE_AFTER_MULTIPLIER",
            "definitionsCreateNoInventory": True,
        },
        "openItems": {
            "EVI-01": "Random distribution and runtime creation/persistence of a piece value.",
            "EVI-02": "Runtime collection and admissible-evidence processing integration.",
            "EVI-03": "Bulk discoveries, duplicate rewards and collection stacking.",
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
        validate_instances(args.root, result)
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

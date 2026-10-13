"""Collection models and exact value preview; no runtime inventory or execution."""
import argparse
import json
import re
from decimal import Decimal, localcontext, ROUND_HALF_UP
from datetime import datetime, timezone
from pathlib import Path
import doda_network_rules as net
import doda_collection_rules as collection
import doda_resource_rules as resources

DEVICES_FILE = "collection_device_types.csv"
DEVICE_COLUMNS = ["device_type_id", "display_name", "description", "sort_order", "active"]
MODELS_FILE = "collection_models.csv"
MODEL_COLUMNS = [
    "model_id", "display_name", "collection_kind", "collection_type_id",
    "brand", "model_name", "evidence_types", "evidence_value_multiplier",
    "description", "sort_order", "active",
]
COLLECTION_KINDS = ("RECEPTACLE", "DEVICE")


def decimal_value(raw, positive=True):
    if isinstance(raw, (bool, float)):
        raise ValueError("Use an exact decimal string or integer")
    text = str(raw).strip()
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", text):
        raise ValueError("Expected a nonnegative plain decimal")
    value = Decimal(text)
    if positive and value <= 0:
        raise ValueError("Multiplier must be positive")
    return value


def piece_value(base_value, multiplier):
    base = decimal_value(base_value, False)
    factor = decimal_value(multiplier)
    with localcontext() as context:
        context.prec = max(
            28, len(base.as_tuple().digits) + len(factor.as_tuple().digits) + 5
        )
        return int((base * factor).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def evidence_ids(raw):
    if not raw.strip():
        return []
    values = [value.strip() for value in raw.split(";")]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise ValueError("Evidence selection has empty or repeated IDs")
    return values


def validate_models(root, result):
    root = Path(root)
    src = root / "data_authoring/source"
    receptacles = collection.validate_collection(root, result)["receptacles"]
    parents = {
        ("RECEPTACLE", item["receptacleId"]): item["active"]
        for item in receptacles
    }
    device_rows = net.read_table(
        src / DEVICES_FILE, DEVICE_COLUMNS, "collection_device_types", result
    )
    devices, seen = [], set()
    for row in device_rows or []:
        ctx = "[collection_device_types] Line " + str(row.get("_line", "?"))
        did = row["device_type_id"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", did) or did in seen:
            result.errors.append(ctx + ": invalid or duplicate device_type_id")
        seen.add(did)
        for name in ("display_name", "description"):
            if not row[name]:
                result.errors.append(ctx + ": " + name + " is required")
        active = net._bool(row["active"], ctx, result)
        order = net._int(row["sort_order"], ctx, "sort_order", result)
        if order is not None and order < 0:
            result.errors.append(ctx + ": sort_order must be nonnegative")
        parents[("DEVICE", did)] = active
        devices.append({
            "deviceTypeId": did, "displayName": row["display_name"],
            "description": row["description"], "sortOrder": order, "active": active,
        })

    resource_data = resources.validate_resources(root, result)["resources"]
    eligible = {
        item["resourceId"]: item["active"] for item in resource_data
        if item["resourceId"].startswith("EVIDENCE_")
        and item["resourceKind"] == "STOCKPILE"
    }
    rows = net.read_table(
        src / MODELS_FILE, MODEL_COLUMNS, "collection_models", result
    )
    models, seen = [], set()
    for row in rows or []:
        ctx = "[collection_models] Line " + str(row.get("_line", "?"))
        mid = row["model_id"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", mid) or mid in seen:
            result.errors.append(ctx + ": invalid or duplicate model_id")
        seen.add(mid)
        for name in ("display_name", "description"):
            if not row[name]:
                result.errors.append(ctx + ": " + name + " is required")
        kind = row["collection_kind"]
        parent = (kind, row["collection_type_id"])
        if kind not in COLLECTION_KINDS:
            result.errors.append(ctx + ": invalid collection_kind")
        if parent not in parents:
            result.errors.append(ctx + ": unknown type for this collection_kind")
        active = net._bool(row["active"], ctx, result)
        if active and parent in parents and not parents[parent]:
            result.errors.append(ctx + ": active model requires active collection type")
        try:
            selected = evidence_ids(row["evidence_types"])
        except ValueError as error:
            selected = []
            result.errors.append(ctx + ": " + str(error))
        for rid in selected:
            if rid not in eligible:
                result.errors.append(ctx + ": not an authored evidence resource: " + rid)
            elif active and not eligible[rid]:
                result.errors.append(ctx + ": active model references inactive evidence: " + rid)
        factor = None
        if row["evidence_value_multiplier"]:
            try:
                factor = decimal_value(row["evidence_value_multiplier"])
            except ValueError as error:
                result.errors.append(ctx + ": invalid multiplier: " + str(error))
        if active and (not selected or factor is None):
            result.errors.append(ctx + ": active model requires evidence types and multiplier")
        elif not active and (not selected or factor is None):
            result.warnings.append(ctx + ": draft collection properties unconfigured")
        order = net._int(row["sort_order"], ctx, "sort_order", result)
        if order is not None and order < 0:
            result.errors.append(ctx + ": sort_order must be nonnegative")
        models.append({
            "modelId": mid, "displayName": row["display_name"],
            "collectionKind": kind, "collectionTypeId": row["collection_type_id"],
            "brand": row["brand"] or None, "modelName": row["model_name"] or None,
            "evidenceTypes": selected,
            "evidenceValueMultiplier": format(factor, "f") if factor is not None else None,
            "description": row["description"], "sortOrder": order, "active": active,
        })
    return {
        "deviceTypes": sorted(devices, key=lambda item: (item["sortOrder"] or 0, item["deviceTypeId"])),
        "models": sorted(models, key=lambda item: (item["sortOrder"] or 0, item["modelId"])),
    }


def export(root):
    root = Path(root)
    result = net.Result()
    data = validate_models(root, result)
    if not result.valid:
        return result, None
    path = root / "generated/data/collection_models.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.collection_models", "toolVersion": "0.1.0",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "runtimeImplemented": False, **data,
        "rules": {
            "multiplierOwner": "MODEL",
            "multiplierRepresentation": "EXACT_DECIMAL_STRING",
            "rounding": "ROUND_HALF_UP_PER_PIECE",
            "pieceCountUnchanged": True,
            "definitionsCreateNoInventory": True,
            "stackingImplemented": False,
            "repeatedPhotographRewardsImplemented": False,
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
        validate_models(args.root, result)
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

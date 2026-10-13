"""Task prerequisite definitions only; no allocation or runtime checks."""
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import doda_network_rules as net
import doda_weapon_rules as weapons

PREREQUISITES_FILE = "task_prerequisites.csv"
COLUMNS = [
    "prerequisite_id", "task_template_id", "requirement_kind", "scope",
    "personnel_role", "requirement_value", "min_quantity",
    "description", "sort_order", "active",
]
KINDS = ("WEAPON_TYPE", "APPLICABLE_COLLECTION_RECEPTACLE", "MOTOR_VEHICLE")
SCOPES = ("PER_ASSIGNED_AGENT", "TASK")


def template_index(root, result):
    path = Path(root) / "data_authoring/source/task_templates.csv"
    items = {}
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not {"task_template_id", "active"}.issubset(reader.fieldnames or []):
                raise ValueError("invalid parent header")
            for row in reader:
                tid = (row.get("task_template_id") or "").strip()
                if not tid:
                    continue
                if tid in items:
                    result.errors.append("[task_prerequisites] duplicate parent " + tid)
                state = (row.get("active") or "").strip().upper()
                if state not in ("TRUE", "FALSE"):
                    result.errors.append("[task_prerequisites] invalid parent active " + tid)
                items[tid] = state == "TRUE"
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        result.errors.append("[task_prerequisites] parent read: " + str(error))
    return items


def validate_prerequisites(root, result):
    root = Path(root)
    parents = template_index(root, result)
    rows = net.read_table(
        root / "data_authoring/source" / PREREQUISITES_FILE,
        COLUMNS, "task_prerequisites", result,
    )
    items, seen, semantics = [], set(), set()
    for row in rows or []:
        ctx = "[task_prerequisites] Line " + str(row.get("_line", "?"))
        pid = row["prerequisite_id"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", pid) or pid in seen:
            result.errors.append(ctx + ": invalid or duplicate prerequisite_id")
        seen.add(pid)
        tid, kind, scope = row["task_template_id"], row["requirement_kind"], row["scope"]
        role, value = row["personnel_role"], row["requirement_value"]
        key = (tid, kind, scope, role, value)
        if key in semantics:
            result.errors.append(ctx + ": duplicate semantic requirement")
        semantics.add(key)
        active = net._bool(row["active"], ctx, result)
        if tid not in parents:
            result.errors.append(ctx + ": unknown task_template_id")
        elif active and not parents[tid]:
            result.errors.append(ctx + ": active prerequisite requires active parent")
        if kind not in KINDS:
            result.errors.append(ctx + ": invalid requirement_kind")
        if scope not in SCOPES:
            result.errors.append(ctx + ": invalid scope")
        if scope == "PER_ASSIGNED_AGENT" and role != "AGENT":
            result.errors.append(ctx + ": per-agent scope requires AGENT role")
        if scope == "TASK" and role:
            result.errors.append(ctx + ": TASK scope must leave personnel_role blank")
        if kind in ("WEAPON_TYPE", "APPLICABLE_COLLECTION_RECEPTACLE"):
            if scope != "PER_ASSIGNED_AGENT":
                result.errors.append(ctx + ": this requirement uses per-agent scope")
        if kind == "WEAPON_TYPE":
            if value not in weapons.WEAPON_TYPES:
                result.errors.append(ctx + ": unknown weapon type")
        elif value:
            result.errors.append(ctx + ": generic requirement must leave requirement_value blank")
        if kind == "MOTOR_VEHICLE" and scope != "TASK":
            result.errors.append(ctx + ": motor-vehicle requirement uses TASK scope")
        quantity = None
        raw = row["min_quantity"]
        if raw:
            if not re.fullmatch(r"[0-9]+", raw) or int(raw) < 1:
                result.errors.append(ctx + ": min_quantity must be a positive whole number")
            else:
                quantity = int(raw)
        if active and quantity is None:
            result.errors.append(ctx + ": active prerequisite requires min_quantity")
        elif not active and quantity is None:
            result.warnings.append(ctx + ": draft minimum quantity unconfigured")
        if not row["description"]:
            result.errors.append(ctx + ": description is required")
        order = net._int(row["sort_order"], ctx, "sort_order", result)
        if order is not None and order < 0:
            result.errors.append(ctx + ": sort_order must be nonnegative")
        items.append({
            "prerequisiteId": pid, "taskTemplateId": tid, "requirementKind": kind,
            "scope": scope, "personnelRole": role or None,
            "requirementValue": value or None, "minQuantity": quantity,
            "description": row["description"], "sortOrder": order, "active": active,
        })
    return {"prerequisites": sorted(items, key=lambda item: (
        item["taskTemplateId"], item["sortOrder"] or 0, item["prerequisiteId"]
    ))}


def export(root):
    root = Path(root)
    result = net.Result()
    data = validate_prerequisites(root, result)
    if not result.valid:
        return result, None
    path = root / "generated/data/task_prerequisites.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.task_prerequisites", "toolVersion": "0.1.0",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data, "runtimeImplemented": False,
        "rules": {
            "definitionsCreateNoInventory": True,
            "perAgentQuantityAppliesSeparatelyToEachAssignedAgent": True,
            "applicableReceptacle": "RECEPTACLE_MODEL_WITH_MATCHING_EVIDENCE_CATEGORY",
            "collectionDevicesDoNotSatisfyReceptacleRequirement": True,
            "weaponTypeIsNotBrandOrModel": True,
            "blankQuantity": "UNCONFIGURED",
            "personalDeviceLimitsUnchanged": True,
            "runtimeEligibilityImplemented": False,
        },
        "openItems": {
            "PRE-01": "Owned vehicle quantities, runtime capacity enforcement and allocation; generic vehicle types and capacities are authored separately.",
            "PRE-02": "Missing-receptacle behavior for weighted evidence selection.",
            "PRE-03": "Runtime inventory, equipment assignment and eligibility.",
            "PRE-04": "Consumption, reuse and capacity rules.",
        },
    }
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return result, path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "export"))
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.command == "export":
        result, path = export(args.root)
    else:
        result = net.Result()
        validate_prerequisites(args.root, result)
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

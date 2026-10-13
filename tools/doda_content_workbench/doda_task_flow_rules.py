"""Task resource-flow definitions; no balances or runtime execution."""
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as resources

FLOWS_FILE = "task_template_flows.csv"
FLOW_COLUMNS = [
    "task_template_id", "direction", "resource_id", "flow_mode",
    "amount", "weight", "sort_order", "active",
]
DIRECTIONS = ("IN", "OUT")
FLOW_MODES = ("FIXED", "WEIGHTED")
TOOL_VERSION = "0.1.0"

def optional_positive(raw, field, ctx, res):
    if not raw:
        return None
    value = net._int(raw, ctx, field, res)
    if value is not None and value < 1:
        res.errors.append(ctx + ": " + field + " must be positive")
        return None
    return value

def template_index(root, res):
    path = Path(root) / "data_authoring/source/task_templates.csv"
    if not path.is_file():
        res.errors.append("[task_template_flows] task_templates.csv is required")
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"task_template_id", "active"}.issubset(reader.fieldnames or []):
            res.errors.append("[task_template_flows] invalid task-template header")
            return {}
        result = {}
        for row in reader:
            key = row.get("task_template_id", "").strip()
            if not key:
                continue
            if key in result:
                res.errors.append("[task_template_flows] duplicate parent template: " + key)
            result[key] = row
        return result

def validate_flows(root, res):
    root = Path(root)
    rows = net.read_table(
        root / "data_authoring/source" / FLOWS_FILE,
        FLOW_COLUMNS, "task_template_flows", res
    )
    templates = template_index(root, res)
    resource_data = resources.validate_resources(root, res)
    resource_index = {r["resourceId"]: r for r in resource_data["resources"]}
    seen, items, groups, unfinished = set(), [], {}, set()
    for row in rows or []:
        ctx = "[task_template_flows] Line " + str(row.get("_line", "?"))
        tid, rid = row["task_template_id"], row["resource_id"]
        direction, mode = row["direction"].upper(), row["flow_mode"].upper()
        key = (tid, direction, rid)
        if key in seen:
            res.errors.append(ctx + ": duplicate template/direction/resource")
        seen.add(key)
        if direction not in DIRECTIONS:
            res.errors.append(ctx + ": direction must be IN or OUT")
        if mode not in FLOW_MODES:
            res.errors.append(ctx + ": invalid flow_mode")
        active = net._bool(row["active"], ctx, res)
        amount = optional_positive(row["amount"], "amount", ctx, res)
        weight = optional_positive(row["weight"], "weight", ctx, res)
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(ctx + ": sort_order must be nonnegative")
        parent = templates.get(tid)
        resource = resource_index.get(rid)
        if parent is None:
            res.errors.append(ctx + ": unknown task_template_id " + tid)
        elif active and parent.get("active", "").strip().upper() != "TRUE":
            res.errors.append(ctx + ": active flow needs an active parent template")
        if resource is None:
            res.errors.append(ctx + ": unknown resource_id " + rid)
        elif resource["resourceKind"] != "STOCKPILE":
            res.errors.append(ctx + ": task flows require STOCKPILE resources")
        elif active and not resource["active"]:
            res.errors.append(ctx + ": active flow needs an active resource")
        if direction == "IN" and mode != "FIXED":
            res.errors.append(ctx + ": input flows must be FIXED")
        if mode == "FIXED" and row["weight"]:
            res.errors.append(ctx + ": FIXED flow must leave weight blank")
        if active and amount is None:
            res.errors.append(ctx + ": active flow requires amount")
        if active and mode == "WEIGHTED" and weight is None:
            res.errors.append(ctx + ": active WEIGHTED flow requires weight")
        if not active and (amount is None or mode == "WEIGHTED" and weight is None):
            unfinished.add(tid)
        item = {
            "taskTemplateId": tid, "direction": direction,
            "resourceId": rid, "flowMode": mode,
            "amount": amount, "weight": weight,
            "sortOrder": order, "active": active,
        }
        items.append(item)
        if direction == "OUT":
            groups.setdefault(tid, []).append(item)
    for tid, group in groups.items():
        modes = {r["flowMode"] for r in group}
        if len(modes) > 1:
            res.errors.append(
                "[task_template_flows] " + tid +
                ": output group cannot mix FIXED and WEIGHTED rows"
            )
        if modes == {"WEIGHTED"}:
            amounts = {r["amount"] for r in group if r["amount"] is not None}
            if len(amounts) > 1:
                res.errors.append(
                    "[task_template_flows] " + tid +
                    ": weighted output rows must agree on amount (units selected)"
                )
    for tid in sorted(unfinished):
        res.warnings.append(
            "[task_template_flows] " + tid + ": draft amounts/weights unconfigured"
        )
    return {"flows": sorted(items, key=lambda r: (
        r["taskTemplateId"], r["sortOrder"] or 0, r["direction"], r["resourceId"]
    ))}

def export(root):
    root = Path(root)
    res = net.Result()
    data = validate_flows(root, res)
    if not res.valid:
        return res, None
    path = root / "generated/data/task_resource_flows.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.task_resource_flows", "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data, "runtimeImplemented": False,
        "rules": {
            "inputMode": "FIXED",
            "weightedOutputSelection": "ONE_RESOURCE_TYPE_PER_UNIT",
            "weightedAmount": "TOTAL_UNITS_SELECTED_PER_CREDIT_EVENT",
            "weightMeaning": "RELATIVE_WEIGHT_NOT_PERCENT",
            "creditTiming": "OWNED_BY_TASK_EXECUTION",
            "draftRowsExecute": False,
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
        validate_flows(args.root, res)
        path = None
    for message in res.warnings:
        print("WARNING:", message)
    for message in res.errors:
        print("ERROR:", message)
    if path:
        print("Exported:", path)
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1

if __name__ == "__main__":
    raise SystemExit(main())

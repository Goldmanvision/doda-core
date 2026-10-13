"""Task-specific staffing definitions; no allocation or runtime execution."""
import argparse
import csv
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

STAFFING_FILE = "task_staffing_rules.csv"
COLUMNS = [
    "task_template_id", "personnel_role", "min_contributors",
    "preferred_contributors", "max_contributors", "sort_order", "active",
]
PERSONNEL_ROLES = ("AGENT", "ANALYST", "CONFIDENTIAL_INFORMANT")


@dataclass
class Result:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def valid(self):
        return not self.errors


def read_rows(path, columns, result):
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != columns:
                result.errors.append(str(path.name) + ": header must match exactly")
                return []
            rows = []
            for line, raw in enumerate(reader, 2):
                if None in raw or any(value is None for value in raw.values()):
                    result.errors.append(str(path.name) + ": malformed row " + str(line))
                    continue
                row = {key: value.strip() for key, value in raw.items()}
                if any(row.values()):
                    row["_line"] = line
                    rows.append(row)
            return rows
    except (OSError, UnicodeError, csv.Error) as error:
        result.errors.append(str(path.name) + ": " + str(error))
        return []


def validate_staffing(root, result):
    src = Path(root) / "data_authoring/source"
    templates = {}
    try:
        with (src / "task_templates.csv").open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not {"task_template_id", "active"}.issubset(reader.fieldnames or []):
                result.errors.append("[task_staffing_rules] invalid parent header")
            else:
                for raw in reader:
                    tid = (raw.get("task_template_id") or "").strip()
                    if not tid:
                        continue
                    if tid in templates:
                        result.errors.append("[task_staffing_rules] duplicate parent: " + tid)
                    state = (raw.get("active") or "").strip().upper()
                    if state not in {"TRUE", "FALSE"}:
                        result.errors.append("[task_staffing_rules] invalid parent active: " + tid)
                    templates[tid] = state == "TRUE"
    except (OSError, UnicodeError, csv.Error) as error:
        result.errors.append("[task_staffing_rules] parent read failed: " + str(error))

    rows = read_rows(src / STAFFING_FILE, COLUMNS, result)
    result.stats["task_staffing_rules"] = len(rows)
    items, seen = [], set()

    for row in rows:
        ctx = "[task_staffing_rules] Line " + str(row["_line"])
        tid, role = row["task_template_id"], row["personnel_role"]
        key = (tid, role)
        if key in seen:
            result.errors.append(ctx + ": duplicate template/personnel_role")
        seen.add(key)
        if tid not in templates:
            result.errors.append(ctx + ": unknown task_template_id " + tid)
        if role not in PERSONNEL_ROLES:
            result.errors.append(ctx + ": invalid personnel_role")
        state = row["active"].upper()
        if state not in {"TRUE", "FALSE"}:
            result.errors.append(ctx + ": active must be true or false")
        active = state == "TRUE"
        if active and tid in templates and not templates[tid]:
            result.errors.append(ctx + ": active rule requires active parent")

        counts = {}
        for field_name in (
            "min_contributors", "preferred_contributors", "max_contributors",
        ):
            raw = row[field_name]
            value = None
            if raw:
                if not raw.isascii() or not raw.isdecimal() or int(raw) < 1:
                    result.errors.append(ctx + ": " + field_name + " must be a positive whole number")
                else:
                    value = int(raw)
            counts[field_name] = value

        minimum = counts["min_contributors"]
        preferred = counts["preferred_contributors"]
        maximum = counts["max_contributors"]
        for left, right, label in (
            (minimum, preferred, "minimum exceeds preferred"),
            (minimum, maximum, "minimum exceeds maximum"),
            (preferred, maximum, "preferred exceeds maximum"),
        ):
            if left is not None and right is not None and left > right:
                result.errors.append(ctx + ": " + label)
        if active and minimum is None:
            result.errors.append(ctx + ": active rule requires min_contributors")
        elif not active and minimum is None:
            result.warnings.append(ctx + ": draft minimum unconfigured")

        raw_order = row["sort_order"]
        order = None
        if not raw_order.isascii() or not raw_order.isdecimal():
            result.errors.append(ctx + ": sort_order must be nonnegative whole number")
        else:
            order = int(raw_order)

        items.append({
            "taskTemplateId": tid, "personnelRole": role,
            "minContributors": minimum, "preferredContributors": preferred,
            "maxContributors": maximum, "sortOrder": order, "active": active,
        })

    return {"staffingRules": sorted(items, key=lambda item: (
        item["taskTemplateId"], item["sortOrder"] or 0, item["personnelRole"]
    ))}


def export(root):
    root = Path(root)
    result = Result()
    data = validate_staffing(root, result)
    if not result.valid:
        return result, None
    path = root / "generated/data/task_staffing_rules.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.task_staffing_rules", "toolVersion": "0.1.0",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "runtimeImplemented": False, **data,
        "rules": {
            "scope": "TASK_SPECIFIC_ROLE_COUNTS",
            "capabilityStaffingIsSeparate": True,
            "blankMinimum": "UNCONFIGURED",
            "blankPreferred": "UNSPECIFIED",
            "blankMaximum": "UNSPECIFIED_NOT_CONFIRMED_UNLIMITED",
            "draftRowsExecute": False,
            "skillAndQualificationMappingsImplemented": False,
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
        result = Result()
        validate_staffing(args.root, result)
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

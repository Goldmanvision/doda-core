#!/usr/bin/env python3
r"""
DoDA Content Workbench - CLI validator.

Validates authored CSV source data before any content export, PK3 packaging,
or game integration occurs.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_VERSION = "0.1.0"


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    @property
    def valid(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


TABLE_SPECS: dict[str, dict[str, Any]] = {
    "enum_catalog": {
        "filename": "enum_catalog.csv",
        "required_columns": [
            "enum_group",
            "enum_value",
            "display_label",
            "description",
            "sort_order",
            "active",
        ],
        "key_columns": ["enum_group", "enum_value"],
    },
    "department_tracks": {
        "filename": "department_tracks.csv",
        "required_columns": [
            "track_id",
            "display_name",
            "description",
            "sort_order",
            "active",
        ],
        "key_columns": ["track_id"],
    },
    "metrics": {
        "filename": "metrics.csv",
        "required_columns": [
            "metric_id",
            "display_name",
            "description",
            "owner_system",
            "internal_min",
            "internal_max",
            "default_value",
            "polarity",
            "ui_display_mode",
            "update_notes",
            "active",
        ],
        "key_columns": ["metric_id"],
    },
    "metric_tiers": {
        "filename": "metric_tiers.csv",
        "required_columns": [
            "metric_id",
            "tier_id",
            "min_inclusive",
            "max_inclusive",
            "display_label",
            "short_status",
            "ui_color",
            "flavor_text_id",
            "sort_order",
        ],
        "key_columns": ["metric_id", "tier_id"],
    },
    "facilities": {
        "filename": "facilities.csv",
        "required_columns": [
            "facility_id",
            "display_name",
            "track_id",
            "hq_zone_id",
            "description",
            "personnel_capacity",
            "initial_tier_id",
            "interaction_asset_id",
            "foims_panel_id",
            "active",
        ],
        "key_columns": ["facility_id"],
    },
    "flavor_text": {
        "filename": "flavor_text.csv",
        "required_columns": [
            "flavor_text_id",
            "category",
            "title",
            "body",
            "active",
        ],
        "key_columns": ["flavor_text_id"],
    },
    "qualification_catalog": {
        "filename": "qualification_catalog.csv",
        "required_columns": [
            "qualification_id",
            "display_name",
            "description",
            "sort_order",
            "active",
        ],
        "key_columns": ["qualification_id"],
    },
    "capabilities": {
        "filename": "capabilities.csv",
        "required_columns": [
            "capability_id",
            "display_name",
            "description",
            "standing_operation_label",
            "sort_order",
            "active",
        ],
        "key_columns": ["capability_id"],
    },
    "facility_capabilities": {
        "filename": "facility_capabilities.csv",
        "required_columns": [
            "facility_id",
            "capability_id",
            "display_name_override",
            "max_concurrent_personnel",
            "initial_tier_id",
            "foims_panel_id",
            "sort_order",
            "active",
        ],
        "key_columns": ["facility_id", "capability_id"],
    },
    "capability_staffing_rules": {
        "filename": "capability_staffing_rules.csv",
        "required_columns": [
            "capability_id",
            "qualification_id",
            "min_contributors",
            "preferred_contributors",
            "max_contributors",
            "sort_order",
            "active",
        ],
        "key_columns": ["capability_id", "qualification_id"],
    },
    "facility_capability_staffing_overrides": {
        "filename": "facility_capability_staffing_overrides.csv",
        "required_columns": [
            "facility_id",
            "capability_id",
            "qualification_id",
            "min_contributors",
            "preferred_contributors",
            "max_contributors",
            "sort_order",
            "active",
        ],
        "key_columns": ["facility_id", "capability_id", "qualification_id"],
    },
    "task_templates": {
        "filename": "task_templates.csv",
        "required_columns": [
            "task_template_id",
            "display_name",
            "description",
            "capability_id",
            "priority",
            "default_target_effort_minutes",
            "default_deadline_minutes",
            "auto_allocate",
            "sort_order",
            "active",
        ],
        "key_columns": ["task_template_id"],
    },
}


def find_project_root(start: Path) -> Path:
    current = start.resolve()

    for candidate in (current, *current.parents):
        if (
            (candidate / "data_authoring").is_dir()
            and (candidate / "tools").is_dir()
            and (candidate / "DoDA").is_dir()
        ):
            return candidate

    raise FileNotFoundError(
        "Unable to locate DoDA project root. Expected a folder containing "
        "'data_authoring', 'tools', and 'DoDA'. Use --root to provide it explicitly."
    )


def load_csv(
    path: Path,
    required_columns: list[str],
    table_name: str,
    result: ValidationResult,
) -> list[dict[str, str]]:
    if not path.is_file():
        result.error(f"[{table_name}] Missing required source file: {path}")
        return []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source_file:
            reader = csv.DictReader(source_file)

            if reader.fieldnames is None:
                result.error(f"[{table_name}] File has no CSV header row: {path.name}")
                return []

            actual_columns = [column.strip() for column in reader.fieldnames]
            missing_columns = [
                column for column in required_columns if column not in actual_columns
            ]

            if missing_columns:
                result.error(
                    f"[{table_name}] Missing required columns in {path.name}: "
                    + ", ".join(missing_columns)
                )
                return []

            rows: list[dict[str, str]] = []

            for line_number, raw_row in enumerate(reader, start=2):
                row = {
                    key.strip(): (value or "").strip()
                    for key, value in raw_row.items()
                    if key is not None
                }

                if not any(row.values()):
                    continue

                row["_line_number"] = str(line_number)
                rows.append(row)

            result.stats[table_name] = len(rows)

            if not rows:
                result.warning(f"[{table_name}] Source file contains no data rows: {path.name}")

            return rows

    except UnicodeDecodeError as error:
        result.error(f"[{table_name}] Could not read UTF-8 CSV {path.name}: {error}")
        return []
    except csv.Error as error:
        result.error(f"[{table_name}] CSV parsing error in {path.name}: {error}")
        return []


def validate_keys(
    table_name: str,
    rows: list[dict[str, str]],
    key_columns: list[str],
    result: ValidationResult,
) -> None:
    seen_keys: dict[tuple[str, ...], int] = {}

    for row in rows:
        line_number = row["_line_number"]
        key = tuple(row.get(column, "").strip() for column in key_columns)

        if any(not value for value in key):
            result.error(
                f"[{table_name}] Line {line_number}: blank key value in "
                + ", ".join(key_columns)
            )
            continue

        if key in seen_keys:
            original_line = seen_keys[key]
            result.error(
                f"[{table_name}] Line {line_number}: duplicate key "
                f"{' / '.join(key)}; first defined on line {original_line}"
            )
        else:
            seen_keys[key] = int(line_number)


def validate_active_values(
    table_name: str,
    rows: list[dict[str, str]],
    result: ValidationResult,
) -> None:
    if not rows or "active" not in rows[0]:
        return

    for row in rows:
        value = row.get("active", "").upper()

        if value not in {"TRUE", "FALSE"}:
            result.error(
                f"[{table_name}] Line {row['_line_number']}: active must be TRUE "
                f"or FALSE, found '{row.get('active', '')}'"
            )


def parse_int(
    table_name: str,
    row: dict[str, str],
    column: str,
    result: ValidationResult,
) -> int | None:
    value = row.get(column, "")

    try:
        return int(value)
    except ValueError:
        result.error(
            f"[{table_name}] Line {row['_line_number']}: {column} must be an "
            f"integer, found '{value}'"
        )
        return None


def parse_bool(
    table_name: str,
    row: dict[str, str],
    column: str,
    result: ValidationResult,
) -> bool | None:
    value = row.get(column, "").upper()

    if value == "TRUE":
        return True

    if value == "FALSE":
        return False

    result.error(
        f"[{table_name}] Line {row['_line_number']}: {column} must be TRUE "
        f"or FALSE, found '{row.get(column, '')}'"
    )
    return None


def validate_sort_order(
    table_name: str,
    rows: list[dict[str, str]],
    result: ValidationResult,
) -> None:
    for row in rows:
        if "sort_order" not in row:
            continue

        value = parse_int(table_name, row, "sort_order", result)

        if value is not None and value < 1:
            result.error(
                f"[{table_name}] Line {row['_line_number']}: sort_order must be "
                "at least 1"
            )


def build_id_set(
    rows: list[dict[str, str]],
    column: str,
    active_only: bool = False,
) -> set[str]:
    return {
        row[column]
        for row in rows
        if row.get(column, "").strip()
        and (not active_only or row.get("active", "").upper() == "TRUE")
    }


def build_row_index(
    rows: list[dict[str, str]],
    key_columns: list[str],
    active_only: bool = False,
) -> dict[tuple[str, ...], dict[str, str]]:
    index: dict[tuple[str, ...], dict[str, str]] = {}

    for row in rows:
        if active_only and row.get("active", "").upper() != "TRUE":
            continue

        key = tuple(row.get(column, "") for column in key_columns)

        if all(key):
            index[key] = row

    return index


def build_enum_index(
    rows: list[dict[str, str]],
    active_only: bool = False,
) -> dict[str, set[str]]:
    enum_values: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        if active_only and row.get("active", "").upper() != "TRUE":
            continue

        enum_values[row["enum_group"]].add(row["enum_value"])

    return dict(enum_values)


def validate_metrics(
    metrics: list[dict[str, str]],
    enum_values: dict[str, set[str]],
    result: ValidationResult,
) -> dict[str, dict[str, str]]:
    metric_by_id: dict[str, dict[str, str]] = {}

    allowed_polarity = enum_values.get("METRIC_POLARITY", set())
    allowed_display_modes = enum_values.get("METRIC_DISPLAY_MODE", set())

    for row in metrics:
        metric_id = row["metric_id"]
        metric_by_id[metric_id] = row

        minimum = parse_int("metrics", row, "internal_min", result)
        maximum = parse_int("metrics", row, "internal_max", result)
        default_value = parse_int("metrics", row, "default_value", result)

        if minimum is not None and maximum is not None and minimum > maximum:
            result.error(
                f"[metrics] Line {row['_line_number']}: internal_min ({minimum}) "
                f"cannot exceed internal_max ({maximum}) for {metric_id}"
            )

        if (
            minimum is not None
            and maximum is not None
            and default_value is not None
            and not minimum <= default_value <= maximum
        ):
            result.error(
                f"[metrics] Line {row['_line_number']}: default_value "
                f"({default_value}) is outside [{minimum}, {maximum}] for {metric_id}"
            )

        polarity = row["polarity"]
        if polarity not in allowed_polarity:
            result.error(
                f"[metrics] Line {row['_line_number']}: polarity '{polarity}' "
                "does not exist in active enum_catalog METRIC_POLARITY"
            )

        display_mode = row["ui_display_mode"]
        if display_mode not in allowed_display_modes:
            result.error(
                f"[metrics] Line {row['_line_number']}: ui_display_mode "
                f"'{display_mode}' does not exist in active enum_catalog "
                "METRIC_DISPLAY_MODE"
            )

    return metric_by_id


def validate_metric_tiers(
    tiers: list[dict[str, str]],
    metrics_by_id: dict[str, dict[str, str]],
    flavor_text_ids: set[str],
    result: ValidationResult,
) -> None:
    tiers_by_metric: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in tiers:
        metric_id = row["metric_id"]

        if metric_id not in metrics_by_id:
            result.error(
                f"[metric_tiers] Line {row['_line_number']}: metric_id '{metric_id}' "
                "does not exist in metrics.csv"
            )

        flavor_text_id = row["flavor_text_id"]
        if flavor_text_id not in flavor_text_ids:
            result.error(
                f"[metric_tiers] Line {row['_line_number']}: flavor_text_id "
                f"'{flavor_text_id}' does not exist in flavor_text.csv"
            )

        minimum = parse_int("metric_tiers", row, "min_inclusive", result)
        maximum = parse_int("metric_tiers", row, "max_inclusive", result)

        if minimum is not None and maximum is not None and minimum > maximum:
            result.error(
                f"[metric_tiers] Line {row['_line_number']}: min_inclusive "
                f"({minimum}) cannot exceed max_inclusive ({maximum})"
            )

        tiers_by_metric[metric_id].append(row)

    validate_sort_order("metric_tiers", tiers, result)

    for metric_id, metric_row in metrics_by_id.items():
        metric_tiers = tiers_by_metric.get(metric_id, [])

        if not metric_tiers:
            result.error(f"[metric_tiers] No tiers exist for metric '{metric_id}'")
            continue

        parsed_tiers: list[tuple[int, int, int, dict[str, str]]] = []

        for row in metric_tiers:
            minimum = parse_int("metric_tiers", row, "min_inclusive", result)
            maximum = parse_int("metric_tiers", row, "max_inclusive", result)
            sort_order = parse_int("metric_tiers", row, "sort_order", result)

            if minimum is None or maximum is None or sort_order is None:
                continue

            parsed_tiers.append((minimum, maximum, sort_order, row))

        parsed_tiers.sort(key=lambda item: (item[0], item[1], item[2]))

        metric_minimum = parse_int("metrics", metric_row, "internal_min", result)
        metric_maximum = parse_int("metrics", metric_row, "internal_max", result)

        if metric_minimum is None or metric_maximum is None or not parsed_tiers:
            continue

        first_minimum = parsed_tiers[0][0]
        if first_minimum != metric_minimum:
            result.error(
                f"[metric_tiers] Metric '{metric_id}' begins at {first_minimum}, "
                f"but metrics.csv defines internal_min {metric_minimum}"
            )

        expected_next_minimum = metric_minimum

        for minimum, maximum, _, row in parsed_tiers:
            if minimum < expected_next_minimum:
                result.error(
                    f"[metric_tiers] Line {row['_line_number']}: tier range "
                    f"[{minimum}, {maximum}] overlaps or starts before the "
                    f"expected next value {expected_next_minimum} for {metric_id}"
                )
            elif minimum > expected_next_minimum:
                result.error(
                    f"[metric_tiers] Line {row['_line_number']}: tier range "
                    f"[{minimum}, {maximum}] leaves a gap after "
                    f"{expected_next_minimum - 1} for {metric_id}"
                )

            expected_next_minimum = max(expected_next_minimum, maximum + 1)

        final_maximum = parsed_tiers[-1][1]
        if final_maximum != metric_maximum:
            result.error(
                f"[metric_tiers] Metric '{metric_id}' ends at {final_maximum}, "
                f"but metrics.csv defines internal_max {metric_maximum}"
            )


def validate_facilities(
    facilities: list[dict[str, str]],
    track_ids: set[str],
    enum_values: dict[str, set[str]],
    result: ValidationResult,
) -> dict[str, dict[str, str]]:
    facility_by_id: dict[str, dict[str, str]] = {}
    allowed_tiers = enum_values.get("FACILITY_TIER", set())

    for row in facilities:
        facility_id = row["facility_id"]
        facility_by_id[facility_id] = row

        track_id = row["track_id"]
        tier_id = row["initial_tier_id"]
        personnel_capacity = parse_int("facilities", row, "personnel_capacity", result)

        if track_id not in track_ids:
            result.error(
                f"[facilities] Line {row['_line_number']}: track_id '{track_id}' "
                "does not exist in active department_tracks.csv"
            )

        if tier_id not in allowed_tiers:
            result.error(
                f"[facilities] Line {row['_line_number']}: initial_tier_id "
                f"'{tier_id}' does not exist in active enum_catalog FACILITY_TIER"
            )

        if personnel_capacity is not None and personnel_capacity < 1:
            result.error(
                f"[facilities] Line {row['_line_number']}: personnel_capacity "
                "must be at least 1"
            )

    return facility_by_id


def validate_catalog_sort_orders(
    table_name: str,
    rows: list[dict[str, str]],
    result: ValidationResult,
) -> None:
    minimum_allowed = 0 if table_name == "enum_catalog" else 1

    for row in rows:
        value = parse_int(table_name, row, "sort_order", result)

        if value is not None and value < minimum_allowed:
            result.error(
                f"[{table_name}] Line {row['_line_number']}: sort_order must be "
                f"at least {minimum_allowed}"
            )


def validate_facility_capabilities(
    rows: list[dict[str, str]],
    active_facility_ids: set[str],
    active_capability_ids: set[str],
    facility_by_id: dict[str, dict[str, str]],
    enum_values: dict[str, set[str]],
    result: ValidationResult,
) -> dict[tuple[str, str], dict[str, str]]:
    allowed_tiers = enum_values.get("FACILITY_TIER", set())
    active_pairs: dict[tuple[str, str], dict[str, str]] = {}

    for row in rows:
        facility_id = row["facility_id"]
        capability_id = row["capability_id"]
        maximum = parse_int(
            "facility_capabilities",
            row,
            "max_concurrent_personnel",
            result,
        )

        if facility_id not in active_facility_ids:
            result.error(
                f"[facility_capabilities] Line {row['_line_number']}: facility_id "
                f"'{facility_id}' does not exist in active facilities.csv"
            )

        if capability_id not in active_capability_ids:
            result.error(
                f"[facility_capabilities] Line {row['_line_number']}: capability_id "
                f"'{capability_id}' does not exist in active capabilities.csv"
            )

        if row["initial_tier_id"] not in allowed_tiers:
            result.error(
                f"[facility_capabilities] Line {row['_line_number']}: "
                f"initial_tier_id '{row['initial_tier_id']}' does not exist in "
                "active enum_catalog FACILITY_TIER"
            )

        if maximum is not None and maximum < 1:
            result.error(
                f"[facility_capabilities] Line {row['_line_number']}: "
                "max_concurrent_personnel must be at least 1"
            )

        parent = facility_by_id.get(facility_id)
        if parent is not None and maximum is not None:
            capacity = parse_int("facilities", parent, "personnel_capacity", result)
            if capacity is not None and maximum > capacity:
                result.error(
                    f"[facility_capabilities] Line {row['_line_number']}: "
                    f"max_concurrent_personnel ({maximum}) exceeds facility "
                    f"personnel_capacity ({capacity}) for '{facility_id}'"
                )

        if row.get("active", "").upper() == "TRUE":
            active_pairs[(facility_id, capability_id)] = row

    validate_sort_order("facility_capabilities", rows, result)
    return active_pairs


def validate_staffing_range(
    table_name: str,
    row: dict[str, str],
    result: ValidationResult,
) -> None:
    minimum = parse_int(table_name, row, "min_contributors", result)
    preferred = parse_int(table_name, row, "preferred_contributors", result)
    maximum = parse_int(table_name, row, "max_contributors", result)

    if (
        minimum is not None
        and preferred is not None
        and maximum is not None
        and not 0 <= minimum <= preferred <= maximum
    ):
        result.error(
            f"[{table_name}] Line {row['_line_number']}: contributor counts "
            "must satisfy 0 <= min_contributors <= preferred_contributors "
            "<= max_contributors"
        )


def validate_capability_staffing_rules(
    rows: list[dict[str, str]],
    active_capability_ids: set[str],
    active_qualification_ids: set[str],
    result: ValidationResult,
) -> dict[tuple[str, str], dict[str, str]]:
    active_rules: dict[tuple[str, str], dict[str, str]] = {}

    for row in rows:
        capability_id = row["capability_id"]
        qualification_id = row["qualification_id"]

        if capability_id not in active_capability_ids:
            result.error(
                f"[capability_staffing_rules] Line {row['_line_number']}: "
                f"capability_id '{capability_id}' does not exist in active "
                "capabilities.csv"
            )

        if qualification_id not in active_qualification_ids:
            result.error(
                f"[capability_staffing_rules] Line {row['_line_number']}: "
                f"qualification_id '{qualification_id}' does not exist in active "
                "qualification_catalog.csv"
            )

        validate_staffing_range("capability_staffing_rules", row, result)

        if row.get("active", "").upper() == "TRUE":
            active_rules[(capability_id, qualification_id)] = row

    validate_sort_order("capability_staffing_rules", rows, result)

    active_rules_by_capability: dict[str, int] = defaultdict(int)
    for capability_id, _ in active_rules:
        active_rules_by_capability[capability_id] += 1

    for capability_id in active_capability_ids:
        if active_rules_by_capability.get(capability_id, 0) == 0:
            result.error(
                f"[capability_staffing_rules] No active staffing rule exists "
                f"for active capability '{capability_id}'"
            )

    return active_rules


def validate_facility_capability_staffing_overrides(
    rows: list[dict[str, str]],
    active_facility_capabilities: dict[tuple[str, str], dict[str, str]],
    active_qualification_ids: set[str],
    active_global_rules: dict[tuple[str, str], dict[str, str]],
    result: ValidationResult,
) -> None:
    for row in rows:
        facility_id = row["facility_id"]
        capability_id = row["capability_id"]
        qualification_id = row["qualification_id"]

        if (facility_id, capability_id) not in active_facility_capabilities:
            result.error(
                f"[facility_capability_staffing_overrides] Line "
                f"{row['_line_number']}: facility_id/capability_id pair "
                f"'{facility_id}/{capability_id}' does not exist in active "
                "facility_capabilities.csv"
            )

        if qualification_id not in active_qualification_ids:
            result.error(
                f"[facility_capability_staffing_overrides] Line "
                f"{row['_line_number']}: qualification_id '{qualification_id}' "
                "does not exist in active qualification_catalog.csv"
            )

        if (capability_id, qualification_id) not in active_global_rules:
            result.error(
                f"[facility_capability_staffing_overrides] Line "
                f"{row['_line_number']}: no active global staffing rule exists "
                f"for '{capability_id}/{qualification_id}'"
            )

        validate_staffing_range(
            "facility_capability_staffing_overrides",
            row,
            result,
        )

    validate_sort_order(
        "facility_capability_staffing_overrides",
        rows,
        result,
    )


def validate_task_templates(
    rows: list[dict[str, str]],
    active_capability_ids: set[str],
    active_facility_capabilities: dict[tuple[str, str], dict[str, str]],
    enum_values: dict[str, set[str]],
    result: ValidationResult,
) -> None:
    allowed_priorities = enum_values.get("TASK_PRIORITY", set())
    installed_capability_ids = {
        capability_id
        for _, capability_id in active_facility_capabilities
    }

    for row in rows:
        capability_id = row["capability_id"]
        priority = row["priority"]

        if capability_id not in active_capability_ids:
            result.error(
                f"[task_templates] Line {row['_line_number']}: capability_id "
                f"'{capability_id}' does not exist in active capabilities.csv"
            )

        if priority not in allowed_priorities:
            result.error(
                f"[task_templates] Line {row['_line_number']}: priority "
                f"'{priority}' does not exist in active enum_catalog TASK_PRIORITY"
            )

        target_effort = parse_int(
            "task_templates",
            row,
            "default_target_effort_minutes",
            result,
        )
        deadline = parse_int(
            "task_templates",
            row,
            "default_deadline_minutes",
            result,
        )

        if target_effort is not None and target_effort <= 0:
            result.error(
                f"[task_templates] Line {row['_line_number']}: "
                "default_target_effort_minutes must be greater than 0"
            )

        if deadline is not None and deadline <= 0:
            result.error(
                f"[task_templates] Line {row['_line_number']}: "
                "default_deadline_minutes must be greater than 0"
            )

        parse_bool("task_templates", row, "auto_allocate", result)

        if (
            row.get("active", "").upper() == "TRUE"
            and capability_id in active_capability_ids
            and capability_id not in installed_capability_ids
        ):
            result.error(
                f"[task_templates] Line {row['_line_number']}: active capability "
                f"'{capability_id}' has no active Facility Capability installation"
            )

    validate_sort_order("task_templates", rows, result)


def warn_on_facility_capacity_overcommit(
    facilities: list[dict[str, str]],
    facility_capabilities: list[dict[str, str]],
    result: ValidationResult,
) -> None:
    capacity_by_facility: dict[str, int] = {}

    for row in facilities:
        if row.get("active", "").upper() != "TRUE":
            continue

        capacity = parse_int("facilities", row, "personnel_capacity", result)
        if capacity is not None:
            capacity_by_facility[row["facility_id"]] = capacity

    concurrent_total: dict[str, int] = defaultdict(int)

    for row in facility_capabilities:
        if row.get("active", "").upper() != "TRUE":
            continue

        maximum = parse_int(
            "facility_capabilities",
            row,
            "max_concurrent_personnel",
            result,
        )
        if maximum is not None:
            concurrent_total[row["facility_id"]] += maximum

    for facility_id, total in sorted(concurrent_total.items()):
        capacity = capacity_by_facility.get(facility_id)
        if capacity is not None and total > capacity:
            result.warning(
                f"[facility_capabilities] Active Facility Capability maximum "
                f"concurrency totals {total} for '{facility_id}', exceeding "
                f"facility personnel_capacity {capacity}. This is permitted as "
                "a strategic allocation tradeoff."
            )


def validate_project(project_root: Path) -> ValidationResult:
    result = ValidationResult()
    source_directory = project_root / "data_authoring" / "source"
    loaded_tables: dict[str, list[dict[str, str]]] = {}

    for table_name, specification in TABLE_SPECS.items():
        path = source_directory / specification["filename"]
        rows = load_csv(
            path,
            specification["required_columns"],
            table_name,
            result,
        )
        loaded_tables[table_name] = rows
        validate_keys(table_name, rows, specification["key_columns"], result)
        validate_active_values(table_name, rows, result)

    for table_name in (
        "enum_catalog",
        "department_tracks",
        "qualification_catalog",
        "capabilities",
    ):
        validate_catalog_sort_orders(table_name, loaded_tables[table_name], result)

    enum_values = build_enum_index(
        loaded_tables["enum_catalog"],
        active_only=True,
    )
    track_ids = build_id_set(
        loaded_tables["department_tracks"],
        "track_id",
        active_only=True,
    )
    flavor_text_ids = build_id_set(
        loaded_tables["flavor_text"],
        "flavor_text_id",
        active_only=True,
    )
    active_facility_ids = build_id_set(
        loaded_tables["facilities"],
        "facility_id",
        active_only=True,
    )
    active_qualification_ids = build_id_set(
        loaded_tables["qualification_catalog"],
        "qualification_id",
        active_only=True,
    )
    active_capability_ids = build_id_set(
        loaded_tables["capabilities"],
        "capability_id",
        active_only=True,
    )

    metrics_by_id = validate_metrics(
        loaded_tables["metrics"],
        enum_values,
        result,
    )
    validate_metric_tiers(
        loaded_tables["metric_tiers"],
        metrics_by_id,
        flavor_text_ids,
        result,
    )
    facility_by_id = validate_facilities(
        loaded_tables["facilities"],
        track_ids,
        enum_values,
        result,
    )
    active_facility_capabilities = validate_facility_capabilities(
        loaded_tables["facility_capabilities"],
        active_facility_ids,
        active_capability_ids,
        facility_by_id,
        enum_values,
        result,
    )
    active_global_rules = validate_capability_staffing_rules(
        loaded_tables["capability_staffing_rules"],
        active_capability_ids,
        active_qualification_ids,
        result,
    )
    validate_facility_capability_staffing_overrides(
        loaded_tables["facility_capability_staffing_overrides"],
        active_facility_capabilities,
        active_qualification_ids,
        active_global_rules,
        result,
    )
    validate_task_templates(
        loaded_tables["task_templates"],
        active_capability_ids,
        active_facility_capabilities,
        enum_values,
        result,
    )
    warn_on_facility_capacity_overcommit(
        loaded_tables["facilities"],
        loaded_tables["facility_capabilities"],
        result,
    )

    return result


def write_report(project_root: Path, result: ValidationResult) -> Path:
    report_directory = project_root / "generated" / "reports"
    report_directory.mkdir(parents=True, exist_ok=True)

    report_path = report_directory / "content_validation_report.json"

    report = {
        "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "projectRoot": str(project_root),
        "valid": result.valid,
        "errorCount": len(result.errors),
        "warningCount": len(result.warnings),
        "stats": result.stats,
        "errors": result.errors,
        "warnings": result.warnings,
    }

    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    return report_path


def print_result(project_root: Path, result: ValidationResult, report_path: Path) -> None:
    print()
    print("=" * 72)
    print("DoDA Content Workbench Validation")
    print("=" * 72)
    print(f"Project root: {project_root}")
    print()

    print("Loaded rows:")
    for table_name in sorted(result.stats):
        print(f"  {table_name}: {result.stats[table_name]}")

    print()

    if result.warnings:
        print(f"Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  WARNING: {warning}")
        print()

    if result.errors:
        print(f"Validation failed with {len(result.errors)} error(s):")
        for error in result.errors:
            print(f"  ERROR: {error}")
    else:
        print("Validation passed with zero errors.")

    print()
    print(f"Report written to: {report_path}")
    print("=" * 72)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doda_content_workbench",
        description="Validate DoDA authored content.",
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Path to the doda-core project root. Defaults to auto-detection.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "validate",
        help="Validate authored CSV source data and write a JSON report.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    arguments = parser.parse_args()

    try:
        project_root = (
            arguments.root.resolve()
            if arguments.root is not None
            else find_project_root(Path.cwd())
        )
    except FileNotFoundError as error:
        parser.error(str(error))
        return 2

    if arguments.command == "validate":
        result = validate_project(project_root)
        report_path = write_report(project_root, result)
        print_result(project_root, result, report_path)
        return 0 if result.valid else 1

    parser.error(f"Unsupported command: {arguments.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
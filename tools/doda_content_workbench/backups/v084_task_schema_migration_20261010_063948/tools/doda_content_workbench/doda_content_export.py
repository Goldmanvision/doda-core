#!/usr/bin/env python3
r"""
DoDA Content Workbench - content exporter and PK3 builder.

This script performs a safe, data-only export pipeline:

1. Runs the CSV validator.
2. Loads validated authoring CSV files.
3. Creates normalized JSON content data.
4. Creates a future UZDoom LANGUAGE fragment.
5. Creates a source/output hash manifest.
6. Builds a standalone PK3 overlay archive.

This version deliberately does not edit MAPINFO, GAMEINFO, LANGUAGE, zscript.txt,
maps, native C++, ZScript, or the doda-core package.

Usage:
    python tools/doda_content_workbench/doda_content_export.py
    python tools/doda_content_workbench/doda_content_export.py --root C:/Dev/uzdoom_src/doda-core
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_VERSION = "0.1.1"
SCHEMA_VERSION = 2

TABLE_FILES = {
    "enum_catalog": "enum_catalog.csv",
    "department_tracks": "department_tracks.csv",
    "metrics": "metrics.csv",
    "metric_tiers": "metric_tiers.csv",
    "facilities": "facilities.csv",
    "flavor_text": "flavor_text.csv",
    "qualification_catalog": "qualification_catalog.csv",
    "capabilities": "capabilities.csv",
    "facility_capabilities": "facility_capabilities.csv",
    "capability_staffing_rules": "capability_staffing_rules.csv",
    "facility_capability_staffing_overrides": (
        "facility_capability_staffing_overrides.csv"
    ),
    "task_templates": "task_templates.csv",
}

INTEGER_COLUMNS = {
    "enum_catalog": {"sort_order"},
    "department_tracks": {"sort_order"},
    "metrics": {"internal_min", "internal_max", "default_value"},
    "metric_tiers": {"min_inclusive", "max_inclusive", "sort_order"},
    "facilities": {"personnel_capacity"},
    "qualification_catalog": {"sort_order"},
    "capabilities": {"sort_order"},
    "facility_capabilities": {
        "max_concurrent_personnel",
        "sort_order",
    },
    "capability_staffing_rules": {
        "min_contributors",
        "preferred_contributors",
        "max_contributors",
        "sort_order",
    },
    "facility_capability_staffing_overrides": {
        "min_contributors",
        "preferred_contributors",
        "max_contributors",
        "sort_order",
    },
    "task_templates": {
        "default_target_effort_minutes",
        "default_deadline_minutes",
        "sort_order",
    },
}

BOOLEAN_COLUMNS = {
    "enum_catalog": {"active"},
    "department_tracks": {"active"},
    "metrics": {"active"},
    "facilities": {"active"},
    "flavor_text": {"active"},
    "qualification_catalog": {"active"},
    "capabilities": {"active"},
    "facility_capabilities": {"active"},
    "capability_staffing_rules": {"active"},
    "facility_capability_staffing_overrides": {"active"},
    "task_templates": {"auto_allocate", "active"},
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
        "Unable to locate the DoDA project root. Use --root to provide it explicitly."
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def run_validator(project_root: Path) -> None:
    validator_path = (
        project_root
        / "tools"
        / "doda_content_workbench"
        / "doda_content_workbench.py"
    )

    if not validator_path.is_file():
        raise FileNotFoundError(
            f"Validator script was not found: {validator_path}"
        )

    command = [
        sys.executable,
        str(validator_path),
        "--root",
        str(project_root),
        "validate",
    ]

    print("Running source-data validation...")
    completed = subprocess.run(command, cwd=project_root)

    if completed.returncode != 0:
        raise RuntimeError(
            "Source-data validation failed. Export was not attempted. "
            "Correct CSV source data first, then run export again."
        )


def normalize_value(table_name: str, column_name: str, value: str) -> Any:
    normalized = value.strip()

    if column_name in INTEGER_COLUMNS.get(table_name, set()):
        return int(normalized)

    if column_name in BOOLEAN_COLUMNS.get(table_name, set()):
        return normalized.upper() == "TRUE"

    return normalized


def load_table(
    project_root: Path,
    table_name: str,
    filename: str,
) -> list[dict[str, Any]]:
    path = project_root / "data_authoring" / "source" / filename

    with path.open("r", encoding="utf-8-sig", newline="") as source_file:
        reader = csv.DictReader(source_file)
        rows: list[dict[str, Any]] = []

        for raw_row in reader:
            if raw_row is None:
                continue

            if not any((value or "").strip() for value in raw_row.values()):
                continue

            row: dict[str, Any] = {}

            for column_name, raw_value in raw_row.items():
                if column_name is None:
                    continue

                row[column_name.strip()] = normalize_value(
                    table_name,
                    column_name.strip(),
                    raw_value or "",
                )

            rows.append(row)

        return rows


def escape_language_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
    )


def language_key_from_flavor_id(flavor_text_id: str) -> str:
    safe_key = re.sub(r"[^A-Za-z0-9_]", "_", flavor_text_id.upper())
    return f"DODA_{safe_key}"


def build_language_fragment(flavor_rows: list[dict[str, Any]]) -> str:
    lines = [
        "// GENERATED FILE - DO NOT EDIT BY HAND",
        "// Source: data_authoring/source/flavor_text.csv",
        "// Generated by DoDA Content Workbench.",
        "",
        "[default]",
        "",
    ]

    for row in sorted(flavor_rows, key=lambda item: item["flavor_text_id"]):
        base_key = language_key_from_flavor_id(str(row["flavor_text_id"]))
        title = escape_language_text(str(row["title"]))
        body = escape_language_text(str(row["body"]))

        lines.append(f'{base_key}_TITLE = "{title}";')
        lines.append(f'{base_key}_BODY = "{body}";')
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_pk3(
    pk3_path: Path,
    department_json_path: Path,
    language_path: Path,
    manifest_path: Path,
) -> list[str]:
    pk3_path.parent.mkdir(parents=True, exist_ok=True)

    archive_entries = {
        "data/department_content.json": department_json_path,
        "language/DODA_GENERATED_LANGUAGE.txt": language_path,
        "manifest/content_manifest.json": manifest_path,
    }

    package_readme = (
        "DoDA Generated Content Overlay\n"
        "==============================\n"
        "\n"
        "This PK3 was generated by DoDA Content Workbench.\n"
        "\n"
        "It is currently a data-packaging proof. The archive contains generated\n"
        "department data, a future LANGUAGE fragment, and a build manifest.\n"
        "It does not yet add active runtime behavior because doda-core has not\n"
        "yet been given a native data loader or static include seam for these\n"
        "generated resources.\n"
    )

    temporary_path = pk3_path.with_suffix(".pk3.tmp")

    if temporary_path.exists():
        temporary_path.unlink()

    with zipfile.ZipFile(
        temporary_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        archive.writestr("README.txt", package_readme)

        for archive_name, source_path in archive_entries.items():
            archive.write(source_path, archive_name)

    if pk3_path.exists():
        pk3_path.unlink()

    temporary_path.replace(pk3_path)

    with zipfile.ZipFile(pk3_path, mode="r") as archive:
        return sorted(archive.namelist())


def export_content(project_root: Path) -> tuple[dict[str, Path], list[str]]:
    run_validator(project_root)

    print()
    print("Loading validated authoring CSV files...")

    tables: dict[str, list[dict[str, Any]]] = {}

    for table_name, filename in TABLE_FILES.items():
        table_rows = load_table(project_root, table_name, filename)
        tables[table_name] = table_rows
        print(f"  {table_name}: {len(table_rows)} row(s)")

    generated_at = datetime.now(timezone.utc).isoformat()

    department_payload = {
        "schemaVersion": SCHEMA_VERSION,
        "toolVersion": TOOL_VERSION,
        "generatedAtUtc": generated_at,
        "tables": tables,
    }

    generated_directory = project_root / "generated"
    department_json_path = generated_directory / "data" / "department_content.json"
    language_path = (
        generated_directory
        / "language"
        / "DODA_GENERATED_LANGUAGE.txt"
    )
    manifest_path = (
        generated_directory
        / "manifest"
        / "content_manifest.json"
    )
    pk3_path = project_root / "build" / "doda-generated-content.pk3"

    write_json(department_json_path, department_payload)

    language_fragment = build_language_fragment(tables["flavor_text"])
    write_text(language_path, language_fragment)

    source_hashes = {
        filename: sha256_file(
            project_root / "data_authoring" / "source" / filename
        )
        for filename in TABLE_FILES.values()
    }

    output_hashes = {
        "generated/data/department_content.json": sha256_file(department_json_path),
        "generated/language/DODA_GENERATED_LANGUAGE.txt": sha256_file(language_path),
    }

    manifest_payload = {
        "schemaVersion": SCHEMA_VERSION,
        "toolVersion": TOOL_VERSION,
        "generatedAtUtc": generated_at,
        "projectRoot": str(project_root),
        "sourceFiles": source_hashes,
        "outputFiles": output_hashes,
        "tableRowCounts": {
            table_name: len(rows)
            for table_name, rows in tables.items()
        },
        "runtimeStatus": {
            "nativeLoaderAvailable": False,
            "mapinfoIntegrationEnabled": False,
            "languageIntegrationEnabled": False,
            "zscriptIntegrationEnabled": False,
            "notes": [
                "This is a generated content overlay proof.",
                "The PK3 is not yet active runtime data.",
                "Do not manually edit generated output files.",
            ],
        },
    }

    write_json(manifest_path, manifest_payload)

    archive_entries = build_pk3(
        pk3_path,
        department_json_path,
        language_path,
        manifest_path,
    )

    outputs = {
        "department_json": department_json_path,
        "language_fragment": language_path,
        "manifest": manifest_path,
        "pk3_overlay": pk3_path,
    }

    return outputs, archive_entries


def print_export_result(
    project_root: Path,
    outputs: dict[str, Path],
    archive_entries: list[str],
) -> None:
    print()
    print("=" * 72)
    print("DoDA Content Workbench Export")
    print("=" * 72)
    print(f"Project root: {project_root}")
    print()

    print("Generated outputs:")
    for output_name, output_path in outputs.items():
        print(f"  {output_name}: {output_path}")

    print()
    print("PK3 archive entries:")
    for entry in archive_entries:
        print(f"  {entry}")

    print()
    print(
        "Export completed successfully. This PK3 is a safe data overlay proof "
        "and does not yet alter live UZDoom behavior."
    )
    print("=" * 72)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doda_content_export",
        description="Export validated DoDA authoring content and build a PK3 overlay.",
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Path to doda-core. Defaults to automatic project-root discovery.",
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

        outputs, archive_entries = export_content(project_root)
        print_export_result(project_root, outputs, archive_entries)
        return 0

    except (
        FileNotFoundError,
        RuntimeError,
        ValueError,
        OSError,
        zipfile.BadZipFile,
    ) as error:
        print()
        print(f"EXPORT FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
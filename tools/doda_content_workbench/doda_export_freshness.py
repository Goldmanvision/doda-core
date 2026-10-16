"""Read-only saved-source/export/catalog freshness. Never generates output."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

import doda_content_export as exporter
import doda_zscript_catalog as zscript_catalog

CURRENT = "CURRENT"
STALE = "STALE"
MISSING = "MISSING"
UNVERIFIED = "UNVERIFIED"
MANIFEST = Path("generated/manifest/content_manifest.json")
DEPARTMENT_JSON = Path("generated/data/department_content.json")


@dataclass(frozen=True)
class Stage:
    state: str
    reason: str
    next_step: str = ""


@dataclass(frozen=True)
class FreshnessReport:
    department: Stage
    catalog: Stage

    @property
    def current(self):
        return self.department.state == CURRENT and self.catalog.state == CURRENT

    @property
    def summary(self):
        return (
            f"Department export: {self.department.state} | "
            f"Catalog vs JSON: {self.catalog.state}"
        )

    @property
    def warnings(self):
        return tuple(
            f"{name} {stage.state}: {stage.reason} {stage.next_step}".strip()
            for name, stage in (
                ("Department export", self.department),
                ("ZScript catalog vs JSON", self.catalog),
            )
            if stage.state != CURRENT
        )


class _ChangedDuringCheck(ValueError):
    pass


class _Reads:
    def __init__(self):
        self.hashes = {}

    def read(self, path):
        path = Path(path).resolve()
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            digest = None
            if path in self.hashes and self.hashes[path] is not None:
                raise _ChangedDuringCheck("An inspected file disappeared.")
            self.hashes[path] = digest
            raise
        digest = hashlib.sha256(data).hexdigest()
        if path in self.hashes and self.hashes[path] != digest:
            raise _ChangedDuringCheck("An inspected file changed.")
        self.hashes[path] = digest
        return data

    def verify(self):
        for path, expected in self.hashes.items():
            try:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
            except FileNotFoundError:
                actual = None
            if actual != expected:
                raise _ChangedDuringCheck("Files changed during freshness inspection.")


def _json(reads, path):
    return json.loads(reads.read(path).decode("utf-8-sig"))


def _recorded_hash(mapping, key):
    value = mapping.get(key)
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise ValueError("Missing or malformed recorded hash: " + key)
    return value.lower()


def _department(root, reads):
    try:
        manifest = _json(reads, root / MANIFEST)
        if not isinstance(manifest, dict):
            raise ValueError("Content manifest must be a JSON object.")
        if manifest.get("schemaVersion") != exporter.SCHEMA_VERSION:
            raise ValueError("Content manifest schema is missing or unsupported.")
        sources = manifest.get("sourceFiles")
        outputs = manifest.get("outputFiles")
        if not isinstance(sources, dict) or not isinstance(outputs, dict):
            raise ValueError("Content manifest sourceFiles/outputFiles must be objects.")
        expected_output = _recorded_hash(outputs, DEPARTMENT_JSON.as_posix())
        changed = []
        for filename in sorted(set(exporter.TABLE_FILES.values())):
            expected = _recorded_hash(sources, filename)
            actual = hashlib.sha256(
                reads.read(root / "data_authoring/source" / filename)
            ).hexdigest()
            if actual != expected:
                changed.append(filename)
        raw = reads.read(root / DEPARTMENT_JSON)
        department = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(department, dict) or department.get("schemaVersion") != exporter.SCHEMA_VERSION:
            raise ValueError("Department JSON schema is missing or unsupported.")
        tables = department.get("tables")
        if not isinstance(tables, dict) or any(
            not isinstance(tables.get(name), list) for name in exporter.TABLE_FILES
        ):
            raise ValueError("Department JSON is missing expected exported tables.")
        reasons = []
        if changed:
            reasons.append("Saved CSV hashes changed: " + ", ".join(changed) + ".")
        if hashlib.sha256(raw).hexdigest() != expected_output:
            reasons.append("Department JSON differs from its recorded output hash.")
        if reasons:
            return Stage(STALE, " ".join(reasons), "Use Export All to refresh saved department content.")
        return Stage(CURRENT, "Saved CSV and department JSON hashes match the content manifest.")
    except _ChangedDuringCheck:
        raise
    except FileNotFoundError as error:
        return Stage(MISSING, "Required source/export file is missing: " + Path(error.filename).name,
                     "Check the missing file; use Export All when saved source is available.")
    except Exception as error:
        return Stage(UNVERIFIED, f"{type(error).__name__}: {error}",
                     "Check export evidence and file access; use Export All to rebuild when appropriate.")


def _catalog(root, reads):
    try:
        for relative in (
            zscript_catalog.NETWORK_JSON, zscript_catalog.EQUIPMENT_JSON,
            zscript_catalog.DEPARTMENT_JSON, zscript_catalog.OUTPUT_ZS,
        ):
            reads.read(root / relative)
        if zscript_catalog.is_current(root):
            return Stage(CURRENT, "Generated ZScript matches existing JSON inputs; this alone does not verify saved CSVs.")
        return Stage(STALE, "Generated ZScript differs from existing JSON inputs.",
                     "Regenerate the catalog from current exports; use Export All if the department export is stale.")
    except _ChangedDuringCheck:
        raise
    except FileNotFoundError as error:
        return Stage(MISSING, "Required catalog/input file is missing: " + Path(error.filename).name,
                     "Use the existing export/catalog generation workflow.")
    except Exception as error:
        return Stage(UNVERIFIED, f"{type(error).__name__}: {error}",
                     "Check catalog inputs before regeneration.")


def inspect_freshness(project_root):
    reads = _Reads()
    try:
        root = Path(project_root).resolve()
        department = _department(root, reads)
        catalog = _catalog(root, reads)
        reads.verify()
        return FreshnessReport(department, catalog)
    except Exception as error:
        stage = Stage(UNVERIFIED, f"{type(error).__name__}: {error}",
                      "Retry the read-only check after files stop changing or file access is restored.")
        return FreshnessReport(stage, stage)
import hashlib
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
work = root / "tools/doda_content_workbench"
src = root / "data_authoring/source"
doc = root / "docs/workbench/spec/DESIGN_DECISIONS_2026-10-08.md"
history = root / "docs/workbench/history/Progression_Identity_Foundations_2026-10-08.md"
module = work / "doda_progression_identity_rules.py"
test = work / "tests/test_progression_identity_rules.py"

def stop(message):
    print("STOP: " + message + " No project files were modified.", flush=True)
    sys.exit(1)

csv_headers = {
    "upgrades.csv": "upgrade_id,display_name,track_id,source_reference,description,sort_order,active",
    "plot_milestones.csv": "milestone_id,display_name,source_reference,description,sort_order,active",
    "plot_items.csv": "plot_item_id,display_name,source_reference,description,sort_order,active",
    "mission_tier_requirements.csv": "requirement_id,tier_id,upgrade_id,milestone_id,plot_item_id,source_reference,description,sort_order,active",
}
new_paths = [module, test, history] + [src / name for name in csv_headers]
for path in new_paths:
    if path.exists():
        stop(str(path) + " already exists.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")
if not doc.is_file():
    stop(str(doc) + " was not found.")

marker = "## Progression identity foundation - CONFIRMED (2026-10-08)"
doc_raw = doc.read_bytes()
if marker in doc_raw.decode("utf-8-sig"):
    stop("The identity foundation is already documented.")

module_text = r'''"""Progression identities and mission-tier requirements.
Authoring/export only. Campaign ownership, completion and inventory are native state.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import doda_network_rules as net

TOOL_VERSION = "0.1.0"
UPGRADES_FILE = "upgrades.csv"
MILESTONES_FILE = "plot_milestones.csv"
ITEMS_FILE = "plot_items.csv"
REQUIREMENTS_FILE = "mission_tier_requirements.csv"

COMMON_COLUMNS = ["source_reference", "description", "sort_order", "active"]
UPGRADE_COLUMNS = ["upgrade_id", "display_name", "track_id"] + COMMON_COLUMNS
MILESTONE_COLUMNS = ["milestone_id", "display_name"] + COMMON_COLUMNS
ITEM_COLUMNS = ["plot_item_id", "display_name"] + COMMON_COLUMNS
REQUIREMENT_COLUMNS = [
    "requirement_id", "tier_id", "upgrade_id", "milestone_id", "plot_item_id"
] + COMMON_COLUMNS

REFERENCE_TYPES = {
    "upgrade_id": "UPGRADE_ACQUIRED",
    "milestone_id": "MILESTONE_COMPLETED",
    "plot_item_id": "PLOT_ITEM_HELD",
}
RULES = {
    "upgradeMeaning": "PURCHASED_OR_UNLOCKED_BENEFIT_ABILITY_STATS_OR_ACCESS",
    "upgradeDefinitionIsNotEquipmentOwnership": True,
    "milestoneCheck": "COMPLETED_PERSISTENT_RECORD",
    "plotItemCheck": "CURRENTLY_HELD_AT_CAPSTONE_PURCHASE",
    "requirementsCombine": "ALL_ACTIVE_REQUIREMENTS",
    "definitionActiveIsNotCampaignAcquired": True,
    "emptyRequiredReferenceSet": "UNCONFIGURED_NOT_AUTOMATICALLY_SATISFIED",
}
OPEN_ITEMS = {
    "PID-OPEN-01": "Actual upgrade, milestone and plot-item definitions.",
    "PID-OPEN-02": "Which major upgrades and plot requirements gate Tier 6.",
    "PID-OPEN-03": "Upgrade acquisition costs, prerequisites and benefits.",
    "PID-OPEN-04": "Capstone mission definition and its stable mission reference.",
}


def _read(src, filename, columns, label, res):
    path = src / filename
    if not path.is_file():
        res.errors.append(f"[{label}] Required source file missing: {filename}")
        return []
    return net.read_table(path, columns, label, res) or []


def _external(src, filename, key, res):
    rows = _read(src, filename, [key, "active"], filename, res)
    index = {}
    for row in rows:
        value = row[key]
        ctx = f"[{filename}] Line {row['_line']}"
        if not value or value in index:
            res.errors.append(f"{ctx}: blank or duplicate {key} '{value}'")
            continue
        index[value] = net._bool(row["active"], ctx, res)
    return index


def _definitions(src, filename, columns, key, label, res, tracks=None):
    rows = _read(src, filename, columns, label, res)
    index = {}
    for row in rows:
        ctx = f"[{label}] Line {row['_line']}"
        value = row[key]
        if not value or value in index:
            res.errors.append(f"{ctx}: blank or duplicate {key} '{value}'")
            continue
        active = net._bool(row["active"], ctx, res)
        if not row["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(f"{ctx}: sort_order must be nonnegative")
        item = {
            "id": value, "displayName": row["display_name"],
            "sourceReference": row["source_reference"] or None,
            "description": row["description"], "sortOrder": order, "active": active,
        }
        if key == "upgrade_id":
            track = row["track_id"]
            if track:
                if tracks is None or track not in tracks:
                    res.errors.append(f"{ctx}: unknown track_id '{track}'")
                elif active and not tracks[track]:
                    res.errors.append(f"{ctx}: active upgrade uses inactive track '{track}'")
            item["trackId"] = track or None
        index[value] = item
    return index


def validate_identities(root, res):
    src = root / "data_authoring/source"
    tracks = None
    track_path = src / "department_tracks.csv"
    if track_path.is_file():
        tracks = _external(src, "department_tracks.csv", "track_id", res)

    upgrades = _definitions(src, UPGRADES_FILE, UPGRADE_COLUMNS,
                            "upgrade_id", "upgrades", res, tracks)
    milestones = _definitions(src, MILESTONES_FILE, MILESTONE_COLUMNS,
                              "milestone_id", "plot_milestones", res)
    items = _definitions(src, ITEMS_FILE, ITEM_COLUMNS,
                         "plot_item_id", "plot_items", res)
    rows = _read(src, REQUIREMENTS_FILE, REQUIREMENT_COLUMNS,
                 "mission_tier_requirements", res)
    tiers = _external(src, "mission_tiers.csv", "tier_id", res) if rows else {}
    catalogs = {"upgrade_id": upgrades, "milestone_id": milestones, "plot_item_id": items}
    requirements, seen, logical = [], set(), set()

    for row in rows:
        ctx = f"[mission_tier_requirements] Line {row['_line']}"
        rid = row["requirement_id"]
        if not rid or rid in seen:
            res.errors.append(f"{ctx}: blank or duplicate requirement_id '{rid}'")
            continue
        seen.add(rid)
        active = net._bool(row["active"], ctx, res)
        tier = row["tier_id"]
        if tier not in tiers:
            res.errors.append(f"{ctx}: unknown tier_id '{tier}'")
        elif active and not tiers[tier]:
            res.errors.append(f"{ctx}: active requirement uses inactive tier '{tier}'")
        references = [key for key in REFERENCE_TYPES if row[key]]
        if len(references) != 1:
            res.errors.append(f"{ctx}: exactly one upgrade, milestone or plot-item reference is required")
            continue
        field = references[0]
        target_id = row[field]
        target = catalogs[field].get(target_id)
        if target is None:
            res.errors.append(f"{ctx}: unknown {field} '{target_id}'")
        elif active and not target["active"]:
            res.errors.append(f"{ctx}: active requirement uses inactive target '{target_id}'")
        combination = (tier, field, target_id)
        if combination in logical:
            res.errors.append(f"{ctx}: duplicate logical requirement for '{target_id}' in '{tier}'")
        logical.add(combination)
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(f"{ctx}: sort_order must be nonnegative")
        requirements.append({
            "requirementId": rid, "tierId": tier,
            "requirementType": REFERENCE_TYPES[field], "referenceId": target_id,
            "sourceReference": row["source_reference"] or None,
            "description": row["description"], "sortOrder": order, "active": active,
        })

    def ordered(index):
        return sorted(index.values(), key=lambda item: (item["sortOrder"] or 0, item["id"]))

    active_final = [row for row in requirements if row["active"] and row["tierId"] == "TIER_6"]
    missing = []
    if not any(row["requirementType"] == "UPGRADE_ACQUIRED" for row in active_final):
        missing.append("REQUIRED_UPGRADE_REFERENCES")
    if not any(row["requirementType"] in ("MILESTONE_COMPLETED", "PLOT_ITEM_HELD")
               for row in active_final):
        missing.append("REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES")
    return {
        "upgrades": ordered(upgrades),
        "plotMilestones": ordered(milestones),
        "plotItems": ordered(items),
        "missionTierRequirements": sorted(
            requirements, key=lambda row: (row["sortOrder"] or 0, row["requirementId"])
        ),
        "finalGateReferenceStatus": {
            "configured": res.valid and not missing,
            "missingConfiguration": missing,
            "isCampaignEligibilityResult": False,
        },
    }


def export(root):
    res = net.Result()
    data = validate_identities(root, res)
    if not res.valid:
        return res, None
    out = root / "generated/data/progression_identity_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.progression_identity_catalog", "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data, "rules": RULES, "openItems": OPEN_ITEMS, "runtimeImplemented": False,
    }
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "export"])
    parser.add_argument("--root", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else net.find_project_root(Path(__file__).parent)
    if args.command == "export":
        res, out = export(root)
    else:
        res = net.Result()
        validate_identities(root, res)
        out = None
    for message in res.warnings:
        print("WARNING:", message)
    for message in res.errors:
        print("ERROR:", message)
    print("Rows:", res.stats)
    if out:
        print("Exported:", out)
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1


if __name__ == "__main__":
    sys.exit(main())
'''

test_text = r'''import csv
import json
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doda_network_rules as net
import doda_progression_identity_rules as pid


class ProgressionIdentityTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.gettempdir()) / ("doda_pid_" + uuid.uuid4().hex)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        for name, columns in [
            (pid.UPGRADES_FILE, pid.UPGRADE_COLUMNS),
            (pid.MILESTONES_FILE, pid.MILESTONE_COLUMNS),
            (pid.ITEMS_FILE, pid.ITEM_COLUMNS),
            (pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS),
        ]:
            self.write(name, columns, [])
        self.write("department_tracks.csv", ["track_id", "active"],
                   [{"track_id": "TRACK", "active": "true"}])
        self.write("mission_tiers.csv", ["tier_id", "active"],
                   [{"tier_id": "TIER_6", "active": "true"}])

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, name, columns, rows):
        with (self.src / name).open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def definition(self, columns, key, value, active="true", **changes):
        row = {column: "" for column in columns}
        row.update({key: value, "display_name": value, "sort_order": "10", "active": active})
        row.update(changes)
        return row

    def upgrade(self, active="true", track="TRACK"):
        row = self.definition(pid.UPGRADE_COLUMNS, "upgrade_id", "UP", active, track_id=track)
        self.write(pid.UPGRADES_FILE, pid.UPGRADE_COLUMNS, [row])

    def requirement(self, **changes):
        row = {column: "" for column in pid.REQUIREMENT_COLUMNS}
        row.update(requirement_id="REQ", tier_id="TIER_6",
                   upgrade_id="UP", sort_order="10", active="true")
        row.update(changes)
        self.write(pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS, [row])
        return row

    def validate(self):
        res = net.Result()
        return res, pid.validate_identities(self.root, res)

    def test_empty_catalogs_valid_but_unconfigured(self):
        res, data = self.validate()
        self.assertTrue(res.valid, res.errors)
        self.assertFalse(data["finalGateReferenceStatus"]["configured"])

    def test_upgrade_reference(self):
        self.upgrade()
        self.requirement()
        res, data = self.validate()
        self.assertTrue(res.valid, res.errors)
        self.assertEqual(data["missionTierRequirements"][0]["requirementType"], "UPGRADE_ACQUIRED")

    def test_unknown_track(self):
        self.upgrade(track="MISSING")
        res, _ = self.validate()
        self.assertTrue(any("unknown track_id" in error for error in res.errors))

    def test_duplicate_definition(self):
        row = self.definition(pid.ITEM_COLUMNS, "plot_item_id", "ITEM")
        self.write(pid.ITEMS_FILE, pid.ITEM_COLUMNS, [row, row])
        res, _ = self.validate()
        self.assertTrue(any("duplicate plot_item_id" in error for error in res.errors))

    def test_exactly_one_reference(self):
        self.upgrade()
        self.requirement(milestone_id="MILE")
        res, _ = self.validate()
        self.assertTrue(any("exactly one" in error for error in res.errors))

    def test_unknown_target(self):
        self.requirement()
        res, _ = self.validate()
        self.assertTrue(any("unknown upgrade_id" in error for error in res.errors))

    def test_unknown_tier(self):
        self.upgrade()
        self.requirement(tier_id="MISSING")
        res, _ = self.validate()
        self.assertTrue(any("unknown tier_id" in error for error in res.errors))

    def test_inactive_target(self):
        self.upgrade(active="false")
        self.requirement()
        res, _ = self.validate()
        self.assertTrue(any("inactive target" in error for error in res.errors))

    def test_inactive_tier(self):
        self.upgrade()
        self.requirement()
        self.write("mission_tiers.csv", ["tier_id", "active"],
                   [{"tier_id": "TIER_6", "active": "false"}])
        res, _ = self.validate()
        self.assertTrue(any("inactive tier" in error for error in res.errors))

    def test_duplicate_logical_requirement(self):
        self.upgrade()
        first = self.requirement()
        second = dict(first, requirement_id="REQ_2")
        self.write(pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS, [first, second])
        res, _ = self.validate()
        self.assertTrue(any("duplicate logical" in error for error in res.errors))

    def test_export_is_not_campaign_state(self):
        res, out = pid.export(self.root)
        self.assertTrue(res.valid, res.errors)
        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(payload["runtimeImplemented"])
        self.assertFalse(payload["finalGateReferenceStatus"]["isCampaignEligibilityResult"])
        self.assertEqual(payload["rules"]["plotItemCheck"], "CURRENTLY_HELD_AT_CAPSTONE_PURCHASE")

    def test_shipped_data(self):
        root = net.find_project_root(Path(__file__).resolve().parent)
        res = net.Result()
        data = pid.validate_identities(root, res)
        self.assertTrue(res.valid, res.errors)
        self.assertFalse(data["finalGateReferenceStatus"]["configured"])


if __name__ == "__main__":
    unittest.main()
'''
compile(module_text, str(module), "exec")
compile(test_text, str(test), "exec")

addendum = """
## Progression identity foundation - CONFIRMED (2026-10-08)
- PID-01: Upgrade is a broad term for something purchased or unlocked that grants abilities, better stats, access or other benefits. It is not limited to equipment contracts.
- PID-02: Upgrade definitions are distinct from individual equipment ownership and from campaign acquisition state. Optional department-track references group upgrades.
- PID-03: Milestone requirements check persistent completion. Plot-item requirements check current possession at capstone purchase. Permanent credit for acquiring an item can be represented by a milestone.
- PID-04: Tier requirements combine with ALL semantics. Each row has exactly one typed reference: upgrade, milestone or plot item.
- PID-05: Four catalogs seeded empty: upgrades, plot_milestones, plot_items, mission_tier_requirements. No mandatory definitions or requirements invented.
- PID-06: Numeric requirements stay in territory_settings.csv. Capstone mission reference remains unresolved pending mission authoring.
- Implementation stage A: standalone identity module, validator/exporter and twelve tests. GUI, Validate All/Export All wiring and territory-contract integration are pending stage B.
- Active definition means available authored content, not acquired/completed/held campaign state.
"""
history_text = """# Progression Identity Foundations - 2026-10-08

Stage A: authoring definitions and validation only.

Created:
- doda_progression_identity_rules.py
- upgrades.csv
- plot_milestones.csv
- plot_items.csv
- mission_tier_requirements.csv
- test_progression_identity_rules.py (12 tests)

Four source tables are header-only. No plot or upgrade definitions invented.
Requirements use exactly one typed reference and combine with ALL semantics.
The standalone exporter targets progression_identity_catalog.json.

GUI wiring, full export-chain integration and territory reference-status
integration remain pending stage B. Native campaign behavior is not implemented.
"""

backups = work / "backups"
numbers = []
if backups.exists():
    for path in backups.iterdir():
        match = re.match(r"^v(\d+)_", path.name)
        if path.is_dir() and match:
            numbers.append(int(match.group(1)))
backup = backups / (
    f"v{max(numbers, default=54)+1:03d}_progression_identity_a_" +
    datetime.now().strftime("%Y%m%d_%H%M%S")
)
target = backup / doc.relative_to(root)
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(doc, target)
digest = hashlib.sha256(doc_raw).hexdigest()
if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
    stop("Backup verification failed.")
(backup / "MANIFEST.txt").write_text(
    digest + "  " + doc.relative_to(root).as_posix() + "\n", encoding="utf-8"
)

writes = {
    module: module_text.encode("utf-8"),
    test: test_text.encode("utf-8"),
    history: history_text.encode("utf-8"),
    doc: doc_raw + (
        ("" if doc_raw.endswith(b"\n") else "\n") + addendum
    ).encode("utf-8"),
}
for name, header in csv_headers.items():
    writes[src / name] = (header + "\r\n").encode("utf-8")
originals = {path: path.read_bytes() if path.exists() else None for path in writes}
try:
    for path, data in writes.items():
        path.write_bytes(data)
except Exception:
    for path, data in originals.items():
        if data is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(data)
    raise

print("=== COPY FROM HERE ===", flush=True)
print("Backup folder:", backup, flush=True)
print("Created identity catalogs: 4; rows: 0; added tests: 12", flush=True)
for label, arguments in [
    ("test suite", ["-m", "unittest", "discover", "-s", "tests"]),
    ("identity: real data", ["doda_progression_identity_rules.py", "validate"]),
]:
    print("--- " + label + " ---", flush=True)
    result = subprocess.run(
        [sys.executable, *arguments], cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, errors="replace",
    )
    print(result.stdout, end="", flush=True)
    print("Process exit code:", result.returncode, flush=True)
    if result.returncode:
        print("Patch remains applied; do not rerun. Paste the failure.", flush=True)
        sys.exit(result.returncode)
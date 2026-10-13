import hashlib
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
work = root / "tools/doda_content_workbench"
module = work / "doda_territory_rules.py"
doc = root / "docs/workbench/spec/DESIGN_DECISIONS_2026-10-08.md"
test = work / "tests/test_territory_identity_integration.py"
history = root / "docs/workbench/history/Territory_Identity_Integration_2026-10-08.md"

def stop(message):
    print("STOP: " + message + " No project files were modified.", flush=True)
    sys.exit(1)

for path in (module, doc, work / "doda_progression_identity_rules.py"):
    if not path.is_file():
        stop(str(path) + " was not found.")
for path in (test, history):
    if path.exists():
        stop(str(path) + " already exists.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")

raw = module.read_bytes()
original = raw.decode("utf-8-sig")
crlf = "\r\n" in original
text = original.replace("\r\n", "\n")
if "progressionIdentities" in text:
    stop("Territory identity integration is already present.")

def replace_once(anchor, replacement):
    global text
    count = text.count(anchor)
    if count != 1:
        stop("Anchor found %d times: %s" % (count, anchor[:100]))
    text = text.replace(anchor, replacement)

replace_once(
    "import doda_network_rules as net\n",
    "import doda_network_rules as net\n"
    "import doda_progression_identity_rules as progression_identity_rules\n",
)

old_blockers = '''    missing_gate.extend([
        "REQUIRED_UPGRADE_REFERENCES",
        "REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES",
        "CAPSTONE_MISSION_REFERENCE",
    ])
'''
new_blockers = '''    identities = data.get("progressionIdentities")
    if identities is None:
        reference_status = {
            "configured": False,
            "missingConfiguration": [
                "REQUIRED_UPGRADE_REFERENCES",
                "REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES",
            ],
        }
        requirements = []
    else:
        reference_status = identities["finalGateReferenceStatus"]
        requirements = [
            row for row in identities["missionTierRequirements"]
            if row["active"] and row["tierId"] == "TIER_6"
        ]
    missing_gate.extend(reference_status["missingConfiguration"])
    missing_gate.append("CAPSTONE_MISSION_REFERENCE")
    upgrade_references = [
        row["referenceId"] for row in requirements
        if row["requirementType"] == "UPGRADE_ACQUIRED"
    ]
    plot_references = [
        {"requirementType": row["requirementType"], "referenceId": row["referenceId"]}
        for row in requirements
        if row["requirementType"] in ("MILESTONE_COMPLETED", "PLOT_ITEM_HELD")
    ]
'''
replace_once(old_blockers, new_blockers)

replace_once(
    '"contractVersion": "2026-10-08.1",',
    '"contractVersion": "2026-10-08.2",',
)
replace_once(
    '        "finalGate": {\n            "numericSettings":',
    '        "finalGate": {\n'
    '            "requiredUpgradeReferences": upgrade_references or None,\n'
    '            "requiredPlotMilestoneOrItemReferences": plot_references or None,\n'
    '            "requirements": requirements,\n'
    '            "referenceConfigurationReady": reference_status["configured"],\n'
    '            "isCampaignEligibilityResult": False,\n'
    '            "numericSettings":',
)

replace_once(
    '        "requiredUpgradeReferences": None,\n'
    '        "requiredPlotMilestoneOrItemReferences": None,\n',
    '        "requiredUpgradeReferencesSource": "missionProgression.finalGate.requiredUpgradeReferences",\n'
    '        "requiredPlotMilestoneOrItemReferencesSource": "missionProgression.finalGate.requiredPlotMilestoneOrItemReferences",\n',
)

old_validate_tail = '''    if res.valid:
        data["missionProgression"] = build_mission_progression(data)
    return data
'''
new_validate_tail = '''    identity_files = (
        progression_identity_rules.UPGRADES_FILE,
        progression_identity_rules.MILESTONES_FILE,
        progression_identity_rules.ITEMS_FILE,
        progression_identity_rules.REQUIREMENTS_FILE,
    )
    identity_scope_present = (
        any((src / filename).is_file() for filename in identity_files)
        or (root / "tools" / "doda_content_workbench").is_dir()
    )
    if identity_scope_present:
        data["progressionIdentities"] = progression_identity_rules.validate_identities(root, res)
    if res.valid:
        data["missionProgression"] = build_mission_progression(data)
    return data
'''
replace_once(old_validate_tail, new_validate_tail)
compile(text, str(module), "exec")

test_text = r'''import csv
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import doda_network_rules as net
import doda_territory_rules as terr
import doda_progression_identity_rules as pid
import test_territory_rules as base


class TerritoryIdentityIntegrationTests(unittest.TestCase):
    setUp = base.TerritoryTests.setUp
    tearDown = base.TerritoryTests.tearDown
    make_root = base.TerritoryTests.make_root

    def write(self, root, filename, columns, rows):
        path = root / "data_authoring/source" / filename
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def row(self, columns, **changes):
        row = {column: "" for column in columns}
        row.update(sort_order="10", active="true")
        row.update(changes)
        return row

    def fixture(self, populated=False, requirements_active=True):
        tiers = [
            base._row(terr.TIER_COLUMNS, tier_id="TIER_1", display_name="One",
                      min_lifetime_evidence="0", authored_content="false",
                      sort_order="10", active="true"),
            base._row(terr.TIER_COLUMNS, tier_id="TIER_5", display_name="Five",
                      min_lifetime_evidence="100", authored_content="false",
                      sort_order="50", active="true"),
            base._row(terr.TIER_COLUMNS, tier_id="TIER_6", display_name="Six",
                      min_lifetime_evidence="1000", authored_content="true",
                      sort_order="60", active="true"),
        ]
        root = self.make_root(tiers=tiers)
        upgrades, milestones, requirements = [], [], []
        if populated:
            upgrades = [self.row(pid.UPGRADE_COLUMNS, upgrade_id="UP_TEST", display_name="Upgrade")]
            milestones = [self.row(pid.MILESTONE_COLUMNS, milestone_id="PLOT_TEST", display_name="Milestone")]
            active = "true" if requirements_active else "false"
            requirements = [
                self.row(pid.REQUIREMENT_COLUMNS, requirement_id="REQ_UP",
                         tier_id="TIER_6", upgrade_id="UP_TEST", active=active),
                self.row(pid.REQUIREMENT_COLUMNS, requirement_id="REQ_PLOT",
                         tier_id="TIER_6", milestone_id="PLOT_TEST",
                         sort_order="20", active=active),
            ]
        self.write(root, pid.UPGRADES_FILE, pid.UPGRADE_COLUMNS, upgrades)
        self.write(root, pid.MILESTONES_FILE, pid.MILESTONE_COLUMNS, milestones)
        self.write(root, pid.ITEMS_FILE, pid.ITEM_COLUMNS, [])
        self.write(root, pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS, requirements)
        return root

    def validate(self, root):
        result = net.Result()
        data = terr.validate_territory(root, result)
        self.assertTrue(result.valid, result.errors)
        return data

    def test_empty_catalogs_keep_reference_blockers(self):
        data = self.validate(self.fixture())
        gate = data["missionProgression"]["finalGate"]
        self.assertFalse(gate["referenceConfigurationReady"])
        self.assertIn("REQUIRED_UPGRADE_REFERENCES", gate["missingConfiguration"])
        self.assertIn("REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES",
                      gate["missingConfiguration"])
        self.assertIsNone(gate["requiredUpgradeReferences"])

    def test_authored_references_clear_only_reference_blockers(self):
        data = self.validate(self.fixture(populated=True))
        gate = data["missionProgression"]["finalGate"]
        self.assertTrue(gate["referenceConfigurationReady"])
        self.assertNotIn("REQUIRED_UPGRADE_REFERENCES", gate["missingConfiguration"])
        self.assertNotIn("REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES",
                         gate["missingConfiguration"])
        self.assertIn("CAPSTONE_MISSION_REFERENCE", gate["missingConfiguration"])
        self.assertFalse(gate["configured"])
        self.assertFalse(gate["isCampaignEligibilityResult"])
        self.assertEqual(gate["requiredUpgradeReferences"], ["UP_TEST"])

    def test_inactive_requirements_do_not_configure_gate(self):
        data = self.validate(self.fixture(populated=True, requirements_active=False))
        gate = data["missionProgression"]["finalGate"]
        self.assertFalse(gate["referenceConfigurationReady"])
        self.assertEqual(gate["requirements"], [])

    def test_invalid_identity_reference_blocks_territory_export(self):
        root = self.fixture()
        bad = self.row(pid.REQUIREMENT_COLUMNS, requirement_id="BAD",
                       tier_id="TIER_6", upgrade_id="MISSING")
        self.write(root, pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS, [bad])
        result, output = terr.export(root)
        self.assertFalse(result.valid)
        self.assertIsNone(output)
        self.assertTrue(any("unknown upgrade_id" in error for error in result.errors))
        self.assertFalse((root / "generated/data/territory_catalog.json").exists())

    def test_partial_identity_installation_blocks_export(self):
        root = self.fixture()
        (root / "data_authoring/source" / pid.ITEMS_FILE).unlink()
        result, output = terr.export(root)
        self.assertFalse(result.valid)
        self.assertIsNone(output)
        self.assertTrue(any("Required source file missing" in error for error in result.errors))

    def test_export_carries_definitions_and_typed_requirements(self):
        result, output = terr.export(self.fixture(populated=True))
        self.assertTrue(result.valid, result.errors)
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["missionProgression"]["contractVersion"], "2026-10-08.2")
        self.assertEqual(payload["progressionIdentities"]["upgrades"][0]["id"], "UP_TEST")
        gate = payload["missionProgression"]["finalGate"]
        self.assertEqual(len(gate["requirements"]), 2)
        self.assertEqual(
            gate["requiredPlotMilestoneOrItemReferences"],
            [{"requirementType": "MILESTONE_COMPLETED", "referenceId": "PLOT_TEST"}],
        )
        self.assertFalse(gate["isCampaignEligibilityResult"])
        self.assertFalse(payload["runtimeImplemented"])


if __name__ == "__main__":
    unittest.main()
'''
compile(test_text, str(test), "exec")

doc_raw = doc.read_bytes()
marker = "## Territory identity integration - implementation (2026-10-08)"
if marker in doc_raw.decode("utf-8-sig"):
    stop("B2 is already documented.")
addendum = """
## Territory identity integration - implementation (2026-10-08)
- B2 complete: territory validation reads progression identities when identity sources are present, and requires them in the actual workbench project.
- territory_catalog.json includes progressionIdentities and active typed Tier 6 requirements.
- Upgrade/plot reference blockers derive from validated authored requirements, not hard-coded missing entries.
- Empty catalogs remain unconfigured; inactive requirements do not satisfy reference configuration.
- Invalid references or partial identity installations block territory export.
- referenceConfigurationReady describes authored configuration only, never campaign eligibility.
- Numeric thresholds and the capstone mission reference remain unresolved.
- missionProgression contractVersion advanced to 2026-10-08.2.
- Added six integration tests. No campaign behavior implemented.
- This completes the B2 work marked pending in the earlier identity-wiring entry.
"""
history_text = """# Territory Identity Integration - 2026-10-08

Stage B2 complete. Territory validation/export now consumes the identity
catalogs and exports active typed Tier 6 requirements.

Empty or inactive requirements cannot silently configure the final gate.
Invalid references and partial identity installations prevent export.
Authored configuration is explicitly not campaign eligibility.

Added six integration tests. Numeric thresholds, concrete requirements and
the capstone mission remain undecided. No native campaign runtime changed.

Original territory module and decisions saved in a numbered hash-verified backup.
"""

backups = work / "backups"
numbers = []
if backups.exists():
    for path in backups.iterdir():
        match = re.match(r"^v(\d+)_", path.name)
        if path.is_dir() and match:
            numbers.append(int(match.group(1)))
backup = backups / (
    f"v{max(numbers, default=56)+1:03d}_territory_identity_b2_" +
    datetime.now().strftime("%Y%m%d_%H%M%S")
)
manifest = []
for path, data in ((module, raw), (doc, doc_raw)):
    relative = path.relative_to(root)
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    digest = hashlib.sha256(data).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed.")
    manifest.append(f"{digest}  {relative.as_posix()}")
(backup / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

out = text.replace("\n", "\r\n") if crlf else text
writes = {
    module: (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + out.encode("utf-8"),
    doc: doc_raw + (("" if doc_raw.endswith(b"\n") else "\n") + addendum).encode("utf-8"),
    test: test_text.encode("utf-8"),
    history: history_text.encode("utf-8"),
}
originals = {module: raw, doc: doc_raw, test: None, history: None}
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

print("Backup folder:", backup, flush=True)
print("Integrated territory identity references; added tests: 6", flush=True)
for label, arguments in [
    ("test suite", ["-m", "unittest", "discover", "-s", "tests"]),
    ("territory: real data", ["doda_territory_rules.py", "validate"]),
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
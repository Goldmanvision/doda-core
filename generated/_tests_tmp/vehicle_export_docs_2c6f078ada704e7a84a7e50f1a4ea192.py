import ast
import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
w = root / "tools/doda_content_workbench"
src = root / "data_authoring/source"
rules_path = w / "doda_task_prerequisite_rules.py"

guards = {
    rules_path:
        "56c4212e6861ee0228547f5c79213164ac562b3bb05f76073d094fd91a2651c6",
    src / "task_prerequisites.csv":
        "1c79e6e8eb41e21f5fa6c43b7e67056cb59a9bce4f560b78d352830bd1e163cf",
    src / "vehicle_types.csv":
        "c738588dff81934e7b978ed0a9d8d8f5dc89babbca976ab295f3404ea499e673",
    w / "doda_task_requirements_preview.py":
        "3112987c276bfc0dc90759909585a91d391993b0c3664b1d6f5f787c603c77ed",
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for path, expected in guards.items():
    if not path.is_file() or digest(path) != expected:
        raise SystemExit("STOP: File differs from accepted checkpoint: " + str(path))

original_rules = rules_path.read_bytes()
rules = original_rules.decode("utf-8-sig")

old = '"PRE-01": "Vehicle catalog, quantity, capacity and allocation.",'
new = (
    '"PRE-01": "Owned vehicle quantities, runtime capacity enforcement and allocation; '
    'generic vehicle types and capacities are authored separately.",'
)
if rules.count(old) != 1:
    raise SystemExit("STOP: Expected open-item text was not unique.")
rules = rules.replace(old, new, 1)

tests = '''import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import doda_task_prerequisite_rules as prerequisites
import doda_vehicle_rules as vehicles

W = Path(__file__).resolve().parents[1]
ROOT = W.parents[1]
FILES = ("task_templates.csv", "task_prerequisites.csv", "vehicle_types.csv")


class VehiclePrerequisiteDocumentationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="vehicle-documentation-")
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.live_source = ROOT / "data_authoring/source"
        self.live_before = {}
        for name in FILES:
            source = self.live_source / name
            self.live_before[name] = source.read_bytes()
            shutil.copy2(source, self.src / name)

    def tearDown(self):
        self.tmp.cleanup()

    def vehicle_prerequisite(self):
        with (self.src / "task_prerequisites.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            return next(
                row for row in csv.DictReader(handle)
                if row["prerequisite_id"] == "PRE_INVESTIGATE_VEHICLE"
            )

    def prerequisite_export(self):
        result, path = prerequisites.export(self.root)
        self.assertTrue(result.valid, result.errors)
        self.assertIsNotNone(path)
        return json.loads(path.read_text(encoding="utf-8"))

    def test_description_recognizes_catalog_and_runtime_boundary(self):
        text = self.vehicle_prerequisite()["description"]
        self.assertIn("Generic vehicle types are cataloged", text)
        self.assertIn(
            "runtime capacity enforcement and allocation are not implemented",
            text,
        )
        self.assertNotIn(
            "Vehicle catalog and runtime capacity/allocation checks are not implemented",
            text,
        )

    def test_prerequisite_export_preserves_source_description_and_semantics(self):
        source = self.vehicle_prerequisite()
        payload = self.prerequisite_export()
        row = next(
            item for item in payload["prerequisites"]
            if item["prerequisiteId"] == source["prerequisite_id"]
        )
        self.assertEqual(row["description"], source["description"])
        self.assertEqual(row["taskTemplateId"], source["task_template_id"])
        self.assertEqual(row["requirementKind"], source["requirement_kind"])
        self.assertEqual(row["scope"], source["scope"])
        self.assertEqual(row["minQuantity"], int(source["min_quantity"]))
        self.assertEqual(row["active"], source["active"].upper() == "TRUE")
        self.assertFalse(payload["runtimeImplemented"])

    def test_exported_open_item_distinguishes_catalog_from_runtime(self):
        payload = self.prerequisite_export()
        self.assertEqual(
            payload["openItems"]["PRE-01"],
            "Owned vehicle quantities, runtime capacity enforcement and allocation; "
            "generic vehicle types and capacities are authored separately.",
        )

    def test_vehicle_export_matches_authored_capacities_and_boundaries(self):
        with (self.src / "vehicle_types.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            expected = {
                row["vehicle_type_id"]: int(row["max_team_members"])
                for row in csv.DictReader(handle)
            }
        result, path = vehicles.export(self.root)
        self.assertTrue(result.valid, result.errors)
        self.assertIsNotNone(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        actual = {
            row["vehicleTypeId"]: row["maxTeamMembers"]
            for row in payload["vehicleTypes"]
        }
        self.assertEqual(actual, expected)
        self.assertFalse(payload["runtimeImplemented"])
        self.assertTrue(payload["rules"]["definitionsCreateNoInventory"])
        self.assertTrue(payload["rules"]["capacityDoesNotChangeTaskStaffingLimits"])
        self.assertFalse(payload["rules"]["runtimeCapacityChecksImplemented"])
        self.assertFalse(payload["rules"]["allocationImplemented"])

    def test_temporary_exports_do_not_modify_source_files(self):
        before = {name: (self.src / name).read_bytes() for name in FILES}
        self.prerequisite_export()
        result, path = vehicles.export(self.root)
        self.assertTrue(result.valid, result.errors)
        self.assertIsNotNone(path)
        for name in FILES:
            self.assertEqual((self.src / name).read_bytes(), before[name])
            self.assertEqual(
                (self.live_source / name).read_bytes(), self.live_before[name]
            )
'''

history = """# Vehicle prerequisite export documentation alignment v115

Only PRE-01 open-item text in the prerequisite export payload is changed.
Generic vehicle types and capacities are recognized as authored data.
Owned quantities, runtime capacity enforcement and allocation remain open.
No validation logic, source CSV, export schema or runtime behavior is changed.
Five regression tests cover:
- Corrected authored prerequisite description.
- Export/source description and requirement-semantic agreement.
- Updated exported PRE-01 wording.
- Vehicle export/source capacities and implementation boundaries.
- Temporary exports preserving authoring source files.
Expected tests: 663 baseline; 668 after installation.
Live generated JSON is refreshed separately using Export All.
"""

targets = {
    rules_path: rules,
    w / "tests/test_vehicle_prerequisite_documentation.py": tests,
    root / "docs/workbench/history/vehicle_prerequisite_export_docs_v115.md": history,
}

for path, text in targets.items():
    if path != rules_path and path.exists():
        raise SystemExit("STOP: New target already exists: " + str(path))
    if path.suffix == ".py":
        compile(text, str(path), "exec")
        ast.parse(text)

print("CHECKPOINT HASHES AND METADATA-ONLY CANDIDATE: PASS", flush=True)
source_before = {path: digest(path) for path in src.glob("*.csv")}

def suite(expected):
    done = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=w, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    output = done.stdout + "\n" + done.stderr
    match = re.search(r"Ran (\d+) tests", output)
    print(output, flush=True)
    if done.returncode or not match or int(match.group(1)) != expected:
        raise RuntimeError("Expected " + str(expected) + " passing tests.")

suite(663)

backup = w / "backups" / (
    "v115_vehicle_export_docs_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
)
backup.mkdir(parents=True, exist_ok=False)
(backup / "doda_task_prerequisite_rules.py").write_bytes(original_rules)
(backup / "new_files_manifest.txt").write_text(
    "\n".join(
        str(path.relative_to(root))
        for path in targets if path != rules_path
    ) + "\n",
    encoding="utf-8",
)
print("Backup folder:", backup, flush=True)

written = []
try:
    for path, expected in guards.items():
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError("Checkpoint changed during preparation: " + str(path))

    for path, text in targets.items():
        if path != rules_path and path.exists():
            raise RuntimeError("New target appeared during preparation: " + str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
        written.append(path)
        path.write_bytes(text.encode("utf-8"))
        print("WROTE SHA256", digest(path), path.relative_to(root), flush=True)

    suite(668)

    for path, expected in source_before.items():
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError("Existing source CSV changed: " + str(path))
    for path, expected in guards.items():
        if path != rules_path and digest(path) != expected:
            raise RuntimeError("Read-only checkpoint file changed: " + str(path))

    print("RESULT: PASS. 668 tests; all existing source CSVs unchanged.", flush=True)
    print("Prerequisite export open-item wording aligned with the authored vehicle catalog.", flush=True)
    print("No runtime behavior changed. Live generated outputs were not rewritten.", flush=True)

except BaseException:
    for path in reversed(written):
        if path == rules_path:
            path.write_bytes(original_rules)
        else:
            path.unlink(missing_ok=True)
    print("PATCH ROLLED BACK. Prerequisite rules restored; new files removed.", flush=True)
    raise
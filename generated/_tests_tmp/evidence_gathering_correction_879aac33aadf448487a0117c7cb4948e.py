import ast
import csv
import hashlib
import io
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
w = root / "tools/doda_content_workbench"
src = root / "data_authoring/source"
sys.path.insert(0, str(w))

flow_path = src / "task_template_flows.csv"
expected = "9a62046821ad3fbd1774d7d9d7c21a861e4a478cbaefd46927bf56930602a7b2"
if not flow_path.is_file() or hashlib.sha256(flow_path.read_bytes()).hexdigest() != expected:
    raise SystemExit("STOP: Flow source differs from diagnostic.")

import doda_content_workbench as core
import doda_task_flow_rules as flows

with flow_path.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    if reader.fieldnames != flows.FLOW_COLUMNS:
        raise SystemExit("STOP: Unexpected flow header.")
    old_rows = list(reader)

allowed = {
    "EVIDENCE_PHOTOGRAPHIC", "EVIDENCE_AUDIO", "EVIDENCE_VIDEO",
}
removed = [
    row for row in old_rows
    if row["task_template_id"] == "FIELD_SURVEILLANCE"
    and row["direction"] == "OUT"
    and row["resource_id"] not in allowed
]
expected_removed = {
    "EVIDENCE_PAPER", "EVIDENCE_DIGITAL",
    "EVIDENCE_CHEMICAL", "EVIDENCE_PHYSICAL",
}
if len(old_rows) != 48 or len(removed) != 4:
    raise SystemExit("STOP: Expected 48 flows and four removals.")
if {row["resource_id"] for row in removed} != expected_removed:
    raise SystemExit("STOP: Unexpected rows selected for removal.")
if any(
    row["active"].lower() != "false" or row["amount"] or row["weight"]
    for row in removed
):
    raise SystemExit("STOP: Removed rows have been configured or activated; review first.")

kept = [row for row in old_rows if row not in removed]
template_order = list(dict.fromkeys(row["task_template_id"] for row in kept))
new_rows = []
for tid in template_order:
    group = [row for row in kept if row["task_template_id"] == tid]
    group.sort(key=lambda row: (
        int(row["sort_order"]), row["direction"], row["resource_id"]
    ))
    new_rows.extend(group)

def key(row):
    return tuple(row[column] for column in flows.FLOW_COLUMNS)

assert sorted(map(key, new_rows)) == sorted(map(key, kept))
assert len(new_rows) == 44

physical = [
    row for row in new_rows
    if row["task_template_id"] == "INVESTIGATE"
    and row["direction"] == "OUT"
    and row["resource_id"] == "EVIDENCE_PHYSICAL"
]
if len(physical) != 1 or physical[0]["flow_mode"] != "WEIGHTED":
    raise SystemExit("STOP: Investigate Physical Evidence row not preserved.")

buffer = io.StringIO(newline="")
writer = csv.DictWriter(
    buffer, fieldnames=flows.FLOW_COLUMNS, lineterminator="\r\n"
)
writer.writeheader()
writer.writerows(new_rows)
candidate = buffer.getvalue().encode("utf-8")

tests = '''import csv
import unittest
from pathlib import Path


class EvidenceGatheringSourceTests(unittest.TestCase):
    def rows(self):
        root = Path(__file__).resolve().parents[3]
        with (root / "data_authoring/source/task_template_flows.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            return list(csv.DictReader(handle))

    def test_field_surveillance_output_categories(self):
        rows = [
            row for row in self.rows()
            if row["task_template_id"] == "FIELD_SURVEILLANCE"
            and row["direction"] == "OUT"
        ]
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            {row["resource_id"] for row in rows},
            {"EVIDENCE_PHOTOGRAPHIC", "EVIDENCE_AUDIO", "EVIDENCE_VIDEO"},
        )
        self.assertTrue(all(row["flow_mode"] == "WEIGHTED" for row in rows))

    def test_investigate_has_physical_evidence_choice(self):
        rows = [
            row for row in self.rows()
            if row["task_template_id"] == "INVESTIGATE"
            and row["direction"] == "OUT"
            and row["resource_id"] == "EVIDENCE_PHYSICAL"
        ]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["flow_mode"], "WEIGHTED")
'''

history = """# Evidence gathering correction v095

Confirmed:
- Field Surveillance gathers only Photographic, Audio and Video Evidence.
- Investigate retains its Physical Evidence weighted choice.

Changes:
- Removed four inactive, unconfigured Field Surveillance outputs:
  Paper, Digital, Chemical and Physical.
- Grouped flow CSV rows by template for editor visibility.
- Preserved every retained row's values, including sort_order.
- Staffing, resources, equipment and task templates unchanged.
- No runtime execution or collection-kit selection behavior added.

This supersedes v094's seven-choice expectation for Field Surveillance.
Investigate and the three Undercover templates retain seven choices.
Acceptance: 502 baseline tests; 504 after correction; 44 flow rows.
Manual acceptance pending: editor, preview, Validate All and Export All.
"""

test_path = w / "tests/test_evidence_gathering_source.py"
history_path = root / "docs/workbench/history/evidence_gathering_correction_v095.md"
if test_path.exists() or history_path.exists():
    raise SystemExit("STOP: New test/history file already exists.")
compile(tests, str(test_path), "exec")
ast.parse(tests)

targets = {
    flow_path: candidate,
    test_path: tests.encode("utf-8"),
    history_path: history.encode("utf-8"),
}
print("Candidate: 44 flows; Field Surveillance limited to three categories.",
      flush=True)

def suite():
    done = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=w, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    combined = done.stdout + "\n" + done.stderr
    match = re.search(r"Ran (\d+) tests", combined)
    if done.returncode or not match:
        print(combined, flush=True)
        raise RuntimeError("Regression suite failed.")
    print(combined[combined.rfind("----------------------------------------------------------------------"):],
          flush=True)
    return int(match.group(1))

if suite() != 502:
    raise SystemExit("STOP: Expected 502 baseline tests.")

with tempfile.TemporaryDirectory(prefix="gathering-candidate-") as directory:
    temporary = Path(directory)
    temporary_src = temporary / "data_authoring/source"
    shutil.copytree(src, temporary_src)
    (temporary / "tools").mkdir()
    (temporary_src / flow_path.name).write_bytes(candidate)
    result = core.validate_project(temporary)
    if not result.valid:
        raise RuntimeError("Candidate validation failed: " + repr(result.errors))
    result, exported = flows.export(temporary)
    if not result.valid or exported is None:
        raise RuntimeError("Candidate export failed: " + repr(result.errors))
print("Staged validation and temporary export: PASS", flush=True)

source_before = {
    p: hashlib.sha256(p.read_bytes()).hexdigest() for p in src.glob("*.csv")
}
originals = {
    p: p.read_bytes() if p.exists() else None for p in targets
}
backup = w / "backups" / (
    "v095_evidence_gathering_correction_" +
    datetime.now().strftime("%Y%m%d_%H%M%S")
)
backup.mkdir(parents=True, exist_ok=False)
print("Backup folder:", backup, flush=True)
for p, original in originals.items():
    if original is not None:
        destination = backup / p.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, destination)
        print("BACKUP SHA256", hashlib.sha256(original).hexdigest(),
              p.relative_to(root), flush=True)

written = []
try:
    for p, data in targets.items():
        if p.exists() and p.read_bytes() != originals[p]:
            raise RuntimeError("File changed during preparation: " + str(p))
        p.parent.mkdir(parents=True, exist_ok=True)
        written.append(p)
        p.write_bytes(data)
        print("WROTE SHA256", hashlib.sha256(data).hexdigest(),
              p.relative_to(root), flush=True)

    if suite() != 504:
        raise RuntimeError("Expected 504 post-change tests.")

    result = core.validate_project(root)
    if not result.valid:
        raise RuntimeError("Main validation failed: " + repr(result.errors))

    import doda_task_flow_preview as preview
    models, warnings = preview.load_previews(root)
    index = {m["template"]["task_template_id"]: m for m in models}
    field_outputs = [
        row for row in index["FIELD_SURVEILLANCE"]["flows"]
        if row["direction"] == "OUT"
    ]
    assert len(field_outputs) == 3
    assert {row["resourceId"] for row in field_outputs} == allowed

    for tid in (
        "INVESTIGATE", "UNDERCOVER_7_DAY",
        "UNDERCOVER_14_DAY", "UNDERCOVER_31_DAY",
    ):
        outputs = [
            row for row in index[tid]["flows"]
            if row["direction"] == "OUT"
        ]
        assert len(outputs) == 7, tid
        assert any(row["resourceId"] == "EVIDENCE_PHYSICAL" for row in outputs), tid

    for p, digest in source_before.items():
        if p != flow_path:
            if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
                raise RuntimeError("Unrelated source CSV changed: " + str(p))

    print("MAIN VALIDATION AND CORRECTED PREVIEWS: PASS", flush=True)
    print("Investigate Physical Evidence row:", physical[0], flush=True)
    print("Staffing and all unrelated source CSVs unchanged.", flush=True)
    print("RESULT: PASS. 504 tests; 44 flows.", flush=True)
    print("Restart Workbench; inspect Task Resource Flows and previews.",
          flush=True)
    print("Then Validate All and Export All.", flush=True)
except BaseException:
    for p in reversed(written):
        original = originals[p]
        if original is None:
            p.unlink(missing_ok=True)
        else:
            p.write_bytes(original)
    print("PATCH ROLLED BACK: original flow CSV restored; new files removed.",
          flush=True)
    raise
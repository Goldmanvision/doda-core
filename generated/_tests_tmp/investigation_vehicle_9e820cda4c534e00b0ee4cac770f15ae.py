import csv
import hashlib
import io
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
w = root / "tools/doda_content_workbench"
src = root / "data_authoring/source"
catalog = src / "task_prerequisites.csv"
history = root / "docs/workbench/history/investigation_vehicle_v108.md"
expected = {
    catalog: "0ecf7cf3e77582f65056541b50aa390488506e656915c5be3d4adc015b27d664",
    w / "doda_network_editor.py":
        "a72ff2dbf0f1f15eba4d726392e8fa0686297d20c710076696ee19e1172c8e1d",
    w / "doda_task_prerequisite_rules.py":
        "56c4212e6861ee0228547f5c79213164ac562b3bb05f76073d094fd91a2651c6",
}
for p, digest in expected.items():
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        raise SystemExit("STOP: File differs from verified checkpoint: " + str(p))
if history.exists():
    raise SystemExit("STOP: v108 history already exists.")

original = catalog.read_bytes()
reader = csv.DictReader(io.StringIO(original.decode("utf-8-sig")))
columns = reader.fieldnames
rows = list(reader)
before_rows = [dict(row) for row in rows]
matches = [row for row in rows if row["prerequisite_id"] == "PRE_INVESTIGATE_VEHICLE"]
if len(matches) != 1:
    raise SystemExit("STOP: Expected one Investigation vehicle prerequisite.")
vehicle = matches[0]
assert vehicle["task_template_id"] == "INVESTIGATE"
assert vehicle["requirement_kind"] == "MOTOR_VEHICLE"
assert vehicle["scope"] == "TASK"
assert vehicle["personnel_role"] == vehicle["requirement_value"] == ""
assert vehicle["min_quantity"] == ""
assert vehicle["active"].lower() == "false"

vehicle["min_quantity"] = "1"
vehicle["description"] = (
    "One shared motor vehicle per Investigation task assignment. "
    "Standard vehicle supports teams up to 4; van supports teams up to 6. "
    "Staffing limits remain separate. Vehicle catalog and runtime capacity/allocation checks are not implemented."
)
buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\r\n")
writer.writeheader()
writer.writerows(rows)
candidate = buffer.getvalue().encode("utf-8")

history_text = """# Investigation vehicle prerequisite v108

Confirmed by user 2026-10-10:
- One shared motor vehicle per Investigation task assignment.
- Standard vehicle supports team sizes up to 4.
- Van supports team sizes up to 6.
- Capacity is distinct from minimum vehicle quantity.

Changed PRE_INVESTIGATE_VEHICLE min_quantity from blank to 1.
Updated that row's description only; all other fields and rows are preserved.
All three Investigation prerequisite definitions remain inactive drafts.
Investigation staffing maximum remains 2 agents; no staffing change implied.

Capacity values are documented only in this slice.
No structured vehicle catalog, seat checks, multiple-vehicle allocation,
travel timing, inventory creation or runtime task eligibility is added.
Teams beyond vehicle capacity and multiple-vehicle rules remain unresolved.
Existing historical records of unconfigured quantities are left intact.

Acceptance: 606 baseline and post-change tests.
Main/candidate validation and temporary prerequisite export checked.
Only task_prerequisites.csv is intentionally changed among source CSVs.
Manual acceptance pending: quantity 1, Validate All and Export All.
"""

def suite():
    done = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=w, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    output = done.stdout + "\n" + done.stderr
    match = re.search(r"Ran (\d+) tests", output)
    if done.returncode or not match:
        print(output, flush=True)
        raise RuntimeError("Regression suite failed.")
    print(output[output.rfind("----------------------------------------------------------------------"):], flush=True)
    return int(match.group(1))

print("Candidate CSV prepared: vehicle quantity/description only.", flush=True)
if suite() != 606:
    raise SystemExit("STOP: Expected 606 baseline tests.")

source_before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in src.glob("*.csv")}
backup = w / "backups" / (
    "v108_investigation_vehicle_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)
backup.mkdir(parents=True, exist_ok=False)
destination = backup / catalog.relative_to(root)
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(catalog, destination)
print("Backup folder:", backup, flush=True)
print("BACKUP SHA256", hashlib.sha256(original).hexdigest(), catalog.relative_to(root), flush=True)

catalog_written = False
history_written = False
try:
    if catalog.read_bytes() != original or history.exists():
        raise RuntimeError("Target changed during preparation.")
    catalog_written = True
    catalog.write_bytes(candidate)
    history.parent.mkdir(parents=True, exist_ok=True)
    with history.open("x", encoding="utf-8", newline="\n") as handle:
        history_written = True
        handle.write(history_text)
    for p in (catalog, history):
        print("WROTE SHA256", hashlib.sha256(p.read_bytes()).hexdigest(),
              p.relative_to(root), flush=True)

    if suite() != 606:
        raise RuntimeError("Expected 606 post-change tests.")

    sys.path.insert(0, str(w))
    import doda_content_workbench as core
    import doda_network_editor as editor
    import doda_network_rules as net
    import doda_task_prerequisite_rules as prerequisites
    result = core.validate_project(root)
    assert result.valid, result.errors
    result = editor.validate_candidate(root, "task_prerequisites", rows)
    assert result.valid, result.errors

    result = net.Result()
    data = prerequisites.validate_prerequisites(root, result)
    assert result.valid, result.errors
    assert not any("draft minimum quantity unconfigured" in message for message in result.warnings)
    vehicle_item = next(
        item for item in data["prerequisites"]
        if item["prerequisiteId"] == "PRE_INVESTIGATE_VEHICLE"
    )
    assert vehicle_item["minQuantity"] == 1
    assert vehicle_item["scope"] == "TASK" and not vehicle_item["active"]

    with catalog.open(encoding="utf-8-sig", newline="") as handle:
        after_rows = list(csv.DictReader(handle))
    changes = [
        (old["prerequisite_id"], key)
        for old, new in zip(before_rows, after_rows)
        for key in columns if old[key] != new[key]
    ]
    assert len(before_rows) == len(after_rows)
    assert set(changes) == {
        ("PRE_INVESTIGATE_VEHICLE", "min_quantity"),
        ("PRE_INVESTIGATE_VEHICLE", "description"),
    }, changes

    import tempfile
    import json
    with tempfile.TemporaryDirectory(prefix="vehicle-prerequisite-export-") as directory:
        temporary = Path(directory)
        shutil.copytree(src, temporary / "data_authoring/source")
        result, path = prerequisites.export(temporary)
        assert result.valid and path is not None, result.errors
        payload = json.loads(path.read_text(encoding="utf-8"))
        exported_vehicle = next(
            item for item in payload["prerequisites"]
            if item["prerequisiteId"] == "PRE_INVESTIGATE_VEHICLE"
        )
        assert exported_vehicle["minQuantity"] == 1
        assert not payload["runtimeImplemented"]
    for p, digest in source_before.items():
        if p != catalog and (
            not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != digest
        ):
            raise RuntimeError("Unrelated source CSV changed: " + str(p))
    print("MAIN/CANDIDATE VALIDATION, TWO-FIELD CHANGE AND TEMP EXPORT: PASS", flush=True)
    print("RESULT: PASS. 606 tests; only vehicle quantity/description changed in source CSVs.", flush=True)
    print("Capacity 4 / van 6 documented; staffing and runtime remain unchanged.", flush=True)
    print("Restart Workbench; confirm vehicle quantity 1, then Validate All and Export All.", flush=True)
except BaseException:
    if catalog_written:
        catalog.write_bytes(original)
    if history_written:
        history.unlink(missing_ok=True)
    print("PATCH ROLLED BACK: original CSV restored; new history removed.", flush=True)
    raise
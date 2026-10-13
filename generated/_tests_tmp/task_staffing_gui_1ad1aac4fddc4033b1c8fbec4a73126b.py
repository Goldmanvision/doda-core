import ast
import csv
import hashlib
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
w = root / "tools/doda_content_workbench"

expected = {
    "doda_content_gui.py": "3b9b219853b66d55c32427b4c9d220a0ce85ecea46a03e1c239d734101b16faa",
    "doda_network_editor.py": "b3a25dbbe014955681ec2d9ad626c9f237983b9bfccd37de593b80f6e58086f3",
    "doda_task_staffing_rules.py": "29795ec7d5e4fc106a40407a548734f0e22941a6765eed672ec472c6b96eb2f6",
}
for name, digest in expected.items():
    path = w / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit("STOP: File differs from verified checkpoint: " + name)

def once(body, old, new):
    if body.count(old) != 1:
        raise RuntimeError("STOP: Expected one exact anchor: " + old[:100])
    return body.replace(old, new)

def after_statement(body, statement, additions):
    lines = body.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.strip() == statement]
    if len(matches) != 1:
        raise RuntimeError("STOP: Expected one full statement: " + statement)
    index = matches[0]
    original = lines[index].rstrip("\r\n")
    indent = original[:len(original) - len(original.lstrip())]
    lines[index:index + 1] = [original + "\n"] + [
        indent + line + "\n" for line in additions.splitlines()
    ]
    return "".join(lines)

gui_path = w / "doda_content_gui.py"
editor_path = w / "doda_network_editor.py"
registry_path = w / "doda_page_registry.py"

gui = gui_path.read_text(encoding="utf-8-sig")
editor = editor_path.read_text(encoding="utf-8-sig")
registry = registry_path.read_text(encoding="utf-8-sig")

gui = once(
    gui, "import doda_task_flow_rules\n",
    "import doda_task_flow_rules\nimport doda_task_staffing_rules\n",
)
gui = after_statement(
    gui, "result.warnings += flow_result.warnings",
    '''staffing_result, staffing_path = doda_task_staffing_rules.export(self.project_root)
result.errors += staffing_result.errors
result.warnings += staffing_result.warnings
if staffing_path is not None:
    self.log(f"Task staffing rules exported: {staffing_path}")''',
)
gui = after_statement(
    gui, "doda_task_flow_rules.validate_flows(self.project_root, result)",
    "doda_task_staffing_rules.validate_staffing(self.project_root, result)",
)

editor = once(
    editor, "import doda_task_flow_rules as task_flow_rules\n",
    "import doda_task_flow_rules as task_flow_rules\n"
    "import doda_task_staffing_rules as task_staffing_rules\n",
)
editor = after_statement(
    editor, "task_flow_rules.validate_flows(tmp_root, res)",
    '''if (tmp_src / task_staffing_rules.STAFFING_FILE).is_file():
    task_staffing_rules.validate_staffing(tmp_root, res)''',
)

anchor = "    for e in app.network_editors:\n        e.load()\n"
editor = once(editor, anchor, '''    staffing_tab = ttk.Frame(app.notebook, padding=10)
    app.notebook.add(staffing_tab, text="Task Staffing — Editor")
    app.task_staffing_tab = staffing_tab
    app.network_editors.append(NetworkTableEditor(
        app, staffing_tab, "task_staffing_rules", "Task Staffing"))
''' + anchor)

metadata = '''
import doda_task_staffing_rules as task_staffing_rules

PAGES += (
    PageSpec("task_staffing_rules", "Tasks", "Task Staffing",
             "Task Staffing", ("task_staffing_rules",)),
)
TABLE_METADATA["task_staffing_rules"] = TableSpec(
    "task_staffing_rules", task_staffing_rules.STAFFING_FILE,
    "task_template_id+personnel_role", (
        FieldSpec("task_template_id", "Task Template", kind="task_ref"),
        FieldSpec("personnel_role", "Personnel Role", kind="choice",
                  choices=task_staffing_rules.PERSONNEL_ROLES),
        FieldSpec("min_contributors", "Minimum (blank unconfigured)",
                  kind="int", required=False),
        FieldSpec("preferred_contributors", "Preferred (blank unspecified)",
                  kind="int", required=False),
        FieldSpec("max_contributors", "Maximum (blank unspecified)",
                  kind="int", required=False),
        FieldSpec("sort_order", "Sort Order", kind="int"),
        FieldSpec("active", "Active", kind="bool"),
    ),
)

'''
registry = once(
    registry, "def page_for_tab_text(text: str) -> PageSpec | None:\n",
    metadata + "def page_for_tab_text(text: str) -> PageSpec | None:\n",
)
registry = once(
    registry, "    problems: list[str] = []\n",
    '''    problems: list[str] = []
    if TABLE_METADATA["task_staffing_rules"].columns != task_staffing_rules.COLUMNS:
        problems.append("task_staffing_rules metadata differs from validator")
''',
)

tests = '''import inspect
import unittest
import doda_task_staffing_rules as staffing
import doda_network_editor as editor
import doda_page_registry as registry


class TaskStaffingIntegrationTests(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(
            registry.TABLE_METADATA["task_staffing_rules"].columns,
            staffing.COLUMNS,
        )

    def test_composite_key(self):
        self.assertEqual(
            registry.TABLE_METADATA["task_staffing_rules"].key_columns,
            ("task_template_id", "personnel_role"),
        )

    def test_optional_counts_and_role_choices(self):
        fields = {
            field.name: field
            for field in registry.TABLE_METADATA["task_staffing_rules"].fields
        }
        for name in ("min_contributors", "preferred_contributors", "max_contributors"):
            self.assertFalse(fields[name].required)
            self.assertEqual(fields[name].kind, "int")
        self.assertEqual(fields["personnel_role"].choices, staffing.PERSONNEL_ROLES)

    def test_page_and_registry(self):
        page = registry.page_for_tab_text("Task Staffing — Editor")
        self.assertEqual(page.group, "Tasks")
        self.assertEqual(page.tables, ("task_staffing_rules",))
        self.assertEqual(registry.check_registry(), [])

    def test_editor_wiring(self):
        candidate = inspect.getsource(editor.validate_candidate)
        installer = inspect.getsource(editor.install_network_editor)
        self.assertIn("task_staffing_rules.validate_staffing(tmp_root, res)", candidate)
        self.assertIn('"task_staffing_rules", "Task Staffing"', installer)
'''

history_path = root / "docs/workbench/history/task_staffing_gui_v092.md"
history = """# Task Staffing GUI and export integration v092

- Added Tasks > Task Staffing using the shared metadata-driven editor.
- Composite key: task_template_id+personnel_role.
- Minimum, preferred, and maximum fields remain optional in draft forms.
- Candidate validation checks task staffing alongside the other saved tables.
- Validate All and rules validation include task staffing.
- Export All and rules export produce generated/data/task_staffing_rules.json.
- Existing staffing seed and all source CSVs are preserved.
- No runtime staffing allocation, task execution, or PK3 staffing payload added.

Automated acceptance: 488 baseline tests; 493 after integration.
Manual acceptance pending: page, draft validation, Validate All, Export All.
"""

targets = {
    gui_path: gui,
    editor_path: editor,
    registry_path: registry,
    w / "tests/test_task_staffing_integration.py": tests,
    history_path: history,
}
for path in list(targets)[3:]:
    if path.exists():
        raise SystemExit("STOP: New target already exists: " + str(path))
for path, text in targets.items():
    if path.suffix == ".py":
        compile(text, str(path), "exec")
        ast.parse(text)
print("Candidate syntax: PASS", flush=True)

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

if suite() != 488:
    raise SystemExit("STOP: Expected 488 baseline tests.")

source_before = {
    path: hashlib.sha256(path.read_bytes()).hexdigest()
    for path in (root / "data_authoring/source").glob("*.csv")
}
originals = {
    path: path.read_bytes() if path.exists() else None for path in targets
}
backup = w / "backups" / (
    "v092_task_staffing_gui_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)
backup.mkdir(parents=True, exist_ok=False)
print("Backup folder:", backup, flush=True)
for path, original in originals.items():
    if original is not None:
        destination = backup / path.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        print("BACKUP SHA256", hashlib.sha256(original).hexdigest(),
              path.relative_to(root), flush=True)

written = []
try:
    for path, text in targets.items():
        if path.exists() and path.read_bytes() != originals[path]:
            raise RuntimeError("File changed during preparation: " + str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
        newline = "\r\n" if originals[path] and b"\r\n" in originals[path] else "\n"
        written.append(path)
        path.write_text(text, encoding="utf-8", newline=newline)
        print("WROTE SHA256", hashlib.sha256(path.read_bytes()).hexdigest(),
              path.relative_to(root), flush=True)

    if suite() != 493:
        raise RuntimeError("Expected 493 post-change tests.")

    check_script = r'''
import csv
import json
import shutil
import tempfile
from pathlib import Path
import doda_content_gui
import doda_network_editor as editor
import doda_page_registry as registry
import doda_task_staffing_rules as staffing

root = Path(ROOT_VALUE)
assert not registry.check_registry(), registry.check_registry()
src = root / "data_authoring/source"
with (src / staffing.STAFFING_FILE).open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
result = editor.validate_candidate(root, "task_staffing_rules", rows)
assert result.valid, result.errors
bad = [dict(row) for row in rows]
bad[0]["min_contributors"] = "0"
blocked = editor.validate_candidate(root, "task_staffing_rules", bad)
assert any(
    "[task_staffing_rules]" in message and "positive whole number" in message
    for message in blocked.errors
), blocked.errors
with tempfile.TemporaryDirectory(prefix="staffing-export-check-") as directory:
    temporary = Path(directory)
    shutil.copytree(src, temporary / "data_authoring/source")
    result, path = staffing.export(temporary)
    assert result.valid and path is not None, result.errors
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["runtimeImplemented"] is False
    assert len(payload["staffingRules"]) == 1
    assert payload["staffingRules"][0]["minContributors"] == 3
print("GUI IMPORTS, REGISTRY, CANDIDATE VALIDATION AND TEMP EXPORT: PASS")
'''
    check_script = check_script.replace("ROOT_VALUE", repr(str(root)))
    check = subprocess.run(
        [sys.executable, "-c", check_script],
        cwd=w, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    print(check.stdout, flush=True)
    if check.returncode:
        raise RuntimeError(check.stderr)

    for path, digest in source_before.items():
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError("Source CSV changed during patch: " + str(path))

    print("RESULT: PASS. 493 tests; all source CSVs unchanged.", flush=True)
    print("Restart Workbench. Inspect Tasks > Task Staffing.", flush=True)
    print("Then Validate Draft, Validate All and Export All.", flush=True)
except BaseException:
    for path in reversed(written):
        original = originals[path]
        if original is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(original)
    print("PATCH ROLLED BACK: originals restored; new files removed.", flush=True)
    raise
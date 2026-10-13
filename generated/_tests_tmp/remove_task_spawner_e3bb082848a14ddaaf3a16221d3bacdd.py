import ast
import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
work = root / "tools/doda_content_workbench"
preview = work / "doda_foims_x_preview.py"
retired = [
    work / "doda_foims_x_tasks.py",
    work / "doda_foims_x_task_catalog.py",
    work / "tests/test_foims_x_tasks.py",
    work / "tests/test_foims_x_task_catalog.py",
]
test_path = work / "tests/test_removed_task_spawner.py"
history_path = root / "docs/workbench/history/Remove_Task_Spawner_2026-10-10.md"

def stop(message):
    raise SystemExit("STOP: " + message + " No patch files were modified.")

for path in [preview] + retired:
    if not path.is_file():
        stop("Missing " + str(path))
for path in (test_path, history_path):
    if path.exists():
        stop(str(path) + " already exists; do not rerun.")
    if not path.parent.is_dir():
        stop("Missing directory " + str(path.parent))

originals = {p: p.read_bytes() for p in [preview] + retired}
text = originals[preview].decode("utf-8-sig").replace("\r\n", "\n")

def once(body, old, replacement=""):
    count = body.count(old)
    if count != 1:
        stop("Expected one anchor, found %d: %s" % (count, old[:100]))
    return body.replace(old, replacement)

text = once(
    text,
    "from doda_foims_x_task_catalog import TasksCatalog\n"
)
text = once(
    text,
    "from doda_foims_x_tasks import TaskBoard\n"
)
text = once(text, "        self.task_board = TaskBoard(app.tables)\n")
text = once(
    text,
    "        self.sandbox.reset(self.app.tables)\n"
    "        self.roster.reset()\n"
    "        self.task_board.reset()\n",
    "        self.sandbox.reset(self.app.tables)\n"
    "        self.roster.reset()\n"
)

start = "        task_row = ttk.Frame(self.controls)\n"
end = "        quick = ttk.Frame(self.toolbar_frame)\n"
if text.count(start) != 1 or text.count(end) != 1:
    stop("Could not uniquely locate task controls.")
a, b = text.index(start), text.index(end)
if b <= a:
    stop("Task control boundaries are out of order.")
block = text[a:b]
for expected in (
    'text="Spawn Task"', 'text="Cancel Selected Task"',
    'text="Clear Tasks"', "self._populate_task_templates()"
):
    if expected not in block:
        stop("Task controls differ from the uploaded version.")
text = text[:a] + text[b:]

text = once(
    text,
    '        elif mode == "Tasks":\n'
    "            self._facility_catalog = TasksCatalog(\n"
    "                self.app.tables, self.task_board, self._task_now\n"
    "            )\n"
)
text = once(
    text,
    '        if hasattr(self, "task_template_combo"):\n'
    "            self._populate_task_templates()\n"
)
text = once(
    text,
    '        if self.catalog_mode.get() == "Tasks":\n'
    "            self._catalog_rows = self._facility_catalog.facilities()\n"
)

old_modes = '"Personnel", "Tasks"'
if text.count(old_modes) != 2:
    stop("Expected two screen-list references to Tasks.")
text = text.replace(old_modes, '"Personnel"')

methods_to_remove = {
    "_task_now", "_populate_task_templates", "_task_changed",
    "_task_spawn", "_task_cancel", "_task_clear",
}
tree = ast.parse(text)
classes = [
    n for n in tree.body
    if isinstance(n, ast.ClassDef) and n.name == "FoimsXPreview"
]
if len(classes) != 1:
    stop("Expected one FoimsXPreview class.")
methods = [
    n for n in classes[0].body
    if isinstance(n, ast.FunctionDef) and n.name in methods_to_remove
]
if {n.name for n in methods} != methods_to_remove or len(methods) != 6:
    stop("Task methods differ from the uploaded version.")
if any(n.decorator_list for n in methods):
    stop("Unexpected decorators on obsolete task methods.")
lines = text.splitlines(keepends=True)
for node in sorted(methods, key=lambda n: n.lineno, reverse=True):
    del lines[node.lineno - 1:node.end_lineno]
text = "".join(lines)
compile(text, str(preview), "exec")

for token in (
    "TaskBoard", "TasksCatalog", "self.task_board",
    "task_template_combo", "_task_spawn", '"Tasks"',
):
    if token in text:
        stop("Unexpected remaining task-spawner reference: " + token)

removed_count = 0
for path in retired[2:]:
    parsed = ast.parse(originals[path].decode("utf-8-sig"))
    removed_count += sum(
        isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
        for n in ast.walk(parsed)
    )
if removed_count != 16:
    stop("Expected 16 obsolete tests; found " + str(removed_count))

tests = r'''import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

WORK = Path(__file__).resolve().parents[1]
SOURCE = (WORK / "doda_foims_x_preview.py").read_text(encoding="utf-8-sig")

def cls():
    return next(
        n for n in ast.parse(SOURCE).body
        if isinstance(n, ast.ClassDef) and n.name == "FoimsXPreview"
    )

class RemovedTaskSpawnerTests(unittest.TestCase):
    def test_obsolete_files_absent(self):
        for name in (
            "doda_foims_x_" + "tasks.py",
            "doda_foims_x_" + "task_catalog.py",
            "tests/test_foims_x_" + "tasks.py",
            "tests/test_foims_x_" + "task_catalog.py",
        ):
            self.assertFalse((WORK / name).exists(), name)

    def test_no_spawner_imports_methods_or_controls(self):
        imports = {
            n.module for n in ast.walk(ast.parse(SOURCE))
            if isinstance(n, ast.ImportFrom)
        }
        self.assertNotIn("doda_foims_x_" + "tasks", imports)
        self.assertNotIn("doda_foims_x_" + "task_catalog", imports)
        methods = {n.name for n in cls().body if isinstance(n, ast.FunctionDef)}
        for name in (
            "_task_" + "now", "_task_" + "spawn", "_task_" + "cancel",
            "_task_" + "clear", "_task_" + "changed",
            "_populate_task_" + "templates",
        ):
            self.assertNotIn(name, methods)
        for label in ("Spawn " + "Task", "Cancel Selected " + "Task", "Clear " + "Tasks"):
            self.assertNotIn(label, SOURCE)

    def test_session_reset_preserves_sandbox_and_roster(self):
        node = next(
            n for n in cls().body
            if isinstance(n, ast.FunctionDef) and n.name == "_reset_simulation"
        )
        namespace = {}
        module = ast.Module(body=[node], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "preview reset", "exec"), namespace)
        tables = {}
        owner = SimpleNamespace(
            app=SimpleNamespace(tables=tables),
            sandbox=SimpleNamespace(reset=Mock()),
            roster=SimpleNamespace(reset=Mock()),
            _populate_metric_controls=Mock(),
            _facility_catalog=object(),
            _refresh_facility_catalog=Mock(),
            render=Mock(),
        )
        namespace["_reset_simulation"](owner)
        owner.sandbox.reset.assert_called_once_with(tables)
        owner.roster.reset.assert_called_once_with()
        owner._populate_metric_controls.assert_called_once_with()
        owner._refresh_facility_catalog.assert_called_once_with()
        owner.render.assert_called_once_with()

    def test_catalog_and_debug_features_preserved(self):
        for value in ('"Task Templates"', '"Personnel"', '"Facilities"', '"Qualifications"'):
            self.assertIn(value, SOURCE)
        self.assertIn("self.controls = ttk.Frame(self.debug_window", SOURCE)
        self.assertIn("self.toolbar_frame.pack_forget()", SOURCE)
        self.assertIn("command=self._roster_toggle", SOURCE)
        self.assertIn("command=self._roster_reset", SOURCE)
'''
compile(tests, str(test_path), "exec")

old = originals[preview]
encoded_text = text.replace("\n", "\r\n") if b"\r\n" in old else text
new_preview = (
    b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
) + encoded_text.encode("utf-8")

history = (
    "# Remove Incorrect Sandbox Task Spawner - 2026-10-10\n\n"
    "Removed deadline-based TaskBoard and TasksCatalog runtime modules,\n"
    "Tasks screen, task-spawning controls and six preview helper methods.\n"
    "Removed 16 tests of the rejected runtime design; added four regression\n"
    "tests of removal and retained session reset/catalog/debug behavior.\n"
    "Personnel, Debug Panel, sandbox clock/metrics/Evidence remain intact.\n"
    "Source CSVs and generated catalogs are unchanged in this block.\n"
    "Authoring schema migration follows; no runtime compatibility shim retained.\n"
)

def suite():
    done = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=work, capture_output=True, text=True, errors="replace",
    )
    output = done.stdout + done.stderr
    match = re.search(r"Ran (\d+) tests", output)
    return done.returncode, int(match.group(1)) if match else None, output

rc, baseline, output = suite()
if rc or baseline is None:
    print(output)
    stop("Baseline tests failed.")
expected = baseline - removed_count + 4
print("Baseline tests:", baseline, flush=True)
print("Retired tests:", removed_count, "| replacement tests: 4", flush=True)
print("Expected test total:", expected, flush=True)

backups = work / "backups"
numbers = [
    int(m.group(1)) for p in backups.iterdir()
    if p.is_dir() and (m := re.match(r"v(\d+)_", p.name))
]
backup = backups / (
    f"v{max(numbers, default=82)+1:03d}_remove_task_spawner_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)
manifest = []
for path, data in originals.items():
    rel = path.relative_to(root)
    target = backup / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed.")
    manifest.append(digest + "  " + rel.as_posix())
(backup / "MANIFEST.txt").write_text("\n".join(manifest) + "\n")
print("Backup folder:", backup, flush=True)

source = root / "data_authoring/source"
source_before = {p: p.read_bytes() for p in source.glob("*.csv")}

try:
    preview.write_bytes(new_preview)
    for path in retired:
        path.unlink()
    test_path.write_text(tests, encoding="utf-8", newline="\n")
    history_path.write_text(history, encoding="utf-8", newline="\n")
    rc, count, output = suite()
    print(output, flush=True)
    print("Tests after:", count, "| expected:", expected, flush=True)
    if rc or count != expected:
        raise RuntimeError("Tests failed or count changed unexpectedly.")
    if {p: p.read_bytes() for p in source.glob("*.csv")} != source_before:
        raise RuntimeError("Source CSVs changed.")
except BaseException:
    for path, data in originals.items():
        path.write_bytes(data)
    test_path.unlink(missing_ok=True)
    history_path.unlink(missing_ok=True)
    print("PATCH ROLLED BACK: preview and retired files restored.", flush=True)
    raise

print("Source CSVs unchanged.", flush=True)
print("RESULT: PASS. Old task spawner removed; restart Workbench and verify remaining screens.", flush=True)
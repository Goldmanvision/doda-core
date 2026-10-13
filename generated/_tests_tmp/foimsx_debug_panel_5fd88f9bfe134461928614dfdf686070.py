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
test = work / "tests/test_foims_x_debug_panel.py"
history = root / "docs/workbench/history/FOIMSX_Debug_Panel_2026-10-10.md"

def stop(message):
    print("STOP: " + message + " No project files were modified.", flush=True)
    sys.exit(1)

if not preview.is_file():
    stop(str(preview) + " was not found.")
for path in (test, history):
    if path.exists():
        stop(str(path) + " already exists. Verify before rerunning.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")

raw = preview.read_bytes()
original = raw.decode("utf-8-sig")
crlf = "\r\n" in original
text = original.replace("\r\n", "\n")
if "_build_debug_window" in text:
    stop("Debug panel integration appears to exist already.")
if "PersonnelCatalog" not in text:
    stop("Personnel screen patch is not installed; apply it first.")

def replace_once(body, anchor, replacement, label):
    count = body.count(anchor)
    if count != 1:
        stop("%s: expected one anchor, found %d: %s" % (label, count, anchor[:100]))
    return body.replace(anchor, replacement)

def rewrite_method(body, name, fn):
    parsed = ast.parse(body)
    classes = [n for n in parsed.body
               if isinstance(n, ast.ClassDef) and n.name == "FoimsXPreview"]
    if len(classes) != 1:
        stop("Expected one FoimsXPreview class.")
    methods = [n for n in classes[0].body
               if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(methods) != 1:
        stop("Expected one method named " + name + ".")
    method = methods[0]
    if method.decorator_list:
        stop("Unexpected decorators on " + name + ".")
    lines = body.splitlines(keepends=True)
    source = "".join(lines[method.lineno - 1:method.end_lineno])
    lines[method.lineno - 1:method.end_lineno] = [fn(source)]
    return "".join(lines)

def retarget_controls(source):
    moved = source.replace("self.controls", "self.debug_frame")
    header_old = (
        "        self.debug_frame = ttk.Frame(self.window, padding=(10, 8))\n"
        "        self.debug_frame.pack(fill=tk.X)\n"
        "        toolbar = ttk.Frame(self.debug_frame)\n"
        "        toolbar.pack(fill=tk.X)\n"
        "        controls = toolbar\n"
    )
    header_new = (
        "        self.controls = ttk.Frame(self.window, padding=(10, 4))\n"
        "        self.controls.pack(fill=tk.X)\n"
        "        toolbar = ttk.Frame(self.controls)\n"
        "        toolbar.pack(fill=tk.X)\n"
        "        controls = toolbar\n"
        "        self._build_debug_window(toolbar)\n"
    )
    if moved.count(header_old) != 1:
        stop("_build_controls header anchor not found exactly once.")
    result = moved.replace(header_old, header_new)
    if result.count("self.controls") != 4:
        stop("_build_controls retarget produced an unexpected reference count.")
    for needed in (
        "simulation_controls = ttk.Frame(self.debug_frame)",
        "metric_controls = ttk.Frame(self.debug_frame)",
        "evidence_controls = ttk.Frame(self.debug_frame)",
    ):
        if needed not in result:
            stop("Expected debug row not found: " + needed)
    return result

new_methods = '''
    def _build_debug_window(self, toolbar):
        self.debug_window = tk.Toplevel(self.window)
        self.debug_window.title("FOIMS-X Debug Panel")
        self.debug_window.geometry("900x300")
        self.debug_window.minsize(640, 220)
        self.debug_window.transient(self.window)
        self.debug_window.protocol("WM_DELETE_WINDOW", self._hide_debug)
        self.debug_window.bind("<F2>", self.toggle_debug_window)
        self.debug_frame = ttk.Frame(self.debug_window, padding=(10, 8))
        self.debug_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Button(
            toolbar, text="Debug Panel (F2)", command=self.toggle_debug_window
        ).pack(side=tk.RIGHT, padx=(0, 8))
        self.debug_window.withdraw()

    def toggle_debug_window(self, _event=None):
        if str(self.debug_window.state()) == "withdrawn":
            self.debug_window.deiconify()
            self.debug_window.lift()
        else:
            self.debug_window.withdraw()
        return "break"

    def _hide_debug(self):
        self.debug_window.withdraw()
'''

text = rewrite_method(text, "_build_controls", retarget_controls)
text = replace_once(
    text,
    "        roster_row = ttk.Frame(self.controls)\n",
    "        roster_row = ttk.Frame(self.debug_frame)\n",
    "roster row"
)
text = replace_once(
    text,
    '        self.window.bind("<F11>", self.toggle_fullscreen)\n',
    '        self.window.bind("<F11>", self.toggle_fullscreen)\n'
    '        self.window.bind("<F2>", self.toggle_debug_window)\n',
    "F2 binding"
)
text = rewrite_method(
    text, "_roster_reset",
    lambda source: source.rstrip("\n") + "\n" + new_methods
)

test_text = r'''import ast
import unittest
from pathlib import Path

PREVIEW = Path(__file__).resolve().parents[1] / "doda_foims_x_preview.py"

def source():
    return PREVIEW.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")

def method_source(name):
    body = source()
    for node in ast.walk(ast.parse(body)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return "\n".join(body.splitlines()[node.lineno - 1:node.end_lineno])
    raise AssertionError("missing method " + name)

class DebugPanelStructureTests(unittest.TestCase):
    def test_methods_exist(self):
        for name in ("_build_debug_window", "toggle_debug_window", "_hide_debug"):
            self.assertIn("def " + name, source())

    def test_debug_rows_use_debug_frame(self):
        text = method_source("_build_controls")
        for row in ("simulation_controls", "metric_controls", "evidence_controls"):
            self.assertIn(row + " = ttk.Frame(self.debug_frame)", text)

    def test_main_window_keeps_slim_controls(self):
        text = method_source("_build_controls")
        self.assertIn("self.controls = ttk.Frame(self.window", text)
        self.assertIn("self._build_debug_window(toolbar)", text)
        self.assertIn("row = ttk.Frame(self.controls)", method_source("_build_catalog_controls"))
        self.assertIn("roster_row = ttk.Frame(self.debug_frame)", method_source("_build_catalog_controls"))

    def test_f2_binding_and_start_hidden(self):
        self.assertIn('self.window.bind("<F2>", self.toggle_debug_window)', source())
        self.assertIn("self.debug_window.withdraw()", method_source("_build_debug_window"))

if __name__ == "__main__":
    unittest.main()
'''

history_text = """# FOIMS-X Debug Panel - 2026-10-10

Moved the Simulation, Sandbox metric, Sandbox Evidence and Sandbox roster
control rows into a separate Debug Panel window (F2 or toolbar button, hidden
by default, transient to the preview). The main window keeps the title
toolbar and the FOIMS-X screen/entry row. Fullscreen handling is unchanged;
the panel is destroyed with the preview window. Added 4 structural tests.
"""

for path, body in ((preview, text), (test, test_text)):
    compile(body, str(path), "exec")

backups = work / "backups"
numbers = []
if backups.exists():
    for p in backups.iterdir():
        m = re.match(r"^v(\d+)_", p.name)
        if p.is_dir() and m:
            numbers.append(int(m.group(1)))
backup = backups / (
    f"v{max(numbers, default=77)+1:03d}_foimsx_debug_panel_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)
relative = preview.relative_to(root)
target = backup / relative
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(raw)
digest = hashlib.sha256(raw).hexdigest()
if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
    stop("Backup verification failed.")
(backup / "MANIFEST.txt").write_text(
    digest + "  " + relative.as_posix() + "\n", encoding="utf-8"
)

body = text.replace("\n", "\r\n") if crlf else text
writes = {
    preview: (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"")
             + body.encode("utf-8"),
    test: test_text.encode("utf-8"),
    history: history_text.encode("utf-8"),
}
source_dir = root / "data_authoring/source"
source_before = {p: p.read_bytes() for p in source_dir.glob("*.csv")}

def rollback():
    preview.write_bytes(raw)
    for path in (test, history):
        path.unlink(missing_ok=True)

print("Backup folder:", backup, flush=True)
print("Expected test total: 418", flush=True)
try:
    for path, data in writes.items():
        path.write_bytes(data)
    suite = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, errors="replace"
    )
    print(suite.stdout, flush=True)
    print("Process exit code:", suite.returncode, flush=True)
    if suite.returncode:
        raise RuntimeError("Full test suite failed")
    if {p: p.read_bytes() for p in source_dir.glob("*.csv")} != source_before:
        raise RuntimeError("Source CSVs changed during tests")
except BaseException:
    rollback()
    print("PATCH ROLLED BACK: prior preview restored; new test and history removed.", flush=True)
    raise

print("Source CSVs unchanged.", flush=True)
print("RESULT: PASS. Restart Workbench and test the Debug Panel.", flush=True)
"""Run the metric patch with its AST fingerprint computed in the local Python runtime.
The expected model is extracted from the ORIGINAL sandbox foundation installer;
the installed model must still match. No safety check is bypassed.
"""
import argparse
import ast
import hashlib
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, default=Path(r"E:\Dev\uzdoom_src\doda-core"))
parser.add_argument("--foundation", type=Path)
parser.add_argument("--metrics", type=Path)
args = parser.parse_args()

def choose(title, filename):
    import tkinter as tk
    from tkinter import filedialog
    window = tk.Tk()
    window.withdraw()
    try:
        selected = filedialog.askopenfilename(title=title, initialfile=filename,
                                             filetypes=[("Python installers", "*.py")], parent=window)
    finally:
        window.destroy()
    if not selected:
        raise SystemExit("Cancelled. No project files were modified.")
    return Path(selected)

foundation = args.foundation or choose("1 of 2: Select ORIGINAL sandbox foundation installer", "install_foimsx_sandbox.py")
metrics = args.metrics or choose("2 of 2: Select metric controls installer", "install_foimsx_metric_activity.py")
foundation_source = foundation.read_text(encoding="utf-8-sig")
foundation_ast = ast.parse(foundation_source)
entries = [n for n in foundation_ast.body if isinstance(n, ast.Assign)
           and any(isinstance(t, ast.Name) and t.id == "MODEL_TEXT" for t in n.targets)]
if len(entries) != 1:
    raise SystemExit("STOP: First file is not the expected foundation installer. No project files were modified.")
expected_model = ast.literal_eval(entries[0].value)
if not isinstance(expected_model, str) or "class FoimsXSandbox:" not in expected_model:
    raise SystemExit("STOP: Foundation model not found. No project files were modified.")
installed = args.root / "tools/doda_content_workbench/doda_foims_x_sandbox.py"
if not installed.is_file():
    raise SystemExit("STOP: Installed sandbox model is missing. No project files were modified.")
expected_tree = ast.dump(ast.parse(expected_model), include_attributes=False)
actual_tree = ast.dump(ast.parse(installed.read_text(encoding="utf-8-sig")), include_attributes=False)
if actual_tree != expected_tree:
    raise SystemExit("STOP: Installed model really differs from the ORIGINAL installer. Attach doda_foims_x_sandbox.py. No project files were modified.")
source = metrics.read_text(encoding="utf-8-sig")
patch_tree = ast.parse(source)
assignments = [n for n in patch_tree.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "EXPECTED_MODEL_AST_SHA256" for t in n.targets)]
if len(assignments) != 1 or "PATCH_OPERATIONS" not in source:
    raise SystemExit("STOP: Second file is not the expected metric installer. No project files were modified.")
assignment = assignments[0]
old_hash = ast.literal_eval(assignment.value)
local_hash = hashlib.sha256(expected_tree.encode()).hexdigest()
assignment.value = ast.Constant(value=local_hash)
ast.fix_missing_locations(patch_tree)
print("=== COPY FROM HERE ===", flush=True)
print("Local Python:", sys.version.split()[0], flush=True)
print("Installed sandbox matches original foundation: yes", flush=True)
print("Original metric fingerprint:", old_hash, flush=True)
print("Locally computed fingerprint:", local_hash, flush=True)
if old_hash == local_hash:
    print("Fingerprint already matches; earlier STOP may have used a different installer or Python runtime.", flush=True)
print("Running original metric patch with all backup, anchor, test and rollback checks intact.", flush=True)
sys.argv = [str(metrics), "--root", str(args.root)]
exec(compile(patch_tree, str(metrics), "exec"), {"__name__": "__main__", "__file__": str(metrics)})

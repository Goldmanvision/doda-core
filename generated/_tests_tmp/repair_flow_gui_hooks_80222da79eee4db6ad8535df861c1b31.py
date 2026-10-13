import ast
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
temporary = root / "generated/_tests_tmp"
runners = sorted(
    temporary.glob("task_resource_flows_*.py"),
    key=lambda p: p.stat().st_mtime_ns,
    reverse=True,
)
if not runners:
    raise SystemExit("STOP: Saved Task Resource Flows runner not found.")

runner = runners[0]
body = runner.read_text(encoding="utf-8-sig")
tree = ast.parse(body)
updates = []

validation_anchor = "doda_resource_rules.validate_resources(self.project_root, result)"
export_anchor = "result.warnings += resource_result.warnings"

for node in tree.body:
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        continue
    target = node.targets[0]
    if not (
        isinstance(target, ast.Subscript)
        and isinstance(target.value, ast.Name)
        and target.value.id == "texts"
        and isinstance(target.slice, ast.Constant)
        and target.slice.value == "gui"
    ):
        continue
    call = node.value
    if not (
        isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == "once"
        and len(call.args) == 3
        and isinstance(call.args[1], ast.Constant)
        and isinstance(call.args[1].value, str)
    ):
        continue

    anchor = call.args[1].value.strip()
    if anchor == validation_anchor:
        extra = "doda_task_flow_rules.validate_flows(self.project_root, result)"
    elif anchor == export_anchor:
        extra = (
            "flow_result, flow_path = doda_task_flow_rules.export(self.project_root)\n"
            "result.errors += flow_result.errors\n"
            "result.warnings += flow_result.warnings\n"
            "if flow_path is not None:\n"
            '    self.log(f"Task resource flows exported: {flow_path}")'
        )
    else:
        continue

    replacement = (
        'texts["gui"] = line_hook(texts["gui"], '
        + repr(anchor) + ", " + repr(extra) + ")\n"
    )
    updates.append((node.lineno, node.end_lineno, replacement))

if len(updates) != 2:
    raise SystemExit(
        "STOP: Expected two original GUI hook instructions; found " + str(len(updates))
    )

lines = body.splitlines(keepends=True)
for first, last, replacement in sorted(updates, reverse=True):
    lines[first - 1:last] = [replacement]
body = "".join(lines)

helper = '''def line_hook(body, anchor, extra):
    lines = body.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.strip() == anchor]
    if len(matches) != 1:
        stop("Expected one complete GUI statement: " + anchor)
    index = matches[0]
    original = lines[index].rstrip("\\r\\n")
    indentation = original[:len(original) - len(original.lstrip())]
    additions = [
        indentation + line + "\\n" if line else "\\n"
        for line in extra.splitlines()
    ]
    lines[index:index + 1] = [original + "\\n"] + additions
    return "".join(lines)

'''
anchor = "def replace_function(body, name, replacement):"
if body.count(anchor) != 1:
    raise SystemExit("STOP: Could not uniquely place indentation-preserving helper.")
body = body.replace(anchor, helper + anchor)
compile(body, str(runner), "exec")
runner.write_text(body, encoding="utf-8", newline="\n")

print("Corrected GUI hooks: existing statement indentation preserved.", flush=True)
print("Rerunning:", runner.name, flush=True)
done = subprocess.run([sys.executable, str(runner), str(root)])
raise SystemExit(done.returncode)
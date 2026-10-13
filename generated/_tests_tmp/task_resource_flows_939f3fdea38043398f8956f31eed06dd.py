import ast
import csv
import io
import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
work = root / "tools/doda_content_workbench"
source = root / "data_authoring/source"
rules = work / "doda_task_flow_rules.py"
flow_csv = source / "task_template_flows.csv"
test = work / "tests/test_task_flow_rules.py"
history = root / "docs/workbench/history/Task_Resource_Flows_2026-10-10.md"
paths = {
    "registry": work / "doda_page_registry.py",
    "editor": work / "doda_network_editor.py",
    "gui": work / "doda_content_gui.py",
    "validator": work / "doda_content_workbench.py",
}

def stop(message):
    raise SystemExit("STOP: " + message + " No project files were modified.")

for p in paths.values():
    if not p.is_file():
        stop("Missing " + str(p))
for p in (rules, flow_csv, test, history):
    if p.exists() or not p.parent.is_dir():
        stop("New file exists or parent missing: " + str(p))
if not (work / "doda_task_schema.py").is_file():
    stop("Task-schema migration must be applied first.")

originals = {p: p.read_bytes() for p in paths.values()}
texts = {k: originals[p].decode("utf-8-sig").replace("\r\n", "\n")
         for k, p in paths.items()}

def once(body, old, new):
    if body.count(old) != 1:
        stop("Expected one anchor: " + old[:100])
    return body.replace(old, new)

def line_hook(body, anchor, extra):
    lines = body.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.strip() == anchor]
    if len(matches) != 1:
        stop("Expected one complete GUI statement: " + anchor)
    index = matches[0]
    original = lines[index].rstrip("\r\n")
    indentation = original[:len(original) - len(original.lstrip())]
    additions = [
        indentation + line + "\n" if line else "\n"
        for line in extra.splitlines()
    ]
    lines[index:index + 1] = [original + "\n"] + additions
    return "".join(lines)

def replace_function(body, name, replacement):
    matches = [n for n in ast.parse(body).body
               if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(matches) != 1 or matches[0].decorator_list:
        stop("Unexpected function: " + name)
    n = matches[0]
    lines = body.splitlines(keepends=True)
    lines[n.lineno - 1:n.end_lineno] = [replacement.rstrip() + "\n"]
    return "".join(lines)

rules_text = r'''"""Task resource-flow definitions; no balances or runtime execution."""
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as resources

FLOWS_FILE = "task_template_flows.csv"
FLOW_COLUMNS = [
    "task_template_id", "direction", "resource_id", "flow_mode",
    "amount", "weight", "sort_order", "active",
]
DIRECTIONS = ("IN", "OUT")
FLOW_MODES = ("FIXED", "WEIGHTED")
TOOL_VERSION = "0.1.0"

def optional_positive(raw, field, ctx, res):
    if not raw:
        return None
    value = net._int(raw, ctx, field, res)
    if value is not None and value < 1:
        res.errors.append(ctx + ": " + field + " must be positive")
        return None
    return value

def template_index(root, res):
    path = Path(root) / "data_authoring/source/task_templates.csv"
    if not path.is_file():
        res.errors.append("[task_template_flows] task_templates.csv is required")
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"task_template_id", "active"}.issubset(reader.fieldnames or []):
            res.errors.append("[task_template_flows] invalid task-template header")
            return {}
        result = {}
        for row in reader:
            key = row.get("task_template_id", "").strip()
            if not key:
                continue
            if key in result:
                res.errors.append("[task_template_flows] duplicate parent template: " + key)
            result[key] = row
        return result

def validate_flows(root, res):
    root = Path(root)
    rows = net.read_table(
        root / "data_authoring/source" / FLOWS_FILE,
        FLOW_COLUMNS, "task_template_flows", res
    )
    templates = template_index(root, res)
    resource_data = resources.validate_resources(root, res)
    resource_index = {r["resourceId"]: r for r in resource_data["resources"]}
    seen, items, groups, unfinished = set(), [], {}, set()
    for row in rows or []:
        ctx = "[task_template_flows] Line " + str(row.get("_line", "?"))
        tid, rid = row["task_template_id"], row["resource_id"]
        direction, mode = row["direction"].upper(), row["flow_mode"].upper()
        key = (tid, direction, rid)
        if key in seen:
            res.errors.append(ctx + ": duplicate template/direction/resource")
        seen.add(key)
        if direction not in DIRECTIONS:
            res.errors.append(ctx + ": direction must be IN or OUT")
        if mode not in FLOW_MODES:
            res.errors.append(ctx + ": invalid flow_mode")
        active = net._bool(row["active"], ctx, res)
        amount = optional_positive(row["amount"], "amount", ctx, res)
        weight = optional_positive(row["weight"], "weight", ctx, res)
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(ctx + ": sort_order must be nonnegative")
        parent = templates.get(tid)
        resource = resource_index.get(rid)
        if parent is None:
            res.errors.append(ctx + ": unknown task_template_id " + tid)
        elif active and parent.get("active", "").strip().upper() != "TRUE":
            res.errors.append(ctx + ": active flow needs an active parent template")
        if resource is None:
            res.errors.append(ctx + ": unknown resource_id " + rid)
        elif resource["resourceKind"] != "STOCKPILE":
            res.errors.append(ctx + ": task flows require STOCKPILE resources")
        elif active and not resource["active"]:
            res.errors.append(ctx + ": active flow needs an active resource")
        if direction == "IN" and mode != "FIXED":
            res.errors.append(ctx + ": input flows must be FIXED")
        if mode == "FIXED" and row["weight"]:
            res.errors.append(ctx + ": FIXED flow must leave weight blank")
        if active and amount is None:
            res.errors.append(ctx + ": active flow requires amount")
        if active and mode == "WEIGHTED" and weight is None:
            res.errors.append(ctx + ": active WEIGHTED flow requires weight")
        if not active and (amount is None or mode == "WEIGHTED" and weight is None):
            unfinished.add(tid)
        item = {
            "taskTemplateId": tid, "direction": direction,
            "resourceId": rid, "flowMode": mode,
            "amount": amount, "weight": weight,
            "sortOrder": order, "active": active,
        }
        items.append(item)
        if direction == "OUT":
            groups.setdefault(tid, []).append(item)
    for tid, group in groups.items():
        modes = {r["flowMode"] for r in group}
        if len(modes) > 1:
            res.errors.append(
                "[task_template_flows] " + tid +
                ": output group cannot mix FIXED and WEIGHTED rows"
            )
        if modes == {"WEIGHTED"}:
            amounts = {r["amount"] for r in group if r["amount"] is not None}
            if len(amounts) > 1:
                res.errors.append(
                    "[task_template_flows] " + tid +
                    ": weighted output rows must agree on amount (units selected)"
                )
    for tid in sorted(unfinished):
        res.warnings.append(
            "[task_template_flows] " + tid + ": draft amounts/weights unconfigured"
        )
    return {"flows": sorted(items, key=lambda r: (
        r["taskTemplateId"], r["sortOrder"] or 0, r["direction"], r["resourceId"]
    ))}

def export(root):
    root = Path(root)
    res = net.Result()
    data = validate_flows(root, res)
    if not res.valid:
        return res, None
    path = root / "generated/data/task_resource_flows.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.task_resource_flows", "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data, "runtimeImplemented": False,
        "rules": {
            "inputMode": "FIXED",
            "weightedOutputSelection": "ONE_RESOURCE_TYPE_PER_UNIT",
            "weightedAmount": "TOTAL_UNITS_SELECTED_PER_CREDIT_EVENT",
            "weightMeaning": "RELATIVE_WEIGHT_NOT_PERCENT",
            "creditTiming": "OWNED_BY_TASK_EXECUTION",
            "draftRowsExecute": False,
        },
    }
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return res, path

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "export"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "export":
        res, path = export(args.root)
    else:
        res = net.Result()
        validate_flows(args.root, res)
        path = None
    for message in res.warnings:
        print("WARNING:", message)
    for message in res.errors:
        print("ERROR:", message)
    if path:
        print("Exported:", path)
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1

if __name__ == "__main__":
    raise SystemExit(main())
'''

texts["registry"] = once(
    texts["registry"],
    "import doda_resource_rules as resource_rules\n",
    "import doda_resource_rules as resource_rules\n"
    "import doda_task_flow_rules as task_flow_rules\n"
)
metadata = '''
PAGES += (
    PageSpec("task_template_flows", "Tasks", "Task Resource Flows",
             "Task Resource Flows", ("task_template_flows",)),
)
TABLE_METADATA["task_template_flows"] = TableSpec(
    "task_template_flows", task_flow_rules.FLOWS_FILE,
    "task_template_id+direction+resource_id", (
        FieldSpec("task_template_id", "Task Template", kind="task_ref"),
        FieldSpec("direction", "Direction", kind="choice",
                  choices=task_flow_rules.DIRECTIONS),
        FieldSpec("resource_id", "Resource", kind="ref", ref_table="resources"),
        FieldSpec("flow_mode", "Flow Mode", kind="choice",
                  choices=task_flow_rules.FLOW_MODES),
        FieldSpec("amount", "Amount (blank unconfigured)", kind="int", required=False),
        FieldSpec("weight", "Relative Weight (weighted outputs)", kind="int", required=False),
        FieldSpec("sort_order", "Sort Order", kind="int"),
        FieldSpec("active", "Active", kind="bool"),
    ),
)

'''
texts["registry"] = once(
    texts["registry"], "def page_for_tab_text(",
    metadata + "def page_for_tab_text("
)
texts["registry"] = once(
    texts["registry"], "    problems: list[str] = []\n",
    "    problems: list[str] = []\n"
    '    if TABLE_METADATA["task_template_flows"].columns != task_flow_rules.FLOW_COLUMNS:\n'
    '        problems.append("task_template_flows metadata differs from validator")\n'
)

texts["editor"] = once(
    texts["editor"], "import doda_resource_rules as resource_rules\n",
    "import doda_resource_rules as resource_rules\n"
    "import doda_task_flow_rules as task_flow_rules\n"
)
texts["editor"] = replace_function(
    texts["editor"], "reference_keys",
    '''def reference_keys(source_directory, field):
    if field.kind in ("track_ref", "task_ref"):
        filename, key = (
            ("department_tracks.csv", "track_id")
            if field.kind == "track_ref"
            else ("task_templates.csv", "task_template_id")
        )
        path = source_directory / filename
        if not path.is_file():
            return []
        with path.open(encoding="utf-8-sig", newline="") as handle:
            keys = [(r.get(key) or "").strip() for r in csv.DictReader(handle)]
        return list(dict.fromkeys(k for k in keys if k))
    ref = TABLE_METADATA[field.ref_table]
    return [row[ref.key] for row in read_rows(source_directory / ref.filename, ref)]
'''
)
texts["editor"] = once(
    texts["editor"], 'elif f.kind in ("choice", "ref", "track_ref"):',
    'elif f.kind in ("choice", "ref", "track_ref", "task_ref"):'
)
texts["editor"] = once(
    texts["editor"], 'if f.kind in ("ref", "track_ref"):',
    'if f.kind in ("ref", "track_ref", "task_ref"):'
)
texts["editor"] = once(
    texts["editor"],
    "        resource_rules.validate_resources(tmp_root, res)\n",
    "        resource_rules.validate_resources(tmp_root, res)\n"
    "        task_flow_rules.validate_flows(tmp_root, res)\n"
)
texts["editor"] = once(
    texts["editor"],
    '        track_path = src / "department_tracks.csv"\n',
    '        task_path = src / "task_templates.csv"\n'
    "        if task_path.is_file():\n"
    "            shutil.copy2(task_path, tmp_src / task_path.name)\n"
    '        track_path = src / "department_tracks.csv"\n'
)
texts["editor"] = once(
    texts["editor"],
    "    for e in app.network_editors:\n",
    "    flow_tab = ttk.Frame(app.notebook, padding=10)\n"
    '    app.notebook.add(flow_tab, text="Task Resource Flows Editor")\n'
    "    app.network_editors.append(NetworkTableEditor(\n"
    '        app, flow_tab, "task_template_flows", "Task Resource Flows"\n'
    "    ))\n"
    "    for e in app.network_editors:\n"
)

texts["gui"] = once(
    texts["gui"], "import doda_resource_rules\n",
    "import doda_resource_rules\nimport doda_task_flow_rules\n"
)
texts["gui"] = line_hook(texts["gui"], 'doda_resource_rules.validate_resources(self.project_root, result)', 'doda_task_flow_rules.validate_flows(self.project_root, result)')
texts["gui"] = line_hook(texts["gui"], 'result.warnings += resource_result.warnings', 'flow_result, flow_path = doda_task_flow_rules.export(self.project_root)\nresult.errors += flow_result.errors\nresult.warnings += flow_result.warnings\nif flow_path is not None:\n    self.log(f"Task resource flows exported: {flow_path}")')

texts["validator"] = once(
    texts["validator"],
    '    validate_task_station_links(loaded_tables["task_templates"], project_root, result)\n',
    '    validate_task_station_links(loaded_tables["task_templates"], project_root, result)\n'
    '    if (source_directory / "task_template_flows.csv").is_file():\n'
    "        import doda_task_flow_rules\n"
    "        doda_task_flow_rules.validate_flows(project_root, result)\n"
)

writes = {}
def encode_like(body, raw):
    if b"\r\n" in raw:
        body = body.replace("\n", "\r\n")
    return (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + body.encode()

for key, path in paths.items():
    writes[path] = encode_like(texts[key], originals[path])

for path in work.glob("*_editor.py"):
    raw = originals.get(path, path.read_bytes())
    body = writes[path].decode("utf-8-sig").replace("\r\n", "\n") if path in writes else raw.decode("utf-8-sig").replace("\r\n", "\n")
    assignments = [n for n in ast.parse(body).body
                   if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "FILES" for t in n.targets)]
    if not assignments:
        continue
    expressions = [ast.get_source_segment(body, n.value) for n in assignments]
    if not any("task_templates.csv" in e or "TABLE_SPECS" in e for e in expressions):
        continue
    if any("task_template_flows.csv" in e for e in expressions):
        stop("Flow candidate integration already exists in " + path.name)
    lines = body.splitlines(keepends=True)
    lines.insert(assignments[-1].end_lineno,
        'FILES = tuple(dict.fromkeys(tuple(FILES) + ("resources.csv", "task_template_flows.csv")))\n')
    originals.setdefault(path, raw)
    writes[path] = encode_like("".join(lines), raw)

evidence = ("PAPER", "PHOTOGRAPHIC", "DIGITAL", "AUDIO", "VIDEO", "CHEMICAL")
rows = []
def add(tid, direction, rid, mode):
    rows.append((tid, direction, rid, mode, "", "", str(len(rows) * 10 + 10), "false"))

for kind in evidence:
    add("PROCESS_EVIDENCE_" + kind, "IN", "EVIDENCE_" + kind, "FIXED")
    add("PROCESS_EVIDENCE_" + kind, "OUT", "ADMISSIBLE_EVIDENCE", "FIXED")
for tid in ("INVESTIGATE", "UNDERCOVER_7_DAY", "UNDERCOVER_14_DAY",
            "UNDERCOVER_31_DAY", "FIELD_SURVEILLANCE"):
    for kind in evidence:
        add(tid, "OUT", "EVIDENCE_" + kind, "WEIGHTED")
add("TECH_DEVELOPMENT", "OUT", "RESEARCH_POINTS", "FIXED")

columns = ["task_template_id", "direction", "resource_id", "flow_mode",
           "amount", "weight", "sort_order", "active"]
stream = io.StringIO(newline="")
writer = csv.writer(stream, lineterminator="\n")
writer.writerow(columns)
writer.writerows(rows)

tests = r'''import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as resources
import doda_task_flow_rules as flows
from doda_page_registry import TABLE_METADATA, page_for_tab_text

class TaskFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.parent_active = "true"
        self.resource_active = "true"
        self.resource_kind = "STOCKPILE"
        self.rows = [
            dict(zip(flows.FLOW_COLUMNS,
                     ("T", "OUT", "R", "FIXED", "1", "", "10", "true")))
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, filename, columns, rows):
        with (self.src / filename).open("w", newline="") as handle:
            w = csv.DictWriter(handle, fieldnames=columns)
            w.writeheader()
            w.writerows(rows)

    def validate(self):
        self.write("task_templates.csv", ["task_template_id", "active"],
                   [{"task_template_id": "T", "active": self.parent_active}])
        self.write("resources.csv", resources.RESOURCE_COLUMNS, [
            dict(zip(resources.RESOURCE_COLUMNS,
                     ("R", "Resource", "Test resource.", self.resource_kind,
                      "false", "10", self.resource_active))),
            dict(zip(resources.RESOURCE_COLUMNS,
                     ("S", "Second", "Test resource.", "STOCKPILE",
                      "false", "20", "true"))),
        ])
        self.write(flows.FLOWS_FILE, flows.FLOW_COLUMNS, self.rows)
        result = net.Result()
        data = flows.validate_flows(self.root, result)
        return result, data

    def test_valid_fixed(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(data["flows"][0]["amount"], 1)

    def test_draft_blanks(self):
        self.rows[0].update(active="false", amount="", flow_mode="WEIGHTED", weight="")
        self.parent_active = "false"
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertIsNone(data["flows"][0]["amount"])
        self.assertTrue(result.warnings)

    def test_active_requires_values_and_parent(self):
        self.rows[0]["amount"] = ""
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["amount"] = "1"
        self.parent_active = "false"
        self.assertFalse(self.validate()[0].valid)

    def test_resource_references(self):
        self.rows[0]["resource_id"] = "MISSING"
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["resource_id"] = "R"
        self.resource_active = "false"
        self.assertFalse(self.validate()[0].valid)
        self.resource_active = "true"
        self.resource_kind = "HEADCOUNT"
        self.assertFalse(self.validate()[0].valid)

    def test_inputs_fixed_and_fixed_weight_blank(self):
        self.rows[0].update(direction="IN", flow_mode="WEIGHTED", weight="2")
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["flow_mode"] = "FIXED"
        self.assertFalse(self.validate()[0].valid)

    def test_weighted_positive_weights(self):
        self.rows[0].update(flow_mode="WEIGHTED", weight="2", amount="10")
        self.assertTrue(self.validate()[0].valid)
        self.rows[0]["weight"] = "0"
        self.assertFalse(self.validate()[0].valid)

    def test_weighted_amounts_and_modes_agree(self):
        self.rows[0].update(flow_mode="WEIGHTED", weight="2", amount="10")
        self.rows.append(dict(self.rows[0], resource_id="S", weight="3", amount="11"))
        self.assertFalse(self.validate()[0].valid)
        self.rows[1]["amount"] = "10"
        self.assertTrue(self.validate()[0].valid)
        self.rows[1].update(flow_mode="FIXED", weight="")
        self.assertFalse(self.validate()[0].valid)

    def test_duplicate_and_bad_amount(self):
        self.rows.append(dict(self.rows[0]))
        self.assertFalse(self.validate()[0].valid)
        self.rows.pop()
        self.rows[0]["amount"] = "-1"
        self.assertFalse(self.validate()[0].valid)

    def test_export_failure_preserves_output(self):
        self.validate()
        result, path = flows.export(self.root)
        self.assertTrue(result.valid)
        old = path.read_bytes()
        self.assertFalse(json.loads(old)["runtimeImplemented"])
        self.rows[0]["resource_id"] = "MISSING"
        self.validate()
        result, failed = flows.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed)
        self.assertEqual(path.read_bytes(), old)

    def test_metadata(self):
        self.assertEqual(TABLE_METADATA["task_template_flows"].columns, flows.FLOW_COLUMNS)
        self.assertEqual(TABLE_METADATA["task_template_flows"].key_columns,
                         ("task_template_id", "direction", "resource_id"))
        self.assertEqual(page_for_tab_text("Task Resource Flows Editor").group, "Tasks")
'''

writes[rules] = rules_text.encode()
writes[flow_csv] = stream.getvalue().encode()
writes[test] = tests.encode()
writes[history] = (
    "# Task Resource Flows - 2026-10-10\n\n"
    "Added 43 inactive draft flows: typed processing inputs and pooled output,\n"
    "weighted investigation/undercover/surveillance outputs and Research Points.\n"
    "Amounts and weights intentionally blank. Mission Deployment has no fixed flow.\n"
    "Metadata-driven Tasks > Task Resource Flows editor, complete candidate projects,\n"
    "core/GUI validation and rules export integrated. No runtime execution or UI layout changes.\n"
    "Export writes generated/data/task_resource_flows.json; PK3/ZScript flow lookup integration\n"
    "is not included in this authoring slice. Added 10 tests.\n"
).encode()

for path, data in writes.items():
    if path.suffix == ".py":
        compile(data.decode("utf-8-sig"), str(path), "exec")

def suite():
    done = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=work, capture_output=True, text=True, errors="replace"
    )
    output = done.stdout + done.stderr
    match = re.search(r"Ran (\d+) tests", output)
    return done.returncode, int(match.group(1)) if match else None, output

rc, baseline, output = suite()
if rc or baseline is None:
    print(output)
    stop("Baseline tests failed.")
print("Baseline tests:", baseline, flush=True)
print("Expected tests:", baseline + 10, flush=True)

backups = work / "backups"
numbers = [int(m.group(1)) for p in backups.iterdir()
           if p.is_dir() and (m := re.match(r"v(\d+)_", p.name))]
backup = backups / (
    f"v{max(numbers, default=86)+1:03d}_task_resource_flows_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)
manifest = []
for path, raw in originals.items():
    target = backup / path.relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed.")
    manifest.append(digest + "  " + path.relative_to(root).as_posix())
(backup / "MANIFEST.txt").write_text("\n".join(manifest) + "\n")
print("Backup folder:", backup, flush=True)

source_before = {p: p.read_bytes() for p in source.glob("*.csv")}
try:
    for path, data in writes.items():
        path.write_bytes(data)
    rc, count, output = suite()
    print(output, flush=True)
    print("Tests after:", count, "| expected:", baseline + 10, flush=True)
    if rc or count != baseline + 10:
        raise RuntimeError("Tests failed or count changed unexpectedly.")
    done = subprocess.run(
        [sys.executable, str(rules), "validate", "--root", str(root)],
        cwd=work, capture_output=True, text=True, errors="replace"
    )
    print(done.stdout + done.stderr, flush=True)
    if done.returncode:
        raise RuntimeError("Flow validation failed.")
    if any(p.read_bytes() != data for p, data in source_before.items()):
        raise RuntimeError("An existing source CSV changed.")
except BaseException:
    for path, raw in originals.items():
        path.write_bytes(raw)
    for path in writes:
        if path not in originals:
            path.unlink(missing_ok=True)
    print("PATCH ROLLED BACK: original code restored; new flow files removed.", flush=True)
    raise

print("Existing source CSVs unchanged; added 43 inactive draft flows.", flush=True)
print("RESULT: PASS. Restart Workbench; inspect Tasks > Task Resource Flows, then Validate All and Export All.", flush=True)
import ast
import csv
import hashlib
import io
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
work = root / "tools/doda_content_workbench"
new_paths = {
    "rules": work / "doda_resource_rules.py",
    "csv": root / "data_authoring/source/resources.csv",
    "test": work / "tests/test_resource_rules.py",
    "history": root / "docs/workbench/history/Resources_Catalog_2026-10-10.md",
}
code_paths = [
    work / "doda_page_registry.py",
    work / "doda_network_editor.py",
    work / "doda_content_gui.py",
]

def stop(message):
    raise SystemExit("STOP: " + message + " No patch files were modified.")

for p in code_paths:
    if not p.is_file():
        stop("Missing " + str(p))
for p in new_paths.values():
    if p.exists():
        stop(str(p) + " already exists; do not rerun.")
    if not p.parent.is_dir():
        stop("Missing directory " + str(p.parent))

originals = {p: p.read_bytes() for p in code_paths}
texts = {
    p: data.decode("utf-8-sig").replace("\r\n", "\n")
    for p, data in originals.items()
}
if any("doda_resource_rules" in s for s in texts.values()):
    stop("Resource integration already present.")

def once(s, old, new):
    if s.count(old) != 1:
        stop("Expected one anchor: " + old[:100])
    return s.replace(old, new)

def hook_line(s, pattern, extra):
    rx = re.compile(r"^([ \t]*)(" + pattern + r")[ \t]*$", re.M)
    matches = list(rx.finditer(s))
    if len(matches) != 1:
        stop("Expected one structural line: " + pattern)
    match = matches[0]
    indent = match.group(1)
    replacement = match.group(0) + "\n" + "\n".join(
        indent + line if line else "" for line in extra.splitlines()
    )
    return s[:match.start()] + replacement + s[match.end():]

rules = r'''"""Resource definitions only. Balances and entity counts are runtime state."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import doda_network_rules as net

TOOL_VERSION = "0.1.0"
RESOURCES_FILE = "resources.csv"
RESOURCE_COLUMNS = [
    "resource_id", "display_name", "description", "resource_kind",
    "tracks_lifetime", "sort_order", "active",
]
RESOURCE_KINDS = ("STOCKPILE", "HOLDING", "HEADCOUNT")

def validate_resources(root, res):
    path = Path(root) / "data_authoring/source" / RESOURCES_FILE
    rows = net.read_table(path, RESOURCE_COLUMNS, "resources", res)
    if rows is None:
        return {"resources": []}
    items, seen = [], set()
    for row in rows:
        ctx = "[resources] Line " + str(row.get("_line", "?"))
        rid = row["resource_id"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", rid) or rid in seen:
            res.errors.append(ctx + ": invalid or duplicate resource_id " + rid)
        seen.add(rid)
        for field in ("display_name", "description"):
            if not row[field]:
                res.errors.append(ctx + ": " + field + " is required")
        kind = row["resource_kind"].upper()
        if kind not in RESOURCE_KINDS:
            res.errors.append(ctx + ": invalid resource_kind " + kind)
        lifetime = net._bool(row["tracks_lifetime"], ctx, res)
        active = net._bool(row["active"], ctx, res)
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(ctx + ": sort_order must be nonnegative")
        if kind != "STOCKPILE" and lifetime:
            res.errors.append(ctx + ": lifetime tracking applies only to STOCKPILE")
        items.append({
            "resourceId": rid,
            "displayName": row["display_name"],
            "description": row["description"],
            "resourceKind": kind,
            "tracksLifetime": lifetime,
            "sortOrder": order,
            "active": active,
        })
    return {"resources": sorted(
        items, key=lambda r: (r["sortOrder"] or 0, r["resourceId"])
    )}

def export(root):
    root = Path(root)
    res = net.Result()
    data = validate_resources(root, res)
    if not res.valid:
        return res, None
    path = root / "generated/data/resource_catalog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.resource_catalog",
        "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data,
        "runtimeImplemented": False,
        "rules": {
            "stockpilesAreBalances": True,
            "holdingsCountOwnedEntities": True,
            "headcountsDerivedFromPersonnel": True,
            "catalogStoresNoCurrentValues": True,
            "lifetimeCountsCreditsNotCurrentBalance": True,
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
        validate_resources(args.root, res)
        path = None
    for message in res.errors:
        print("ERROR:", message)
    for message in res.warnings:
        print("WARNING:", message)
    if path:
        print("Exported:", path)
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1

if __name__ == "__main__":
    raise SystemExit(main())
'''

registry, editor, gui = code_paths
texts[registry] = once(
    texts[registry],
    "import doda_network_rules as network_rules\n",
    "import doda_network_rules as network_rules\n"
    "import doda_resource_rules as resource_rules\n"
)
metadata = '''
PAGES += (
    PageSpec("resources", "Department", "Resources", "Resources", ("resources",)),
)
TABLE_METADATA["resources"] = TableSpec(
    "resources", resource_rules.RESOURCES_FILE, "resource_id", (
        FieldSpec("resource_id", "Resource ID"),
        FieldSpec("display_name", "Display Name"),
        FieldSpec("description", "Description", multiline=True),
        FieldSpec("resource_kind", "Resource Kind", kind="choice",
                  choices=resource_rules.RESOURCE_KINDS),
        FieldSpec("tracks_lifetime", "Tracks Lifetime", kind="bool"),
        FieldSpec("sort_order", "Sort Order", kind="int"),
        FieldSpec("active", "Active", kind="bool"),
    ),
)

'''
texts[registry] = once(
    texts[registry], "def page_for_tab_text(",
    metadata + "def page_for_tab_text("
)
texts[registry] = once(
    texts[registry], "    problems: list[str] = []\n",
    "    problems: list[str] = []\n"
    '    if TABLE_METADATA["resources"].columns != resource_rules.RESOURCE_COLUMNS:\n'
    '        problems.append("resources metadata columns differ from validator")\n'
)

texts[editor] = once(
    texts[editor], "import doda_network_rules as network_rules\n",
    "import doda_network_rules as network_rules\n"
    "import doda_resource_rules as resource_rules\n"
)
texts[editor] = hook_line(
    texts[editor],
    r"authored_mission_rules\.validate_authored_missions\(tmp_root, res\)",
    "resource_rules.validate_resources(tmp_root, res)"
)
texts[editor] = hook_line(
    texts[editor],
    r"for e in app\.network_editors:",
    'resource_tab = ttk.Frame(app.notebook, padding=10)\n'
    'app.notebook.add(resource_tab, text="Resources Editor")\n'
    'app.network_editors.append(NetworkTableEditor(\n'
    '    app, resource_tab, "resources", "Resources"\n'
    '))'
)
# The hook above must be inserted BEFORE the loop, not into its body.
bad = (
    "    for e in app.network_editors:\n"
    "    resource_tab = ttk.Frame(app.notebook, padding=10)\n"
    '    app.notebook.add(resource_tab, text="Resources Editor")\n'
    "    app.network_editors.append(NetworkTableEditor(\n"
    '        app, resource_tab, "resources", "Resources"\n'
    "    ))\n"
)
good = (
    "    resource_tab = ttk.Frame(app.notebook, padding=10)\n"
    '    app.notebook.add(resource_tab, text="Resources Editor")\n'
    "    app.network_editors.append(NetworkTableEditor(\n"
    '        app, resource_tab, "resources", "Resources"\n'
    "    ))\n"
    "    for e in app.network_editors:\n"
)
texts[editor] = once(texts[editor], bad, good)

texts[gui] = once(
    texts[gui], "import doda_zscript_catalog\n",
    "import doda_zscript_catalog\nimport doda_resource_rules\n"
)
texts[gui] = hook_line(
    texts[gui],
    r"doda_authored_mission_rules\.validate_authored_missions\(self\.project_root, result\)",
    "doda_resource_rules.validate_resources(self.project_root, result)"
)
texts[gui] = hook_line(
    texts[gui],
    r"result, outpath = doda_network_rules\.export\(self\.project_root\)",
    "resource_result, resource_path = doda_resource_rules.export(self.project_root)\n"
    "result.errors += resource_result.errors\n"
    "result.warnings += resource_result.warnings\n"
    "if resource_path is not None:\n"
    '    self.log(f"Resource catalog exported: {resource_path}")'
)

seed = []
for suffix, label, description in (
    ("PAPER", "Paper Evidence", "Notes, letters, documents and receipts."),
    ("PHOTOGRAPHIC", "Photographic Evidence", "Photographs and photographic evidence."),
    ("DIGITAL", "Digital Evidence", "Computer and internet evidence."),
    ("AUDIO", "Audio Evidence", "Tapes, audio reels, CDs and other audio evidence."),
    ("VIDEO", "Video Evidence", "VHS, DVDs, film stock and other video evidence."),
    ("CHEMICAL", "Chemical Evidence", "Chemical and biological evidence."),
):
    seed.append(("EVIDENCE_" + suffix, label, description, "STOCKPILE", "false"))
seed.extend([
    ("ADMISSIBLE_EVIDENCE", "Admissible Evidence",
     "Pooled processed evidence. Lifetime credits drive mission-tier thresholds.",
     "STOCKPILE", "true"),
    ("RESEARCH_POINTS", "Research Points",
     "Tech Development output for explicitly research-unlockable equipment.",
     "STOCKPILE", "false"),
    ("DEPARTMENT_FUNDING", "Department Funding",
     "Department funds with current balance and lifetime credits.",
     "STOCKPILE", "true"),
    ("LEADS", "Leads", "Owned lead records, counted from their authoritative state.",
     "HOLDING", "false"),
    ("OPERATIONAL_TERRITORIES", "Operational Territories",
     "Owned operational territories, counted from campaign territory state.",
     "HOLDING", "false"),
    ("AGENTS", "Agents", "Current agent headcount derived from personnel records.",
     "HEADCOUNT", "false"),
    ("ANALYSTS", "Analysts", "Current analyst headcount derived from personnel records.",
     "HEADCOUNT", "false"),
    ("CONFIDENTIAL_INFORMANTS", "Confidential Informants",
     "Current confidential informant count derived from personnel records.",
     "HEADCOUNT", "false"),
])
columns = ["resource_id", "display_name", "description", "resource_kind",
           "tracks_lifetime", "sort_order", "active"]
stream = io.StringIO(newline="")
writer = csv.writer(stream, lineterminator="\n")
writer.writerow(columns)
for i, row in enumerate(seed, 1):
    writer.writerow((*row, i * 10, "true"))

tests = r'''import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as rules
from doda_page_registry import TABLE_METADATA, page_for_tab_text

class ResourceRulesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "data_authoring/source"
        self.source.mkdir(parents=True)
        self.rows = [{
            "resource_id": "ADMISSIBLE_EVIDENCE",
            "display_name": "Admissible Evidence",
            "description": "Processed evidence.",
            "resource_kind": "STOCKPILE",
            "tracks_lifetime": "true", "sort_order": "10", "active": "true",
        }]

    def tearDown(self):
        self.tmp.cleanup()

    def write(self):
        with (self.source / rules.RESOURCES_FILE).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rules.RESOURCE_COLUMNS)
            writer.writeheader()
            writer.writerows(self.rows)

    def validate(self):
        self.write()
        result = net.Result()
        data = rules.validate_resources(self.root, result)
        return result, data

    def test_valid_typed_export(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertIs(data["resources"][0]["tracksLifetime"], True)
        self.assertEqual(data["resources"][0]["sortOrder"], 10)

    def test_duplicate_and_bad_id(self):
        self.rows.append(dict(self.rows[0]))
        self.assertFalse(self.validate()[0].valid)
        self.rows = [dict(self.rows[0], resource_id="bad-id")]
        self.assertFalse(self.validate()[0].valid)

    def test_kind_and_lifetime(self):
        self.rows[0]["resource_kind"] = "HEADCOUNT"
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["tracks_lifetime"] = "false"
        self.assertTrue(self.validate()[0].valid)
        self.rows[0]["resource_kind"] = "UNKNOWN"
        self.assertFalse(self.validate()[0].valid)

    def test_invalid_fields(self):
        for field, value in (
            ("active", "maybe"), ("sort_order", "-1"),
            ("tracks_lifetime", "maybe"), ("display_name", ""),
        ):
            with self.subTest(field=field):
                before = self.rows[0][field]
                self.rows[0][field] = value
                self.assertFalse(self.validate()[0].valid)
                self.rows[0][field] = before

    def test_export_and_failed_export_preserves_file(self):
        self.write()
        result, path = rules.export(self.root)
        self.assertTrue(result.valid)
        original = path.read_bytes()
        self.assertFalse(json.loads(original)["runtimeImplemented"])
        self.rows[0]["active"] = "maybe"
        self.write()
        result, failed_path = rules.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed_path)
        self.assertEqual(path.read_bytes(), original)

    def test_metadata(self):
        self.assertEqual(TABLE_METADATA["resources"].columns, rules.RESOURCE_COLUMNS)
        self.assertEqual(page_for_tab_text("Resources Editor").group, "Department")
'''

new_data = {
    new_paths["rules"]: rules.encode(),
    new_paths["csv"]: stream.getvalue().encode(),
    new_paths["test"]: tests.encode(),
    new_paths["history"]: (
        "# Resources Catalog - 2026-10-10\n\n"
        "Added 14 resource definitions and metadata-driven Department > Resources editor.\n"
        "Candidate validation and GUI Validate All/Export All include resources.\n"
        "Export writes generated/data/resource_catalog.json; no live balances,\n"
        "PK3 integration or ZScript resource lookups in this slice.\n"
        "Existing source CSVs and FOIMS-X behavior remain unchanged.\n"
    ).encode(),
}
for p, text in texts.items():
    compile(text, str(p), "exec")
    old = originals[p]
    if b"\r\n" in old:
        text = text.replace("\n", "\r\n")
    new_data[p] = (b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b"") + text.encode()
compile(rules, str(new_paths["rules"]), "exec")
compile(tests, str(new_paths["test"]), "exec")

def suite():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=work, capture_output=True, text=True, errors="replace",
    )
    output = result.stdout + result.stderr
    match = re.search(r"Ran (\d+) tests", output)
    return result.returncode, int(match.group(1)) if match else None, output

rc, baseline, output = suite()
if rc or baseline is None:
    print(output)
    stop("Baseline tests failed.")
print("Baseline tests:", baseline, flush=True)

backups = work / "backups"
numbers = [
    int(m.group(1)) for p in backups.iterdir()
    if p.is_dir() and (m := re.match(r"v(\d+)_", p.name))
]
backup = backups / (
    f"v{max(numbers, default=80)+1:03d}_resources_catalog_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)
manifest = []
for p, data in originals.items():
    target = backup / p.relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed.")
    manifest.append(digest + "  " + p.relative_to(root).as_posix())
(backup / "MANIFEST.txt").write_text("\n".join(manifest) + "\n")
print("Backup folder:", backup, flush=True)

source = root / "data_authoring/source"
before_csv = {p: p.read_bytes() for p in source.glob("*.csv")}
try:
    for p, data in new_data.items():
        p.write_bytes(data)
    rc, count, output = suite()
    print(output, flush=True)
    print("Tests after:", count, "| expected:", baseline + 6, flush=True)
    if rc or count != baseline + 6:
        raise RuntimeError("Tests failed or count changed unexpectedly")
    done = subprocess.run(
        [sys.executable, str(new_paths["rules"]), "validate", "--root", str(root)],
        cwd=work, capture_output=True, text=True,
    )
    print(done.stdout + done.stderr, flush=True)
    if done.returncode:
        raise RuntimeError("Resource validation failed")
    if any(p.read_bytes() != data for p, data in before_csv.items()):
        raise RuntimeError("An existing source CSV changed")
except BaseException:
    for p, data in originals.items():
        p.write_bytes(data)
    for p in new_paths.values():
        p.unlink(missing_ok=True)
    print("PATCH ROLLED BACK: original code restored; new files removed.", flush=True)
    raise

print("Existing source CSVs unchanged; resources.csv added with 14 rows.", flush=True)
print("RESULT: PASS. Restart Workbench; inspect Department > Resources, then Validate All and Export All.", flush=True)
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
work = root / "tools/doda_content_workbench"
src = root / "data_authoring/source"
module = work / "doda_territory_rules.py"
registry = work / "doda_page_registry.py"
territories_csv = src / "territories.csv"
greater_csv = src / "greater_territories.csv"
label_test = work / "tests/test_greater_territory_labels.py"
table_test = work / "tests/test_greater_territory_table.py"
doc = root / "docs/workbench/spec/DESIGN_DECISIONS_2026-10-08.md"
history = root / "docs/workbench/history/Greater_Territory_Table_2026-10-08.md"

def stop(message):
    print("STOP: " + message + " No project files were modified.", flush=True)
    sys.exit(1)

for path in (module, registry, territories_csv, label_test, doc):
    if not path.is_file():
        stop(str(path) + " was not found.")
for path in (greater_csv, table_test, history):
    if path.exists():
        stop(str(path) + " already exists.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")

SOURCE = "User decision 2026-10-08 (TERR-34)"
BIOME = "Biome-like grouping label read by the mission-area map generator. "
greater_rows = [
    ("GT_UPSTATE_NEW_YORK", "Upstate New York", "10", BIOME + "Contains Ebon Falls."),
    ("GT_NEW_YORK_CITY", "New York City", "20", BIOME + "Planned. Contains Manhattan; densely populated and different in presentation from Upstate New York."),
    ("GT_NEW_MEXICO", "New Mexico", "30", BIOME + "Contains Roswell."),
    ("GT_SOUTH_CAROLINA", "South Carolina", "40", BIOME + "Contains the Savannah River Site."),
    ("GT_MARYLAND", "Maryland", "50", BIOME + "Planned. Will contain Washington D.C. and Baltimore as separate operational territories."),
    ("GT_THE_DREAMLANDS", "The Dreamlands", "60", BIOME + "Contains Unknown Kaddath."),
]
greater_columns = ["greater_territory_id", "display_name", "source_reference", "description",
                   "sort_order", "active"]
buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=greater_columns, lineterminator="\r\n")
writer.writeheader()
for gid, name, order, description in greater_rows:
    writer.writerow({"greater_territory_id": gid, "display_name": name, "source_reference": SOURCE,
                     "description": description, "sort_order": order, "active": "false"})
greater_new = buffer.getvalue().encode("utf-8")

territories_raw = territories_csv.read_bytes()
reader = csv.DictReader(io.StringIO(territories_raw.decode("utf-8-sig"), newline=""))
territory_columns = reader.fieldnames
territory_rows = list(reader)
migration = {
    "TERR_EBON_FALLS": ("Upstate New York", "GT_UPSTATE_NEW_YORK"),
    "TERR_ROSEWELL": ("New Mexico", "GT_NEW_MEXICO"),
    "TERR_SRS_NUCLEAR_FACILITY": ("South Carolina", "GT_SOUTH_CAROLINA"),
    "TERR_UNKNOWN_KADDATH": ("The Dreamlands", "GT_THE_DREAMLANDS"),
}
for territory_id, (old, new) in migration.items():
    matches = [row for row in territory_rows if row["territory_id"] == territory_id]
    if len(matches) != 1 or matches[0]["region"] != old:
        stop("Territory %s does not have region '%s'." % (territory_id, old))
    matches[0]["region"] = new
buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=territory_columns, lineterminator="\r\n")
writer.writeheader()
writer.writerows(territory_rows)
territories_new = buffer.getvalue().encode("utf-8")

module_raw = module.read_bytes()
module_original = module_raw.decode("utf-8-sig")
module_crlf = "\r\n" in module_original
text = module_original.replace("\r\n", "\n")
if "GREATER_TERRITORIES_FILE" in text:
    stop("The Greater Territory table is already installed in the module.")

def replace_once(source, anchor, replacement, label):
    count = source.count(anchor)
    if count != 1:
        stop("%s anchor found %d times: %s" % (label, count, anchor[:80]))
    return source.replace(anchor, replacement)

text = replace_once(text, 'TERRITORIES_FILE = "territories.csv"\n',
    'TERRITORIES_FILE = "territories.csv"\n'
    'GREATER_TERRITORIES_FILE = "greater_territories.csv"\n'
    'GREATER_TERRITORY_COLUMNS = ["greater_territory_id", "display_name", "source_reference", "description",\n'
    '                             "sort_order", "active"]\n', "files")
new_function = '''def _validate_greater_territories(src, res):
    path = src / GREATER_TERRITORIES_FILE
    if not path.is_file():
        return [], None
    rows = net.read_table(path, GREATER_TERRITORY_COLUMNS, "greater_territories", res) or []
    seen, names, items = set(), set(), []
    for r in rows:
        ctx = f"[greater_territories] Line {r['_line']}"
        gid = r["greater_territory_id"]
        if not gid or gid in seen:
            res.errors.append(f"{ctx}: blank or duplicate greater_territory_id '{gid}'")
            continue
        seen.add(gid)
        name = r["display_name"]
        if not name:
            res.errors.append(f"{ctx}: display_name is required")
        elif name.casefold() in names:
            res.errors.append(f"{ctx}: duplicate display_name '{name}'")
        else:
            names.add(name.casefold())
        items.append({"greaterTerritoryId": gid, "displayName": name,
                      "sourceReference": r["source_reference"] or None, "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                      "active": net._bool(r["active"], ctx, res)})
    return sorted(items, key=lambda x: (x["sortOrder"] or 0, x["greaterTerritoryId"])), seen


def _validate_territories(src, res, greater_ids=None):
'''
text = replace_once(text, "def _validate_territories(src, res):\n", new_function, "territories def")
text = replace_once(text,
    '''            res.warnings.append(f"{ctx}: hq_name '{r['hq_name']}' does not follow '<locality> DoDA Office'")\n''',
    '''            res.warnings.append(f"{ctx}: hq_name '{r['hq_name']}' does not follow '<locality> DoDA Office'")
        if greater_ids is not None and r["region"] and r["region"] not in greater_ids:
            res.errors.append(f"{ctx}: region '{r['region']}' is not a known greater_territory_id")
        if greater_ids is not None and not r["region"]:
            res.warnings.append(f"{ctx}: territory '{tid}' has no Greater Territory yet")
''', "hq warning")
text = replace_once(text, '"region": r["region"] or None,',
                    '"region": r["region"] or None, "greaterTerritoryId": r["region"] or None,', "export item")
text = replace_once(text, "    formats = _validate_formats(src, res)\n",
    "    formats = _validate_formats(src, res)\n"
    "    greater_items, greater_ids = _validate_greater_territories(src, res)\n", "formats")
text = replace_once(text, '"territories": _validate_territories(src, res),',
                    '"territories": _validate_territories(src, res, greater_ids),', "dict call")
text = replace_once(text, "    identity_files = (\n",
    '    if greater_ids is not None:\n        data["greaterTerritories"] = greater_items\n\n    identity_files = (\n',
    "identity files")
compile(text, str(module), "exec")

registry_raw = registry.read_bytes()
registry_original = registry_raw.decode("utf-8-sig")
registry_crlf = "\r\n" in registry_original
registry_lines = registry_original.replace("\r\n", "\n").split("\n")
if any("greater_territories" in line for line in registry_lines):
    stop("The registry already mentions greater_territories.")

def insert_before(lines, stripped, new_lines, label):
    found = [i for i, line in enumerate(lines) if line.strip() == stripped]
    if len(found) != 1:
        stop("Registry anchor '%s' found %d times." % (label, len(found)))
    index = found[0]
    indent = lines[index][: len(lines[index]) - len(lines[index].lstrip())]
    lines[index:index] = [indent + line if line else line for line in new_lines]

insert_before(registry_lines,
    'PageSpec("territories", "Territory and Missions", "Territories", "Territories", ("territories",)),',
    ['PageSpec("greater_territories", "Territory and Missions", "Greater Territories", "Greater Territories", ("greater_territories",)),'],
    "territories page")
insert_before(registry_lines, '"territories": TableSpec(', [
    '"greater_territories": TableSpec(',
    '    "greater_territories", territory_rules.GREATER_TERRITORIES_FILE, "greater_territory_id", (',
    '        FieldSpec("greater_territory_id", "Greater Territory ID"),',
    '        FieldSpec("display_name", "Display Name"),',
    '        FieldSpec("source_reference", "Source Reference", required=False),',
    '        FieldSpec("description", "Description", required=False, multiline=True),',
    '        FieldSpec("sort_order", "Sort Order", kind="int"),',
    '        FieldSpec("active", "Active", kind="bool"),',
    '    )),',
], "territories table")
registry_text = "\n".join(registry_lines)
registry_text = replace_once(registry_text,
    'FieldSpec("region", "Greater Territory", required=False),',
    'FieldSpec("region", "Greater Territory", kind="ref", ref_table="greater_territories", required=False),',
    "region field")
compile(registry_text, str(registry), "exec")

label_text = r'''import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net

ROOT = net.find_project_root(Path(__file__).resolve().parent)


def territories():
    path = ROOT / "data_authoring/source/territories.csv"
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {row["territory_id"]: row for row in csv.DictReader(fh)}


class GreaterTerritoryLabelTests(unittest.TestCase):
    def test_greater_territory_ids(self):
        rows = territories()
        self.assertEqual(rows["TERR_EBON_FALLS"]["region"], "GT_UPSTATE_NEW_YORK")
        self.assertEqual(rows["TERR_ROSEWELL"]["region"], "GT_NEW_MEXICO")
        self.assertEqual(rows["TERR_SRS_NUCLEAR_FACILITY"]["region"], "GT_SOUTH_CAROLINA")
        self.assertEqual(rows["TERR_UNKNOWN_KADDATH"]["region"], "GT_THE_DREAMLANDS")

    def test_descriptions_are_not_stale(self):
        for row in territories().values():
            with self.subTest(territory=row["territory_id"]):
                self.assertNotIn("HQ name is blank", row["description"])
                self.assertNotIn("HQ name and", row["description"])


if __name__ == "__main__":
    unittest.main()
'''
table_text = r'''import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net
import doda_page_registry as registry
import doda_territory_rules as terr

ROOT = net.find_project_root(Path(__file__).resolve().parent)
EXPECTED = {"GT_UPSTATE_NEW_YORK", "GT_NEW_YORK_CITY", "GT_NEW_MEXICO",
            "GT_SOUTH_CAROLINA", "GT_MARYLAND", "GT_THE_DREAMLANDS"}


def validate(root):
    result = net.Result()
    data = terr.validate_territory(root, result)
    return result, data


class GreaterTerritoryTableTests(unittest.TestCase):
    def copy_source(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / "data_authoring" / "source"
        shutil.copytree(ROOT / "data_authoring" / "source", target)
        return Path(temp.name), target

    def test_seeded_table_and_export(self):
        result, data = validate(ROOT)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual({item["greaterTerritoryId"] for item in data["greaterTerritories"]}, EXPECTED)
        for item in data["territories"]:
            self.assertIn(item["greaterTerritoryId"], EXPECTED)
            self.assertEqual(item["greaterTerritoryId"], item["region"])

    def test_unknown_reference_is_an_error(self):
        temp_root, source = self.copy_source()
        path = source / "territories.csv"
        path.write_text(path.read_text(encoding="utf-8-sig").replace("GT_NEW_MEXICO", "GT_BOGUS"),
                        encoding="utf-8", newline="")
        result, _ = validate(temp_root)
        self.assertTrue(any("not a known greater_territory_id" in e for e in result.errors))

    def test_duplicate_id_is_an_error(self):
        temp_root, source = self.copy_source()
        path = source / "greater_territories.csv"
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        lines.append(lines[1])
        path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
        result, _ = validate(temp_root)
        self.assertTrue(any("duplicate greater_territory_id" in e for e in result.errors))

    def test_editor_registers_table_and_reference(self):
        spec = registry.TABLE_METADATA["greater_territories"]
        self.assertEqual(spec.fields[0].name, "greater_territory_id")
        region = next(f for f in registry.TABLE_METADATA["territories"].fields if f.name == "region")
        self.assertEqual(region.kind, "ref")
        self.assertEqual(region.ref_table, "greater_territories")


if __name__ == "__main__":
    unittest.main()
'''
compile(label_text, str(label_test), "exec")
compile(table_text, str(table_test), "exec")

doc_raw = doc.read_bytes()
marker = "## Greater Territory table - CONFIRMED (2026-10-08)"
if marker in doc_raw.decode("utf-8-sig"):
    stop("This update is already documented.")
addendum = """
## Greater Territory table - CONFIRMED (2026-10-08)
- TERR-43: greater_territories.csv now holds the Greater Territory vocabulary: Upstate New York, New York City, New Mexico, South Carolina, Maryland, The Dreamlands. All seeded inactive. The validator rejects unknown, blank or duplicate IDs and duplicate display names.
- TERR-44: The legacy region column on territories now holds a greater_territory_id (editor field: Greater Territory, a reference). The export adds greaterTerritoryId beside region, and the catalog adds a greaterTerritories list. Renaming the column is a later patch.
- TERR-45: Maryland will contain Washington D.C. and Baltimore as separate operational territories; New York City will contain Manhattan. Those operational territories are not added yet.
- OPEN: Greater Territory tags for the procedural generator (textures, enemies, prefabs). The tag vocabulary is not defined yet.
- Authoring only. No generator behavior implemented.
"""
history_text = """# Greater Territory Table - 2026-10-08

Added greater_territories.csv with six seeded rows, validator rules, an editor
page and a reference field on territories. The region column now holds the
Greater Territory ID. Export keeps region and adds greaterTerritoryId.
Tags are pending the generator's vocabulary.
"""

backups = work / "backups"
numbers = []
if backups.exists():
    for path in backups.iterdir():
        match = re.match(r"^v(\d+)_", path.name)
        if path.is_dir() and match:
            numbers.append(int(match.group(1)))
backup = backups / (f"v{max(numbers, default=63)+1:03d}_greater_territory_table_" +
                    datetime.now().strftime("%Y%m%d_%H%M%S"))
backed_up = [(module, module_raw), (registry, registry_raw), (territories_csv, territories_raw),
             (label_test, label_test.read_bytes()), (doc, doc_raw)]
manifest = []
for path, data in backed_up:
    relative = path.relative_to(root)
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    digest = hashlib.sha256(data).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed.")
    manifest.append(f"{digest}  {relative.as_posix()}")
(backup / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

def encode(body, original_raw, use_crlf):
    out = body.replace("\n", "\r\n") if use_crlf else body
    return (b"\xef\xbb\xbf" if original_raw.startswith(b"\xef\xbb\xbf") else b"") + out.encode("utf-8")

writes = {
    module: encode(text, module_raw, module_crlf),
    registry: encode(registry_text, registry_raw, registry_crlf),
    territories_csv: territories_new,
    greater_csv: greater_new,
    label_test: label_text.encode("utf-8"),
    table_test: table_text.encode("utf-8"),
    doc: doc_raw + (("" if doc_raw.endswith(b"\n") else "\n") + addendum).encode("utf-8"),
    history: history_text.encode("utf-8"),
}
originals = {path: data for path, data in backed_up}
for new_path in (greater_csv, table_test, history):
    originals[new_path] = None

def rollback():
    for path, data in originals.items():
        if data is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(data)

try:
    for path, data in writes.items():
        path.write_bytes(data)
except Exception:
    rollback()
    raise

print("Backup folder:", backup, flush=True)
print("Expected test total: 312", flush=True)
print("--- test suite ---", flush=True)
suite = subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=work,
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
)
if suite.returncode != 0:
    rollback()
    print("TESTS FAILED. All files were restored from the originals and new files removed.", flush=True)
    print("\n".join(suite.stdout.splitlines()[-70:]), flush=True)
    sys.exit(1)
print(suite.stdout, end="", flush=True)
print("Process exit code:", suite.returncode, flush=True)

failed = 0
for label, arguments in [
    ("territory: real data", ["doda_territory_rules.py", "validate"]),
    ("territory: export", ["doda_territory_rules.py", "export"]),
]:
    print("--- " + label + " ---", flush=True)
    result = subprocess.run(
        [sys.executable, *arguments], cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
    )
    print(result.stdout, end="", flush=True)
    print("Process exit code:", result.returncode, flush=True)
    failed = failed or result.returncode
if failed:
    print("Validation failed after tests passed; patch remains applied. Paste the failure.", flush=True)
    sys.exit(failed)
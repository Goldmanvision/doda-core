import sys
from pathlib import Path

D = Path(sys.argv[1])
files = {}


def load(p):
    raw = p.read_bytes()
    text = raw.decode("utf-8-sig")
    return raw.startswith(b"\xef\xbb\xbf"), "\r\n" in text, text.replace("\r\n", "\n")


def prepare(name, marker, edits):
    path = D / name
    bom, crlf, text = load(path)
    if marker in text:
        sys.exit("STOP: %s already mentions %s. Nothing was modified." % (name, marker))
    for i, (old, new) in enumerate(edits, 1):
        n = text.count(old)
        if n != 1:
            sys.exit("STOP: %s edit %d anchor found %d times (need 1): %s. Nothing was modified." % (name, i, n, old[:60]))
        text = text.replace(old, new)
    compile(text, str(path), "exec")
    files[path] = (bom, crlf, text)


fields = [
    'FieldSpec("hostile_id", "Hostile ID")', 'FieldSpec("display_name", "Display Name")',
    'FieldSpec("engine_class", "Engine Class (optional)", required=False)',
    'FieldSpec("weapon_id", "Weapon (optional)", kind="ref", ref_table="weapons", required=False)',
    'FieldSpec("tier_id", "Mission Tier (blank for authored-only)", kind="ref", ref_table="mission_tiers", required=False)',
    'FieldSpec("authored_only", "Authored Mission Areas Only", kind="bool")',
    'FieldSpec("placeholder", "Placeholder (to be replaced)", kind="bool")',
    'FieldSpec("source_reference", "Source Reference", required=False)',
    'FieldSpec("description", "Description", required=False, multiline=True)',
    'FieldSpec("sort_order", "Sort Order", kind="int")', 'FieldSpec("active", "Active", kind="bool")']
table = '    "hostiles": TableSpec(\n        "hostiles", hostile_rules.HOSTILES_FILE, "hostile_id", (\n'
for f in fields:
    table += "            " + f + ",\n"
table += "        )),\n"

prepare("doda_page_registry.py", "hostile_rules", [
    ('import doda_weapon_rules as weapon_rules\n', 'import doda_weapon_rules as weapon_rules\nimport doda_hostile_rules as hostile_rules\n'),
    ('    PageSpec("weapons", "Territory and Missions", "Weapons", "Weapons", ("weapons",)),',
     '    PageSpec("weapons", "Territory and Missions", "Weapons", "Weapons", ("weapons",)),\n'
     '    PageSpec("hostiles", "Territory and Missions", "Hostiles", "Hostiles", ("hostiles",)),'),
    ('    "time_settings": TableSpec(', table + '    "time_settings": TableSpec('),
    ('("weapons", weapon_rules.WEAPON_COLUMNS)):',
     '("weapons", weapon_rules.WEAPON_COLUMNS),\n                       ("hostiles", hostile_rules.HOSTILE_COLUMNS)):')])

prepare("doda_network_editor.py", "hostile_rules", [
    ('import doda_weapon_rules as weapon_rules', 'import doda_weapon_rules as weapon_rules\nimport doda_hostile_rules as hostile_rules'),
    ('weapon_rules.validate_weapons(tmp_root, res)',
     'weapon_rules.validate_weapons(tmp_root, res)\n        hostile_rules.validate_hostiles(tmp_root, res)'),
    ('("weapons", "Weapons")):', '("weapons", "Weapons"),\n' + " " * 25 + '("hostiles", "Hostiles")):')])

prepare("doda_content_gui.py", "doda_hostile_rules", [
    ('import doda_weapon_rules\nimport doda_zscript_catalog', 'import doda_weapon_rules\nimport doda_hostile_rules\nimport doda_zscript_catalog'),
    ('self.log(f"Weapon catalog exported: {weapon_path}")',
     'self.log(f"Weapon catalog exported: {weapon_path}")\n'
     '                    hostile_result, hostile_path = doda_hostile_rules.export(self.project_root)\n'
     '                    result.errors += hostile_result.errors\n'
     '                    result.warnings += hostile_result.warnings\n'
     '                    if hostile_path is not None:\n'
     '                        self.log(f"Hostile catalog exported: {hostile_path}")'),
    ('doda_weapon_rules.validate_weapons(self.project_root, result)',
     'doda_weapon_rules.validate_weapons(self.project_root, result)\n'
     '                doda_hostile_rules.validate_hostiles(self.project_root, result)')])

for path, (bom, crlf, text) in files.items():
    out = text.replace("\n", "\r\n") if crlf else text
    tmp = path.with_name(path.name + ".new")
    tmp.write_bytes((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    tmp.replace(path)
    print("PATCHED", path.name)
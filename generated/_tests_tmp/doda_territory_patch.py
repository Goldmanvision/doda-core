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


def spec(table, const, key, fields):
    out = '    "%s": TableSpec(\n        "%s", %s, "%s", (\n' % (table, table, const, key)
    for f in fields:
        out += "            " + f + ",\n"
    return out + "        )),\n"


COMMON = ['FieldSpec("source_reference", "Source Reference", required=False)',
          'FieldSpec("description", "Description", required=False, multiline=True)',
          'FieldSpec("sort_order", "Sort Order", kind="int")',
          'FieldSpec("active", "Active", kind="bool")']
tables = (
    spec("territories", "territory_rules.TERRITORIES_FILE", "territory_id", [
        'FieldSpec("territory_id", "Territory ID")', 'FieldSpec("display_name", "Display Name")',
        'FieldSpec("locality", "Locality", required=False)', 'FieldSpec("region", "Region or State", required=False)',
        'FieldSpec("kind", "Kind", kind="choice", choices=territory_rules.KINDS)',
        'FieldSpec("hq_name", "HQ Name", required=False)',
        'FieldSpec("agents_allowed", "Agents Can Be Directed Here", kind="bool")',
        'FieldSpec("population", "Population (whole number)", kind="int", required=False)'] + COMMON)
    + spec("territory_settings", "territory_rules.SETTINGS_FILE", "setting_id", [
        'FieldSpec("setting_id", "Setting", kind="choice", choices=tuple(territory_rules.SETTING_UNITS))',
        'FieldSpec("display_name", "Display Name")',
        'FieldSpec("value", "Value (blank = undecided)", required=False)',
        'FieldSpec("unit", "Unit", kind="choice", choices=tuple(dict.fromkeys(territory_rules.SETTING_UNITS.values())))'] + COMMON)
    + spec("mission_tiers", "territory_rules.TIERS_FILE", "tier_id", [
        'FieldSpec("tier_id", "Tier ID")', 'FieldSpec("display_name", "Display Name")',
        'FieldSpec("min_lifetime_evidence", "Starts At Lifetime Evidence (blank = undecided)", kind="int", required=False)',
        'FieldSpec("authored_content", "Authored End-Game Content", kind="bool")'] + COMMON)
    + spec("map_formats", "territory_rules.FORMATS_FILE", "format_id", [
        'FieldSpec("format_id", "Format ID")', 'FieldSpec("display_name", "Display Name")',
        'FieldSpec("role", "Role", kind="choice", choices=territory_rules.FORMAT_ROLES)'] + COMMON)
    + spec("maps", "territory_rules.MAPS_FILE", "map_id", [
        'FieldSpec("map_id", "Map ID")',
        'FieldSpec("format_id", "Map Format", kind="ref", ref_table="map_formats")',
        'FieldSpec("display_name", "Display Name")', 'FieldSpec("has_objective", "Has an Objective", kind="bool")',
        'FieldSpec("agent_deployable", "Agents Can Be Deployed", kind="bool")'] + COMMON)
    + spec("weapons", "weapon_rules.WEAPONS_FILE", "weapon_id", [
        'FieldSpec("weapon_id", "Weapon ID")', 'FieldSpec("display_name", "Display Name")',
        'FieldSpec("weapon_type", "Weapon Type", kind="choice", choices=weapon_rules.WEAPON_TYPES)',
        'FieldSpec("engine_class", "Engine Class (optional)", required=False)',
        'FieldSpec("tags", "Tags (separate with ;)", required=False)'] + COMMON))

pages = ('("sobriety_shift_rules",)),',
         '("sobriety_shift_rules",)),\n'
         '    PageSpec("territories", "Territory and Missions", "Territories", "Territories", ("territories",)),\n'
         '    PageSpec("territory_settings", "Territory and Missions", "Territory Settings", "Territory Settings", ("territory_settings",)),\n'
         '    PageSpec("mission_tiers", "Territory and Missions", "Mission Tiers", "Mission Tiers", ("mission_tiers",)),\n'
         '    PageSpec("map_formats", "Territory and Missions", "Map Formats", "Map Formats", ("map_formats",)),\n'
         '    PageSpec("maps", "Territory and Missions", "Maps", "Maps", ("maps",)),\n'
         '    PageSpec("weapons", "Territory and Missions", "Weapons", "Weapons", ("weapons",)),')
checks = ('if TABLE_METADATA["effect_levels"].columns != rc_rules.LEVEL_COLUMNS:',
          'for name, cols in (("territories", territory_rules.TERRITORY_COLUMNS),\n'
          '                       ("territory_settings", territory_rules.SETTING_COLUMNS),\n'
          '                       ("mission_tiers", territory_rules.TIER_COLUMNS),\n'
          '                       ("map_formats", territory_rules.FORMAT_COLUMNS),\n'
          '                       ("maps", territory_rules.MAP_COLUMNS),\n'
          '                       ("weapons", weapon_rules.WEAPON_COLUMNS)):\n'
          '        if TABLE_METADATA[name].columns != cols:\n'
          '            problems.append(f"{name} metadata columns differ from validator")\n'
          '    if TABLE_METADATA["effect_levels"].columns != rc_rules.LEVEL_COLUMNS:')

prepare("doda_page_registry.py", "territory_rules", [
    ('import doda_sobriety_rules as sobriety_rules\n',
     'import doda_sobriety_rules as sobriety_rules\nimport doda_territory_rules as territory_rules\nimport doda_weapon_rules as weapon_rules\n'),
    ('"Tasks",\n    "Personnel and Care",', '"Tasks",\n    "Territory and Missions",\n    "Personnel and Care",'),
    pages, ('"time_settings": TableSpec(', tables + '    "time_settings": TableSpec('), checks])

pad = " " * 25
prepare("doda_network_editor.py", "territory_rules", [
    ('import doda_sobriety_rules as sobriety_rules',
     'import doda_sobriety_rules as sobriety_rules\nimport doda_territory_rules as territory_rules\nimport doda_weapon_rules as weapon_rules'),
    ('sobriety_rules.validate_sobriety(tmp_root, res)',
     'sobriety_rules.validate_sobriety(tmp_root, res)\n'
     '        territory_rules.validate_territory(tmp_root, res)\n'
     '        weapon_rules.validate_weapons(tmp_root, res)'),
    ('("sobriety_shift_rules", "Sobriety Shift Rules")):',
     '("sobriety_shift_rules", "Sobriety Shift Rules"),\n'
     + pad + '("territories", "Territories"),\n' + pad + '("territory_settings", "Territory Settings"),\n'
     + pad + '("mission_tiers", "Mission Tiers"),\n' + pad + '("map_formats", "Map Formats"),\n'
     + pad + '("maps", "Maps"),\n' + pad + '("weapons", "Weapons")):')])

prepare("doda_content_gui.py", "doda_territory_rules", [
    ('import doda_sobriety_rules\nimport doda_zscript_catalog',
     'import doda_sobriety_rules\nimport doda_territory_rules\nimport doda_weapon_rules\nimport doda_zscript_catalog'),
    ('self.log(f"Sobriety catalog exported: {sobriety_path}")',
     'self.log(f"Sobriety catalog exported: {sobriety_path}")\n'
     '                    territory_result, territory_path = doda_territory_rules.export(self.project_root)\n'
     '                    result.errors += territory_result.errors\n'
     '                    result.warnings += territory_result.warnings\n'
     '                    if territory_path is not None:\n'
     '                        self.log(f"Territory catalog exported: {territory_path}")\n'
     '                    weapon_result, weapon_path = doda_weapon_rules.export(self.project_root)\n'
     '                    result.errors += weapon_result.errors\n'
     '                    result.warnings += weapon_result.warnings\n'
     '                    if weapon_path is not None:\n'
     '                        self.log(f"Weapon catalog exported: {weapon_path}")'),
    ('doda_sobriety_rules.validate_sobriety(self.project_root, result)',
     'doda_sobriety_rules.validate_sobriety(self.project_root, result)\n'
     '                doda_territory_rules.validate_territory(self.project_root, result)\n'
     '                doda_weapon_rules.validate_weapons(self.project_root, result)')])

for path, (bom, crlf, text) in files.items():
    out = text.replace("\n", "\r\n") if crlf else text
    tmp = path.with_name(path.name + ".new")
    tmp.write_bytes((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    tmp.replace(path)
    print("PATCHED", path.name)
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
doc = root / "docs/workbench/spec/DESIGN_DECISIONS_2026-10-08.md"
history = root / "docs/workbench/history/Authored_Missions_And_Capstone_Chain_2026-10-08.md"
module = work / "doda_authored_mission_rules.py"
test = work / "tests/test_authored_mission_rules.py"
missions_csv = src / "authored_missions.csv"
objectives_csv = src / "authored_mission_objectives.csv"
territories_csv = src / "territories.csv"

def stop(message):
    print("STOP: " + message + " No project files were modified.", flush=True)
    sys.exit(1)

for path in (module, test, history, missions_csv, objectives_csv):
    if path.exists():
        stop(str(path) + " already exists.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")
for name in ("doda_territory_rules.py", "doda_page_registry.py",
             "doda_network_editor.py", "doda_content_gui.py"):
    if not (work / name).is_file():
        stop(name + " was not found.")
for path in (doc, territories_csv):
    if not path.is_file():
        stop(str(path) + " was not found.")

MISSION_HEADER = ("mission_id,display_name,kind,chain_id,chain_position,tier_id,unlocks_tier_id,"
                  "territory_id,map_id,player_only,source_reference,description,sort_order,active")
OBJECTIVE_HEADER = ("objective_id,mission_id,display_name,required,source_reference,"
                    "description,sort_order,active")
TERRITORY_ID = "TERR_SRS_NUCLEAR_FACILITY"
TERRITORY_COLUMNS = ["territory_id", "display_name", "locality", "region", "kind", "hq_name",
                     "agents_allowed", "population", "source_reference", "description",
                     "sort_order", "active"]

module_text = r'''"""Authored missions: plot missions and the Tier 5 capstone chain.
Authoring/export only. Campaign progress and completion are native state."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import doda_network_rules as net

TOOL_VERSION = "0.1.0"
MISSIONS_FILE = "authored_missions.csv"
OBJECTIVES_FILE = "authored_mission_objectives.csv"
MISSION_COLUMNS = [
    "mission_id", "display_name", "kind", "chain_id", "chain_position", "tier_id",
    "unlocks_tier_id", "territory_id", "map_id", "player_only", "source_reference",
    "description", "sort_order", "active",
]
OBJECTIVE_COLUMNS = [
    "objective_id", "mission_id", "display_name", "required", "source_reference",
    "description", "sort_order", "active",
]
KINDS = ("PLOT_MISSION", "TIER_CAPSTONE")
RULES = {
    "sharedTableForPlotMissionsAndCapstone": True,
    "plotMissionsPlayerOnly": True,
    "capstoneIsMissionChain": True,
    "chainPositionsContiguousFromOne": True,
    "capstoneRequiresRequiredObjectivePerMission": True,
    "tier6UnlockTrigger": "FINAL_CHAIN_MISSION_REQUIRED_OBJECTIVES_COMPLETE_PROPOSED",
    "oneLeadPurchaseUnlocksWholeChain": "PROPOSED",
    "campaignProgressIsNativeState": True,
}
OPEN_ITEMS = {
    "CAP-OPEN-01": "Confirm names and setting spelling; the real Savannah River Site is in South Carolina.",
    "CAP-OPEN-02": "Capstone territory kind (plot or player-only) and HQ name.",
    "CAP-OPEN-03": "Chain mission names, maps and authored objectives.",
    "CAP-OPEN-04": "Confirm Tier 6 unlock trigger and whether one Lead purchase unlocks the whole chain.",
}


def _lookup(src, filename, columns, key, label, res):
    path = src / filename
    if not path.is_file():
        return {}
    scratch = net.Result()
    rows = net.read_table(path, columns, label, scratch) or []
    res.errors.extend(scratch.errors)
    return {row[key]: row for row in rows if row[key]}


def _flag(row, field="active"):
    return row.get(field, "").strip().lower() in ("true", "1", "yes")


def _order(row):
    try:
        return int(row["sort_order"])
    except (KeyError, ValueError):
        return 0


def _capstone_status(missions, objectives):
    caps = [m for m in missions if m["kind"] == "TIER_CAPSTONE"]
    if not caps:
        return {"chainId": None, "missionIds": [], "unlocksTierId": None,
                "configured": False, "missingConfiguration": ["CAPSTONE_MISSION_REFERENCE"]}
    caps.sort(key=lambda m: (m["chainPosition"] or 0, m["missionId"]))
    missing = []
    if any(not m["active"] for m in caps):
        missing.append("CAPSTONE_MISSIONS_INACTIVE")
    if any(not m["mapId"] for m in caps):
        missing.append("CAPSTONE_MAPS")
    if any(not m["territoryId"] for m in caps):
        missing.append("CAPSTONE_TERRITORY")
    covered = {o["missionId"] for o in objectives if o["required"] and o["active"]}
    if any(m["missionId"] not in covered for m in caps):
        missing.append("CAPSTONE_REQUIRED_OBJECTIVES")
    return {"chainId": caps[0]["chainId"], "missionIds": [m["missionId"] for m in caps],
            "unlocksTierId": caps[-1]["unlocksTierId"],
            "configured": not missing, "missingConfiguration": missing}


def validate_authored_missions(root, res):
    src = root / "data_authoring/source"
    tiers = _lookup(src, "mission_tiers.csv", ["tier_id", "active", "sort_order"],
                    "tier_id", "mission_tiers", res)
    territories = _lookup(src, "territories.csv", ["territory_id", "active"],
                          "territory_id", "territories", res)
    maps = _lookup(src, "maps.csv", ["map_id", "active"], "map_id", "maps", res)
    missions, ids = [], set()
    for path, label in ((src / MISSIONS_FILE, "authored_missions"),
                        (src / OBJECTIVES_FILE, "authored_mission_objectives")):
        if not path.is_file():
            res.errors.append(f"[{label}] Required source file missing: {path.name}")
    mission_rows = (net.read_table(src / MISSIONS_FILE, MISSION_COLUMNS, "authored_missions", res)
                    if (src / MISSIONS_FILE).is_file() else []) or []
    objective_rows = (net.read_table(src / OBJECTIVES_FILE, OBJECTIVE_COLUMNS,
                                     "authored_mission_objectives", res)
                      if (src / OBJECTIVES_FILE).is_file() else []) or []

    for row in mission_rows:
        ctx = f"[authored_missions] Line {row['_line']}"
        mid = row["mission_id"]
        if not mid or mid in ids:
            res.errors.append(f"{ctx}: blank or duplicate mission_id '{mid}'")
            continue
        ids.add(mid)
        if not row["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        kind = row["kind"].upper()
        if kind not in KINDS:
            res.errors.append(f"{ctx}: kind must be one of {', '.join(KINDS)}")
        if not row["chain_id"]:
            res.errors.append(f"{ctx}: chain_id is required")
        position = net._int(row["chain_position"], ctx, "chain_position", res)
        if position is not None and position < 1:
            res.errors.append(f"{ctx}: chain_position must be at least 1")
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(f"{ctx}: sort_order must be nonnegative")
        active = net._bool(row["active"], ctx, res)
        player_only = net._bool(row["player_only"], ctx, res)
        if kind == "PLOT_MISSION" and not player_only:
            res.errors.append(f"{ctx}: plot missions must be player_only")
        tier, unlocks = row["tier_id"], row["unlocks_tier_id"]
        if kind == "TIER_CAPSTONE" and not tier:
            res.errors.append(f"{ctx}: a capstone mission needs tier_id")
        if tier:
            if tier not in tiers:
                res.errors.append(f"{ctx}: unknown tier_id '{tier}'")
            elif active and not _flag(tiers[tier]):
                res.errors.append(f"{ctx}: active mission uses inactive tier '{tier}'")
        if unlocks:
            if kind != "TIER_CAPSTONE":
                res.errors.append(f"{ctx}: only a capstone mission can unlock a tier")
            elif unlocks not in tiers:
                res.errors.append(f"{ctx}: unknown unlocks_tier_id '{unlocks}'")
            elif tier in tiers and _order(tiers[unlocks]) <= _order(tiers[tier]):
                res.errors.append(f"{ctx}: unlocks_tier_id must come after tier_id")
        for field, index, label in (("territory_id", territories, "territory"),
                                    ("map_id", maps, "map")):
            value = row[field]
            if not value:
                continue
            if value not in index:
                res.errors.append(f"{ctx}: unknown {field} '{value}'")
            elif active and not _flag(index[value]):
                res.errors.append(f"{ctx}: active mission uses inactive {label} '{value}'")
        if kind == "TIER_CAPSTONE" and not row["map_id"]:
            res.warnings.append(f"{ctx}: capstone mission '{mid}' has no map yet")
        missions.append({
            "missionId": mid, "displayName": row["display_name"], "kind": kind,
            "chainId": row["chain_id"], "chainPosition": position,
            "tierId": tier or None, "unlocksTierId": unlocks or None,
            "territoryId": row["territory_id"] or None, "mapId": row["map_id"] or None,
            "playerOnly": player_only, "sourceReference": row["source_reference"] or None,
            "description": row["description"], "sortOrder": order, "active": active,
        })

    chains = {}
    for mission in missions:
        chains.setdefault(mission["chainId"], []).append(mission)
    capstone_chains = [cid for cid, items in chains.items()
                       if any(m["kind"] == "TIER_CAPSTONE" for m in items)]
    if len(capstone_chains) > 1:
        res.errors.append("[authored_missions] only one capstone chain is allowed")
    for chain_id, items in chains.items():
        label = f"[authored_missions] Chain '{chain_id}'"
        if len({m["kind"] for m in items}) > 1:
            res.errors.append(f"{label}: missions in one chain must share a kind")
        positions = sorted(m["chainPosition"] for m in items if m["chainPosition"])
        if len(positions) != len(set(positions)):
            res.errors.append(f"{label}: duplicate chain_position")
        elif positions != list(range(1, len(positions) + 1)):
            res.errors.append(f"{label}: chain positions must be contiguous from 1")
        if any(m["kind"] == "TIER_CAPSTONE" for m in items):
            if len({m["tierId"] for m in items}) > 1:
                res.errors.append(f"{label}: capstone missions must share one tier_id")
            final = max((m["chainPosition"] or 0) for m in items)
            with_unlock = [m for m in items if m["unlocksTierId"]]
            if len(with_unlock) != 1 or with_unlock[0]["chainPosition"] != final:
                res.errors.append(f"{label}: exactly the final mission must set unlocks_tier_id")

    mission_index = {m["missionId"]: m for m in missions}
    objectives, objective_ids = [], set()
    for row in objective_rows:
        ctx = f"[authored_mission_objectives] Line {row['_line']}"
        oid = row["objective_id"]
        if not oid or oid in objective_ids:
            res.errors.append(f"{ctx}: blank or duplicate objective_id '{oid}'")
            continue
        objective_ids.add(oid)
        if not row["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        active = net._bool(row["active"], ctx, res)
        required = net._bool(row["required"], ctx, res)
        order = net._int(row["sort_order"], ctx, "sort_order", res)
        if order is not None and order < 0:
            res.errors.append(f"{ctx}: sort_order must be nonnegative")
        parent = mission_index.get(row["mission_id"])
        if parent is None:
            res.errors.append(f"{ctx}: unknown mission_id '{row['mission_id']}'")
        elif active and not parent["active"]:
            res.errors.append(f"{ctx}: active objective belongs to inactive mission")
        objectives.append({
            "objectiveId": oid, "missionId": row["mission_id"],
            "displayName": row["display_name"], "required": required,
            "sourceReference": row["source_reference"] or None,
            "description": row["description"], "sortOrder": order, "active": active,
        })
    return {
        "missions": sorted(missions, key=lambda m: (m["chainId"], m["chainPosition"] or 0, m["missionId"])),
        "objectives": sorted(objectives, key=lambda o: (o["missionId"], o["sortOrder"] or 0, o["objectiveId"])),
        "capstoneStatus": _capstone_status(missions, objectives),
    }


def export(root):
    res = net.Result()
    data = validate_authored_missions(root, res)
    if not res.valid:
        return res, None
    out = root / "generated/data/authored_mission_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.authored_mission_catalog", "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data, "rules": RULES, "openItems": OPEN_ITEMS, "runtimeImplemented": False,
    }
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "export"])
    parser.add_argument("--root", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else net.find_project_root(Path(__file__).parent)
    out = None
    if args.command == "export":
        res, out = export(root)
    else:
        res = net.Result()
        validate_authored_missions(root, res)
    for message in res.warnings:
        print("WARNING:", message)
    for message in res.errors:
        print("ERROR:", message)
    print("Rows:", res.stats)
    if out:
        print("Exported:", out)
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1


if __name__ == "__main__":
    sys.exit(main())
'''

test_text = r'''import ast
import csv
import json
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_authored_mission_rules as am
import doda_network_rules as net
import doda_page_registry as registry
import doda_territory_rules as terr

WORK = Path(__file__).resolve().parents[1]
ROOT = net.find_project_root(WORK)


class AuthoredMissionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.gettempdir()) / ("doda_am_" + uuid.uuid4().hex)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.write("mission_tiers.csv", ["tier_id", "active", "sort_order"], [
            {"tier_id": "TIER_5", "active": "true", "sort_order": "50"},
            {"tier_id": "TIER_6", "active": "true", "sort_order": "60"}])
        self.write("territories.csv", ["territory_id", "active"],
                   [{"territory_id": "T1", "active": "true"}])
        self.write("maps.csv", ["map_id", "active"], [{"map_id": "M1", "active": "true"}])
        self.set_missions([self.mission()])
        self.set_objectives([])

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, name, columns, rows):
        with (self.src / name).open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def mission(self, **changes):
        row = {column: "" for column in am.MISSION_COLUMNS}
        row.update(mission_id="M_1", display_name="Cap", kind="TIER_CAPSTONE",
                   chain_id="CH", chain_position="1", tier_id="TIER_5",
                   unlocks_tier_id="TIER_6", territory_id="T1", player_only="true",
                   sort_order="10", active="true")
        row.update(changes)
        return row

    def objective(self, **changes):
        row = {column: "" for column in am.OBJECTIVE_COLUMNS}
        row.update(objective_id="O_1", mission_id="M_1", display_name="Objective",
                   required="true", sort_order="10", active="true")
        row.update(changes)
        return row

    def set_missions(self, rows):
        self.write(am.MISSIONS_FILE, am.MISSION_COLUMNS, rows)

    def set_objectives(self, rows):
        self.write(am.OBJECTIVES_FILE, am.OBJECTIVE_COLUMNS, rows)

    def validate(self):
        res = net.Result()
        return res, am.validate_authored_missions(self.root, res)

    def has(self, res, text):
        return any(text in error for error in res.errors)

    def test_incomplete_capstone_is_valid_but_unconfigured(self):
        res, data = self.validate()
        self.assertTrue(res.valid, res.errors)
        self.assertTrue(any("has no map yet" in w for w in res.warnings))
        missing = data["capstoneStatus"]["missingConfiguration"]
        self.assertIn("CAPSTONE_MAPS", missing)
        self.assertIn("CAPSTONE_REQUIRED_OBJECTIVES", missing)

    def test_complete_capstone_is_configured(self):
        self.set_missions([self.mission(map_id="M1")])
        self.set_objectives([self.objective()])
        res, data = self.validate()
        self.assertTrue(res.valid, res.errors)
        self.assertTrue(data["capstoneStatus"]["configured"])
        self.assertEqual(data["capstoneStatus"]["chainId"], "CH")

    def test_no_capstone_reports_missing_reference(self):
        self.set_missions([self.mission(kind="PLOT_MISSION", unlocks_tier_id="")])
        res, data = self.validate()
        self.assertTrue(res.valid, res.errors)
        self.assertEqual(data["capstoneStatus"]["missingConfiguration"],
                         ["CAPSTONE_MISSION_REFERENCE"])

    def test_chain_gap_rejected(self):
        self.set_missions([self.mission(unlocks_tier_id=""),
                           self.mission(mission_id="M_3", chain_position="3")])
        res, _ = self.validate()
        self.assertTrue(self.has(res, "contiguous from 1"))

    def test_duplicate_position_rejected(self):
        self.set_missions([self.mission(unlocks_tier_id=""),
                           self.mission(mission_id="M_2")])
        res, _ = self.validate()
        self.assertTrue(self.has(res, "duplicate chain_position"))

    def test_unlock_only_on_final_mission(self):
        self.set_missions([self.mission(),
                           self.mission(mission_id="M_2", chain_position="2", unlocks_tier_id="")])
        res, _ = self.validate()
        self.assertTrue(self.has(res, "exactly the final mission"))

    def test_plot_mission_rules(self):
        self.set_missions([self.mission(kind="PLOT_MISSION", player_only="false",
                                        unlocks_tier_id="")])
        res, _ = self.validate()
        self.assertTrue(self.has(res, "plot missions must be player_only"))
        self.set_missions([self.mission(kind="PLOT_MISSION")])
        res, _ = self.validate()
        self.assertTrue(self.has(res, "only a capstone mission can unlock a tier"))

    def test_unknown_references(self):
        self.set_missions([self.mission(territory_id="NOPE", map_id="NOPE", tier_id="NOPE")])
        res, _ = self.validate()
        for text in ("unknown territory_id", "unknown map_id", "unknown tier_id"):
            self.assertTrue(self.has(res, text), text)

    def test_unlock_must_follow_tier(self):
        self.set_missions([self.mission(unlocks_tier_id="TIER_5")])
        res, _ = self.validate()
        self.assertTrue(self.has(res, "must come after tier_id"))

    def test_objective_rules(self):
        self.set_objectives([self.objective(mission_id="NOPE"), self.objective()])
        res, _ = self.validate()
        self.assertTrue(self.has(res, "unknown mission_id"))
        self.set_objectives([self.objective(), self.objective()])
        res, _ = self.validate()
        self.assertTrue(self.has(res, "duplicate objective_id"))

    def test_two_capstone_chains_rejected(self):
        self.set_missions([self.mission(), self.mission(mission_id="M_2", chain_id="OTHER")])
        res, _ = self.validate()
        self.assertTrue(self.has(res, "only one capstone chain"))

    def test_export_is_not_runtime(self):
        res, out = am.export(self.root)
        self.assertTrue(res.valid, res.errors)
        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(payload["runtimeImplemented"])
        self.assertTrue(payload["rules"]["campaignProgressIsNativeState"])

    def test_shipped_authoring_data(self):
        res = net.Result()
        data = am.validate_authored_missions(ROOT, res)
        self.assertTrue(res.valid, res.errors)
        status = data["capstoneStatus"]
        self.assertEqual(status["chainId"], "CHAIN_TIER5_CAPSTONE")
        self.assertFalse(status["configured"])
        self.assertIn("CAPSTONE_MAPS", status["missingConfiguration"])

    def test_registry_columns_match(self):
        self.assertEqual(registry.TABLE_METADATA["authored_missions"].columns, am.MISSION_COLUMNS)
        self.assertEqual(registry.TABLE_METADATA["authored_mission_objectives"].columns,
                         am.OBJECTIVE_COLUMNS)

    def test_territory_export_names_capstone_chain(self):
        res = net.Result()
        data = terr.validate_territory(ROOT, res)
        self.assertTrue(res.valid, res.errors)
        gate = data["missionProgression"]["finalGate"]
        self.assertEqual(gate["capstoneMissionReference"], "CHAIN_TIER5_CAPSTONE")
        self.assertNotIn("CAPSTONE_MISSION_REFERENCE", gate["missingConfiguration"])
        self.assertFalse(gate["configured"])
        self.assertFalse(gate["isCampaignEligibilityResult"])

    def test_gui_calls_present(self):
        tree = ast.parse((WORK / "doda_content_gui.py").read_text(encoding="utf-8-sig"))
        methods = {
            node.func.attr for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "doda_authored_mission_rules"
        }
        self.assertTrue({"validate_authored_missions", "export"}.issubset(methods))


if __name__ == "__main__":
    unittest.main()
'''
compile(module_text, str(module), "exec")
compile(test_text, str(test), "exec")

prepared, originals = {}, {}

def prepare(path, edits):
    raw = path.read_bytes()
    original = raw.decode("utf-8-sig")
    text = original.replace("\r\n", "\n")
    if "authored_mission_rules" in text:
        stop(path.name + " already mentions authored_mission_rules.")
    for anchor, replacement in edits:
        count = text.count(anchor)
        if count != 1:
            stop("%s: anchor found %d times: %s" % (path.name, count, anchor[:90]))
        text = text.replace(anchor, replacement)
    compile(text, str(path), "exec")
    if "\r\n" in original:
        text = text.replace("\n", "\r\n")
    prepared[path] = (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + text.encode("utf-8")
    originals[path] = raw

common = [
    'FieldSpec("source_reference", "Source Reference", required=False)',
    'FieldSpec("description", "Description", required=False, multiline=True)',
    'FieldSpec("sort_order", "Sort Order", kind="int")',
    'FieldSpec("active", "Active", kind="bool")',
]

def table(name, filename, key, fields):
    lines = ['    "%s": TableSpec(' % name,
             '        "%s", authored_mission_rules.%s, "%s", (' % (name, filename, key)]
    lines.extend("            " + field + "," for field in fields + common)
    lines.append("        )),")
    return "\n".join(lines) + "\n"

tables = (
    table("authored_missions", "MISSIONS_FILE", "mission_id", [
        'FieldSpec("mission_id", "Mission ID")',
        'FieldSpec("display_name", "Display Name")',
        'FieldSpec("kind", "Kind", kind="choice", choices=authored_mission_rules.KINDS)',
        'FieldSpec("chain_id", "Chain ID")',
        'FieldSpec("chain_position", "Chain Position (1 = first)", kind="int")',
        'FieldSpec("tier_id", "Mission Tier", kind="ref", ref_table="mission_tiers", required=False)',
        'FieldSpec("unlocks_tier_id", "Unlocks Tier (final mission only)", kind="ref", ref_table="mission_tiers", required=False)',
        'FieldSpec("territory_id", "Territory", kind="ref", ref_table="territories", required=False)',
        'FieldSpec("map_id", "Map (blank until authored)", kind="ref", ref_table="maps", required=False)',
        'FieldSpec("player_only", "Player Only", kind="bool")',
    ])
    + table("authored_mission_objectives", "OBJECTIVES_FILE", "objective_id", [
        'FieldSpec("objective_id", "Objective ID")',
        'FieldSpec("mission_id", "Mission", kind="ref", ref_table="authored_missions")',
        'FieldSpec("display_name", "Display Name")',
        'FieldSpec("required", "Required For Completion", kind="bool")',
    ])
)
pages = "\n".join(
    '    PageSpec("%s", "Territory and Missions", "%s", "%s", ("%s",)),' % (name, title, title, name)
    for name, title in (("authored_missions", "Authored Missions"),
                        ("authored_mission_objectives", "Mission Objectives"))
)
last_page = ('    PageSpec("mission_tier_requirements", "Territory and Missions", '
             '"Mission Tier Requirements", "Mission Tier Requirements", ("mission_tier_requirements",)),')

prepare(work / "doda_page_registry.py", [
    ("import doda_progression_identity_rules as progression_identity_rules\n",
     "import doda_progression_identity_rules as progression_identity_rules\n"
     "import doda_authored_mission_rules as authored_mission_rules\n"),
    (last_page, last_page + "\n" + pages),
    ('    "time_settings": TableSpec(', tables + '    "time_settings": TableSpec('),
    ('("mission_tier_requirements", progression_identity_rules.REQUIREMENT_COLUMNS)):',
     '("mission_tier_requirements", progression_identity_rules.REQUIREMENT_COLUMNS),\n'
     '                       ("authored_missions", authored_mission_rules.MISSION_COLUMNS),\n'
     '                       ("authored_mission_objectives", authored_mission_rules.OBJECTIVE_COLUMNS)):'),
])

pad = " " * 25
prepare(work / "doda_network_editor.py", [
    ("import doda_progression_identity_rules as progression_identity_rules",
     "import doda_progression_identity_rules as progression_identity_rules\n"
     "import doda_authored_mission_rules as authored_mission_rules"),
    ("progression_identity_rules.validate_identities(tmp_root, res)",
     "progression_identity_rules.validate_identities(tmp_root, res)\n"
     "        authored_mission_rules.validate_authored_missions(tmp_root, res)"),
    ('("mission_tier_requirements", "Mission Tier Requirements")):',
     '("mission_tier_requirements", "Mission Tier Requirements"),\n'
     + pad + '("authored_missions", "Authored Missions"),\n'
     + pad + '("authored_mission_objectives", "Mission Objectives")):'),
])

prepare(work / "doda_content_gui.py", [
    ("import doda_progression_identity_rules\nimport doda_zscript_catalog",
     "import doda_progression_identity_rules\nimport doda_authored_mission_rules\n"
     "import doda_zscript_catalog"),
    ('self.log(f"Progression identity catalog exported: {identity_path}")',
     'self.log(f"Progression identity catalog exported: {identity_path}")\n'
     '                    mission_result, mission_path = doda_authored_mission_rules.export(self.project_root)\n'
     '                    result.errors += mission_result.errors\n'
     '                    result.warnings += mission_result.warnings\n'
     '                    if mission_path is not None:\n'
     '                        self.log(f"Authored mission catalog exported: {mission_path}")'),
    ("doda_progression_identity_rules.validate_identities(self.project_root, result)",
     "doda_progression_identity_rules.validate_identities(self.project_root, result)\n"
     "                doda_authored_mission_rules.validate_authored_missions(self.project_root, result)"),
])

prepare(work / "doda_territory_rules.py", [
    ("import doda_progression_identity_rules as progression_identity_rules\n",
     "import doda_progression_identity_rules as progression_identity_rules\n"
     "import doda_authored_mission_rules as authored_mission_rules\n"),
    ('        data["progressionIdentities"] = progression_identity_rules.validate_identities(root, res)\n',
     '        data["progressionIdentities"] = progression_identity_rules.validate_identities(root, res)\n'
     '    authored_files = (authored_mission_rules.MISSIONS_FILE, authored_mission_rules.OBJECTIVES_FILE)\n'
     '    if any((src / name).is_file() for name in authored_files):\n'
     '        data["authoredMissions"] = authored_mission_rules.validate_authored_missions(root, res)\n'),
    ('    missing_gate.append("CAPSTONE_MISSION_REFERENCE")\n',
     '    capstone_status = (data.get("authoredMissions") or {}).get("capstoneStatus")\n'
     '    if capstone_status is None:\n'
     '        missing_gate.append("CAPSTONE_MISSION_REFERENCE")\n'
     '        capstone_chain = None\n'
     '    else:\n'
     '        missing_gate.extend(capstone_status["missingConfiguration"])\n'
     '        capstone_chain = capstone_status["chainId"]\n'),
    ('            "isCampaignEligibilityResult": False,\n            "numericSettings":',
     '            "capstoneMissionReference": capstone_chain,\n'
     '            "capstoneStatus": capstone_status,\n'
     '            "isCampaignEligibilityResult": False,\n            "numericSettings":'),
    ('"contractVersion": "2026-10-08.2",', '"contractVersion": "2026-10-08.3",'),
    ('"capstoneMissionReference": None,',
     '"capstoneMissionReferenceSource": "missionProgression.finalGate.capstoneMissionReference",'),
])

territory_raw = territories_csv.read_bytes()
reader = csv.DictReader(io.StringIO(territory_raw.decode("utf-8-sig"), newline=""))
if reader.fieldnames != TERRITORY_COLUMNS:
    stop("territories.csv has an unexpected header.")
if any(row["territory_id"] == TERRITORY_ID for row in reader):
    stop("The capstone territory already exists.")
new_row = {column: "" for column in TERRITORY_COLUMNS}
new_row.update(
    territory_id=TERRITORY_ID,
    display_name="Savanah River Site Nuclear Research Facility, Savanah River, Georgia",
    locality="Savanah River", region="Georgia", kind="PLOT", agents_allowed="true",
    source_reference="User decision 2026-10-08 (CAP-02)",
    description="Authored territory for the Tier 5 capstone chain. Kind and agent access are assumptions pending confirmation; HQ undecided.",
    sort_order="40", active="false",
)
buffer = io.StringIO(newline="")
csv.DictWriter(buffer, fieldnames=TERRITORY_COLUMNS, lineterminator="\r\n").writerow(new_row)
territory_new = territory_raw + (b"" if territory_raw.endswith(b"\n") else b"\r\n") + buffer.getvalue().encode("utf-8")
originals[territories_csv] = territory_raw

seed = {column: "" for column in (MISSION_HEADER.split(","))}
seed.update(
    mission_id="MISSION_TIER5_CAPSTONE_01",
    display_name="Savanah River Site Nuclear Research Facility, Georgia",
    kind="TIER_CAPSTONE", chain_id="CHAIN_TIER5_CAPSTONE", chain_position="1",
    tier_id="TIER_5", unlocks_tier_id="TIER_6", territory_id=TERRITORY_ID, map_id="",
    player_only="true", source_reference="User decision 2026-10-08 (CAP-01 to CAP-05)",
    description="First mission of the Tier 5 capstone chain. Map, objectives and further chain missions are not yet designed.",
    sort_order="10", active="false",
)
buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=MISSION_HEADER.split(","), lineterminator="\r\n")
writer.writeheader()
writer.writerow(seed)
missions_text = buffer.getvalue()

doc_raw = doc.read_bytes()
marker = "## Authored missions and capstone chain - CONFIRMED (2026-10-08)"
if marker in doc_raw.decode("utf-8-sig"):
    stop("The capstone chain is already documented.")
addendum = """
## Authored missions and capstone chain - CONFIRMED (2026-10-08)
- CAP-01: Plot missions and the Tier 5 capstone share one authored_missions table, separated by kind.
- CAP-02: The capstone is named "Savanah River Site Nuclear Research Facility, Georgia" (as written). It lives in a new authored territory, "Savanah River Site Nuclear Research Facility, Savanah River, Georgia" - not Rosewell and not a random territory.
- CAP-03: The capstone map stays blank; the mission has not been designed.
- CAP-04: Objectives are a separate table. Each capstone mission needs at least one active required objective before the final gate counts as configured.
- CAP-05: The capstone is a chain of missions, not a single mission.

### Assumptions recorded as OPEN (not confirmed)
- CAP-OPEN-01: The real Savannah River Site has two n's and is in South Carolina. Names are stored as written; confirm spelling and state.
- CAP-OPEN-02: The new territory is seeded as kind PLOT with agents allowed and no HQ. Confirm plot versus player-only.
- CAP-OPEN-03: Tier 6 unlocks when the final chain mission's required objectives complete (unlocks_tier_id sits on the final position only).
- CAP-OPEN-04: One capstone Lead purchase unlocks the whole chain with no further purchases. Capstone missions are player-only.

### Implementation status
- Authoring/export only. Added authored_missions.csv (one inactive seed), authored_mission_objectives.csv (empty), the new territory row, and two editor pages.
- The territory final gate now exports capstoneMissionReference and capstoneStatus. Missing map, objectives or inactive status keep the gate unconfigured.
- Contract version 2026-10-08.3. No campaign behavior implemented.
"""
history_text = """# Authored Missions and Capstone Chain - 2026-10-08

Authoring/export only. Added doda_authored_mission_rules.py, authored_missions.csv
(one inactive capstone seed), authored_mission_objectives.csv (empty), a new
authored territory row, two editor pages, GUI validate/export wiring and tests.

The territory contract now derives the capstone reference and its blockers from
the authored chain. Names are stored exactly as written; open items record the
real-world spelling/state difference and unconfirmed assumptions.
Backups are numbered with SHA-256 manifests.
"""

backups = work / "backups"
numbers = []
if backups.exists():
    for path in backups.iterdir():
        match = re.match(r"^v(\d+)_", path.name)
        if path.is_dir() and match:
            numbers.append(int(match.group(1)))
backup = backups / (f"v{max(numbers, default=57)+1:03d}_authored_missions_" +
                    datetime.now().strftime("%Y%m%d_%H%M%S"))
originals[doc] = doc_raw
manifest = []
for path, raw in originals.items():
    relative = path.relative_to(root)
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    digest = hashlib.sha256(raw).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed.")
    manifest.append(f"{digest}  {relative.as_posix()}")
(backup / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

writes = dict(prepared)
writes.update({
    territories_csv: territory_new,
    module: module_text.encode("utf-8"),
    test: test_text.encode("utf-8"),
    missions_csv: missions_text.encode("utf-8"),
    objectives_csv: (OBJECTIVE_HEADER + "\r\n").encode("utf-8"),
    history: history_text.encode("utf-8"),
    doc: doc_raw + (("" if doc_raw.endswith(b"\n") else "\n") + addendum).encode("utf-8"),
})
for path in (module, test, missions_csv, objectives_csv, history):
    originals[path] = None
try:
    for path, data in writes.items():
        path.write_bytes(data)
except Exception:
    for path, data in originals.items():
        if data is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(data)
    raise

print("Backup folder:", backup, flush=True)
print("Authored missions installed; seed mission: 1; territory added: 1; new tests: 17", flush=True)
for label, arguments in [
    ("test suite", ["-m", "unittest", "discover", "-s", "tests"]),
    ("authored missions: real data", ["doda_authored_mission_rules.py", "validate"]),
    ("territory: real data", ["doda_territory_rules.py", "validate"]),
]:
    print("--- " + label + " ---", flush=True)
    result = subprocess.run(
        [sys.executable, *arguments], cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, errors="replace",
    )
    print(result.stdout, end="", flush=True)
    print("Process exit code:", result.returncode, flush=True)
    if result.returncode:
        print("Patch remains applied; do not rerun. Paste the failure.", flush=True)
        sys.exit(result.returncode)
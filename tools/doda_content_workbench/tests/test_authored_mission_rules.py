import ast
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

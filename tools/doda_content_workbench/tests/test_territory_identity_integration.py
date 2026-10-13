import csv
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import doda_network_rules as net
import doda_territory_rules as terr
import doda_progression_identity_rules as pid
import test_territory_rules as base


class TerritoryIdentityIntegrationTests(unittest.TestCase):
    setUp = base.TerritoryTests.setUp
    tearDown = base.TerritoryTests.tearDown
    make_root = base.TerritoryTests.make_root

    def write(self, root, filename, columns, rows):
        path = root / "data_authoring/source" / filename
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def row(self, columns, **changes):
        row = {column: "" for column in columns}
        row.update(sort_order="10", active="true")
        row.update(changes)
        return row

    def fixture(self, populated=False, requirements_active=True):
        tiers = [
            base._row(terr.TIER_COLUMNS, tier_id="TIER_1", display_name="One",
                      min_lifetime_admissible_evidence="0", authored_content="false",
                      sort_order="10", active="true"),
            base._row(terr.TIER_COLUMNS, tier_id="TIER_5", display_name="Five",
                      min_lifetime_admissible_evidence="100", authored_content="false",
                      sort_order="50", active="true"),
            base._row(terr.TIER_COLUMNS, tier_id="TIER_6", display_name="Six",
                      min_lifetime_admissible_evidence="1000", authored_content="true",
                      sort_order="60", active="true"),
        ]
        root = self.make_root(tiers=tiers)
        upgrades, milestones, requirements = [], [], []
        if populated:
            upgrades = [self.row(pid.UPGRADE_COLUMNS, upgrade_id="UP_TEST", display_name="Upgrade")]
            milestones = [self.row(pid.MILESTONE_COLUMNS, milestone_id="PLOT_TEST", display_name="Milestone")]
            active = "true" if requirements_active else "false"
            requirements = [
                self.row(pid.REQUIREMENT_COLUMNS, requirement_id="REQ_UP",
                         tier_id="TIER_6", upgrade_id="UP_TEST", active=active),
                self.row(pid.REQUIREMENT_COLUMNS, requirement_id="REQ_PLOT",
                         tier_id="TIER_6", milestone_id="PLOT_TEST",
                         sort_order="20", active=active),
            ]
        self.write(root, pid.UPGRADES_FILE, pid.UPGRADE_COLUMNS, upgrades)
        self.write(root, pid.MILESTONES_FILE, pid.MILESTONE_COLUMNS, milestones)
        self.write(root, pid.ITEMS_FILE, pid.ITEM_COLUMNS, [])
        self.write(root, pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS, requirements)
        return root

    def validate(self, root):
        result = net.Result()
        data = terr.validate_territory(root, result)
        self.assertTrue(result.valid, result.errors)
        return data

    def test_empty_catalogs_keep_reference_blockers(self):
        data = self.validate(self.fixture())
        gate = data["missionProgression"]["finalGate"]
        self.assertFalse(gate["referenceConfigurationReady"])
        self.assertIn("REQUIRED_UPGRADE_REFERENCES", gate["missingConfiguration"])
        self.assertIn("REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES",
                      gate["missingConfiguration"])
        self.assertIsNone(gate["requiredUpgradeReferences"])

    def test_authored_references_clear_only_reference_blockers(self):
        data = self.validate(self.fixture(populated=True))
        gate = data["missionProgression"]["finalGate"]
        self.assertTrue(gate["referenceConfigurationReady"])
        self.assertNotIn("REQUIRED_UPGRADE_REFERENCES", gate["missingConfiguration"])
        self.assertNotIn("REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES",
                         gate["missingConfiguration"])
        self.assertIn("CAPSTONE_MISSION_REFERENCE", gate["missingConfiguration"])
        self.assertFalse(gate["configured"])
        self.assertFalse(gate["isCampaignEligibilityResult"])
        self.assertEqual(gate["requiredUpgradeReferences"], ["UP_TEST"])

    def test_inactive_requirements_do_not_configure_gate(self):
        data = self.validate(self.fixture(populated=True, requirements_active=False))
        gate = data["missionProgression"]["finalGate"]
        self.assertFalse(gate["referenceConfigurationReady"])
        self.assertEqual(gate["requirements"], [])

    def test_invalid_identity_reference_blocks_territory_export(self):
        root = self.fixture()
        bad = self.row(pid.REQUIREMENT_COLUMNS, requirement_id="BAD",
                       tier_id="TIER_6", upgrade_id="MISSING")
        self.write(root, pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS, [bad])
        result, output = terr.export(root)
        self.assertFalse(result.valid)
        self.assertIsNone(output)
        self.assertTrue(any("unknown upgrade_id" in error for error in result.errors))
        self.assertFalse((root / "generated/data/territory_catalog.json").exists())

    def test_partial_identity_installation_blocks_export(self):
        root = self.fixture()
        (root / "data_authoring/source" / pid.ITEMS_FILE).unlink()
        result, output = terr.export(root)
        self.assertFalse(result.valid)
        self.assertIsNone(output)
        self.assertTrue(any("Required source file missing" in error for error in result.errors))

    def test_export_carries_definitions_and_typed_requirements(self):
        result, output = terr.export(self.fixture(populated=True))
        self.assertTrue(result.valid, result.errors)
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["missionProgression"]["contractVersion"], "2026-10-08.5")
        self.assertEqual(payload["progressionIdentities"]["upgrades"][0]["id"], "UP_TEST")
        gate = payload["missionProgression"]["finalGate"]
        self.assertEqual(len(gate["requirements"]), 2)
        self.assertEqual(
            gate["requiredPlotMilestoneOrItemReferences"],
            [{"requirementType": "MILESTONE_COMPLETED", "referenceId": "PLOT_TEST"}],
        )
        self.assertFalse(gate["isCampaignEligibilityResult"])
        self.assertFalse(payload["runtimeImplemented"])


if __name__ == "__main__":
    unittest.main()

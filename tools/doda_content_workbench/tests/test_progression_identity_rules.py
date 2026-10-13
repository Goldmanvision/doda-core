import csv
import json
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doda_network_rules as net
import doda_progression_identity_rules as pid


class ProgressionIdentityTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.gettempdir()) / ("doda_pid_" + uuid.uuid4().hex)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        for name, columns in [
            (pid.UPGRADES_FILE, pid.UPGRADE_COLUMNS),
            (pid.MILESTONES_FILE, pid.MILESTONE_COLUMNS),
            (pid.ITEMS_FILE, pid.ITEM_COLUMNS),
            (pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS),
        ]:
            self.write(name, columns, [])
        self.write("department_tracks.csv", ["track_id", "active"],
                   [{"track_id": "TRACK", "active": "true"}])
        self.write("mission_tiers.csv", ["tier_id", "active"],
                   [{"tier_id": "TIER_6", "active": "true"}])

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, name, columns, rows):
        with (self.src / name).open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def definition(self, columns, key, value, active="true", **changes):
        row = {column: "" for column in columns}
        row.update({key: value, "display_name": value, "sort_order": "10", "active": active})
        row.update(changes)
        return row

    def upgrade(self, active="true", track="TRACK"):
        row = self.definition(pid.UPGRADE_COLUMNS, "upgrade_id", "UP", active, track_id=track)
        self.write(pid.UPGRADES_FILE, pid.UPGRADE_COLUMNS, [row])

    def requirement(self, **changes):
        row = {column: "" for column in pid.REQUIREMENT_COLUMNS}
        row.update(requirement_id="REQ", tier_id="TIER_6",
                   upgrade_id="UP", sort_order="10", active="true")
        row.update(changes)
        self.write(pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS, [row])
        return row

    def validate(self):
        res = net.Result()
        return res, pid.validate_identities(self.root, res)

    def test_empty_catalogs_valid_but_unconfigured(self):
        res, data = self.validate()
        self.assertTrue(res.valid, res.errors)
        self.assertFalse(data["finalGateReferenceStatus"]["configured"])

    def test_upgrade_reference(self):
        self.upgrade()
        self.requirement()
        res, data = self.validate()
        self.assertTrue(res.valid, res.errors)
        self.assertEqual(data["missionTierRequirements"][0]["requirementType"], "UPGRADE_ACQUIRED")

    def test_unknown_track(self):
        self.upgrade(track="MISSING")
        res, _ = self.validate()
        self.assertTrue(any("unknown track_id" in error for error in res.errors))

    def test_duplicate_definition(self):
        row = self.definition(pid.ITEM_COLUMNS, "plot_item_id", "ITEM")
        self.write(pid.ITEMS_FILE, pid.ITEM_COLUMNS, [row, row])
        res, _ = self.validate()
        self.assertTrue(any("duplicate plot_item_id" in error for error in res.errors))

    def test_exactly_one_reference(self):
        self.upgrade()
        self.requirement(milestone_id="MILE")
        res, _ = self.validate()
        self.assertTrue(any("exactly one" in error for error in res.errors))

    def test_unknown_target(self):
        self.requirement()
        res, _ = self.validate()
        self.assertTrue(any("unknown upgrade_id" in error for error in res.errors))

    def test_unknown_tier(self):
        self.upgrade()
        self.requirement(tier_id="MISSING")
        res, _ = self.validate()
        self.assertTrue(any("unknown tier_id" in error for error in res.errors))

    def test_inactive_target(self):
        self.upgrade(active="false")
        self.requirement()
        res, _ = self.validate()
        self.assertTrue(any("inactive target" in error for error in res.errors))

    def test_inactive_tier(self):
        self.upgrade()
        self.requirement()
        self.write("mission_tiers.csv", ["tier_id", "active"],
                   [{"tier_id": "TIER_6", "active": "false"}])
        res, _ = self.validate()
        self.assertTrue(any("inactive tier" in error for error in res.errors))

    def test_duplicate_logical_requirement(self):
        self.upgrade()
        first = self.requirement()
        second = dict(first, requirement_id="REQ_2")
        self.write(pid.REQUIREMENTS_FILE, pid.REQUIREMENT_COLUMNS, [first, second])
        res, _ = self.validate()
        self.assertTrue(any("duplicate logical" in error for error in res.errors))

    def test_export_is_not_campaign_state(self):
        res, out = pid.export(self.root)
        self.assertTrue(res.valid, res.errors)
        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(payload["runtimeImplemented"])
        self.assertFalse(payload["finalGateReferenceStatus"]["isCampaignEligibilityResult"])
        self.assertEqual(payload["rules"]["plotItemCheck"], "CURRENTLY_HELD_AT_CAPSTONE_PURCHASE")

    def test_shipped_data(self):
        root = net.find_project_root(Path(__file__).resolve().parent)
        res = net.Result()
        data = pid.validate_identities(root, res)
        self.assertTrue(res.valid, res.errors)
        self.assertFalse(data["finalGateReferenceStatus"]["configured"])


if __name__ == "__main__":
    unittest.main()

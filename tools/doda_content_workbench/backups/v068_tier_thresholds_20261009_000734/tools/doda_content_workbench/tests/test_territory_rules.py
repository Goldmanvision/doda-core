import csv
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net
import doda_territory_rules as terr

REF = "User decision 2026-10-08 (territory)"


def _row(cols, **kw):
    base = {c: "" for c in cols}
    base.update(source_reference=REF, active="false")
    base.update(kw)
    return base


def territory_rows():
    c = terr.TERRITORY_COLUMNS
    return [_row(c, territory_id="T_START", display_name="Start", kind="STARTING", hq_name="Office",
                 agents_allowed="true", sort_order="10"),
            _row(c, territory_id="T_PLOT", display_name="Plot", kind="PLOT", agents_allowed="true", sort_order="20"),
            _row(c, territory_id="T_ONLY", display_name="Only", kind="PLAYER_ONLY", agents_allowed="false",
                 sort_order="30")]


def setting_rows():
    c = terr.SETTING_COLUMNS
    return [_row(c, setting_id=k, display_name=k, unit=u, sort_order=str(i * 10), value="4" if i == 1 else "")
            for i, (k, u) in enumerate(terr.SETTING_UNITS.items(), 1)]


def tier_rows():
    c = terr.TIER_COLUMNS
    return [_row(c, tier_id="T1", display_name="One", min_lifetime_evidence="0", authored_content="false", sort_order="10"),
            _row(c, tier_id="T2", display_name="Two", min_lifetime_evidence="100", authored_content="false", sort_order="20"),
            _row(c, tier_id="T3", display_name="Three", min_lifetime_evidence="1000", authored_content="true", sort_order="30")]


def format_rows():
    c = terr.FORMAT_COLUMNS
    return [_row(c, format_id="F_M", display_name="Mission", role="MISSION", sort_order="10"),
            _row(c, format_id="F_H", display_name="Hub", role="HUB", sort_order="20")]


def map_rows():
    c = terr.MAP_COLUMNS
    return [_row(c, map_id="M1", format_id="F_M", display_name="M1", has_objective="true", agent_deployable="true", sort_order="10"),
            _row(c, map_id="M2", format_id="F_M", display_name="M2", has_objective="false", agent_deployable="true", sort_order="20"),
            _row(c, map_id="M3", format_id="F_H", display_name="M3", has_objective="false", agent_deployable="false", sort_order="30")]


def edit(rows, field, match, **changes):
    for r in rows:
        if r[field] == match:
            r.update(changes)
    return rows


class TerritoryTests(unittest.TestCase):
    def setUp(self):
        self.roots = []

    def tearDown(self):
        for root in self.roots:
            shutil.rmtree(root, ignore_errors=True)

    def make_root(self, **tables):
        root = Path(tempfile.gettempdir()) / f"doda_terr_test_{uuid.uuid4().hex}"
        src = root / "data_authoring" / "source"
        src.mkdir(parents=True)
        spec = (("territories", terr.TERRITORIES_FILE, terr.TERRITORY_COLUMNS, territory_rows),
                ("settings", terr.SETTINGS_FILE, terr.SETTING_COLUMNS, setting_rows),
                ("tiers", terr.TIERS_FILE, terr.TIER_COLUMNS, tier_rows),
                ("formats", terr.FORMATS_FILE, terr.FORMAT_COLUMNS, format_rows),
                ("maps", terr.MAPS_FILE, terr.MAP_COLUMNS, map_rows))
        for key, name, cols, default in spec:
            rows = tables[key] if key in tables else default()
            with (src / name).open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
                w.writeheader()
                w.writerows(rows)
        self.roots.append(root)
        return root

    def validate(self, **tables):
        res = net.Result()
        return res, terr.validate_territory(self.make_root(**tables), res)

    def has(self, res, text):
        return any(text in e for e in res.errors)

    def test_valid_and_warnings(self):
        res, data = self.validate()
        self.assertEqual(res.errors, [])
        self.assertTrue(any("'M2' has no objective yet" in w for w in res.warnings))
        self.assertFalse(any("'M3'" in w for w in res.warnings))
        self.assertEqual(len(data["territories"]), 3)

    def test_exactly_one_starting(self):
        res, _ = self.validate(territories=[r for r in territory_rows() if r["territory_id"] != "T_START"])
        self.assertTrue(self.has(res, "exactly one territory must have kind STARTING"))

    def test_player_only_agents(self):
        res, _ = self.validate(territories=edit(territory_rows(), "territory_id", "T_ONLY", agents_allowed="true"))
        self.assertTrue(self.has(res, "must set agents_allowed to false"))
        res, _ = self.validate(territories=edit(territory_rows(), "territory_id", "T_PLOT", agents_allowed="false"))
        self.assertTrue(self.has(res, "only a PLAYER_ONLY territory can set agents_allowed to false"))

    def test_starting_needs_hq(self):
        res, _ = self.validate(territories=edit(territory_rows(), "territory_id", "T_START", hq_name=""))
        self.assertTrue(self.has(res, "needs an hq_name"))

    def test_population(self):
        res, _ = self.validate(territories=edit(territory_rows(), "territory_id", "T_START", population="0"))
        self.assertTrue(self.has(res, "population must be at least 1"))

    def test_settings(self):
        res, _ = self.validate(settings=[r for r in setting_rows() if r["setting_id"] != "OPEN_MISSION_AREA_CAP"])
        self.assertTrue(self.has(res, "Required setting 'OPEN_MISSION_AREA_CAP' is missing"))
        res, _ = self.validate(settings=edit(setting_rows(), "setting_id", "MAX_AGENT_SHARE_PER_HOUSING_PLACE", value="150"))
        self.assertTrue(self.has(res, "at most 100"))
        res, _ = self.validate(settings=edit(setting_rows(), "setting_id", "TEAM_SIZE_LIMIT", unit="COUNT"))
        self.assertTrue(self.has(res, "TEAM_SIZE_LIMIT must use unit AGENTS"))

    def test_tiers(self):
        res, _ = self.validate(tiers=edit(tier_rows(), "tier_id", "T1", min_lifetime_evidence="5"))
        self.assertTrue(self.has(res, "the first tier must start at 0"))
        res, _ = self.validate(tiers=edit(tier_rows(), "tier_id", "T2", min_lifetime_evidence="0"))
        self.assertTrue(self.has(res, "must strictly increase"))
        res, _ = self.validate(tiers=edit(tier_rows(), "tier_id", "T1", authored_content="true"))
        self.assertTrue(self.has(res, "only one tier can be marked authored_content"))

    def test_maps(self):
        res, _ = self.validate(maps=edit(map_rows(), "map_id", "M1", format_id="NOPE"))
        self.assertTrue(self.has(res, "unknown format_id 'NOPE'"))
        res, _ = self.validate(maps=edit(map_rows(), "map_id", "M1", active="true"))
        self.assertTrue(self.has(res, "active map uses inactive format"))
        res, _ = self.validate(maps=edit(map_rows(), "map_id", "M3", agent_deployable="true"))
        self.assertTrue(self.has(res, "a HUB map cannot be agent_deployable"))

    def test_export_not_runtime(self):
        res, out = terr.export(self.make_root())
        self.assertTrue(res.valid, res.errors)
        import json
        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(payload["runtimeImplemented"])
        self.assertEqual(payload["territories"][0]["unlockMethod"], "AT_START")

    def test_shipped_data(self):
        res = net.Result()
        terr.validate_territory(net.find_project_root(Path(__file__).resolve().parent), res)
        self.assertEqual(res.errors, [])


if __name__ == "__main__":
    unittest.main()
"""Tests for doda_agent_attribute_rules. Run: python -m unittest discover -s tests"""
import shutil, sys, tempfile, unittest, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doda_agent_attribute_rules as attr, doda_network_rules as net

TH = ",".join(attr.TRAIT_COLUMNS) + "\n"
GH = ",".join(attr.TRAINING_COLUMNS) + "\n"
# id,name,category,min,max,default,creation,changes,contributes,formula,ref,uses,systems,src,desc,sort,active
COURAGE = "COURAGE,Courage,PERSONALITY,0,100,,RANDOM_IN_RANGE,false,false,,,,,,,10,true\n"
AGILITY = "AGILITY,Agility,ATTRIBUTE,0,100,50,DEFAULT,false,false,,,,,,,20,true\n"
# id,name,category,eligible,uses,systems,src,desc,sort,active
COMBAT = "TRAIN_COMBAT,Combat,TACTICAL,true,,,,,10,true\n"
MEDIC = "TRAIN_MEDICAL,Medical,MEDICAL,true,,,,,20,true\n"
ALIASED = ("TRAIN_CULINARY,Culinary,PERSONAL_CARE,true,,,,,30,false\n"
           "TRAIN_HOSPITALITY,Hospitality,PERSONAL_CARE,true,,,,,40,false\n"
           "TRAIN_SURVIVALIST,Survivalist,PERSONAL_CARE,true,,,,,50,false\n"
           "TRAIN_MAGIC,Magic,ARCANE,true,,,,,60,false\n")


class T(unittest.TestCase):
    def setUp(self):
        self.dirs = []

    def tearDown(self):
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def run_rows(self, traits=COURAGE + AGILITY, training=None):
        if training is None:
            training = COMBAT + MEDIC + ALIASED
        d = Path(tempfile.gettempdir()) / f"doda_attrtest_{uuid.uuid4().hex}"
        self.dirs.append(d)
        s = d / "data_authoring" / "source"
        s.mkdir(parents=True)
        (s / attr.TRAITS_FILE).write_text(TH + traits, encoding="utf-8")
        (s / attr.TRAINING_FILE).write_text(GH + training, encoding="utf-8")
        r = net.Result()
        return r, attr.validate_attributes(d, r)

    def has(self, r, text):
        return any(text in e for e in r.errors)

    def test_valid(self):
        r, data = self.run_rows()
        self.assertTrue(r.valid, r.errors)
        self.assertEqual([t["id"] for t in data["traits"]], ["COURAGE", "AGILITY"])
        self.assertEqual([t["id"] for t in data["training"]][:2], ["TRAIN_COMBAT", "TRAIN_MEDICAL"])
        self.assertEqual(len(data["training"]), 6)
        self.assertFalse(r.warnings)

    def test_missing_files_skipped(self):
        d = Path(tempfile.gettempdir()) / f"doda_attrtest_{uuid.uuid4().hex}"
        self.dirs.append(d)
        (d / "data_authoring" / "source").mkdir(parents=True)
        r = net.Result()
        self.assertEqual(attr.validate_attributes(d, r), {"traits": [], "training": []})
        self.assertTrue(r.valid)

    def test_duplicate_and_cross_table_ids(self):
        r, _ = self.run_rows(COURAGE + COURAGE)
        self.assertTrue(self.has(r, "duplicate trait_id"))
        r, _ = self.run_rows(COURAGE, COMBAT.replace("TRAIN_COMBAT", "COURAGE") + MEDIC + ALIASED)
        self.assertTrue(self.has(r, "also used in personnel_traits"))

    def test_category_per_table(self):
        r, _ = self.run_rows(COURAGE.replace("PERSONALITY", "TACTICAL"))
        self.assertTrue(self.has(r, "trait_category"))
        r, _ = self.run_rows(training=COMBAT.replace("TACTICAL", "PERSONALITY") + MEDIC + ALIASED)
        self.assertTrue(self.has(r, "training_category"))

    def test_range_and_default(self):
        r, _ = self.run_rows(COURAGE.replace(",0,100,", ",0,,"))
        self.assertTrue(self.has(r, "are required"))
        r, _ = self.run_rows(COURAGE.replace(",0,100,", ",100,0,"))
        self.assertTrue(self.has(r, "below maximum_value"))
        r, _ = self.run_rows(AGILITY.replace(",50,DEFAULT", ",150,DEFAULT"))
        self.assertTrue(self.has(r, "outside the range"))

    def test_creation_rules(self):
        r, _ = self.run_rows(AGILITY.replace(",50,DEFAULT", ",,DEFAULT"))
        self.assertTrue(self.has(r, "DEFAULT needs a default_value"))
        r, _ = self.run_rows(COURAGE.replace(",,RANDOM", ",40,RANDOM"))
        self.assertTrue(self.has(r, "unused by RANDOM_IN_RANGE"))
        r, _ = self.run_rows(COURAGE.replace("RANDOM_IN_RANGE", "COPY_OF_STAT"))
        self.assertTrue(self.has(r, "creation_rule must be one of"))

    def test_health_option(self):
        r, _ = self.run_rows(COURAGE.replace(",false,false,,,", ",false,true,NORMALIZED,,"))
        self.assertTrue(r.valid, r.errors)
        r, _ = self.run_rows(COURAGE.replace(",false,false,,,", ",false,true,,,"))
        self.assertTrue(self.has(r, "needs a health_formula"))
        r, _ = self.run_rows(COURAGE.replace(",false,false,,,", ",false,false,NORMALIZED,,"))
        self.assertTrue(self.has(r, "only set when the value counts"))
        r, _ = self.run_rows(COURAGE.replace(",false,false,,,", ",false,true,NORMALIZED,AGILITY,") + AGILITY)
        self.assertTrue(self.has(r, "only used by PERCENT_OF_REFERENCE"))

    def test_percent_of_reference(self):
        pct = ",false,true,PERCENT_OF_REFERENCE,{},"
        r, _ = self.run_rows(COURAGE.replace(",false,false,,,", pct.format("AGILITY")) +
                             AGILITY.replace(",0,100,50,", ",1,100,50,"))
        self.assertTrue(r.valid, r.errors)
        r, _ = self.run_rows(COURAGE.replace(",false,false,,,", pct.format("AGILITY")) + AGILITY)
        self.assertTrue(self.has(r, "minimum of at least 1"))
        r, _ = self.run_rows(COURAGE.replace(",false,false,,,", pct.format("TRAIN_COMBAT")))
        self.assertTrue(self.has(r, "must be in personnel_traits"))
        r, _ = self.run_rows(COURAGE.replace(",false,false,,,", pct.format("COURAGE")).replace(",0,100,", ",1,100,"))
        self.assertTrue(self.has(r, "its own Health reference"))

    def test_export(self):
        self.run_rows()
        res, out = attr.export(self.dirs[-1])
        self.assertTrue(res.valid, res.errors)
        self.assertIn('"runtimeImplemented": false', out.read_text(encoding="utf-8"))

    def test_export_blocked_when_invalid(self):
        self.run_rows(COURAGE + COURAGE)
        res, out = attr.export(self.dirs[-1])
        self.assertFalse(res.valid)
        self.assertIsNone(out)

    def test_training_is_binary_schema(self):
        self.assertNotIn("minimum_value", attr.TRAINING_COLUMNS)
        self.assertNotIn("contributes_to_health", attr.TRAINING_COLUMNS)

    def test_training_duplicate_and_bools(self):
        r, _ = self.run_rows(training=COMBAT + COMBAT + MEDIC + ALIASED)
        self.assertTrue(self.has(r, "duplicate training_id"))
        r, _ = self.run_rows(training=COMBAT.replace(",TACTICAL,true,", ",TACTICAL,maybe,") + MEDIC + ALIASED)
        self.assertFalse(r.valid)

    def test_creation_pool_warning(self):
        r, _ = self.run_rows(training=COMBAT + MEDIC.replace(",MEDICAL,true,", ",MEDICAL,false,") + ALIASED)
        self.assertTrue(r.valid, r.errors)
        self.assertTrue(any("PERS-16" in w for w in r.warnings))
        r, _ = self.run_rows(training=COMBAT.replace(",10,true", ",10,false") + MEDIC.replace(",20,true", ",20,false") + ALIASED)
        self.assertFalse(r.warnings)  # no active trainings: nothing to roll yet

    def test_export_training_model(self):
        self.run_rows()
        res, out = attr.export(self.dirs[-1])
        text = out.read_text(encoding="utf-8")
        self.assertIn('"binary": true', text)
        self.assertIn('"TRAINED_MEDIC": "TRAIN_MEDICAL"', text)
        self.assertIn('"TRAINED_SURVIVALIST": "TRAIN_SURVIVALIST"', text)
        self.assertIn('"skillDistribution": "UNIFORM_WITHOUT_REPLACEMENT"', text)

    def test_alias_targets_must_exist(self):
        r, _ = self.run_rows(training=COMBAT + MEDIC)
        self.assertTrue(self.has(r, "TRAINED_MAGIC maps to missing training 'TRAIN_MAGIC'"))
        r, _ = self.run_rows(training=ALIASED)
        self.assertTrue(self.has(r, "TRAINED_MEDIC maps to missing"))


if __name__ == "__main__":
    unittest.main()

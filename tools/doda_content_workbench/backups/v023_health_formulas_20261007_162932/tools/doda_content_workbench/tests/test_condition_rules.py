"""Tests for doda_condition_rules. Run: python -m unittest discover -s tests"""
import shutil, sys, tempfile, unittest, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doda_condition_rules as cond, doda_care_rules as care, doda_network_rules as net

SH = ",".join(cond.STAT_COLUMNS) + "\n"
BH = ",".join(cond.BAND_COLUMNS) + "\n"
# id,name,category,min,max,default,direction,storage,derivation,contributes,visibility,high,low,src,desc,sort,active
HEALTH = "HEALTH,Health,SUMMARY,0,100,100,POSITIVE,DERIVED,AVERAGE_OF_CONTRIBUTORS,false,VISIBLE_BOTH,,,,,10,true\n"
STRESS = "STRESS,Stress,CONDITION,0,100,0,NEGATIVE,DIRECT,,true,VISIBLE_BOTH,,,,,20,true\n"
HP = "CURRENT_HP,HP,PHYSICAL,0,,,POSITIVE,DIRECT,,false,DETAIL_ONLY,,,,,30,true\n"
STATS = HEALTH + STRESS + HP
# id,stat,min,max,label,severity,effect,offduty,action,care,warning,color,src,desc,sort,active
BANDS = ("H_LOW,HEALTH,0,49,Sick,HIGH,NONE,false,,,,#EF5B5B,,,10,true\n"
         "H_OK,HEALTH,50,100,Healthy,NONE,NONE,false,,,,,,,20,true\n"
         "S_LOW,STRESS,0,89,Fine,NONE,NONE,false,,,,,,,10,true\n"
         "S_HIGH,STRESS,90,100,Breakdown,CRITICAL,HARD_BLOCK,true,Therapy,TH,,,,,20,true\n")
CARE = ",".join(care.CARE_COLUMNS) + "\nTH,Therapy,THERAPY,PLAYER_ASSIGNED,AUTOMATIC,COSTED,,,,,,10,false\n"


class T(unittest.TestCase):
    def setUp(self):
        self.dirs = []

    def tearDown(self):
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def run_rows(self, stats=STATS, bands=BANDS, care_rows=CARE):
        d = Path(tempfile.gettempdir()) / f"doda_condtest_{uuid.uuid4().hex}"
        self.dirs.append(d)
        s = d / "data_authoring" / "source"
        s.mkdir(parents=True)
        (s / cond.STATS_FILE).write_text(SH + stats, encoding="utf-8")
        (s / cond.BANDS_FILE).write_text(BH + bands, encoding="utf-8")
        (s / care.CARE_FILE).write_text(care_rows, encoding="utf-8")
        r = net.Result()
        return r, cond.validate_conditions(d, r)

    def has(self, r, text):
        return any(text in e for e in r.errors)

    def test_valid(self):
        r, data = self.run_rows()
        self.assertTrue(r.valid, r.errors)
        self.assertEqual(len(data["stats"]), 3)
        self.assertEqual(len(data["bands"]), 4)

    def test_missing_files_skipped(self):
        d = Path(tempfile.gettempdir()) / f"doda_condtest_{uuid.uuid4().hex}"
        self.dirs.append(d)
        (d / "data_authoring" / "source").mkdir(parents=True)
        r = net.Result()
        self.assertEqual(cond.validate_conditions(d, r), {"stats": [], "bands": []})
        self.assertTrue(r.valid)

    def test_duplicate_stat(self):
        r, _ = self.run_rows(STATS + STRESS)
        self.assertTrue(self.has(r, "duplicate stat_id"))

    def test_bad_enums(self):
        for old, new, field in ((",CONDITION,", ",MOOD,", "stat_category"),
                                (",NEGATIVE,", ",SIDEWAYS,", "direction"),
                                (",VISIBLE_BOTH,", ",SECRET,", "player_visibility")):
            with self.subTest(field=field):
                r, _ = self.run_rows(HEALTH + STRESS.replace(old, new) + HP)
                self.assertTrue(self.has(r, field), r.errors)

    def test_derived_needs_derivation_and_direct_has_none(self):
        r, _ = self.run_rows(HEALTH.replace("AVERAGE_OF_CONTRIBUTORS", "") + STRESS + HP)
        self.assertTrue(self.has(r, "DERIVED stats need a derivation"))
        r, _ = self.run_rows(HEALTH + STRESS.replace("DIRECT,,", "DIRECT,FROM_ASSIGNMENTS,") + HP)
        self.assertTrue(self.has(r, "DIRECT stats have no derivation"))

    def test_range_and_default(self):
        r, _ = self.run_rows(HEALTH + STRESS.replace(",0,100,0,", ",50,40,0,") + HP)
        self.assertTrue(self.has(r, "below maximum_value"))
        r, _ = self.run_rows(HEALTH + STRESS.replace(",0,100,0,", ",0,100,200,") + HP)
        self.assertTrue(self.has(r, "outside the stat range"))

    def test_contributor_needs_known_range(self):
        r, _ = self.run_rows(HEALTH + STRESS + HP.replace(",false,DETAIL_ONLY", ",true,DETAIL_ONLY"))
        self.assertTrue(self.has(r, "needs a known range"))

    def test_active_health_needs_active_contributor(self):
        r, _ = self.run_rows(HEALTH + STRESS.replace(",true,VISIBLE_BOTH", ",false,VISIBLE_BOTH") + HP,
                             BANDS)
        self.assertTrue(self.has(r, "no active contributors"))

    def test_only_one_health_summary(self):
        r, _ = self.run_rows(STATS + HEALTH.replace("HEALTH,Health", "HEALTH2,Health 2"), BANDS)
        self.assertTrue(self.has(r, "Only one stat"))

    def test_health_bands_presentation_only(self):
        r, _ = self.run_rows(bands=BANDS.replace("Sick,HIGH,NONE,false", "Sick,HIGH,MAJOR_PENALTY,false"))
        self.assertTrue(self.has(r, "PERS-04"))
        r, _ = self.run_rows(bands=BANDS.replace("Sick,HIGH,NONE,false", "Sick,HIGH,NONE,true"))
        self.assertTrue(self.has(r, "PERS-04"))

    def test_band_gap_overlap_and_coverage(self):
        r, _ = self.run_rows(bands=BANDS.replace("S_HIGH,STRESS,90", "S_HIGH,STRESS,92"))
        self.assertTrue(self.has(r, "gap before S_HIGH"))
        r, _ = self.run_rows(bands=BANDS.replace("S_HIGH,STRESS,90", "S_HIGH,STRESS,85"))
        self.assertTrue(self.has(r, "overlaps"))
        r, _ = self.run_rows(bands=BANDS.replace("S_HIGH,STRESS,90,100", "S_HIGH,STRESS,90,95"))
        self.assertTrue(self.has(r, "no band covers 96-100"))
        r, _ = self.run_rows(bands=BANDS.replace("S_HIGH,STRESS,90,100", "S_HIGH,STRESS,90,105"))
        self.assertTrue(self.has(r, "past maximum"))

    def test_band_refs_and_values(self):
        r, _ = self.run_rows(bands=BANDS + "X,NOPE,0,1,X,NONE,NONE,false,,,,,,,1,false\n")
        self.assertTrue(self.has(r, "unknown stat_id 'NOPE'"))
        r, _ = self.run_rows(bands=BANDS.replace("Therapy,TH,", "Therapy,MISSING,"))
        self.assertTrue(self.has(r, "unknown suggested_care_service_id"))
        r, _ = self.run_rows(bands=BANDS.replace("#EF5B5B", "red"))
        self.assertTrue(self.has(r, "ui_color"))
        r, _ = self.run_rows(bands=BANDS.replace("HARD_BLOCK", "SCOLDING"))
        self.assertTrue(self.has(r, "assignment_effect"))

    def test_active_band_needs_active_stat(self):
        r, _ = self.run_rows(HEALTH + STRESS.replace(",20,true", ",20,false") + HP)
        self.assertTrue(self.has(r, "inactive stat 'STRESS'"))

    def test_export(self):
        self.run_rows()
        res, out = cond.export(self.dirs[-1])
        self.assertTrue(res.valid, res.errors)
        text = out.read_text(encoding="utf-8")
        self.assertIn('"presentationOnly": true', text)
        self.assertIn('"runtimeImplemented": false', text)

    def test_export_blocked_when_invalid(self):
        self.run_rows(STATS + STRESS)
        res, out = cond.export(self.dirs[-1])
        self.assertFalse(res.valid)
        self.assertIsNone(out)


if __name__ == "__main__":
    unittest.main()

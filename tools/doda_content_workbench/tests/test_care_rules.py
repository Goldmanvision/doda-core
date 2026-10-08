"""Tests for doda_care_rules. Run: python -m unittest discover -s tests"""
import shutil, sys, tempfile, unittest, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doda_care_rules as care, doda_network_rules as net

H = ",".join(care.CARE_COLUMNS) + "\n"
# id,name,category,assignment,provider,cost,duration,follow_up,destination,source,description,sort,active
EMERG = "ER,Emergency,EMERGENCY_MEDICAL,AUTOMATIC,AUTOMATIC,FREE,,MED,,,,10,true\n"
MED = "MED,Medical,MEDICAL,PLAYER_ASSIGNED,AUTOMATIC_OR_AGENT_SKILL,COSTED,60,,,,,20,true\n"
THER = "TH,Therapy,THERAPY,PLAYER_ASSIGNED,AUTOMATIC,COSTED,60,,,,,30,true\n"
FH = ",".join(care.FEATURE_COLUMNS) + "\n"
LH = ",".join(care.LINK_COLUMNS) + "\n"
FEAT = "BASIC,Basic Medical,,,10,true\nTHER_PLACE,Therapy Place,,,20,true\n"
LINKS = "MED,BASIC,10,true\nTH,THER_PLACE,20,true\n"


class T(unittest.TestCase):
    def setUp(self):
        self.dirs = []

    def tearDown(self):
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def run_rows(self, body, features=None, links=None):
        d = Path(tempfile.gettempdir()) / f"doda_caretest_{uuid.uuid4().hex}"
        self.dirs.append(d)
        s = d / "data_authoring" / "source"
        s.mkdir(parents=True)
        (s / care.CARE_FILE).write_text(H + body, encoding="utf-8")
        if features is not None:
            (s / care.FEATURES_FILE).write_text(FH + features, encoding="utf-8")
        if links is not None:
            (s / care.LINKS_FILE).write_text(LH + links, encoding="utf-8")
        r = net.Result()
        data = care.validate_care(d, r)
        return r, data

    def has(self, r, text):
        return any(text in e for e in r.errors)

    def test_valid(self):
        r, data = self.run_rows(EMERG + MED + THER)
        self.assertTrue(r.valid, r.errors)
        self.assertEqual([s["careServiceId"] for s in data["services"]], ["ER", "MED", "TH"])

    def test_missing_file_is_skipped_with_warning(self):
        d = Path(tempfile.gettempdir()) / f"doda_caretest_{uuid.uuid4().hex}"
        self.dirs.append(d)
        (d / "data_authoring" / "source").mkdir(parents=True)
        r = net.Result()
        self.assertEqual(care.validate_care(d, r), {"services": [], "locationFeatures": [], "serviceLocations": []})
        self.assertTrue(r.valid)
        self.assertTrue(r.warnings)

    def test_emergency_must_be_free(self):
        r, _ = self.run_rows(EMERG.replace(",FREE,", ",COSTED,") + MED)
        self.assertTrue(self.has(r, "CARE-02/CARE-07"))

    def test_emergency_is_automated(self):
        r, _ = self.run_rows(EMERG.replace("AUTOMATIC,AUTOMATIC", "PLAYER_ASSIGNED,AUTOMATIC") + MED)
        self.assertTrue(self.has(r, "is automated"))

    def test_emergency_provider_automatic(self):
        r, _ = self.run_rows(EMERG.replace("AUTOMATIC,AUTOMATIC", "AUTOMATIC,NONE") + MED)
        self.assertTrue(self.has(r, "automatic provider"))

    def test_non_emergency_and_therapy_have_costs(self):
        r, _ = self.run_rows(MED.replace(",COSTED,", ",FREE,") + THER.replace(",COSTED,", ",FREE,"))
        self.assertEqual(sum("CARE-07" in e for e in r.errors), 2)

    def test_therapy_player_assigned(self):
        r, _ = self.run_rows(THER.replace("PLAYER_ASSIGNED", "AUTOMATIC"))
        self.assertTrue(self.has(r, "CARE-04"))

    def test_therapy_provider_automatic(self):
        r, _ = self.run_rows(THER.replace(",AUTOMATIC,COSTED", ",AUTOMATIC_OR_AGENT_SKILL,COSTED"))
        self.assertTrue(self.has(r, "handled automatically"))

    def test_unknown_values_rejected(self):
        for old, new, msg in ((",THERAPY,", ",DENTAL,", "care_category"),
                              (",COSTED,", ",CHEAP,", "cost_policy"),
                              (",PLAYER_ASSIGNED,", ",MAYBE,", "recipient_assignment"),
                              (",AUTOMATIC,COSTED", ",STAFF,COSTED", "provider_mode")):
            with self.subTest(msg=msg):
                r, _ = self.run_rows(THER.replace(old, new))
                self.assertTrue(self.has(r, msg), r.errors)

    def test_duplicate_id(self):
        r, _ = self.run_rows(THER + THER)
        self.assertTrue(self.has(r, "duplicate"))

    def test_duration_blank_or_positive(self):
        r, _ = self.run_rows(THER.replace(",60,", ",0,"))
        self.assertTrue(self.has(r, "duration_minutes"))
        r, _ = self.run_rows(THER.replace(",60,", ",abc,"))
        self.assertFalse(r.valid)

    def test_active_without_duration_warns(self):
        r, _ = self.run_rows(EMERG + MED)
        self.assertTrue(r.valid, r.errors)
        self.assertTrue(any("no duration yet" in w for w in r.warnings))

    def test_unknown_follow_up(self):
        r, _ = self.run_rows(EMERG)
        self.assertTrue(self.has(r, "unknown follow_up"))

    def test_self_follow_up(self):
        r, _ = self.run_rows(THER.replace(",60,,", ",60,TH,"))
        self.assertTrue(self.has(r, "its own follow-up"))

    def test_active_follow_up_must_be_active(self):
        r, _ = self.run_rows(EMERG + MED.replace(",true\n", ",false\n"))
        self.assertTrue(self.has(r, "inactive service 'MED'"))

    def test_follow_up_loop(self):
        r, _ = self.run_rows(EMERG + MED.replace(",60,,", ",60,ER,"))
        self.assertEqual(sum("Follow-up loop" in e for e in r.errors), 1)

    def test_export_writes_catalog(self):
        r, _ = self.run_rows(EMERG + MED + THER)
        res, out = care.export(self.dirs[-1])
        self.assertTrue(res.valid, res.errors)
        self.assertTrue(out.is_file())
        self.assertIn('"runtimeImplemented": false', out.read_text(encoding="utf-8"))
        self.assertIn('"providerKind": "HOSPITAL"', out.read_text(encoding="utf-8"))

    def test_export_blocked_when_invalid(self):
        self.run_rows(EMERG)
        res, out = care.export(self.dirs[-1])
        self.assertFalse(res.valid)
        self.assertIsNone(out)

    def test_locations_valid_and_exported(self):
        r, data = self.run_rows(EMERG + MED + THER, FEAT, LINKS)
        self.assertTrue(r.valid, r.errors)
        self.assertEqual(len(data["locationFeatures"]), 2)
        self.assertEqual([(l["careServiceId"], l["featureId"]) for l in data["serviceLocations"]],
                         [("MED", "BASIC"), ("TH", "THER_PLACE")])

    def test_one_service_many_places(self):
        r, data = self.run_rows(EMERG + MED + THER, FEAT, LINKS + "MED,THER_PLACE,30,true\n")
        self.assertTrue(r.valid, r.errors)
        self.assertEqual(sum(l["careServiceId"] == "MED" for l in data["serviceLocations"]), 2)

    def test_duplicate_feature(self):
        r, _ = self.run_rows(THER, FEAT + "BASIC,Again,,,30,true\n", "")
        self.assertTrue(self.has(r, "duplicate feature_id"))

    def test_duplicate_link(self):
        r, _ = self.run_rows(EMERG + MED + THER, FEAT, LINKS + "MED,BASIC,30,true\n")
        self.assertTrue(self.has(r, "duplicate link"))

    def test_link_unknown_references(self):
        r, _ = self.run_rows(THER, FEAT, "NOPE,BASIC,10,true\nTH,NOWHERE,20,true\n")
        self.assertTrue(self.has(r, "unknown care_service_id 'NOPE'"))
        self.assertTrue(self.has(r, "unknown feature_id 'NOWHERE'"))

    def test_active_link_needs_active_ends(self):
        r, _ = self.run_rows(THER.replace(",true\n", ",false\n"), FEAT.replace("20,true", "20,false"),
                             "TH,THER_PLACE,10,true\n")
        self.assertTrue(self.has(r, "inactive service 'TH'"))
        self.assertTrue(self.has(r, "inactive location feature 'THER_PLACE'"))

    def test_unused_active_feature_warns(self):
        r, _ = self.run_rows(THER, FEAT, "TH,THER_PLACE,10,true\n")
        self.assertTrue(r.valid, r.errors)
        self.assertTrue(any("'BASIC' hosts no active services" in w for w in r.warnings))

    def test_destination_valid(self):
        er = EMERG.replace(",MED,,", ",MED,BASIC,")
        r, data = self.run_rows(er + MED + THER, FEAT, LINKS)
        self.assertTrue(r.valid, r.errors)
        self.assertEqual(data["services"][0]["destinationFeatureId"], "BASIC")

    def test_destination_unknown(self):
        r, _ = self.run_rows(EMERG.replace(",MED,,", ",MED,NOWHERE,") + MED + THER, FEAT, LINKS)
        self.assertTrue(self.has(r, "unknown destination_feature_id 'NOWHERE'"))

    def test_follow_up_must_be_offered_at_destination(self):
        r, _ = self.run_rows(EMERG.replace(",MED,,", ",MED,THER_PLACE,") + MED + THER, FEAT, LINKS)
        self.assertTrue(self.has(r, "not offered at destination 'THER_PLACE'"))

    def test_active_destination_must_be_active(self):
        r, _ = self.run_rows(EMERG.replace(",MED,,", ",MED,BASIC,") + MED + THER,
                             FEAT.replace("10,true", "10,false"), LINKS.replace("MED,BASIC,10,true", "MED,BASIC,10,false"))
        self.assertTrue(self.has(r, "inactive location feature 'BASIC'"))


if __name__ == "__main__":
    unittest.main()

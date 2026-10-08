"""Tests for doda_personal_care_rules. Run: python -m unittest discover -s tests"""
import shutil, sys, tempfile, unittest, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doda_personal_care_rules as pc, doda_agent_attribute_rules as attr, doda_network_rules as net

AH = ",".join(pc.ACTION_COLUMNS) + "\n"
# id,name,initiation,offduty,cost,followup,status,src,desc,sort,active
OFF = "REMED_OFF_DUTY,Off Duty,PLAYER_SCHEDULED,true,COST_PAID_LEAVE,REMED_EATING,,,,10,true\n"
EAT = "REMED_EATING,Eating,AGENT_INITIATED,true,,REMED_OFF_DUTY,,,,20,true\n"
REST = "REMED_RESTING,Resting,AGENT_INITIATED,true,,REMED_OFF_DUTY,,,,30,true\n"
PTH = ",".join(pc.PLACE_TYPE_COLUMNS) + "\n"
# id,name,home,owned,occupancy,src,desc,sort,active
HOME = "PLACE_SAFE_HOUSE,Safe House,true,false,BEDS,,,10,true\n"
GYM = "PLACE_GYM,Gym,false,false,UNSPECIFIED,,,20,true\n"
PFH = ",".join(pc.PLACE_TYPE_FEATURE_COLUMNS) + "\n"
PF = "PLACE_SAFE_HOUSE,CAP_REST,10,true\nPLACE_GYM,CAP_RECREATION,20,true\n"
ACH = ",".join(pc.ACTIVITY_COLUMNS) + "\n"
# id,place,name,company,durations,src,desc,sort,active
SWIM = "REC_SWIM,PLACE_GYM,Swim,ALONE;FRIENDS,One hour;Two hours,,,10,true\n"
CARE = "care_service_id\nREMED_RECOVERY\n"
FH = ",".join(pc.FEATURE_COLUMNS) + "\n"
FOOD = ("CAP_FOOD,Food Access,,,10,true\nCAP_REST,Rest,,,20,true\nCAP_RECREATION,Recreation,,,30,true\n")
LH = ",".join(pc.LOCATION_COLUMNS) + "\n"
TH = ",".join(pc.TRAINING_LINK_COLUMNS) + "\n"
TRAIN = (",".join(attr.TRAINING_COLUMNS) + "\n" + "".join(
    f"{t},{t},PERSONAL_CARE,true,,,,,{i},{'true' if t == 'TRAIN_CULINARY' else 'false'}\n"
    for i, t in enumerate(sorted(set(attr.REMEDY_ALIASES.values())))))


class T(unittest.TestCase):
    def setUp(self):
        self.dirs = []

    def tearDown(self):
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def run_rows(self, actions=OFF + EAT + REST, features=FOOD,
                 locations="REMED_OFF_DUTY,CAP_FOOD,10,true\nREMED_EATING,CAP_FOOD,20,true\n"
                           "REMED_RESTING,CAP_REST,30,true\nREMED_OFF_DUTY,CAP_RECREATION,40,true\n",
                 trainings="REMED_EATING,TRAIN_CULINARY,10,true\n", extra=None,
                 place_types=HOME + GYM, place_features=PF, activities=SWIM, care=CARE):
        d = Path(tempfile.gettempdir()) / f"doda_pcaretest_{uuid.uuid4().hex}"
        self.dirs.append(d)
        s = d / "data_authoring" / "source"
        s.mkdir(parents=True)
        (s / pc.ACTIONS_FILE).write_text(AH + actions, encoding="utf-8")
        (s / pc.FEATURES_FILE).write_text(FH + features, encoding="utf-8")
        (s / pc.LOCATIONS_FILE).write_text(LH + locations, encoding="utf-8")
        (s / pc.TRAININGS_FILE).write_text(TH + trainings, encoding="utf-8")
        (s / attr.TRAINING_FILE).write_text(TRAIN, encoding="utf-8")
        (s / pc.PLACE_TYPES_FILE).write_text(PTH + place_types, encoding="utf-8")
        (s / pc.PLACE_TYPE_FEATURES_FILE).write_text(PFH + place_features, encoding="utf-8")
        (s / pc.ACTIVITIES_FILE).write_text(ACH + activities, encoding="utf-8")
        if care is not None:
            (s / "care_services.csv").write_text(care, encoding="utf-8")
        for name, text in (extra or {}).items():
            (s / name).write_text(text, encoding="utf-8")
        r = net.Result()
        return r, pc.validate_personal_care(d, r)

    def has(self, r, text):
        return any(text in e for e in r.errors)

    def test_valid(self):
        r, data = self.run_rows()
        self.assertTrue(r.valid, r.errors)
        self.assertFalse(r.warnings, r.warnings)
        self.assertEqual(len(data["actionLocations"]), 4)
        self.assertEqual(data["recreationActivities"][0]["companyOptions"], ["ALONE", "FRIENDS"])
        self.assertEqual(data["actionTrainings"][0]["trainingId"], "TRAIN_CULINARY")

    def test_action_fields(self):
        r, _ = self.run_rows(OFF.replace("PLAYER_SCHEDULED", "SOMETIMES") + EAT + REST)
        self.assertTrue(self.has(r, "initiation must be one of"))
        r, _ = self.run_rows(OFF + OFF + EAT + REST)
        self.assertTrue(self.has(r, "duplicate action_id"))

    def test_follow_up(self):
        r, _ = self.run_rows(OFF.replace(",REMED_EATING,", ",REMED_NOPE,") + EAT + REST)
        self.assertTrue(self.has(r, "unknown follow_up_action_id"))
        r, _ = self.run_rows(OFF.replace(",REMED_EATING,", ",REMED_OFF_DUTY,") + EAT + REST)
        self.assertTrue(self.has(r, "cannot follow itself"))
        r, _ = self.run_rows(OFF + EAT.replace(",20,true", ",20,false") + REST,
                             locations="REMED_OFF_DUTY,CAP_FOOD,10,true\nREMED_RESTING,CAP_REST,2,true\n", trainings="")
        self.assertTrue(self.has(r, "follows up with inactive"))

    def test_feature_id_must_be_unique_across_place_tables(self):
        r, _ = self.run_rows(extra={"capabilities.csv": "capability_id,display_name\nCAP_FOOD,Food\n"})
        self.assertTrue(self.has(r, "also defined in capabilities.csv"))
        r, _ = self.run_rows(extra={"care_location_features.csv": "feature_id,display_name\nCAP_FOOD,Food\n"})
        self.assertTrue(self.has(r, "also defined in care_location_features.csv"))

    def test_links(self):
        r, _ = self.run_rows(locations="REMED_EATING,CAP_NOPE,10,true\n")
        self.assertTrue(self.has(r, "unknown feature_id"))
        r, _ = self.run_rows(trainings="REMED_EATING,TRAIN_NOPE,10,true\n")
        self.assertTrue(self.has(r, "unknown training_id"))
        r, _ = self.run_rows(trainings="REMED_EATING,TRAIN_MAGIC,10,true\n")
        self.assertTrue(self.has(r, "inactive training 'TRAIN_MAGIC'"))
        r, _ = self.run_rows(trainings="REMED_EATING,TRAIN_CULINARY,10,true\nREMED_EATING,TRAIN_CULINARY,20,true\n")
        self.assertTrue(self.has(r, "duplicate link"))
        r, _ = self.run_rows(features=FOOD.replace("Access,,,10,true", "Access,,,10,false"))
        self.assertTrue(self.has(r, "inactive location feature"))

    def test_warnings(self):
        r, _ = self.run_rows(locations="REMED_OFF_DUTY,CAP_FOOD,10,true\nREMED_RESTING,CAP_REST,2,true\n"
                                       "REMED_OFF_DUTY,CAP_RECREATION,3,true\n", trainings="")
        self.assertTrue(r.valid, r.errors)
        self.assertTrue(any("has no active place or training" in w for w in r.warnings))
        r, _ = self.run_rows(locations="", trainings="REMED_OFF_DUTY,TRAIN_CULINARY,1,true\n"
                                                     "REMED_EATING,TRAIN_CULINARY,2,true\n"
                                                     "REMED_RESTING,TRAIN_CULINARY,3,true\n")
        self.assertTrue(any("hosts no active actions" in w for w in r.warnings))

    def test_export(self):
        self.run_rows()
        res, out = pc.export(self.dirs[-1])
        self.assertTrue(res.valid, res.errors)
        text = out.read_text(encoding="utf-8")
        self.assertIn('"trainingBypassesLocation": true', text)
        self.assertIn('"duringCareServiceIds": [', text)
        self.assertIn('"runtimeImplemented": false', text)

    def test_export_blocked_when_invalid(self):
        self.run_rows(OFF + OFF + EAT + REST)
        res, out = pc.export(self.dirs[-1])
        self.assertIsNone(out)

    def test_place_types(self):
        r, _ = self.run_rows(place_types=HOME + HOME + GYM)
        self.assertTrue(self.has(r, "duplicate place_type_id"))
        r, _ = self.run_rows(place_types=HOME + GYM.replace(",false,false,", ",false,true,"))
        self.assertTrue(self.has(r, "only a home can be agent-owned"))
        r, _ = self.run_rows(place_types=HOME.replace(",BEDS,", ",ROOMS,") + GYM)
        self.assertTrue(self.has(r, "occupancy_rule must be one of"))
        r, _ = self.run_rows(place_features="PLACE_GYM,CAP_RECREATION,20,true\n")
        self.assertTrue(r.valid, r.errors)
        self.assertTrue(any("does not offer CAP_REST" in w for w in r.warnings))

    def test_place_type_features(self):
        r, _ = self.run_rows(place_features=PF + "PLACE_NOPE,CAP_FOOD,30,true\n")
        self.assertTrue(self.has(r, "unknown place_type_id 'PLACE_NOPE'"))
        r, _ = self.run_rows(place_features=PF + "PLACE_GYM,CAP_NOPE,30,true\n")
        self.assertTrue(self.has(r, "unknown feature_id 'CAP_NOPE'"))
        r, _ = self.run_rows(place_features=PF + "PLACE_GYM,CAP_RECREATION,30,true\n")
        self.assertTrue(self.has(r, "duplicate link"))

    def test_activities(self):
        r, _ = self.run_rows(activities=SWIM.replace("PLACE_GYM", "PLACE_SAFE_HOUSE"))
        self.assertTrue(self.has(r, "does not offer CAP_RECREATION"))
        r, _ = self.run_rows(activities=SWIM.replace("ALONE;FRIENDS", "ALONE;PETS"))
        self.assertTrue(self.has(r, "company_options must be from"))
        r, _ = self.run_rows(activities=SWIM.replace("ALONE;FRIENDS", "ALONE;alone"))
        self.assertTrue(self.has(r, "company_options has repeats"))
        r, _ = self.run_rows(activities=SWIM.replace("One hour;Two hours", "One hour;one hour"))
        self.assertTrue(self.has(r, "duration_options has repeats"))
        r, _ = self.run_rows(activities=SWIM + SWIM)
        self.assertTrue(self.has(r, "duplicate activity_id"))

    def test_hospital_rest_rule(self):
        r, _ = self.run_rows(actions=OFF + EAT)
        self.assertTrue(self.has(r, "hospital rest action 'REMED_RESTING' is missing"))
        r, _ = self.run_rows(care="care_service_id\nREMED_CHECKUP\n")
        self.assertTrue(self.has(r, "hospital rest care service 'REMED_RECOVERY' is missing"))
        r, _ = self.run_rows(care=None)
        self.assertTrue(r.valid, r.errors)


if __name__ == "__main__":
    unittest.main()

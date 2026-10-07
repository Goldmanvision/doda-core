"""Tests for doda_equipment_rules. Run: python -m unittest discover -s tests"""
import sys, tempfile, unittest, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doda_equipment_rules as eq, doda_network_rules as net

FH = ",".join(eq.FAMILY_COLUMNS) + "\n"
MH = ",".join(eq.MODEL_COLUMNS) + "\n"
TH = ",".join(net.TIER_COLUMNS) + "\n"
FAMS = ("DESKTOP,D,PERSONAL,2,HDD,NETWORK,,1,true\nLAPTOP,L,PERSONAL,2,HDD,NETWORK,,2,true\n"
        "PDA,P,PERSONAL,2,SC,NETWORK,,3,true\nPHONE,Ph,PERSONAL,2,NONE,PHONE_LINE,,4,true\n"
        "FAX,F,LOCATION,,NONE,PHONE_LINE,,5,true\n")

def make(fams, models, tiers="T1,T,DIALUP,1,,1,true\n"):
    d = Path(tempfile.gettempdir()) / f"doda_eqtest_{uuid.uuid4().hex}"
    s = d / "data_authoring" / "source"; s.mkdir(parents=True); (d / "tools").mkdir()
    (s / eq.FAMILIES_FILE).write_text(FH + fams, encoding="utf-8")
    (s / eq.MODELS_FILE).write_text(MH + models, encoding="utf-8")
    (s / net.TIERS_FILE).write_text(TH + tiers, encoding="utf-8")
    return d

def run(d):
    r = net.Result(); eq.validate_equipment(d, r); return r

class T(unittest.TestCase):
    def test_valid(self):
        r = run(make(FAMS, "DK,Desk,DESKTOP,,T1,1,,1,true\nRP,Rot,PHONE,LANDLINE,,1,,2,true\nFX,Fax,FAX,,,1,,3,true\n"))
        self.assertTrue(r.valid, r.errors)
    def test_eight_device_total(self):
        r = run(make(FAMS.replace("PDA,P,PERSONAL,2", "PDA,P,PERSONAL,3"), ""))
        self.assertTrue(any("total is 9" in e for e in r.errors))
    def test_network_model_needs_tier(self):
        r = run(make(FAMS, "DK,Desk,DESKTOP,,,1,,1,true\n"))
        self.assertTrue(any("needs network_tier_id" in e for e in r.errors))
    def test_phone_not_networked(self):
        r = run(make(FAMS, "RP,Rot,PHONE,LANDLINE,T1,1,,1,true\n"))
        self.assertTrue(any("not network connected" in e for e in r.errors))
    def test_phone_needs_line_kind(self):
        r = run(make(FAMS, "RP,Rot,PHONE,,,1,,1,true\n"))
        self.assertTrue(any("LANDLINE or MOBILE" in e for e in r.errors))
    def test_location_has_no_limit(self):
        r = run(make(FAMS.replace("FAX,F,LOCATION,,", "FAX,F,LOCATION,1,"), ""))
        self.assertTrue(any("LOCATION equipment" in e for e in r.errors))
    def test_phone_line_no_storage(self):
        r = run(make(FAMS.replace("PHONE,Ph,PERSONAL,2,NONE", "PHONE,Ph,PERSONAL,2,HDD"), ""))
        self.assertTrue(any("no HDD/SC" in e for e in r.errors))
    def test_unknown_tier(self):
        r = run(make(FAMS, "DK,Desk,DESKTOP,,ZZ,1,,1,true\n"))
        self.assertTrue(any("unknown network_tier_id" in e for e in r.errors))

if __name__ == "__main__": unittest.main()

import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doda_foims_x_roster import SandboxRoster, Agent, AVAILABLE, UNAVAILABLE

def tables():
    ids = ("SIGNALS_ANALYSIS", "DATA_SYSTEMS", "FIELD_RESPONSE", "OCCULT_RESPONSE")
    return {"qualification_catalog": [
        {"qualification_id": q, "active": "TRUE"} for q in ids
    ]}

class RosterTests(unittest.TestCase):
    def test_fixed_roster_order(self):
        ids = [a.agent_id for a in SandboxRoster(tables()).agents()]
        self.assertEqual(ids, ["AGENT_001", "AGENT_002", "AGENT_003", "AGENT_004"])

    def test_clean_audit(self):
        self.assertEqual(SandboxRoster(tables()).audit(), [])

    def test_missing_qualification_flagged(self):
        t = tables()
        t["qualification_catalog"] = t["qualification_catalog"][1:]
        self.assertTrue(any("SIGNALS_ANALYSIS MISSING" in i for i in SandboxRoster(t).audit()))

    def test_inactive_qualification_flagged(self):
        t = tables()
        t["qualification_catalog"][0]["active"] = "FALSE"
        self.assertTrue(any("INACTIVE" in i for i in SandboxRoster(t).audit()))

    def test_available_with_excludes_unavailable(self):
        ids = [a.agent_id for a in SandboxRoster(tables()).available_with("DATA_SYSTEMS")]
        self.assertEqual(ids, ["AGENT_001"])

    def test_set_availability_and_reset(self):
        r = SandboxRoster(tables())
        r.set_availability("AGENT_004", AVAILABLE)
        self.assertEqual(len(r.available_with("DATA_SYSTEMS")), 2)
        r.reset()
        self.assertEqual(r.get("AGENT_004").availability, UNAVAILABLE)

    def test_invalid_inputs_rejected(self):
        r = SandboxRoster(tables())
        with self.assertRaises(KeyError):
            r.set_availability("NOPE", AVAILABLE)
        with self.assertRaises(ValueError):
            r.set_availability("AGENT_001", "BUSY")
        with self.assertRaises(ValueError):
            SandboxRoster(tables(), agents=(Agent("A", "x", ()), Agent("A", "y", ())))

    def test_tables_not_mutated(self):
        t = tables()
        before = deepcopy(t)
        r = SandboxRoster(t)
        r.audit()
        r.set_availability("AGENT_001", UNAVAILABLE)
        self.assertEqual(t, before)

if __name__ == "__main__":
    unittest.main()

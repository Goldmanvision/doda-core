"""Tests for doda_network_rules (authoring slice). Run: python -m unittest discover -s tests"""
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doda_network_rules as n

TH = "tier_id,display_name,network_type,generation,description,sort_order,active\n"
HH = "model_id,display_name,hardware_kind,tier_id,description,sort_order,active\n"

def make(tiers, hw):
    # Plain mkdir instead of mkdtemp: Python 3.13+ mkdtemp applies owner-only ACLs on Windows,
    # which breaks nested mkdir under restricted/sandboxed accounts.
    import uuid
    d = Path(tempfile.gettempdir()) / f"doda_nettest_{uuid.uuid4().hex}"
    s = d / "data_authoring" / "source"; s.mkdir(parents=True)
    (d / "tools").mkdir()
    if tiers is not None: (s / n.TIERS_FILE).write_text(TH + tiers, encoding="utf-8")
    if hw is not None: (s / n.HARDWARE_FILE).write_text(HH + hw, encoding="utf-8")
    return d

def run(d):
    r = n.Result(); n.validate_contract(r); n.validate_network(d, r); return r

class T(unittest.TestCase):
    def test_contract_self_check(self):
        r = n.Result(); n.validate_contract(r); self.assertEqual(r.errors, [])
    def test_valid_export(self):
        d = make("DIAL_1,Dial,DIALUP,1,,1,true\n", "M1,Modem,MODEM,DIAL_1,,1,true\nR1,Router,ROUTER,DIAL_1,,2,true\n")
        r, out = n.export(d); self.assertTrue(r.valid, r.errors)
        p = json.loads(out.read_text()); self.assertEqual(len(p["hardwareModels"]), 2)
        self.assertFalse(p["contract"]["runtimeImplemented"])
    def test_exact_match_only(self):
        self.assertTrue(n.router_compatible("A", "A")); self.assertFalse(n.router_compatible("A", "B"))
    def test_router_without_modem_warns(self):
        d = make("A,A,DSL,1,,1,true\nB,B,DSL,2,,2,true\n", "M,M,MODEM,A,,1,true\nR,R,ROUTER,B,,2,true\n")
        r = run(d); self.assertTrue(r.valid); self.assertTrue(any("never connect" in w for w in r.warnings))
    def test_unknown_tier_and_kind(self):
        d = make("A,A,DSL,1,,1,true\n", "M,M,SWITCH,Z,,1,true\n")
        r = run(d); self.assertEqual(len(r.errors), 2)
    def test_duplicate_type_generation(self):
        r = run(make("A,A,DSL,1,,1,true\nB,B,dsl,1,,2,true\n", ""))
        self.assertTrue(any("already used" in e for e in r.errors))
    def test_inactive_tier_reference(self):
        r = run(make("A,A,DSL,1,,1,false\n", "M,M,MODEM,A,,1,true\n"))
        self.assertTrue(any("inactive tier" in e for e in r.errors))
    def test_missing_files_skip(self):
        r = run(make(None, None)); self.assertTrue(r.valid); self.assertEqual(len(r.warnings), 2)
    def test_failed_validation_does_not_write(self):
        d = make("A,A,DSL,1,,1,true\n", "M,M,MODEM,Q,,1,true\n")
        r, out = n.export(d); self.assertIsNone(out)
        self.assertFalse((d / "generated").exists())
    def test_signoff_roles_and_no_expiry(self):
        c = n.build_contract()
        self.assertEqual(c["rolePermissions"]["signoff"]["allowed_roles"], ["AGENT", "ANALYST"])
        self.assertFalse(c["ruleFlags"]["awaiting_signoff_expires"]); self.assertFalse(c["ruleFlags"]["global_pause_all"])
    def test_task_interruption_contract(self):
        ti = n.build_contract()["taskInterruption"]
        self.assertEqual(ti["processing"]["incapacity"], "FAIL_DESTROY_UNRESOLVED")
        self.assertEqual(ti["processing"]["takeover_by_qualified"], "KEEP_PROGRESS")
        self.assertEqual(ti["system_update"]["any_interruption"], "RESTART")
        c = n.build_contract()
        self.assertEqual(ti["system_update"]["overdue_risk_through_restart"], "KEEPS_BUILDING_UNTIL_COMPLETE")
        self.assertEqual(c["permanentUnavailabilityCauses"], ["DEATH", "DISMISSAL", "DEFECTION", "RETIREMENT"])
        self.assertEqual(c["ruleFlags"]["technician_both_ends"], "ONLY_IF_CAN_TRAVEL_BETWEEN_LOCATIONS")
        self.assertNotIn("NET-03b", c["openItems"])
    def test_broken_contract_detected(self):
        orig = list(n.TRANSFER_TRANSITIONS)
        try:
            n.TRANSFER_TRANSITIONS.append(("AWAITING_SIGNOFF", "LOST", "timeout", ""))
            r = n.Result(); n.validate_contract(r); self.assertTrue(r.errors)
        finally:
            n.TRANSFER_TRANSITIONS[:] = orig

if __name__ == "__main__": unittest.main()

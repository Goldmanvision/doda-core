import csv
import hashlib
import io
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
work = root / "tools" / "doda_content_workbench"
src = root / "data_authoring" / "source"
module = work / "doda_territory_rules.py"
settings = src / "territory_settings.csv"
decisions = root / "docs/workbench/spec/DESIGN_DECISIONS_2026-10-08.md"
history = root / "docs/workbench/history/Mission_Pricing_And_Gate_Contract_2026-10-08.md"
test_path = work / "tests/test_mission_progression_contract.py"

def stop(message):
    raise SystemExit("STOP: " + message + " No project files were modified.")

for path in (module, settings, decisions):
    if not path.is_file():
        stop(str(path) + " was not found.")
for path in (history, test_path):
    if path.exists():
        stop(str(path) + " already exists.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")

raw = module.read_bytes()
bom = raw.startswith(b"\xef\xbb\xbf")
original = raw.decode("utf-8-sig")
crlf = "\r\n" in original
text = original.replace("\r\n", "\n")
if "PROGRESSION_SETTING_UNITS" in text:
    stop("The progression contract is already installed.")

sys.path.insert(0, str(work))
import doda_territory_rules as old

with settings.open(encoding="utf-8-sig", newline="") as fh:
    reader = csv.DictReader(fh)
    if reader.fieldnames != old.SETTING_COLUMNS:
        stop("territory_settings.csv has an unexpected header.")
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        stop("territory_settings.csv contains malformed rows.")

new_settings = [
    ("LEAD_BASE_COST", "Ordinary Lead Base Cost", "EVIDENCE_POINTS",
     "First ordinary paid Lead cost. Positive whole number; undecided."),
    ("LEAD_COST_INCREMENT", "Lead Cost Increase Per Purchase", "EVIDENCE_POINTS",
     "Added for each prior successful ordinary paid purchase. Positive whole number; undecided."),
    ("FINAL_GATE_CHECK_MINUTES", "Final Gate Check Interval", "STRATEGIC_MINUTES",
     "Periodic eligibility checks after Tier 5 unlocks. Undecided."),
    ("CAPSTONE_LEAD_COST", "Tier 5 Capstone Lead Cost", "EVIDENCE_POINTS",
     "Special purchase price, separate from ordinary Lead pricing. Undecided."),
    ("FINAL_MIN_AVAILABLE_FUNDING", "Final Gate Available Funding Minimum", "FUNDING_UNITS",
     "Checks current available Department Funding, not lifetime funding. Whole-unit threshold undecided."),
    ("FINAL_MIN_PREPAREDNESS", "Final Gate Preparedness Minimum", "METRIC_UNITS",
     "Threshold for the PREPAREDNESS metric. Undecided."),
    ("FINAL_MIN_OPERATIONAL_TERRITORIES", "Final Gate Operational Territories Minimum", "COUNT",
     "Minimum operational territory count. Undecided."),
]
new_ids = {entry[0] for entry in new_settings}
if any(row["setting_id"] in new_ids for row in rows):
    stop("A progression setting already exists.")

addition = '''
REQUIRED_SETTINGS = tuple(SETTING_UNITS)
PROGRESSION_SETTING_UNITS = {
    "LEAD_BASE_COST": "EVIDENCE_POINTS",
    "LEAD_COST_INCREMENT": "EVIDENCE_POINTS",
    "FINAL_GATE_CHECK_MINUTES": "STRATEGIC_MINUTES",
    "CAPSTONE_LEAD_COST": "EVIDENCE_POINTS",
    "FINAL_MIN_AVAILABLE_FUNDING": "FUNDING_UNITS",
    "FINAL_MIN_PREPAREDNESS": "METRIC_UNITS",
    "FINAL_MIN_OPERATIONAL_TERRITORIES": "COUNT",
}
SETTING_UNITS.update(PROGRESSION_SETTING_UNITS)

RULES["missionProgression"] = {
    "lowerTiersRemainAvailable": True,
    "ordinaryLeadPricing": {
        "model": "LINEAR",
        "scope": "DEPARTMENT_WIDE",
        "counter": "SUCCESSFUL_ORDINARY_PAID_LEAD_PURCHASES",
        "formula": "BASE_COST + PRIOR_SUCCESSFUL_PURCHASES * INCREMENT",
        "excluded": ["FREE_TUTORIAL", "FAILED_PURCHASE", "REDEPLOYMENT"],
        "resetsOnTerritoryOrTierChange": False,
    },
    "finalGate": {
        "checksBeginAfterTier": "TIER_5",
        "evaluation": "PERIODIC",
        "requirementsCombine": "ALL",
        "readinessMetricId": "PREPAREDNESS",
        "fundingBasis": "CURRENT_AVAILABLE_DEPARTMENT_FUNDING",
        "requiredUpgradeReferences": None,
        "requiredPlotMilestoneOrItemReferences": None,
        "capstoneMissionReference": None,
    },
    "capstone": {
        "tierId": "TIER_5",
        "priceModel": "SPECIAL_SEPARATE_PRICE",
        "offerRequiresAllFinalGateRequirements": True,
        "expires": False,
        "redeploymentRequiresRepurchase": False,
        "retainsMissionState": True,
        "completion": "AUTHORED_OBJECTIVES",
        "unlocksTierId": "TIER_6",
        "unlockIsPermanent": True,
        "advancesOrdinaryPurchaseCounter": None,
        "eligibilityRechecksAfterPurchase": None,
    },
}


def ordinary_lead_cost(base_cost, increment, prior_purchases):
    values = (base_cost, increment, prior_purchases)
    if any(value is None for value in values):
        return None
    if any(type(value) is not int for value in values):
        raise ValueError("Lead pricing inputs must be whole integers")
    if base_cost < 1 or increment < 1 or prior_purchases < 0:
        raise ValueError("Costs must be positive and purchases nonnegative")
    return base_cost + increment * prior_purchases


def build_mission_progression(data):
    index = {row["settingId"]: row for row in data["settings"]}

    def usable(setting_id):
        row = index.get(setting_id)
        if row is None or not row["active"] or row["value"] is None:
            return None
        return int(row["value"])

    missing_pricing = [
        sid for sid in ("LEAD_BASE_COST", "LEAD_COST_INCREMENT")
        if usable(sid) is None
    ]
    gate_ids = [
        "FINAL_GATE_CHECK_MINUTES", "CAPSTONE_LEAD_COST",
        "FINAL_MIN_AVAILABLE_FUNDING", "FINAL_MIN_PREPAREDNESS",
        "FINAL_MIN_OPERATIONAL_TERRITORIES",
    ]
    missing_gate = [sid for sid in gate_ids if usable(sid) is None]
    tiers = {row["tierId"]: row for row in data["missionTiers"]}
    for tier_id in ("TIER_5", "TIER_6"):
        row = tiers.get(tier_id)
        if row is None or not row["active"] or row["minLifetimeEvidence"] is None:
            missing_gate.append(tier_id + "_ACTIVE_WITH_THRESHOLD")
    missing_gate.extend([
        "REQUIRED_UPGRADE_REFERENCES",
        "REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES",
        "CAPSTONE_MISSION_REFERENCE",
        "CAPSTONE_PURCHASE_COUNTER_POLICY",
        "POST_PURCHASE_ELIGIBILITY_RECHECK_POLICY",
    ])
    return {
        "contractVersion": "2026-10-08.1",
        "ordinaryPricing": {
            "baseCost": usable("LEAD_BASE_COST"),
            "increment": usable("LEAD_COST_INCREMENT"),
            "configured": not missing_pricing,
            "missingConfiguration": missing_pricing,
        },
        "finalGate": {
            "numericSettings": {sid: usable(sid) for sid in gate_ids},
            "configured": not missing_gate,
            "missingConfiguration": missing_gate,
        },
        "unconfiguredPolicy": "DO_NOT_PURCHASE_OR_AUTO_UNLOCK",
        "runtimeImplemented": False,
    }

'''

def replace_once(old_text, new_text):
    global text
    count = text.count(old_text)
    if count != 1:
        stop("Expected one anchor; found %d: %s" % (count, old_text[:70]))
    text = text.replace(old_text, new_text)

replace_once("OPEN_ITEMS = {", addition + "\nOPEN_ITEMS = {")
replace_once(
    "    for sid in SETTING_UNITS:\n",
    "    for sid in REQUIRED_SETTINGS:\n",
)
old_return = '''    return {"territories": _validate_territories(src, res), "settings": _validate_settings(src, res),
            "missionTiers": _validate_tiers(src, res),
            "mapFormats": sorted(formats.values(), key=lambda x: (x["sortOrder"] or 0, x["formatId"])),
            "maps": _validate_maps(src, formats, res)}
'''
new_return = old_return.replace('    return {', '    data = {', 1) + '''
    if res.valid:
        data["missionProgression"] = build_mission_progression(data)
    return data
'''
replace_once(old_return, new_return)
replace_once(
    '"TERR-OPEN-01": "Mission tier names, count and thresholds; gating rules for the final authored tier.",',
    '"TERR-OPEN-01": "Six mission tiers settled; thresholds, concrete final-gate references and values remain open.",',
)
compile(text, str(module), "exec")

sort_order = max([int(row["sort_order"]) for row in rows] or [0])
for index, (sid, name, unit, description) in enumerate(new_settings, 1):
    row = {key: "" for key in old.SETTING_COLUMNS}
    row.update(
        setting_id=sid, display_name=name, unit=unit,
        source_reference="MTIER-03 to MTIER-11 (2026-10-08)",
        description=description,
        sort_order=str(sort_order + index * 10),
        active="false",
    )
    rows.append(row)
buf = io.StringIO(newline="")
writer = csv.DictWriter(buf, fieldnames=old.SETTING_COLUMNS, lineterminator="\r\n")
writer.writeheader()
writer.writerows(rows)

test_text = r'''import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import doda_network_rules as net
import doda_territory_rules as terr
import doda_page_registry as registry
import test_territory_rules as base


class MissionProgressionContractTests(base.TerritoryTests):
    test_valid_and_warnings = None
    test_exactly_one_starting = None
    test_player_only_agents = None
    test_starting_needs_hq = None
    test_population = None
    test_settings = None
    test_tiers = None
    test_maps = None
    test_export_not_runtime = None
    test_shipped_data = None

    def test_linear_cost(self):
        self.assertEqual(terr.ordinary_lead_cost(10, 2, 0), 10)
        self.assertEqual(terr.ordinary_lead_cost(10, 2, 3), 16)

    def test_unconfigured_cost_is_not_zero(self):
        self.assertIsNone(terr.ordinary_lead_cost(None, 2, 0))
        self.assertIsNone(terr.ordinary_lead_cost(10, None, 0))

    def test_invalid_cost_inputs(self):
        for values in [(0, 2, 0), (10, 0, 0), (10, 2, -1), (True, 2, 0)]:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    terr.ordinary_lead_cost(*values)

    def test_editor_choices_include_new_settings(self):
        spec = registry.TABLE_METADATA["territory_settings"]
        choices = next(field.choices for field in spec.fields if field.name == "setting_id")
        self.assertTrue(set(terr.PROGRESSION_SETTING_UNITS).issubset(set(choices)))

    def test_draft_gate_stays_unconfigured(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        contract = data["missionProgression"]
        self.assertFalse(contract["ordinaryPricing"]["configured"])
        self.assertFalse(contract["finalGate"]["configured"])
        self.assertIn("REQUIRED_UPGRADE_REFERENCES",
                      contract["finalGate"]["missingConfiguration"])

    def test_active_pricing_can_be_configured(self):
        rows = base.setting_rows()
        base.edit(rows, "setting_id", "LEAD_BASE_COST", value="10", active="true")
        base.edit(rows, "setting_id", "LEAD_COST_INCREMENT", value="2", active="true")
        result, data = self.validate(settings=rows)
        self.assertTrue(result.valid, result.errors)
        self.assertTrue(data["missionProgression"]["ordinaryPricing"]["configured"])

    def test_zero_increment_rejected(self):
        rows = base.setting_rows()
        base.edit(rows, "setting_id", "LEAD_COST_INCREMENT", value="0")
        result, _ = self.validate(settings=rows)
        self.assertTrue(any("value must be at least 1" in error for error in result.errors))

    def test_capstone_and_final_gate_contract(self):
        rules = terr.RULES["missionProgression"]
        self.assertEqual(rules["finalGate"]["readinessMetricId"], "PREPAREDNESS")
        self.assertEqual(rules["finalGate"]["requirementsCombine"], "ALL")
        self.assertFalse(rules["capstone"]["expires"])
        self.assertFalse(rules["capstone"]["redeploymentRequiresRepurchase"])
        self.assertTrue(rules["capstone"]["retainsMissionState"])
        self.assertTrue(rules["capstone"]["unlockIsPermanent"])
        self.assertEqual(rules["capstone"]["completion"], "AUTHORED_OBJECTIVES")


if __name__ == "__main__":
    unittest.main()
'''
# Remove base-class inheritance without duplicating inherited test methods.
test_text = test_text.replace(
    "class MissionProgressionContractTests(base.TerritoryTests):",
    "class MissionProgressionContractTests(unittest.TestCase):\n"
    "    setUp = base.TerritoryTests.setUp\n"
    "    tearDown = base.TerritoryTests.tearDown\n"
    "    make_root = base.TerritoryTests.make_root\n"
    "    validate = base.TerritoryTests.validate"
)
compile(test_text, str(test_path), "exec")

marker = "## Mission pricing and gate contract - implementation (2026-10-08)"
old_doc = decisions.read_bytes()
doc = old_doc.decode("utf-8-sig")
if marker in doc:
    stop("This implementation is already documented.")
addendum = """
## Mission pricing and gate contract - implementation (2026-10-08)
- Added seven numeric draft settings to territory_settings.csv: ordinary Lead base cost, increment, final-check interval, capstone cost, current available funding minimum, PREPAREDNESS minimum, operational territory minimum.
- All values blank and rows inactive. Numeric settings currently use positive whole units.
- territory_catalog.json now exports missionProgression configuration status and the approved rules under rules.missionProgression.
- Missing or inactive settings are unconfigured, never silently zero.
- Required upgrade/plot references, capstone mission reference, and two capstone policies are unresolved and prevent a fully configured final gate.
- Capstone purchase's effect on the ordinary purchase counter remains OPEN.
- Eligibility rechecks after capstone purchase remain OPEN.
- Added eight tests. No campaign state, Evidence transactions or native runtime implemented.
"""
history_text = """# Mission Pricing and Gate Contract - 2026-10-08

Authoring/export only. No native simulation implemented.

Changes:
- Extended territory_settings.csv with seven inactive blank numeric settings.
- Extended doda_territory_rules.py and its existing territory catalog export.
- Existing Territory Settings editor choices update from the module.
- Added eight mission-progression contract tests.
- Missing configuration blocks readiness; no numerical balance values invented.

Required upgrade/plot IDs and capstone mission reference are not yet authored.
Capstone counter and post-purchase recheck policies remain undecided.

Original module, settings and decisions backed up with SHA-256 manifest.
"""

backups = work / "backups"
numbers = [
    int(match.group(1))
    for path in backups.iterdir()
    if path.is_dir() and (match := re.match(r"^v(\d+)_", path.name))
] if backups.exists() else []
number = max(numbers, default=52) + 1
backup = backups / (
    f"v{number:03d}_mission_pricing_gate_" +
    datetime.now().strftime("%Y%m%d_%H%M%S")
)
manifest = []
for path in (module, settings, decisions):
    relative = path.relative_to(root)
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed.")
    manifest.append(f"{digest}  {relative.as_posix()}")
(backup / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

out_module = text.replace("\n", "\r\n") if crlf else text
writes = {
    module: (b"\xef\xbb\xbf" if bom else b"") + out_module.encode("utf-8"),
    settings: buf.getvalue().encode("utf-8"),
    test_path: test_text.encode("utf-8"),
    history: history_text.encode("utf-8"),
    decisions: old_doc + (("" if doc.endswith("\n") else "\n") + addendum).encode("utf-8"),
}
originals = {path: path.read_bytes() if path.exists() else None for path in writes}
try:
    for path, data in writes.items():
        path.write_bytes(data)
except Exception:
    for path, data in originals.items():
        if data is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(data)
    raise

print("=== COPY FROM HERE ===", flush=True)
print("Backup folder:", backup, flush=True)
print("Added numeric settings: 7; all blank and inactive.", flush=True)

for label, args in [
    ("test suite", ["-m", "unittest", "discover", "-s", "tests"]),
    ("territory: real data", ["doda_territory_rules.py", "validate"]),
]:
    print("--- " + label + " ---", flush=True)
    result = subprocess.run(
        [sys.executable, *args], cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, errors="replace",
    )
    print(result.stdout, end="", flush=True)
    print("Process exit code:", result.returncode, flush=True)
    if result.returncode:
        print("Patch remains applied; do not rerun. Paste the failure output.", flush=True)
        sys.exit(result.returncode)
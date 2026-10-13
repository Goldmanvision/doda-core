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
work = root / "tools/doda_content_workbench"
src = root / "data_authoring/source"
module = work / "doda_territory_rules.py"
authored_module = work / "doda_authored_mission_rules.py"
tiers_csv = src / "mission_tiers.csv"
settings_csv = src / "territory_settings.csv"
capstone_test = work / "tests/test_capstone_setting_corrections.py"
integration_test = work / "tests/test_territory_identity_integration.py"
new_test = work / "tests/test_tier_thresholds_and_generation.py"
doc = root / "docs/workbench/spec/DESIGN_DECISIONS_2026-10-08.md"
history = root / "docs/workbench/history/Tier_Thresholds_And_Generation_2026-10-08.md"

def stop(message):
    print("STOP: " + message + " No project files were modified.", flush=True)
    sys.exit(1)

for path in (module, authored_module, tiers_csv, settings_csv, capstone_test, integration_test, doc):
    if not path.is_file():
        stop(str(path) + " was not found.")
for path in (new_test, history):
    if path.exists():
        stop(str(path) + " already exists.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")

def read_csv(path):
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return raw, reader.fieldnames, list(reader)

def dump_csv(columns, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")

def replace_once(source, anchor, replacement, label):
    count = source.count(anchor)
    if count != 1:
        stop("%s anchor found %d times: %s" % (label, count, anchor[:90]))
    return source.replace(anchor, replacement)

def load(path):
    raw = path.read_bytes()
    original = raw.decode("utf-8-sig")
    return raw, "\r\n" in original, original.replace("\r\n", "\n")

def encode(body, original_raw, use_crlf):
    out = body.replace("\n", "\r\n") if use_crlf else body
    return (b"\xef\xbb\xbf" if original_raw.startswith(b"\xef\xbb\xbf") else b"") + out.encode("utf-8")

tiers_raw, tier_columns, tier_rows = read_csv(tiers_csv)
thresholds = {"TIER_1": "1000", "TIER_2": "10000", "TIER_3": "100000",
              "TIER_4": "1000000", "TIER_5": "10000000", "TIER_6": "100000000"}
descriptions = {
    "TIER_1": "First generated mission tier. Starts at 1,000 lifetime Evidence. The tutorial runs before it, from the 900 starting Evidence.",
    "TIER_2": "Generated mission tier. Starts at 10,000 lifetime Evidence.",
    "TIER_3": "Generated mission tier. Starts at 100,000 lifetime Evidence.",
    "TIER_4": "Generated mission tier. Starts at 1,000,000 lifetime Evidence.",
    "TIER_5": "Generated mission tier. Starts at 10,000,000 lifetime Evidence.",
    "TIER_6": "Authored end-game tier. Starts at 100,000,000 lifetime Evidence. Unlocks automatically when every requirement is met, including completion of the protected Tier 5 capstone after department eligibility checks.",
}
old_values = {"TIER_1": "0", "TIER_2": "", "TIER_3": "", "TIER_4": "", "TIER_5": "", "TIER_6": ""}
for tier_id, value in thresholds.items():
    matches = [row for row in tier_rows if row["tier_id"] == tier_id]
    if len(matches) != 1 or matches[0]["min_lifetime_evidence"] != old_values[tier_id]:
        stop("Tier %s does not have the expected current threshold '%s'." % (tier_id, old_values[tier_id]))
    matches[0]["min_lifetime_evidence"] = value
    matches[0]["description"] = descriptions[tier_id]
tiers_new = dump_csv(tier_columns, tier_rows)

settings_raw, setting_columns, setting_rows = read_csv(settings_csv)
if any(row["setting_id"] == "STARTING_EVIDENCE" for row in setting_rows):
    stop("STARTING_EVIDENCE already exists in territory_settings.csv.")
orders = [int(row["sort_order"]) for row in setting_rows if row["sort_order"].strip().isdigit()]
setting_rows.append({
    "setting_id": "STARTING_EVIDENCE", "display_name": "Starting Evidence", "value": "900",
    "unit": "EVIDENCE_POINTS", "source_reference": "User decision 2026-10-08 (PROG-01)",
    "description": "Evidence the player starts with. The tutorial lets the player easily earn the remaining amount to reach the first tier threshold.",
    "sort_order": str((max(orders) if orders else 0) + 10), "active": "true"})
settings_new = dump_csv(setting_columns, setting_rows)

module_raw, module_crlf, text = load(module)
if "GENERATION_RULES" in text:
    stop("The generation rules are already installed.")
text = replace_once(text, '"LEAD_COST_GROWTH_PERCENT": "PERCENT",',
                    '"LEAD_COST_GROWTH_PERCENT": "PERCENT",\n    "STARTING_EVIDENCE": "EVIDENCE_POINTS",',
                    "progression setting units")
text = replace_once(text,
    '''    if ordered and ordered[0]["minLifetimeEvidence"] not in (None, 0):
        res.errors.append(f"{ordered[0]['_ctx']}: the first tier must start at 0 lifetime Evidence")
''', "", "first tier rule")
generation = '''GENERATION_RULES = {
    "startingEvidenceSetting": "STARTING_EVIDENCE",
    "tutorialBeforeFirstTier": True,
    "tierUnlock": "ALL_REQUIREMENTS_MET_AUTOMATIC",
    "tierUnlockMessaging": "HINTED_IN_GAME_NOT_ANNOUNCED",
    "lifetimeEvidenceIncludesStartingEvidence": True,
    "spendingReducesLifetimeEvidence": False,
    "operationalTerritoryPlacement": "RANDOM_ACROSS_GREATER_TERRITORIES",
    "authoredTerritoriesExcludedUntilUnlocked": True,
    "multipleTerritoriesPerTier": True,
    "missionTierPool": "ALL_TIERS_UP_TO_HIGHEST_ACHIEVED",
    "missionPoolAppliesToEveryUnlockedTerritory": True,
    "missionMixWeights": "EQUAL_ACROSS_UNLOCKED_TIERS",
    "territoryUnlockMechanism": "CONGRESSIONAL_SUPPORT",
    "congressionalSupportGrants": ["DEPARTMENT_FUNDING", "OPERATIONAL_TERRITORIES"],
    "congressionalSupportInputs": ["LIFETIME_EVIDENCE", "PREPAREDNESS", "MISSION_SUCCESS_RATE"],
    "congressionalSupportScoring": "COMPENSATORY_COMBINED_SCORE",
    "congressionalSupportLevels": "DISCRETE_HIDDEN_FROM_PLAYER",
    "congressionalSupportImplemented": False,
}


def ordinary_lead_cost('''
text = replace_once(text, "def ordinary_lead_cost(", generation, "generation rules")
summary = '''def _tutorial_summary(data, starting):
    tiers = sorted(data.get("missionTiers", []), key=lambda t: (t["sortOrder"] or 0, t["tierId"]))
    first = tiers[0]["minLifetimeEvidence"] if tiers else None
    known = starting is not None and first is not None
    return {"startingEvidence": starting, "firstTierThreshold": first,
            "evidenceToFirstTier": (first - starting) if known else None,
            "configured": bool(known and starting < first)}


def build_mission_progression(data):
'''
text = replace_once(text, "def build_mission_progression(data):\n", summary, "progression def")
text = replace_once(text, '"ordinaryPricing": {',
    '"tutorial": _tutorial_summary(data, usable("STARTING_EVIDENCE")),\n        "ordinaryPricing": {',
    "pricing block")
text = replace_once(text, '"contractVersion": "2026-10-08.4",', '"contractVersion": "2026-10-08.5",', "contract version")
text = replace_once(text, '"rules": RULES, "openItems": OPEN_ITEMS,',
                    '"rules": RULES, "generationRules": GENERATION_RULES, "openItems": OPEN_ITEMS,', "export payload")
compile(text, str(module), "exec")

authored_raw, authored_crlf, authored_text = load(authored_module)
pattern = re.compile(r'("tier6UnlockTrigger"\s*:\s*)"UNDECIDED"')
if len(pattern.findall(authored_text)) != 1:
    stop("Expected exactly one tier6UnlockTrigger UNDECIDED entry in the authored mission rules.")
authored_text = pattern.sub(lambda m: m.group(1) + '"ALL_REQUIREMENTS_MET_AUTOMATIC"', authored_text)
authored_text = replace_once(authored_text,
    '"Tier 6 unlock trigger (undecided) and whether one capstone Lead opens the whole chain (leaning no: Leads still open mission areas)."',
    '"Whether one capstone Lead opens the whole chain (leaning no: Leads still open mission areas)."',
    "open item")
compile(authored_text, str(authored_module), "exec")

capstone_raw, capstone_crlf, capstone_text = load(capstone_test)
capstone_text = replace_once(capstone_text,
    'self.assertEqual(am.RULES["tier6UnlockTrigger"], "UNDECIDED")',
    'self.assertEqual(am.RULES["tier6UnlockTrigger"], "ALL_REQUIREMENTS_MET_AUTOMATIC")',
    "capstone test")
compile(capstone_text, str(capstone_test), "exec")

integration_raw, integration_crlf, integration_text = load(integration_test)
old_assert = 'self.assertEqual(payload["missionProgression"]["contractVersion"], "2026-10-08.4")'
integration_text = replace_once(integration_text, old_assert, old_assert.replace(".4", ".5"), "integration test")
compile(integration_text, str(integration_test), "exec")

test_text = r'''import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_authored_mission_rules as am
import doda_network_rules as net
import doda_territory_rules as terr

ROOT = net.find_project_root(Path(__file__).resolve().parent)


def validate(root):
    result = net.Result()
    data = terr.validate_territory(root, result)
    return result, data


class TierThresholdAndGenerationTests(unittest.TestCase):
    def test_tier_thresholds(self):
        result, data = validate(ROOT)
        self.assertTrue(result.valid, result.errors)
        values = [t["minLifetimeEvidence"] for t in data["missionTiers"]]
        self.assertEqual(values, [1000, 10000, 100000, 1000000, 10000000, 100000000])

    def test_tutorial_summary(self):
        result, data = validate(ROOT)
        self.assertTrue(result.valid, result.errors)
        tutorial = data["missionProgression"]["tutorial"]
        self.assertEqual(tutorial["startingEvidence"], 900)
        self.assertEqual(tutorial["firstTierThreshold"], 1000)
        self.assertEqual(tutorial["evidenceToFirstTier"], 100)
        self.assertTrue(tutorial["configured"])

    def test_thresholds_must_still_increase(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / "data_authoring" / "source"
        shutil.copytree(ROOT / "data_authoring" / "source", target)
        path = target / "mission_tiers.csv"
        with path.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
            columns = list(rows[0].keys())
        rows[1]["min_lifetime_evidence"] = "1000"
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\r\n")
            writer.writeheader()
            writer.writerows(rows)
        result, _ = validate(Path(temp.name))
        self.assertTrue(any("must strictly increase" in e for e in result.errors))

    def test_generation_rules(self):
        rules = terr.GENERATION_RULES
        self.assertEqual(rules["tierUnlock"], "ALL_REQUIREMENTS_MET_AUTOMATIC")
        self.assertEqual(rules["missionTierPool"], "ALL_TIERS_UP_TO_HIGHEST_ACHIEVED")
        self.assertEqual(rules["missionMixWeights"], "EQUAL_ACROSS_UNLOCKED_TIERS")
        self.assertEqual(rules["operationalTerritoryPlacement"], "RANDOM_ACROSS_GREATER_TERRITORIES")
        self.assertTrue(rules["authoredTerritoriesExcludedUntilUnlocked"])
        self.assertEqual(rules["territoryUnlockMechanism"], "CONGRESSIONAL_SUPPORT")
        self.assertEqual(rules["congressionalSupportScoring"], "COMPENSATORY_COMBINED_SCORE")
        self.assertTrue(rules["lifetimeEvidenceIncludesStartingEvidence"])
        self.assertFalse(rules["spendingReducesLifetimeEvidence"])
        self.assertFalse(rules["congressionalSupportImplemented"])
        self.assertEqual(am.RULES["tier6UnlockTrigger"], "ALL_REQUIREMENTS_MET_AUTOMATIC")

    def test_starting_evidence_setting(self):
        path = ROOT / "data_authoring/source/territory_settings.csv"
        with path.open(encoding="utf-8-sig", newline="") as fh:
            rows = {row["setting_id"]: row for row in csv.DictReader(fh)}
        row = rows["STARTING_EVIDENCE"]
        self.assertEqual(row["value"], "900")
        self.assertEqual(row["unit"], "EVIDENCE_POINTS")
        self.assertEqual(row["active"].lower(), "true")


if __name__ == "__main__":
    unittest.main()
'''
compile(test_text, str(new_test), "exec")

doc_raw = doc.read_bytes()
marker = "## Tier thresholds, starting Evidence and generation rules - CONFIRMED (2026-10-08)"
if marker in doc_raw.decode("utf-8-sig"):
    stop("This update is already documented.")
addendum = """
## Tier thresholds, starting Evidence and generation rules - CONFIRMED (2026-10-08)
- MTIER-16: Lifetime Evidence thresholds: Tier 1 at 1,000; Tier 2 at 10,000; Tier 3 at 100,000; Tier 4 at 1,000,000; Tier 5 at 10,000,000; Tier 6 at 100,000,000. Thresholds must strictly increase.
- MTIER-17: The old rule that the first tier starts at 0 lifetime Evidence is removed. The tutorial runs before Tier 1.
- PROG-01: The player starts with 900 Evidence (setting STARTING_EVIDENCE) and enough Evidence in the first tutorial mission areas to easily earn the remaining 100 to unlock Tier 1. CONFIRMED: the starting 900 counts toward lifetime Evidence, and spending Evidence never reduces lifetime Evidence.
- MTIER-18: A tier unlocks automatically when every requirement for it is met. The game hints at this through text, dialogue and messages instead of announcing it. This resolves the earlier undecided Tier 6 unlock trigger; Tier 6 still lists completion of the protected Tier 5 capstone after department checks.
- TERR-49: Unlocked operational territories are randomized and can appear in any Greater Territory, except authored territories before they are unlocked. A player can unlock several territories within one mission tier.
- TERR-50: Every operational territory generates missions for all tiers up to the highest tier the player has achieved. A territory unlocked at or before Tier 2 offers Tier 1 to 4 missions when the player reaches Tier 4.
- TERR-51: Missions from all unlocked tiers are weighted equally. This pushes the player to send agents to lower-tier missions and to deploy personally on higher tiers.
- CONG-01: New operational territories and Department Funding come from Congressional Support. It is earned through lifetime Evidence, high preparedness, and a threshold percentage of successful missions.
- CONG-02: Congressional Support is reached in discrete levels, hidden from the player so good play is a surprise and a reward.
- CONG-03: The three inputs combine into one score and a strong input can make up for a weak one, so players can progress in different styles.
- CONG-04: Department Funding is the main spendable currency after Evidence (equipment, tactical gear, hiring). It is not in the metrics table; metrics are bounded 0 to 1000 gauges. Recommended: keep it as a currency. The Congressional Support table is not built yet.
- OPEN: score weights, caps, level thresholds and grant sizes; the success-rate threshold; per-tier upgrade requirements (upgrade names not supplied yet).
- DECIDED: one mission_tier_requirements table is kept. The editor has no filter support; a per-tier view is deferred.
- Authoring only. No generator or Congressional Support behavior implemented.
"""
history_text = """# Tier Thresholds, Starting Evidence And Generation Rules - 2026-10-08

Set the six lifetime Evidence thresholds, added STARTING_EVIDENCE (900), removed
the first-tier-starts-at-zero rule, recorded automatic tier unlock, the random
territory and mission-pool rules, equal mission weighting and Congressional
Support as the territory unlock mechanism in the export (generationRules), and
added a tutorial summary to the mission progression contract (version 2026-10-08.5).
The Congressional Support table is not built yet.
"""

backups = work / "backups"
numbers = []
if backups.exists():
    for path in backups.iterdir():
        match = re.match(r"^v(\d+)_", path.name)
        if path.is_dir() and match:
            numbers.append(int(match.group(1)))
backup = backups / (f"v{max(numbers, default=66)+1:03d}_tier_thresholds_" +
                    datetime.now().strftime("%Y%m%d_%H%M%S"))
backed_up = [(module, module_raw), (authored_module, authored_raw), (tiers_csv, tiers_raw),
             (settings_csv, settings_raw), (capstone_test, capstone_raw),
             (integration_test, integration_raw), (doc, doc_raw)]
manifest = []
for path, data in backed_up:
    relative = path.relative_to(root)
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    digest = hashlib.sha256(data).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed.")
    manifest.append(f"{digest}  {relative.as_posix()}")
(backup / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

writes = {
    module: encode(text, module_raw, module_crlf),
    authored_module: encode(authored_text, authored_raw, authored_crlf),
    tiers_csv: tiers_new,
    settings_csv: settings_new,
    capstone_test: encode(capstone_text, capstone_raw, capstone_crlf),
    integration_test: encode(integration_text, integration_raw, integration_crlf),
    new_test: test_text.encode("utf-8"),
    doc: doc_raw + (("" if doc_raw.endswith(b"\n") else "\n") + addendum).encode("utf-8"),
    history: history_text.encode("utf-8"),
}
originals = {path: data for path, data in backed_up}
originals[new_test] = None
originals[history] = None

def rollback():
    for path, data in originals.items():
        if data is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(data)

try:
    for path, data in writes.items():
        path.write_bytes(data)
except Exception:
    rollback()
    raise

print("Backup folder:", backup, flush=True)
print("Expected test total: 323", flush=True)
print("--- test suite ---", flush=True)
suite = subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=work,
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
)
if suite.returncode != 0:
    rollback()
    print("TESTS FAILED. All files were restored from the originals and new files removed.", flush=True)
    print("\n".join(suite.stdout.splitlines()[-80:]), flush=True)
    print("--- test lines mentioning the first-tier rule ---", flush=True)
    for path in sorted((work / "tests").glob("test_*.py")):
        for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if re.search(r"start at 0|first tier|territory_settings.*1[01]\b", line, re.I):
                print("%s:%d: %s" % (path.name, number, line.strip()[:160]), flush=True)
    sys.exit(1)
print(suite.stdout, end="", flush=True)
print("Process exit code:", suite.returncode, flush=True)

failed = 0
for label, arguments in [
    ("territory: real data", ["doda_territory_rules.py", "validate"]),
    ("territory: export", ["doda_territory_rules.py", "export"]),
]:
    print("--- " + label + " ---", flush=True)
    result = subprocess.run(
        [sys.executable, *arguments], cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
    )
    print(result.stdout, end="", flush=True)
    print("Process exit code:", result.returncode, flush=True)
    failed = failed or result.returncode
if failed:
    print("Validation failed after tests passed; patch remains applied. Paste the failure.", flush=True)
    sys.exit(failed)
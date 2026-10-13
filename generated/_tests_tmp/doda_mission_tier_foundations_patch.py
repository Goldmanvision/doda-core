import csv
import hashlib
import io
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
work = root / "tools" / "doda_content_workbench"
src = root / "data_authoring" / "source"
module = work / "doda_territory_rules.py"
tiers = src / "mission_tiers.csv"
decisions = root / "docs" / "workbench" / "spec" / "DESIGN_DECISIONS_2026-10-08.md"
history = root / "docs" / "workbench" / "history" / "Mission_Tier_Foundations_2026-10-08.md"
test_path = work / "tests" / "test_mission_tier_foundations.py"

def stop(message):
    raise SystemExit("STOP: " + message + " Nothing was modified.")

for path in (module, tiers, decisions):
    if not path.is_file():
        stop(str(path) + " was not found.")
for path in (history, test_path):
    if path.exists():
        stop(str(path) + " already exists.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")

sys.path.insert(0, str(work))
import doda_territory_rules as terr

with tiers.open(encoding="utf-8-sig", newline="") as fh:
    reader = csv.DictReader(fh)
    if reader.fieldnames != terr.TIER_COLUMNS:
        stop("mission_tiers.csv has an unexpected header.")
    if any(any((v or "").strip() for v in row.values()) for row in reader):
        stop("mission_tiers.csv is already populated.")

old_doc = decisions.read_bytes()
doc_text = old_doc.decode("utf-8-sig")
marker = "## Mission-tier progression - CONFIRMED (2026-10-08)"
if marker in doc_text:
    stop("Mission-tier progression is already recorded.")

buf = io.StringIO(newline="")
writer = csv.DictWriter(buf, fieldnames=terr.TIER_COLUMNS, lineterminator="\r\n")
writer.writeheader()
for number in range(1, 7):
    row = {key: "" for key in terr.TIER_COLUMNS}
    row.update(
        tier_id=f"TIER_{number}",
        display_name=f"Tier {number}",
        min_lifetime_evidence="0" if number == 1 else "",
        authored_content="true" if number == 6 else "false",
        source_reference="User decisions 2026-10-08 (mission tiers)",
        description=(
            "Authored end-game tier. Unlock requires completion of the "
            "protected Tier 5 capstone after department eligibility checks."
            if number == 6 else
            "Generated mission tier. Lifetime Evidence threshold is undecided."
        ),
        sort_order=str(number * 10),
        active="false",
    )
    if number == 1:
        row["description"] = (
            "First generated mission tier. Starts at zero lifetime Evidence. "
            "Tutorial pacing is a separate progression rule."
        )
    writer.writerow(row)

test_text = r'''import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net
import doda_territory_rules as terr

ROOT = net.find_project_root(Path(__file__).resolve().parent)


class MissionTierFoundationTests(unittest.TestCase):
    def rows(self):
        path = ROOT / "data_authoring" / "source" / terr.TIERS_FILE
        with path.open(encoding="utf-8-sig", newline="") as fh:
            return list(csv.DictReader(fh))

    def test_six_stable_tier_ids(self):
        rows = self.rows()
        ordered = sorted(rows, key=lambda row: int(row["sort_order"]))
        self.assertEqual(
            [row["tier_id"] for row in ordered],
            [f"TIER_{number}" for number in range(1, 7)],
        )

    def test_only_final_tier_is_authored(self):
        authored = [
            row["tier_id"] for row in self.rows()
            if row["authored_content"].strip().lower() == "true"
        ]
        self.assertEqual(authored, ["TIER_6"])

    def test_first_threshold_is_zero(self):
        rows = {row["tier_id"]: row for row in self.rows()}
        self.assertEqual(int(rows["TIER_1"]["min_lifetime_evidence"]), 0)

    def test_validated_payload_contains_all_tiers(self):
        result = net.Result()
        payload = terr.validate_territory(ROOT, result)
        self.assertEqual(result.errors, [])
        self.assertEqual(len(payload["missionTiers"]), 6)
        self.assertEqual(payload["missionTiers"][-1]["tierId"], "TIER_6")
        self.assertTrue(payload["missionTiers"][-1]["authoredContent"])


if __name__ == "__main__":
    unittest.main()
'''
compile(test_text, str(test_path), "exec")

addendum = """
## Mission-tier progression - CONFIRMED (2026-10-08)
- MTIER-01: Six mission tiers initially. Tiers 1-5 use generated mission content; Tier 6 is authored end-game content. Lower tiers remain available after higher tiers unlock.
- MTIER-02: Lifetime Evidence drives tier eligibility. Spendable Evidence pays for Leads. Spending does not reduce lifetime Evidence.
- MTIER-03: Ordinary Lead prices are not tier-specific. One department-wide counter drives linear growth: next cost = base cost + successful ordinary paid purchases * increment. Base cost and increment are undecided.
- MTIER-04: Successful ordinary paid purchases advance the pricing counter. Free tutorial missions, failed purchase attempts and redeployments do not. Changing territory or choosing a lower tier does not reset it.
- MTIER-05: Starting resources include a small Evidence balance, Department Funding, a couple of personnel, a phone, a FOIMS-X computer with 14.4k internet, and further starter items/currencies. Exact quantities and identities remain open.
- MTIER-06: Introduction: free tutorial mission area, followed by a purchased mission area, followed by a lull teaching passive Evidence gathering through agent investigations and FOIMS-X.
- MTIER-07: After Tier 5 unlocks, periodic checks evaluate final-tier eligibility. The interval is undecided.
- MTIER-08: Eligibility requires the final lifetime Evidence threshold, required major upgrades, sufficient CURRENT AVAILABLE Department Funding, required plot milestones/items, high PREPAREDNESS, and sufficient operational territories. Concrete references and thresholds remain open.
- MTIER-09: When all eligibility checks pass, offer a special expensive authored Tier 5 capstone Lead. Its price is separate from ordinary Lead pricing and remains undecided.
- MTIER-10: Completing the capstone's authored objectives permanently unlocks Tier 6. Eliminating hostiles alone is not its completion condition.
- MTIER-11: The capstone does not expire. Unsuccessful attempts allow redeployment without buying the Lead again; mission state is retained.

### Mission-tier implementation status
- This foundation slice seeds six inactive tier rows and four regression tests.
- Tier 1 starts at zero lifetime Evidence. Tier 2-6 thresholds remain blank.
- Purchasing, pricing-counter state, periodic eligibility evaluation, starter grants, tutorial sequencing and the capstone mission are NOT implemented.
- Open: exact major-upgrade and plot-item references; readiness/funding/territory thresholds; check interval; capstone price, map and objectives.
- Open: whether the special capstone purchase advances the ordinary Lead pricing counter.
- Open: eligibility rechecks after capstone purchase and before completion.
- Earlier TERR-OPEN-01 is narrowed: tier count is now six; thresholds and concrete gate requirements still need authoring.
"""

history_text = """# Mission Tier Foundations - 2026-10-08

## Scope
Authoring foundation only. No native runtime or purchasing behavior changed.

## Changes
- Seeded mission_tiers.csv with TIER_1 through TIER_6.
- Neutral names Tier 1 through Tier 6; all rows inactive.
- Tier 1 threshold is zero; other thresholds undecided.
- Only Tier 6 is authored end-game content.
- Added test_mission_tier_foundations.py with four tests.
- Appended MTIER-01 through MTIER-11 and implementation limitations to the decisions document.

## Approved design, not yet implemented
Department-wide purchase-count Lead pricing; starter grants and tutorial sequence;
periodic Tier 6 eligibility checks after Tier 5; protected, expensive Tier 5
capstone whose authored objectives permanently unlock Tier 6.

## Backups
Numbered mission_tier_foundations backup with repository-relative paths and
SHA-256 manifest. The territory module is included as a baseline snapshot.
"""

backups = work / "backups"
numbers = []
if backups.exists():
    for path in backups.iterdir():
        match = re.match(r"^v(\d+)_", path.name)
        if path.is_dir() and match:
            numbers.append(int(match.group(1)))
number = max(numbers, default=51) + 1
backup = backups / (
    f"v{number:03d}_mission_tier_foundations_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)
manifest = []
for path in (module, tiers, decisions):
    relative = path.relative_to(root)
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise SystemExit("STOP: backup verification failed; no source files changed.")
    manifest.append(f"{digest}  {relative.as_posix()}")

(backup / "MANIFEST.txt").write_text(
    "\n".join(manifest) + "\n", encoding="utf-8"
)

writes = {
    tiers: buf.getvalue().encode("utf-8"),
    test_path: test_text.encode("utf-8"),
    history: history_text.encode("utf-8"),
    decisions: old_doc + (
        ("" if doc_text.endswith("\n") else "\n") + addendum
    ).encode("utf-8"),
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

print("=== COPY FROM HERE ===")
print("Backup folder:", backup)
print("Seeded mission tiers: 6")
print("Added tests: 4")
print("Decisions and history saved.")
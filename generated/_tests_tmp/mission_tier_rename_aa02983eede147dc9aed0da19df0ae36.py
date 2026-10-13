import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
work = root / "tools/doda_content_workbench"
test = work / "tests/test_mission_tier_admissible_evidence.py"
history = root / "docs/workbench/history/MissionTier_Admissible_Evidence_2026-10-10.md"

TOKENS = (
    (b"min_lifetime_evidence", b"min_lifetime_admissible_evidence"),
    (b"minLifetimeEvidence", b"minLifetimeAdmissibleEvidence"),
    (b"Starts At Lifetime Evidence", b"Starts At Lifetime Admissible Evidence"),
)
SKIP = {"backups", "__pycache__", "_tests_tmp", "staging", "history",
        "generated", "build", ".git"}
EXT = {".py", ".csv", ".md", ".txt"}
SCAN_ROOTS = (root / "tools", root / "data_authoring" / "source",
              root / "docs" / "workbench" / "manual")

def stop(message):
    print("STOP: " + message + " No project files were modified.", flush=True)
    sys.exit(1)

if not work.is_dir():
    stop(str(work) + " was not found.")
for path in (test, history):
    if path.exists():
        stop(str(path) + " already exists. Verify before rerunning.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")

changes = {}
for base in SCAN_ROOTS:
    if not base.is_dir():
        continue
    for path in base.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXT:
            continue
        rel = path.relative_to(root)
        if SKIP.intersection(rel.parts):
            continue
        data = path.read_bytes()
        new = data
        for old, repl in TOKENS:
            new = new.replace(old, repl)
        if new != data:
            changes[path] = (data, new)

if not changes:
    stop("No occurrences of the old identifiers were found (already applied?).")

source_dir = root / "data_authoring" / "source"
csv_hits = [p for p in changes if p.parent == source_dir and p.suffix.lower() == ".csv"]
if len(csv_hits) != 1:
    stop("Expected exactly one source CSV with the old column; found %d." % len(csv_hits))

print("Files to change:", flush=True)
for path in sorted(changes):
    print("  " + str(path.relative_to(root)), flush=True)

test_text = r'''import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "tools" / "doda_content_workbench"
OLD = "min_lifetime" + "_evidence"
NEW = "min_lifetime_admissible_evidence"

class MissionTierAdmissibleEvidenceTests(unittest.TestCase):
    def test_source_csv_header_uses_new_column(self):
        headers = []
        for path in (ROOT / "data_authoring" / "source").glob("*.csv"):
            first = path.read_text(encoding="utf-8-sig").splitlines()[:1]
            if first and NEW in first[0].split(","):
                headers.append(path.name)
        self.assertEqual(len(headers), 1)

    def test_no_stale_identifier_in_code(self):
        stale = []
        for path in list(WORK.glob("*.py")) + list((WORK / "tests").glob("*.py")):
            if OLD in path.read_text(encoding="utf-8-sig"):
                stale.append(path.name)
        self.assertEqual(stale, [])

if __name__ == "__main__":
    unittest.main()
'''
history_text = """# Mission Tier Field Rename - 2026-10-10

Renamed mission_tiers.min_lifetime_evidence to min_lifetime_admissible_evidence
(and the exported minLifetimeEvidence key and editor label) so mission-tier
thresholds count lifetime Admissible Evidence, per the 2026-10-10 decision.
Replacement was a byte-level identifier rename across tools, source CSV and
manual. Generated output is refreshed by Export All. Added 2 regression tests.
The STARTING_EVIDENCE setting id is unchanged and is reviewed with the
resource ledger stage.
"""
compile(test_text, str(test), "exec")

def run_suite():
    done = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, errors="replace")
    match = re.search(r"Ran (\d+) tests", done.stdout)
    return done, (int(match.group(1)) if match else None)

def run_cli(script, *args):
    path = work / script
    if not path.is_file():
        return None
    done = subprocess.run(
        [sys.executable, str(path), *args], cwd=root, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, errors="replace")
    return done.returncode

baseline_run, baseline_count = run_suite()
if baseline_run.returncode or baseline_count is None:
    print(baseline_run.stdout[-3000:], flush=True)
    stop("The baseline test suite is not passing; fix that first.")
baseline_validate = run_cli("doda_content_workbench.py", "--root", str(root), "validate")
baseline_territory = run_cli("doda_territory_rules.py", "validate", "--root", str(root))
print("Baseline tests:", baseline_count, flush=True)
print("Baseline validator rc:", baseline_validate, "| territory rc:", baseline_territory, flush=True)

numbers = []
backups = work / "backups"
if backups.exists():
    for p in backups.iterdir():
        m = re.match(r"^v(\d+)_", p.name)
        if p.is_dir() and m:
            numbers.append(int(m.group(1)))
backup = backups / (f"v{max(numbers, default=78)+1:03d}_mission_tier_admissible_rename_"
                    + datetime.now().strftime("%Y%m%d_%H%M%S"))
manifest = []
for path, (original, _) in changes.items():
    rel = path.relative_to(root)
    target = backup / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(original)
    digest = hashlib.sha256(original).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed for " + str(rel))
    manifest.append(digest + "  " + rel.as_posix())
(backup / "MANIFEST.txt").write_text("\n".join(sorted(manifest)) + "\n", encoding="utf-8")
print("Backup folder:", backup, flush=True)

def rollback():
    for path, (original, _) in changes.items():
        path.write_bytes(original)
    for path in (test, history):
        path.unlink(missing_ok=True)

try:
    for path, (_, new) in changes.items():
        path.write_bytes(new)
    test.write_text(test_text, encoding="utf-8", newline="\n")
    history.write_text(history_text, encoding="utf-8", newline="\n")
    run, count = run_suite()
    print(run.stdout, flush=True)
    print("Tests after:", count, "(expected %d)" % (baseline_count + 2), flush=True)
    if run.returncode or count != baseline_count + 2:
        raise RuntimeError("Full test suite failed or count changed unexpectedly")
    after_validate = run_cli("doda_content_workbench.py", "--root", str(root), "validate")
    after_territory = run_cli("doda_territory_rules.py", "validate", "--root", str(root))
    print("After validator rc:", after_validate, "| territory rc:", after_territory, flush=True)
    if baseline_validate == 0 and after_validate != 0:
        raise RuntimeError("Project validation regressed")
    if baseline_territory == 0 and after_territory != 0:
        raise RuntimeError("Territory rules validation regressed")
except BaseException:
    rollback()
    print("PATCH ROLLED BACK: all renamed files restored; new test and history removed.", flush=True)
    raise

print("RESULT: PASS. Now run Actions > Export All Content, Rules, ZScript Catalog, PK3 in the Workbench.", flush=True)
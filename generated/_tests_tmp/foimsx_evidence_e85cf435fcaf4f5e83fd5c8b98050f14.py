import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(sys.argv[1])
work = root / "tools/doda_content_workbench"
preview = work / "doda_foims_x_preview.py"
model = work / "doda_foims_x_sandbox.py"
test = work / "tests/test_foims_x_evidence.py"
history = root / "docs/workbench/history/FOIMSX_Evidence_Transactions_2026-10-09.md"

def stop(message):
    print("STOP: " + message + " No project files were modified.", flush=True)
    sys.exit(1)

for path in (preview, model):
    if not path.is_file():
        stop(str(path) + " was not found.")
for path in (test, history):
    if path.exists():
        stop(str(path) + " already exists. Verify before rerunning.")
    if not path.parent.is_dir():
        stop(str(path.parent) + " was not found.")

def load(path):
    raw = path.read_bytes()
    original = raw.decode("utf-8-sig")
    return raw, "\r\n" in original, original.replace("\r\n", "\n")

def encode(body, raw, crlf):
    if crlf:
        body = body.replace("\n", "\r\n")
    return (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + body.encode("utf-8")

def replace_once(body, anchor, replacement, label):
    count = body.count(anchor)
    if count != 1:
        stop("%s: expected one anchor, found %d: %s" % (label, count, anchor[:100]))
    return body.replace(anchor, replacement)

model_raw, model_crlf, model_text = load(model)
preview_raw, preview_crlf, preview_text = load(preview)

if "def gather_evidence(" in model_text:
    stop("Evidence transactions appear to be installed already.")
if "def set_metric(" not in model_text:
    stop("The metric-controls patch must be installed first.")

model_methods = '''    @staticmethod
    def _positive_evidence(value):
        from decimal import Decimal, InvalidOperation
        if isinstance(value, bool):
            raise ValueError("Evidence amount must be a positive whole number")
        try:
            number = Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            raise ValueError("Evidence amount must be a positive whole number") from None
        if (not number.is_finite() or number <= 0
                or number != number.to_integral_value()):
            raise ValueError("Evidence amount must be a positive whole number")
        return int(number)

    def _record_evidence(self, action, amount, available_before, lifetime_before):
        state = self.snapshot()
        self.activity.append({
            "strategic_minutes": state["strategic_minutes"],
            "timestamp": state["date"] + " " + state["time"],
            "metric_id": "EVIDENCE_" + action,
            "action": action, "amount": amount,
            "before": available_before, "after": self.available_evidence,
            "lifetime_before": lifetime_before,
            "lifetime_after": self.lifetime_evidence,
        })
        self.activity = self.activity[-200:]

    def gather_evidence(self, amount):
        amount = self._positive_evidence(amount)
        available_before = self.available_evidence
        lifetime_before = self.lifetime_evidence
        self._settle()
        self.available_evidence += amount
        self.lifetime_evidence += amount
        self._record_evidence("GATHER", amount, available_before, lifetime_before)

    def spend_evidence(self, amount):
        amount = self._positive_evidence(amount)
        if amount > self.available_evidence:
            raise ValueError(
                f"Insufficient Evidence: available {self.available_evidence}, requested {amount}"
            )
        available_before = self.available_evidence
        lifetime_before = self.lifetime_evidence
        self._settle()
        self.available_evidence -= amount
        self._record_evidence("SPEND", amount, available_before, lifetime_before)

    def evidence_progress(self):
        tiers = []
        unconfigured = []
        for row in self._catalog.get("mission_tiers", []):
            tier_id = row.get("tier_id", "")
            raw = str(row.get("min_lifetime_evidence", "")).strip()
            try:
                threshold = int(raw)
            except (ValueError, TypeError):
                unconfigured.append(tier_id)
                continue
            if not tier_id or threshold < 0:
                unconfigured.append(tier_id)
                continue
            tiers.append({
                "tier_id": tier_id, "threshold": threshold,
                "draft": str(row.get("active", "false")).strip().lower() != "true",
                "evidence_met": self.lifetime_evidence >= threshold,
            })
        tiers.sort(key=lambda row: (row["threshold"], row["tier_id"]))
        reached = [row for row in tiers if row["evidence_met"]]
        pending = [row for row in tiers if not row["evidence_met"]]
        return {
            "thresholds": tiers,
            "highest_evidence_threshold_met": reached[-1] if reached else None,
            "next_evidence_threshold": pending[0] if pending else None,
            "remaining": (
                pending[0]["threshold"] - self.lifetime_evidence if pending else None
            ),
            "unconfigured_tiers": unconfigured,
            "other_requirements_evaluated": False,
            "unlocks_tiers": False,
        }

    def evidence_progress_text(self):
        state = self.evidence_progress()
        highest = state["highest_evidence_threshold_met"]
        next_tier = state["next_evidence_threshold"]
        pieces = []
        if highest:
            label = highest["tier_id"] + (" (draft)" if highest["draft"] else "")
            pieces.append("Evidence met through " + label)
        if next_tier:
            label = next_tier["tier_id"] + (" (draft)" if next_tier["draft"] else "")
            pieces.append(f'Next: {label}, {state["remaining"]:,} Evidence remaining')
        elif state["thresholds"]:
            pieces.append("All configured Evidence thresholds met")
        else:
            pieces.append("No configured Evidence thresholds")
        if state["unconfigured_tiers"]:
            pieces.append("Some thresholds are unconfigured")
        pieces.append("Other requirements unchecked; no tier unlocks")
        return " | ".join(pieces)

    @staticmethod
    def activity_columns(entry):
        if "action" in entry and "lifetime_before" in entry:
            label = f'Evidence {entry["action"].lower()} {entry["amount"]:,}'
            before = f'Avail {entry["before"]:,} / Life {entry["lifetime_before"]:,}'
            after = f'Avail {entry["after"]:,} / Life {entry["lifetime_after"]:,}'
            return entry["timestamp"], label, before, after
        return (
            entry["timestamp"], entry["metric_id"],
            f'{entry["before"]:g}', f'{entry["after"]:g}'
        )

    @staticmethod
    def activity_line(entry):
        if "action" in entry and "lifetime_before" in entry:
            return (
                f'{entry["timestamp"]} {entry["action"]} {entry["amount"]:,}: '
                f'AVAILABLE {entry["before"]:,}->{entry["after"]:,}; '
                f'LIFETIME {entry["lifetime_before"]:,}->{entry["lifetime_after"]:,}'
            )
        return (
            f'{entry["timestamp"]} {entry["metric_id"]}: '
            f'{entry["before"]:g} -> {entry["after"]:g}'
        )

    def metric_rows(self):
'''

model_text = replace_once(
    model_text, "    def metric_rows(self):\n",
    model_methods, "Evidence methods",
)

preview_methods = '''    def _gather_evidence(self):
        try:
            self.sandbox.gather_evidence(self.evidence_amount.get())
        except ValueError as error:
            messagebox.showerror("Sandbox Evidence", str(error), parent=self.window)
            return
        self.render()

    def _spend_evidence(self):
        try:
            self.sandbox.spend_evidence(self.evidence_amount.get())
        except ValueError as error:
            messagebox.showerror("Sandbox Evidence", str(error), parent=self.window)
            return
        self.render()

    def _populate_metric_controls(self):
'''

preview_text = replace_once(
    preview_text, "    def _populate_metric_controls(self):\n",
    preview_methods, "Evidence callbacks",
)

control_anchor = '''        self._populate_metric_controls()

        ttk.Label(
            controls,
            text="FOIMS-X Local Simulation Preview",'''

control_replacement = '''        self._populate_metric_controls()
        evidence_controls = ttk.Frame(self.controls)
        evidence_controls.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(evidence_controls, text="Sandbox Evidence:").pack(side=tk.LEFT)
        self.evidence_amount = tk.StringVar(value="100")
        ttk.Entry(
            evidence_controls, textvariable=self.evidence_amount, width=12
        ).pack(side=tk.LEFT, padx=6)
        ttk.Button(
            evidence_controls, text="Gather", command=self._gather_evidence
        ).pack(side=tk.LEFT)
        ttk.Button(
            evidence_controls, text="Spend", command=self._spend_evidence
        ).pack(side=tk.LEFT, padx=6)
        ttk.Label(
            evidence_controls, text="Manual test transactions; not mission rewards"
        ).pack(side=tk.LEFT, padx=8)
        self.evidence_progress_label = tk.StringVar()
        ttk.Label(
            self.controls, textvariable=self.evidence_progress_label
        ).pack(fill=tk.X, pady=(4, 0))

        ttk.Label(
            controls,
            text="FOIMS-X Local Simulation Preview",'''

preview_text = replace_once(
    preview_text, control_anchor, control_replacement,
    "Evidence control row",
)

preview_text = replace_once(
    preview_text,
    "        self._refresh_activity()\n        state = self._frame_snapshot",
    "        self._refresh_activity()\n"
    "        self.evidence_progress_label.set(self.sandbox.evidence_progress_text())\n"
    "        state = self._frame_snapshot",
    "Evidence progress display",
)

preview_text = replace_once(
    preview_text,
    '''            signature = tuple(
                (e["timestamp"], e["metric_id"], e["before"], e["after"])
                for e in entries
            )''',
    '''            signature = repr(entries)''',
    "activity signature",
)

preview_text = replace_once(
    preview_text,
    '''                    "", "end", values=(
                        entry["timestamp"], entry["metric_id"],
                        f'{entry["before"]:g}', f'{entry["after"]:g}'
                    )''',
    '''                    "", "end", values=self.sandbox.activity_columns(entry)''',
    "activity columns",
)

preview_text = replace_once(
    preview_text,
    '''            ("metric", "Metric", 260),
            ("before", "Before", 100),
            ("after", "After", 100),''',
    '''            ("metric", "Metric / Transaction", 220),
            ("before", "Before", 240),
            ("after", "After", 240),''',
    "activity headings",
)

preview_text = replace_once(
    preview_text,
    '''                f'{entry["timestamp"]} {entry["metric_id"]}: '
                f'{entry["before"]:g} -> {entry["after"]:g}',
                8, PALETTE["text"], max_width=550''',
    '''                self.sandbox.activity_line(entry),
                8, PALETTE["text"], max_width=550''',
    "CRT transaction display",
)

test_text = r'''import sys
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doda_foims_x_sandbox import FoimsXSandbox

class Clock:
    def __init__(self):
        self.now = 0.0
    def __call__(self):
        return self.now

class FoimsXEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.tables = {
            "metrics": [{
                "metric_id": "PREPAREDNESS", "default_value": "300",
                "internal_min": "0", "internal_max": "1000", "active": "true"
            }],
            "territory_settings": [{
                "setting_id": "STARTING_EVIDENCE", "value": "900", "active": "true"
            }],
            "mission_tiers": [
                {"tier_id": "TIER_1", "min_lifetime_evidence": "1000", "active": "false"},
                {"tier_id": "TIER_2", "min_lifetime_evidence": "10000", "active": "false"},
            ],
        }
        self.model = FoimsXSandbox(self.tables, self.clock)

    def test_gather_increases_both(self):
        self.model.gather_evidence("100")
        self.assertEqual(
            (self.model.available_evidence, self.model.lifetime_evidence),
            (1000, 1000)
        )

    def test_spend_changes_only_available(self):
        self.model.spend_evidence(100)
        self.assertEqual(
            (self.model.available_evidence, self.model.lifetime_evidence),
            (800, 900)
        )

    def test_spend_all_is_allowed(self):
        self.model.spend_evidence(900)
        self.assertEqual(self.model.available_evidence, 0)
        self.assertEqual(self.model.lifetime_evidence, 900)

    def test_overspending_is_atomic(self):
        before = self.model.snapshot()
        with self.assertRaises(ValueError):
            self.model.spend_evidence(901)
        self.assertEqual(self.model.snapshot(), before)

    def test_invalid_amounts_are_atomic(self):
        before = self.model.snapshot()
        for value in (0, -1, True, 1.5, "NaN", "Infinity", "", "bad"):
            for method in (self.model.gather_evidence, self.model.spend_evidence):
                with self.subTest(value=value, method=method.__name__):
                    with self.assertRaises(ValueError):
                        method(value)
                    self.assertEqual(self.model.snapshot(), before)

    def test_history_includes_both_balances(self):
        self.model.step(60)
        self.model.gather_evidence(100)
        self.model.spend_evidence(50)
        events = self.model.snapshot()["activity"]
        self.assertEqual(events[0]["timestamp"], "1992-02-01 01:00:00")
        self.assertEqual(
            (events[0]["before"], events[0]["after"],
             events[0]["lifetime_before"], events[0]["lifetime_after"]),
            (900, 1000, 900, 1000)
        )
        self.assertEqual(events[1]["action"], "SPEND")
        self.assertEqual(events[1]["lifetime_after"], 1000)
        columns = self.model.activity_columns(events[1])
        self.assertIn("Life 1,000", columns[3])

    def test_shared_history_preserves_metric_events(self):
        self.model.set_metric("PREPAREDNESS", 500)
        self.model.gather_evidence(100)
        events = self.model.activity
        self.assertEqual(events[0]["metric_id"], "PREPAREDNESS")
        self.assertEqual(events[1]["metric_id"], "EVIDENCE_GATHER")
        self.assertEqual(
            self.model.activity_columns(events[0])[1:],
            ("PREPAREDNESS", "300", "500")
        )

    def test_reset_restores_both_and_clears_history(self):
        self.model.gather_evidence(100)
        self.model.spend_evidence(500)
        self.model.reset()
        self.assertEqual(
            (self.model.available_evidence, self.model.lifetime_evidence),
            (900, 900)
        )
        self.assertEqual(self.model.activity, [])
        self.assertFalse(self.model.running)

    def test_threshold_progress_does_not_unlock(self):
        progress = self.model.evidence_progress()
        self.assertEqual(progress["remaining"], 100)
        self.assertIsNone(progress["highest_evidence_threshold_met"])
        self.model.gather_evidence(100)
        progress = self.model.evidence_progress()
        self.assertEqual(
            progress["highest_evidence_threshold_met"]["tier_id"], "TIER_1"
        )
        self.assertTrue(progress["highest_evidence_threshold_met"]["draft"])
        self.assertEqual(progress["remaining"], 9000)
        self.assertFalse(progress["other_requirements_evaluated"])
        self.assertFalse(progress["unlocks_tiers"])
        self.model.spend_evidence(1000)
        self.assertEqual(self.model.evidence_progress()["remaining"], 9000)

    def test_missing_thresholds_remain_explicit(self):
        tables = deepcopy(self.tables)
        tables["mission_tiers"] = [{
            "tier_id": "TIER_1", "min_lifetime_evidence": "", "active": "false"
        }]
        self.model.reset(tables)
        progress = self.model.evidence_progress()
        self.assertEqual(progress["unconfigured_tiers"], ["TIER_1"])
        self.assertIsNone(progress["next_evidence_threshold"])
        self.assertIn("unconfigured", self.model.evidence_progress_text())

    def test_catalog_and_snapshots_are_detached(self):
        before = deepcopy(self.tables)
        self.model.gather_evidence(100)
        self.model.snapshot()["activity"][0]["lifetime_after"] = 0
        self.assertEqual(self.tables, before)
        self.assertEqual(self.model.activity[0]["lifetime_after"], 1000)

    def test_running_transaction_records_elapsed_time(self):
        self.model.play()
        self.clock.now = 15
        self.model.gather_evidence(100)
        self.assertEqual(self.model.activity[-1]["strategic_minutes"], 15)
        self.assertTrue(self.model.running)

if __name__ == "__main__":
    unittest.main()
'''

for path, body in (
    (model, model_text), (preview, preview_text), (test, test_text)
):
    compile(body, str(path), "exec")

history_text = """# FOIMS-X Evidence Transactions - 2026-10-09

Added manual sandbox Gather and Spend controls. Gather increases available
and lifetime Evidence; Spend reduces only available Evidence and rejects
overspending. Both require positive whole amounts and share the existing
timestamped activity history, retaining the latest 200 events.

Evidence progress reads the session's mission-tier catalog, including draft
rows clearly labeled as drafts. It does not evaluate other requirements,
activate draft tiers, or unlock tiers. Missing thresholds remain explicit.
Reset restores initial balances and clears history.

No source CSV writes, native/game changes, automatic rewards or economy.
Added 12 headless Evidence tests.
"""

backups = work / "backups"
numbers = []
if backups.exists():
    for path in backups.iterdir():
        match = re.match(r"^v(\d+)_", path.name)
        if path.is_dir() and match:
            numbers.append(int(match.group(1)))

backup = backups / (
    f"v{max(numbers, default=73)+1:03d}_foimsx_evidence_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)
originals = {
    preview: preview_raw, model: model_raw, test: None, history: None
}
manifest = []
for path, raw in originals.items():
    if raw is None:
        continue
    relative = path.relative_to(root)
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        stop("Backup verification failed.")
    manifest.append(digest + "  " + relative.as_posix())

(backup / "MANIFEST.txt").write_text(
    "\n".join(manifest) + "\n", encoding="utf-8"
)

writes = {
    preview: encode(preview_text, preview_raw, preview_crlf),
    model: encode(model_text, model_raw, model_crlf),
    test: test_text.encode("utf-8"),
    history: history_text.encode("utf-8"),
}
source = root / "data_authoring/source"
source_before = {p: p.read_bytes() for p in source.glob("*.csv")}

def rollback():
    for path, raw in originals.items():
        if raw is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(raw)

print("Backup folder:", backup, flush=True)
print("Expected test total: 375", flush=True)

try:
    for path, raw in writes.items():
        path.write_bytes(raw)

    suite = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, errors="replace",
    )
    print(suite.stdout, flush=True)
    print("Process exit code:", suite.returncode, flush=True)

    if suite.returncode:
        raise RuntimeError("Full test suite failed")

    if set(source.glob("*.csv")) != set(source_before):
        raise RuntimeError("Source CSV inventory changed during tests")
    if any(p.read_bytes() != raw for p, raw in source_before.items()):
        raise RuntimeError("Source CSV contents changed during tests")
except BaseException:
    rollback()
    print(
        "PATCH ROLLED BACK: prior preview/model restored; "
        "new test and history removed.",
        flush=True,
    )
    raise

print("Source CSVs unchanged.", flush=True)
print("RESULT: PASS. Restart Workbench and test Evidence transactions.", flush=True)
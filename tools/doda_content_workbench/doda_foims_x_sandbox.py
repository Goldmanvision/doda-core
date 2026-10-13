"""In-memory FOIMS-X sandbox; no native calls, persistence, or catalog writes."""
from copy import deepcopy
from datetime import datetime, timedelta
import math
import time

EPOCH = datetime(1992, 2, 1)

class FoimsXSandbox:
    def __init__(self, tables, clock=time.monotonic):
        self._clock = clock
        self.reset(tables)

    def reset(self, tables=None):
        if tables is not None:
            self._catalog = deepcopy(tables)
        self.running = False
        self._minutes = 0.0
        self._last_real = self._clock()
        self.activity = []
        self.metrics = {}
        for row in self._catalog.get("metrics", []):
            if str(row.get("active", "true")).strip().lower() == "false":
                continue
            self.metrics[row["metric_id"]] = float(row["default_value"])
        start = 900
        for row in self._catalog.get("territory_settings", []):
            if row.get("setting_id") == "STARTING_EVIDENCE" and str(row.get("active", "false")).lower() == "true":
                start = int(row["value"])
        if start < 0:
            raise ValueError("starting Evidence cannot be negative")
        self.available_evidence = start
        self.lifetime_evidence = start
        self.department_funding = None

    @staticmethod
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
            raw = str(row.get("min_lifetime_admissible_evidence", "")).strip()
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
        return [deepcopy(row) for row in self._catalog.get("metrics", [])
                if row.get("metric_id") in self.metrics]

    def set_metric(self, metric_id, value):
        from decimal import Decimal, InvalidOperation
        if metric_id not in self.metrics:
            raise ValueError("Select a known active metric")
        if isinstance(value, bool):
            raise ValueError("Metric value must be a whole number")
        try:
            number = Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            raise ValueError("Metric value must be a whole number") from None
        if not number.is_finite() or number != number.to_integral_value():
            raise ValueError("Metric value must be a finite whole number")

        row = next(r for r in self.metric_rows() if r["metric_id"] == metric_id)
        try:
            minimum = Decimal(str(row["internal_min"]))
            maximum = Decimal(str(row["internal_max"]))
        except (InvalidOperation, KeyError):
            raise ValueError("Metric catalog has invalid bounds") from None
        if not minimum.is_finite() or not maximum.is_finite() or maximum < minimum:
            raise ValueError("Metric catalog has invalid bounds")
        if not minimum <= number <= maximum:
            raise ValueError(f"Value must be between {minimum} and {maximum}")

        before = self.metrics[metric_id]
        after = int(number)
        if before == after:
            return False

        self._settle()
        self.metrics[metric_id] = after
        state = self.snapshot()
        self.activity.append({
            "strategic_minutes": state["strategic_minutes"],
            "timestamp": state["date"] + " " + state["time"],
            "metric_id": metric_id, "before": before, "after": after,
        })
        self.activity = self.activity[-200:]
        return True

    def _settle(self):
        now = self._clock()
        if self.running:
            self._minutes += max(0.0, now - self._last_real)
        self._last_real = now

    def play(self):
        self._settle()
        self.running = True

    def pause(self):
        self._settle()
        self.running = False

    def tick(self):
        self._settle()

    def step(self, minutes):
        if self.running:
            raise ValueError("pause before stepping")
        if type(minutes) is not int or minutes <= 0:
            raise ValueError("step must be a positive whole number of minutes")
        self._minutes += minutes

    def snapshot(self):
        minutes = int(self._minutes)
        dt = EPOCH + timedelta(minutes=minutes)
        return {"running": self.running, "strategic_minutes": minutes,
                "date": dt.strftime("%Y-%m-%d"), "time": dt.strftime("%H:%M:%S"),
                "day": minutes // 1440 + 1, "cycle_percent": minutes % 1440 / 1440 * 100,
                "metrics": dict(self.metrics), "activity": deepcopy(self.activity), "available_evidence": self.available_evidence,
                "lifetime_evidence": self.lifetime_evidence,
                "department_funding": self.department_funding}

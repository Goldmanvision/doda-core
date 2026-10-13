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

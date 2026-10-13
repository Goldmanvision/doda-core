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
                "metrics": dict(self.metrics), "available_evidence": self.available_evidence,
                "lifetime_evidence": self.lifetime_evidence,
                "department_funding": self.department_funding}

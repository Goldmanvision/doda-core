#!/usr/bin/env python3
r"""
DoDA Content Workbench - Time settings (authoring slice).

Authored definitions only. Live strategic time is owned by the native
simulation; nothing here changes runtime behaviour.

Settled decisions encoded here (2026-10-07 and 2026-10-08):
  * TIME-01: Global time settings have their own catalog. Per-tick rates for
    activities live in the catalogs of those activities.
  * TIME-02: A Doom tic (engine unit, 35 per real second) differs from a DoDA
    sim tick (strategic-simulation unit).
  * PCARE-OPEN-07: One sim tick is one strategic minute.
  * TIME-03: Decimal authoring, at most four decimal places, scaled-integer export.
  * TIME-06: Outside FOIMS-X one real second is one strategic second. Inside
    FOIMS-X at 1x one sim tick passes per 35 Doom tics.
  * TIME-07: FOIMS-X has three speed multipliers (1x, 2x, 3x), subject to change.

Source file:
  data_authoring/source/time_settings.csv
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import doda_network_rules as net

TOOL_VERSION = "0.1.0"
SETTINGS_FILE = "time_settings.csv"
SETTING_COLUMNS = ["setting_id", "display_name", "category", "value", "unit", "editable",
                   "source_reference", "description", "sort_order", "active"]
CATEGORIES = ("ENGINE", "SIM_TICK", "PACING", "FOIMSX_SPEED")
UNITS = ("TICS_PER_SECOND", "MINUTES", "TICS", "RATIO", "MULTIPLIER")
SCALE = 10000
MAX_DECIMAL_PLACES = 4
ENGINE_TIC_ID = "DOOM_TICS_PER_SECOND"
SIM_TICK_ID = "SIM_TICK_STRATEGIC_MINUTES"
FOIMSX_TICS_ID = "DOOM_TICS_PER_SIM_TICK_FOIMSX_1X"
OUTSIDE_ID = "STRATEGIC_SECONDS_PER_REAL_SECOND_OUTSIDE"
REQUIRED_IDS = (ENGINE_TIC_ID, SIM_TICK_ID, FOIMSX_TICS_ID, OUTSIDE_ID)
EXPECTED_TICRATE = 35
EXPECTED_SPEED_COUNT = 3

PACING_RULES = {
    "outsideFoimsx": "REAL_TIME",
    "speedControlOnlyInsideFoimsx": True,
    "playerStatsTickWithStrategicTime": True,
    "agentActivitiesRealTimeOutsideFoimsx": True,
    "pause": "MAIN_MENU_ONLY_PLUS_DEBUG_CONSOLE_COMMAND",
    "debugPauseCommand": "pausefoimsx",
}

DECISIONS = {
    "TIME-06": "Outside FOIMS-X time is real time; inside FOIMS-X at 1x one sim tick passes per 35 Doom tics.",
    "TIME-07": "Three FOIMS-X speed multipliers (1x, 2x, 3x), subject to change; not available outside FOIMS-X.",
    "TIME-08": "Player stat bands tick while in FOIMS-X, faster at higher speeds.",
    "TIME-10": "After a FOIMS-X ejection the player cannot re-enter until the stat is replenished.",
    "TIME-15": "No in-FOIMS-X pause control; Main Menu pause plus a debug-only pausefoimsx console command.",
    "TIME-16": "Time returns to real time after any exit or ejection.",
    "TIME-18": "2x and 3x multiply the 1x FOIMS-X rate.",
    "TIME-19": "Agent activities run in real time outside FOIMS-X.",
}

OPEN_ITEMS = {
    "TIME-OPEN-01": "Whether the chosen FOIMS-X speed is remembered for the next entry.",
    "TIME-OPEN-02": "Whether the pausefoimsx debug command is excluded from release builds.",
    "TIME-OPEN-03": "Native fractional-tick accumulator for sub-minute time outside FOIMS-X, and its save-schema impact (deferred native task).",
    "TIME-OPEN-04": "Reconcile the earlier metrics sampling policy (every 10 ticks, 50 samples) with the sim tick.",
    "TIME-OPEN-05": "Which condition bands eject the player from FOIMS-X, and per-band message variants (proposed TIME-13).",
}


def _decimal(value: str, ctx: str, field: str, res: net.Result) -> Decimal | None:
    if not value:
        res.errors.append(f"{ctx}: {field} is required")
        return None
    try:
        d = Decimal(value)
    except InvalidOperation:
        res.errors.append(f"{ctx}: {field} must be a number")
        return None
    if not d.is_finite():
        res.errors.append(f"{ctx}: {field} must be a finite number")
        return None
    if d <= 0:
        res.errors.append(f"{ctx}: {field} must be above 0")
        return None
    exponent = d.normalize().as_tuple().exponent
    if isinstance(exponent, int) and exponent < -MAX_DECIMAL_PLACES:
        res.errors.append(f"{ctx}: {field} may have at most {MAX_DECIMAL_PLACES} decimal places")
        return None
    return d


def _plain(d: Decimal) -> str:
    return format(d.normalize(), "f")


def _scaled(d: Decimal) -> int:
    return int((d * SCALE).to_integral_value())


def _derived(settings: dict[str, dict[str, Any]], speeds: list[dict[str, Any]]) -> dict[str, Any]:
    need = [settings.get(i) for i in REQUIRED_IDS]
    if any(s is None or s["_d"] is None for s in need):
        return {}
    tps, sim, tics1x, outside = (s["_d"] for s in need)
    q = Decimal("0.0001")

    def pair(d: Decimal) -> tuple[str, int]:
        d = d.quantize(q)
        return _plain(d), _scaled(d)

    speed_rows = []
    for s in speeds:
        m = s["_d"]
        if m is None:
            continue
        tics, tics_s = pair(tics1x / m)
        sps, sps_s = pair(Decimal(60) * sim * m * tps / tics1x)
        speed_rows.append({"settingId": s["settingId"], "multiplier": _plain(m),
                           "doomTicsPerSimTick": tics, "doomTicsPerSimTickScaled": tics_s,
                           "strategicSecondsPerRealSecond": sps,
                           "strategicSecondsPerRealSecondScaled": sps_s})
    out_tics, out_tics_s = pair(tps * 60 * sim / outside)
    out_real, out_real_s = pair(Decimal(60) * sim / outside)
    return {"foimsxSpeeds": speed_rows,
            "outsideFoimsx": {"strategicSecondsPerRealSecond": _plain(outside),
                              "doomTicsPerSimTick": out_tics, "doomTicsPerSimTickScaled": out_tics_s,
                              "realSecondsPerSimTick": out_real, "realSecondsPerSimTickScaled": out_real_s}}


def validate_time_settings(root: Path, res: net.Result) -> dict[str, Any]:
    src = root / "data_authoring" / "source"
    rows = net.read_table(src / SETTINGS_FILE, SETTING_COLUMNS, "time_settings", res) or []
    settings: dict[str, dict[str, Any]] = {}
    for r in rows:
        ctx = f"[time_settings] Line {r['_line']}"
        sid = r["setting_id"]
        if not sid or sid in settings:
            res.errors.append(f"{ctx}: blank or duplicate setting_id '{sid}'")
            continue
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        category = r["category"].upper()
        if category not in CATEGORIES:
            res.errors.append(f"{ctx}: category must be one of {', '.join(CATEGORIES)}")
        unit = r["unit"].upper()
        if unit not in UNITS:
            res.errors.append(f"{ctx}: unit must be one of {', '.join(UNITS)}")
        value = _decimal(r["value"], ctx, "value", res)
        editable = net._bool(r["editable"], ctx, res)
        if category == "ENGINE" and editable:
            res.errors.append(f"{ctx}: engine constants cannot be editable")
        settings[sid] = {"settingId": sid, "displayName": r["display_name"], "category": category,
                         "unit": unit, "editable": editable,
                         "sourceReference": r["source_reference"] or None,
                         "description": r["description"],
                         "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                         "active": net._bool(r["active"], ctx, res), "_d": value, "_ctx": ctx}
    for sid in REQUIRED_IDS:
        if sid not in settings:
            res.errors.append(f"[time_settings] Required setting '{sid}' is missing")
    sim = settings.get(SIM_TICK_ID)
    if sim and sim["_d"] is not None and sim["_d"] != sim["_d"].to_integral_value():
        res.errors.append(f"{sim['_ctx']}: {SIM_TICK_ID} must be a whole number of minutes")
    eng = settings.get(ENGINE_TIC_ID)
    if eng and eng["_d"] is not None and eng["_d"] != EXPECTED_TICRATE:
        res.warnings.append(f"{eng['_ctx']}: {ENGINE_TIC_ID} is not {EXPECTED_TICRATE} (the engine TICRATE)")
    speeds = sorted((s for s in settings.values() if s["category"] == "FOIMSX_SPEED"),
                    key=lambda s: (s["sortOrder"] or 0, s["settingId"]))
    if len(speeds) != EXPECTED_SPEED_COUNT:
        res.warnings.append(f"[time_settings] Expected {EXPECTED_SPEED_COUNT} FOIMS-X speed settings, found {len(speeds)}")
    for a, b in zip(speeds, speeds[1:]):
        if a["_d"] is not None and b["_d"] is not None and not a["_d"] < b["_d"]:
            res.errors.append(f"{b['_ctx']}: speed multipliers must ascend ({b['settingId']} is not above {a['settingId']})")
    derived = _derived(settings, speeds)
    out_settings = []
    for s in sorted(settings.values(), key=lambda x: (x["sortOrder"] or 0, x["settingId"])):
        item = {k: v for k, v in s.items() if k not in ("_d", "_ctx")}
        d = s["_d"]
        item["value"] = _plain(d) if d is not None else None
        item["valueScaled"] = _scaled(d) if d is not None else None
        out_settings.append(item)
    return {"settings": out_settings, "derived": derived}


def export(root: Path) -> tuple[net.Result, Path | None]:
    res = net.Result()
    data = validate_time_settings(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "time_settings_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "doda.time_settings", "toolVersion": TOOL_VERSION,
               "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
               "decimalPlaces": MAX_DECIMAL_PLACES, "scale": SCALE, **data,
               "pacingRules": PACING_RULES, "decisions": DECISIONS,
               "openItems": OPEN_ITEMS, "runtimeImplemented": False}
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="DoDA time settings: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else net.find_project_root(Path(__file__).parent)
    if a.command == "validate":
        res = net.Result()
        validate_time_settings(root, res)
        out = None
    else:
        res, out = export(root)
    for w in res.warnings:
        print("WARNING:", w)
    for e in res.errors:
        print("ERROR:", e)
    print("Rows:", res.stats)
    if out:
        print("Exported:", out, "sha256", hashlib.sha256(out.read_bytes()).hexdigest())
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1


if __name__ == "__main__":
    sys.exit(main())
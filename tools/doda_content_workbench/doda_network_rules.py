#!/usr/bin/env python3
r"""
DoDA Content Workbench - Network and transfer rules (authoring slice).

Scope: authoring, validation, and export only. No game-runtime behaviour.

Settled decisions encoded here (2026-10-07):
  NET-01  Routers must match the modem's generation and type exactly.
  NET-02  Game auto-selects a compatible modem; player may override.
  NET-03  Receiving end requires an agent/analyst sign-off to complete.
  INT-01  Delivered-but-unsigned transfers wait indefinitely (never expire).
  INT-02  Interrupted sign-off pauses and can resume.
  INT-03  Modem/router failure or disconnect during an ACTIVE transfer loses it,
          unless it was manually paused beforehand.
  INT-04  Only agents and analysts may sign off.
  INT-05  Only the person who started a sign-off may resume it; anyone else
          restarts it from the beginning.
  INT-06  Pausing is a staff task, or a manual per-device player action.
          There is no global "pause all transfers".
  INT-07  Paused transfers resume where they stopped.
  INT-08  Any staff member may perform the pause task.
  INT-09  Pausing staff must be at the device; technicians may pause remotely.
  INT-10  If the sign-off starter is permanently unavailable, the sign-off waits
          until an eligible person restarts it.

Source files (optional; absent files are reported, not fatal to other tables):
  data_authoring/source/network_tiers.csv
  data_authoring/source/network_hardware_models.csv

Balancing values (durations, rates, prices) are intentionally not defined here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL_VERSION = "0.1.0"
CONTRACT_VERSION = "2026-10-07.1"

TIERS_FILE = "network_tiers.csv"
HARDWARE_FILE = "network_hardware_models.csv"

TIER_COLUMNS = ["tier_id", "display_name", "network_type", "generation",
                "description", "sort_order", "active"]
HARDWARE_COLUMNS = ["model_id", "display_name", "hardware_kind", "tier_id",
                    "description", "sort_order", "active"]
HARDWARE_KINDS = {"MODEM", "ROUTER"}

STAFF_ROLES = ["AGENT", "ANALYST", "TECHNICIAN"]

# --------------------------------------------------------------------------
# Code-defined contracts (settled rules, not authored balancing data)
# --------------------------------------------------------------------------

TRANSFER_STATES = {
    "QUEUED": "Created; waiting for a compatible link and an attending person.",
    "ACTIVE": "Data is moving. Vulnerable to link failure (INT-03).",
    "PAUSED_MANUAL": "Paused by a staff task or per-device player action. "
                     "Protected from link loss; resumes where stopped (INT-07).",
    "AWAITING_SIGNOFF": "Delivered. Waits indefinitely for sign-off (INT-01).",
    "SIGNOFF_IN_PROGRESS": "An agent/analyst is verifying (occupies their task slot).",
    "SIGNOFF_PAUSED": "Sign-off interrupted; progress kept for its starter only (INT-02, INT-05).",
    "COMPLETED": "Signed off. Evidence counts as processed.",
    "LOST": "Link failed while ACTIVE. Unresolved value recorded as lost evidence.",
}
TERMINAL_STATES = {"COMPLETED", "LOST"}

TRANSFER_TRANSITIONS = [
    # (from, to, trigger, notes)
    ("QUEUED", "ACTIVE", "start", "Requires exact device-router-modem tier match (NET-01)."),
    ("ACTIVE", "PAUSED_MANUAL", "manual_pause", "Staff pause task or per-device player action (INT-06)."),
    ("PAUSED_MANUAL", "ACTIVE", "resume", "Resumes from stored progress (INT-07)."),
    ("ACTIVE", "LOST", "link_failure", "Modem/router failure or disconnect (INT-03)."),
    ("PAUSED_MANUAL", "PAUSED_MANUAL", "link_failure", "Paused transfers survive link loss (INT-03)."),
    ("ACTIVE", "AWAITING_SIGNOFF", "delivered", "Not yet complete (NET-03)."),
    ("AWAITING_SIGNOFF", "SIGNOFF_IN_PROGRESS", "begin_signoff", "Agent/analyst only (INT-04)."),
    ("SIGNOFF_IN_PROGRESS", "SIGNOFF_PAUSED", "interrupt", "Progress kept, bound to starter (INT-02, INT-05)."),
    ("SIGNOFF_PAUSED", "SIGNOFF_IN_PROGRESS", "resume_by_starter", "Keeps progress (INT-05)."),
    ("SIGNOFF_PAUSED", "SIGNOFF_IN_PROGRESS", "restart_by_other", "Progress reset to zero (INT-05, INT-10)."),
    ("SIGNOFF_IN_PROGRESS", "COMPLETED", "signoff_complete", "Evidence counted as processed."),
]

ROLE_PERMISSIONS = {
    "signoff": {"allowed_roles": ["AGENT", "ANALYST"], "requires_presence": True},
    "pause_transfer_task": {
        "allowed_roles": STAFF_ROLES,
        "requires_presence": True,
        "remote_allowed_roles": ["TECHNICIAN"],
    },
}

RULE_FLAGS = {
    "router_modem_exact_match": True,          # NET-01
    "device_modem_exact_match": True,          # carried forward (settled)
    "shared_bandwidth_contention": False,      # carried forward (settled)
    "modem_selection": "AUTO_WITH_PLAYER_OVERRIDE",  # NET-02
    "completion_requires_signoff": True,       # NET-03
    "awaiting_signoff_expires": False,         # INT-01
    "global_pause_all": False,                 # INT-06
    "player_manual_pause_scope": "PER_DEVICE",  # INT-06
    "pause_task_occupies_task_slot": True,     # INT-06 + one active task per person
    "signoff_occupies_task_slot": True,
    "paused_transfer_resume": "FROM_STORED_PROGRESS",  # INT-07
    "signoff_resume_by_other": "RESTART",      # INT-05
    "signoff_starter_permanently_unavailable": "WAIT_FOR_RESTART",  # INT-10
}

# Processing-task and system-update interruption (2026-10-07)
TASK_INTERRUPTION = {
    "processing": {
        "shift_end": "PAUSE_RESUME_NEXT_SHIFT_UNLESS_PLAYER_REASSIGNS",  # TASK-01a
        "incapacity": "FAIL_DESTROY_UNRESOLVED",   # TASK-01b; processed portion retained
        "player_cancel": "WAIT_PARTLY_PROCESSED",   # TASK-01c
        "takeover_by_qualified": "KEEP_PROGRESS",    # TASK-02
        "equipment_unavailable": "REDUCED_OR_PAUSE_NO_DESTRUCTION",  # settled earlier
    },
    "system_update": {
        "any_interruption": "RESTART",  # UPD-01
        "overdue_risk_through_restart": "KEEPS_BUILDING_UNTIL_COMPLETE",  # UPD-02
    },
}

# INT-11: causes of permanent unavailability (contracts themselves are permanent)
PERMANENT_UNAVAILABILITY_CAUSES = ["DEATH", "DISMISSAL", "DEFECTION", "RETIREMENT"]

# NET-03b: one technician may attend both ends only if able to move between both locations
RULE_FLAGS["technician_both_ends"] = "ONLY_IF_CAN_TRAVEL_BETWEEN_LOCATIONS"

OPEN_ITEMS = {
    "NET-04": "Individual device bandwidth upgrades.",
    "NET-05": "Department-wide transfer efficiency formula.",
    "NET-06": "Partly settled: diagram speed labels kept verbatim; file sizes deliberately exaggerated. "
               "Numeric units/conversion for timing still open.",
}

# --------------------------------------------------------------------------


class Result:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, int] = {}

    @property
    def valid(self) -> bool:
        return not self.errors


def find_project_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "data_authoring").is_dir() and (candidate / "tools").is_dir():
            return candidate
    raise FileNotFoundError("Could not find project root (data_authoring + tools). Use --root.")


def read_table(path: Path, columns: list[str], name: str, res: Result) -> list[dict[str, str]] | None:
    if not path.is_file():
        res.warnings.append(f"[{name}] Source file not present: {path.name} (table skipped)")
        return None
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        header = [c.strip() for c in (reader.fieldnames or [])]
        missing = [c for c in columns if c not in header]
        if missing:
            res.errors.append(f"[{name}] Missing columns: {', '.join(missing)}")
            return []
        rows = []
        for line, raw in enumerate(reader, start=2):
            row = {k.strip(): (v or "").strip() for k, v in raw.items() if k is not None}
            if not any(row.values()):
                continue
            row["_line"] = str(line)
            rows.append(row)
    res.stats[name] = len(rows)
    return rows


def _bool(value: str, ctx: str, res: Result) -> bool:
    v = value.strip().lower()
    if v in ("true", "1", "yes"):
        return True
    if v in ("false", "0", "no"):
        return False
    res.errors.append(f"{ctx}: active must be true/false, got '{value}'")
    return False


def _int(value: str, ctx: str, field: str, res: Result) -> int | None:
    try:
        return int(value)
    except ValueError:
        res.errors.append(f"{ctx}: {field} must be an integer, got '{value}'")
        return None


def validate_contract(res: Result) -> None:
    """Self-check the code-defined state machine so edits cannot silently break it."""
    for frm, to, trig, _ in TRANSFER_TRANSITIONS:
        for s in (frm, to):
            if s not in TRANSFER_STATES:
                res.errors.append(f"[contract] Unknown state '{s}' in transition '{trig}'")
        if frm in TERMINAL_STATES:
            res.errors.append(f"[contract] Terminal state '{frm}' has outgoing transition '{trig}'")
    froms = {t[0] for t in TRANSFER_TRANSITIONS}
    for s in TRANSFER_STATES:
        if s not in TERMINAL_STATES and s not in froms:
            res.errors.append(f"[contract] Non-terminal state '{s}' has no outgoing transition")
    if any(t[0] == "AWAITING_SIGNOFF" and t[1] == "LOST" for t in TRANSFER_TRANSITIONS):
        res.errors.append("[contract] AWAITING_SIGNOFF must never expire to LOST (INT-01)")
    if not any(t[0] == "ACTIVE" and t[2] == "link_failure" and t[1] == "LOST" for t in TRANSFER_TRANSITIONS):
        res.errors.append("[contract] ACTIVE link_failure must lead to LOST (INT-03)")
    if set(ROLE_PERMISSIONS["signoff"]["allowed_roles"]) != {"AGENT", "ANALYST"}:
        res.errors.append("[contract] Sign-off roles must be exactly AGENT and ANALYST (INT-04)")


def validate_network(root: Path, res: Result) -> dict[str, Any]:
    src = root / "data_authoring" / "source"
    tiers = read_table(src / TIERS_FILE, TIER_COLUMNS, "network_tiers", res)
    hw = read_table(src / HARDWARE_FILE, HARDWARE_COLUMNS, "network_hardware_models", res)
    tier_index: dict[str, dict[str, Any]] = {}
    hardware: list[dict[str, Any]] = []

    if tiers is not None:
        seen_pairs: dict[tuple[str, str], str] = {}
        for r in tiers:
            ctx = f"[network_tiers] Line {r['_line']}"
            tid = r["tier_id"]
            if not tid:
                res.errors.append(f"{ctx}: blank tier_id")
                continue
            if tid in tier_index:
                res.errors.append(f"{ctx}: duplicate tier_id '{tid}'")
                continue
            if not r["network_type"] or not r["generation"]:
                res.errors.append(f"{ctx}: network_type and generation are required")
            pair = (r["network_type"].upper(), r["generation"].upper())
            if pair in seen_pairs:
                res.errors.append(f"{ctx}: type/generation {pair} already used by '{seen_pairs[pair]}'")
            seen_pairs[pair] = tid
            tier_index[tid] = {
                "tierId": tid, "displayName": r["display_name"],
                "networkType": r["network_type"], "generation": r["generation"],
                "description": r["description"],
                "sortOrder": _int(r["sort_order"], ctx, "sort_order", res),
                "active": _bool(r["active"], ctx, res),
            }

    if hw is not None:
        seen: set[str] = set()
        for r in hw:
            ctx = f"[network_hardware_models] Line {r['_line']}"
            mid = r["model_id"]
            if not mid or mid in seen:
                res.errors.append(f"{ctx}: blank or duplicate model_id '{mid}'")
                continue
            seen.add(mid)
            kind = r["hardware_kind"].upper()
            if kind not in HARDWARE_KINDS:
                res.errors.append(f"{ctx}: hardware_kind must be MODEM or ROUTER, got '{r['hardware_kind']}'")
            tid = r["tier_id"]
            active = _bool(r["active"], ctx, res)
            if tiers is None:
                res.errors.append(f"{ctx}: references tier '{tid}' but {TIERS_FILE} is missing")
            elif tid not in tier_index:
                res.errors.append(f"{ctx}: unknown tier_id '{tid}'")
            elif active and not tier_index[tid]["active"]:
                res.errors.append(f"{ctx}: active model uses inactive tier '{tid}'")
            hardware.append({
                "modelId": mid, "displayName": r["display_name"], "hardwareKind": kind,
                "tierId": tid, "description": r["description"],
                "sortOrder": _int(r["sort_order"], ctx, "sort_order", res), "active": active,
            })
        # NET-01: every active router tier needs an active modem of the same tier
        modem_tiers = {h["tierId"] for h in hardware if h["hardwareKind"] == "MODEM" and h["active"]}
        for h in hardware:
            if h["hardwareKind"] == "ROUTER" and h["active"] and h["tierId"] not in modem_tiers:
                res.warnings.append(
                    f"[network_hardware_models] Router '{h['modelId']}' has no active modem of tier "
                    f"'{h['tierId']}' and can never connect (NET-01 exact match)")

    return {"tiers": sorted(tier_index.values(), key=lambda t: (t["sortOrder"] or 0, t["tierId"])),
            "hardwareModels": sorted(hardware, key=lambda h: (h["sortOrder"] or 0, h["modelId"]))}


def router_compatible(router_tier: str, modem_tier: str) -> bool:
    """NET-01: exact match of the tier (type + generation). No up/down compatibility."""
    return bool(router_tier) and router_tier == modem_tier


def build_contract() -> dict[str, Any]:
    return {
        "contractVersion": CONTRACT_VERSION,
        "ruleFlags": RULE_FLAGS,
        "transferStates": [{"state": k, "description": v, "terminal": k in TERMINAL_STATES}
                           for k, v in TRANSFER_STATES.items()],
        "transferTransitions": [{"from": f, "to": t, "trigger": g, "notes": n}
                                for f, t, g, n in TRANSFER_TRANSITIONS],
        "rolePermissions": ROLE_PERMISSIONS,
        "evidenceAccounting": {
            "processedOn": "COMPLETED",
            "lostOn": "LOST",
            "pendingExcludedFromRatios": ["QUEUED", "ACTIVE", "PAUSED_MANUAL", "AWAITING_SIGNOFF",
                                          "SIGNOFF_IN_PROGRESS", "SIGNOFF_PAUSED"],
        },
        "taskInterruption": TASK_INTERRUPTION,
        "permanentUnavailabilityCauses": PERMANENT_UNAVAILABILITY_CAUSES,
        "openItems": OPEN_ITEMS,
        "runtimeImplemented": False,
    }


def export(root: Path) -> tuple[Result, Path | None]:
    res = Result()
    validate_contract(res)
    data = validate_network(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "network_transfer_rules.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "doda.network_transfer_rules", "toolVersion": TOOL_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        **data, "contract": build_contract(),
    }
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="DoDA network/transfer rules: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else find_project_root(Path(__file__).parent)
    if a.command == "validate":
        res = Result()
        validate_contract(res)
        validate_network(root, res)
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

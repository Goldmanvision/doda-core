#!/usr/bin/env python3
r"""
DoDA Content Workbench - Equipment families and models (authoring slice).

Authoring, validation, and export only. No runtime behaviour, stats, prices,
or unlock thresholds (deferred balancing).

Settled decisions encoded here (2026-10-07):
  * Per-task maximum: 2 desktops, 2 laptops, 2 phones, 2 PDAs = 8 devices.
  * Desktop/laptop share HDD storage; PDA uses SC storage; phones use none.
  * Two active phones may be any landline/mobile combination.
  * EQ-FAM-01: Fax machines are Department/location equipment with no personal
    owner and do not count toward the personal device limit.
  * EQ-FAM-02: Landline order oldest->newest: rotary, touch-tone, cordless
    system, multi-line system. Mobile phones (calls + touch-tone hotlines) are
    phones. Cellular devices are mobile-internet PDA devices, not phones.
  * EQ-NET-01: Phones and fax machines use phone lines and are not network
    connected (no network tier). Desktop/laptop/PDA models need a network tier
    with exact modem matching.

Source files:
  data_authoring/source/equipment_families.csv
  data_authoring/source/equipment_models.csv
  (equipment_models.network_tier_id references network_tiers.csv)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import doda_network_rules as net

TOOL_VERSION = "0.1.0"

FAMILIES_FILE = "equipment_families.csv"
MODELS_FILE = "equipment_models.csv"

FAMILY_COLUMNS = ["family_id", "display_name", "ownership", "per_task_limit", "storage_kind",
                  "connection_kind", "description", "sort_order", "active"]
MODEL_COLUMNS = ["model_id", "display_name", "family_id", "phone_line_kind", "network_tier_id",
                 "generation_order", "description", "sort_order", "active"]

OWNERSHIP = ("PERSONAL", "LOCATION")
STORAGE_KINDS = ("HDD", "SC", "NONE")
CONNECTION_KINDS = ("NETWORK", "PHONE_LINE")
PHONE_LINE_KINDS = ("LANDLINE", "MOBILE")
TOTAL_PERSONAL_DEVICE_LIMIT = 8

OPEN_ITEMS = {
    "EQ-CELL-01": "Do cellular PDA devices connect through location modems (exact tier match) or a separate mobile-internet path?",
    "EQ-SYS-01": "Are cordless and multi-line phone systems personal phones or location equipment?",
    "EQ-SCOPE-01": "Model stats, abilities, prices, and unlock thresholds (deferred balancing).",
    "EQ-01": "Cross-family replacement during reassignment.",
}


def validate_equipment(root: Path, res: net.Result) -> dict[str, Any]:
    src = root / "data_authoring" / "source"
    fams = net.read_table(src / FAMILIES_FILE, FAMILY_COLUMNS, "equipment_families", res)
    models = net.read_table(src / MODELS_FILE, MODEL_COLUMNS, "equipment_models", res)
    tiers = net.read_table(src / net.TIERS_FILE, net.TIER_COLUMNS, "network_tiers", net.Result()) or []
    tier_active = {t["tier_id"]: t["active"].lower() == "true" for t in tiers}

    fam_index: dict[str, dict[str, Any]] = {}
    out_models: list[dict[str, Any]] = []

    if fams is not None:
        personal_total = 0
        for r in fams:
            ctx = f"[equipment_families] Line {r['_line']}"
            fid = r["family_id"]
            if not fid or fid in fam_index:
                res.errors.append(f"{ctx}: blank or duplicate family_id '{fid}'")
                continue
            own, sto, con = r["ownership"].upper(), r["storage_kind"].upper(), r["connection_kind"].upper()
            if own not in OWNERSHIP:
                res.errors.append(f"{ctx}: ownership must be PERSONAL or LOCATION")
            if sto not in STORAGE_KINDS:
                res.errors.append(f"{ctx}: storage_kind must be HDD, SC, or NONE")
            if con not in CONNECTION_KINDS:
                res.errors.append(f"{ctx}: connection_kind must be NETWORK or PHONE_LINE")
            if con == "PHONE_LINE" and sto != "NONE":
                res.errors.append(f"{ctx}: phone-line equipment has no HDD/SC storage")
            limit_text = r["per_task_limit"]
            limit = None
            if own == "PERSONAL":
                limit = net._int(limit_text, ctx, "per_task_limit", res)
                if limit is not None and limit < 1:
                    res.errors.append(f"{ctx}: personal families need per_task_limit >= 1")
            elif limit_text:
                res.errors.append(f"{ctx}: LOCATION equipment has no personal per_task_limit (leave blank)")
            active = net._bool(r["active"], ctx, res)
            if active and own == "PERSONAL" and limit:
                personal_total += limit
            fam_index[fid] = {"familyId": fid, "displayName": r["display_name"], "ownership": own,
                              "perTaskLimit": limit, "storageKind": sto, "connectionKind": con,
                              "description": r["description"],
                              "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active}
        if fam_index and personal_total != TOTAL_PERSONAL_DEVICE_LIMIT:
            res.errors.append(f"[equipment_families] Active personal per_task_limit total is {personal_total}; "
                              f"settled rule is {TOTAL_PERSONAL_DEVICE_LIMIT} (two of each of four families)")

    if models is not None:
        seen: set[str] = set()
        gen_seen: dict[tuple[str, str, str], str] = {}
        for r in models:
            ctx = f"[equipment_models] Line {r['_line']}"
            mid = r["model_id"]
            if not mid or mid in seen:
                res.errors.append(f"{ctx}: blank or duplicate model_id '{mid}'")
                continue
            seen.add(mid)
            active = net._bool(r["active"], ctx, res)
            fam = fam_index.get(r["family_id"])
            line_kind = r["phone_line_kind"].upper()
            tier = r["network_tier_id"]
            gen = net._int(r["generation_order"], ctx, "generation_order", res)
            if fam is None:
                res.errors.append(f"{ctx}: unknown family_id '{r['family_id']}'")
            else:
                if active and not fam["active"]:
                    res.errors.append(f"{ctx}: active model in inactive family '{fam['familyId']}'")
                if fam["connectionKind"] == "NETWORK":
                    if not tier:
                        res.errors.append(f"{ctx}: network equipment needs network_tier_id (exact modem match)")
                    elif tier not in tier_active:
                        res.errors.append(f"{ctx}: unknown network_tier_id '{tier}'")
                    elif active and not tier_active[tier]:
                        res.errors.append(f"{ctx}: active model uses inactive network tier '{tier}'")
                    if line_kind:
                        res.errors.append(f"{ctx}: phone_line_kind applies only to phone-line equipment")
                else:
                    if tier:
                        res.errors.append(f"{ctx}: phone-line equipment is not network connected; clear network_tier_id")
                    if fam["ownership"] == "PERSONAL" and line_kind not in PHONE_LINE_KINDS:
                        res.errors.append(f"{ctx}: personal phones need phone_line_kind LANDLINE or MOBILE")
                key = (fam["familyId"], line_kind, str(gen))
                if gen is not None and key in gen_seen:
                    res.warnings.append(f"{ctx}: generation_order {gen} repeats '{gen_seen[key]}' in the same family/line")
                gen_seen[key] = mid
            out_models.append({"modelId": mid, "displayName": r["display_name"], "familyId": r["family_id"],
                               "phoneLineKind": line_kind or None, "networkTierId": tier or None,
                               "generationOrder": gen, "description": r["description"],
                               "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active})
        for f in fam_index.values():
            if f["active"] and not any(m["familyId"] == f["familyId"] and m["active"] for m in out_models):
                res.warnings.append(f"[equipment_models] Family '{f['familyId']}' has no active models yet")

    key = lambda x: (x["sortOrder"] or 0, x.get("familyId", ""), x.get("modelId", ""))
    return {"families": sorted(fam_index.values(), key=key), "models": sorted(out_models, key=key)}


def export(root: Path) -> tuple[net.Result, Path | None]:
    res = net.Result()
    data = validate_equipment(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "equipment_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "doda.equipment_catalog", "toolVersion": TOOL_VERSION,
               "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
               "totalPersonalDeviceLimit": TOTAL_PERSONAL_DEVICE_LIMIT, **data,
               "openItems": OPEN_ITEMS, "runtimeImplemented": False}
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="DoDA equipment catalog: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else net.find_project_root(Path(__file__).parent)
    if a.command == "validate":
        res = net.Result(); validate_equipment(root, res); out = None
    else:
        res, out = export(root)
    for w in res.warnings: print("WARNING:", w)
    for e in res.errors: print("ERROR:", e)
    print("Rows:", res.stats)
    if out: print("Exported:", out, "sha256", hashlib.sha256(out.read_bytes()).hexdigest())
    print("RESULT:", "PASS" if res.valid else "FAIL")
    return 0 if res.valid else 1


if __name__ == "__main__":
    sys.exit(main())

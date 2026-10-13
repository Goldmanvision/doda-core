#!/usr/bin/env python3
r"""DoDA Content Workbench - hostile catalog (authoring only, no runtime).
Hostiles share the player's weapon catalog (TERR-09). Tier matches mission tiers, except hostiles
used only in authored mission areas. No balance values are authored here."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import doda_network_rules as net
import doda_territory_rules as terr
import doda_weapon_rules as wpn

TOOL_VERSION = "0.1.0"
HOSTILES_FILE = "hostiles.csv"
HOSTILE_COLUMNS = ["hostile_id", "display_name", "engine_class", "weapon_id", "tier_id", "authored_only",
                   "placeholder", "source_reference", "description", "sort_order", "active"]
CLASS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
RULES = {"sharedWeaponCatalog": True, "tierMatchesMissionTiers": True,
         "authoredMissionAreasMayIgnoreTier": True, "agentsAndPlayerShareWeapons": True}
OPEN_ITEMS = {
    "HOST-OPEN-01": "Engine class names for each hostile.",
    "HOST-OPEN-02": "Hit points, damage and other balance values.",
    "HOST-OPEN-03": "Tier assignments, once mission tiers exist.",
    "HOST-OPEN-04": "Human hostiles that replace the Freedoom placeholders.",
    "HOST-OPEN-05": "How hostile count and tier weight the mission dice.",
}


def _ids(src, name, cols, key, label):
    scratch = net.Result()
    rows = net.read_table(src / name, cols, label, scratch) or []
    return {r[key]: r for r in rows}


def validate_hostiles(root, res):
    src = root / "data_authoring" / "source"
    weapons = _ids(src, wpn.WEAPONS_FILE, wpn.WEAPON_COLUMNS, "weapon_id", "weapons")
    tiers = _ids(src, terr.TIERS_FILE, terr.TIER_COLUMNS, "tier_id", "mission_tiers")
    rows = net.read_table(src / HOSTILES_FILE, HOSTILE_COLUMNS, "hostiles", res) or []
    seen, classes, items = set(), set(), []
    for r in rows:
        ctx = f"[hostiles] Line {r['_line']}"
        hid = r["hostile_id"]
        if not hid or hid in seen:
            res.errors.append(f"{ctx}: blank or duplicate hostile_id '{hid}'")
            continue
        seen.add(hid)
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        active = net._bool(r["active"], ctx, res)
        authored = net._bool(r["authored_only"], ctx, res)
        placeholder = net._bool(r["placeholder"], ctx, res)
        ec = r["engine_class"]
        if ec:
            if not CLASS_RE.match(ec):
                res.errors.append(f"{ctx}: engine_class must be a class name (letters, digits and underscore)")
            elif ec.casefold() in classes:
                res.errors.append(f"{ctx}: duplicate engine_class '{ec}'")
            classes.add(ec.casefold())
        elif active:
            res.warnings.append(f"{ctx}: active hostile '{hid}' has no engine_class yet")
        wid = r["weapon_id"]
        if wid:
            weapon = weapons.get(wid)
            if weapon is None:
                res.errors.append(f"{ctx}: unknown weapon_id '{wid}'")
            elif active and weapon["active"].strip().lower() != "true":
                res.errors.append(f"{ctx}: active hostile uses inactive weapon '{wid}'")
        tid = r["tier_id"]
        if tid:
            if authored:
                res.errors.append(f"{ctx}: an authored_only hostile must not have a tier_id")
            elif tid not in tiers:
                res.errors.append(f"{ctx}: unknown tier_id '{tid}'")
        elif active and not authored:
            res.warnings.append(f"{ctx}: active hostile '{hid}' has no tier_id yet")
        items.append({"hostileId": hid, "displayName": r["display_name"], "engineClass": ec or None,
                      "weaponId": wid or None, "tierId": tid or None, "authoredOnly": authored,
                      "placeholder": placeholder, "sourceReference": r["source_reference"] or None,
                      "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active})
    return {"hostiles": sorted(items, key=lambda x: (x["sortOrder"] or 0, x["hostileId"]))}


def export(root):
    res = net.Result()
    data = validate_hostiles(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "hostile_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "doda.hostile_catalog", "toolVersion": TOOL_VERSION,
               "generatedAtUtc": datetime.now(timezone.utc).isoformat(), **data,
               "rules": RULES, "openItems": OPEN_ITEMS, "runtimeImplemented": False}
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv=None):
    p = argparse.ArgumentParser(description="DoDA hostile catalog: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else net.find_project_root(Path(__file__).parent)
    out = None
    if a.command == "validate":
        res = net.Result()
        validate_hostiles(root, res)
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
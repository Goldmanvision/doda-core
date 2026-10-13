#!/usr/bin/env python3
r"""DoDA Content Workbench - shared weapons catalog (authoring only, no runtime).
TERR-09: one catalog shared by the player, agents and hostiles. No balance values here."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import doda_network_rules as net

TOOL_VERSION = "0.1.0"
WEAPONS_FILE = "weapons.csv"
WEAPON_COLUMNS = ["weapon_id", "display_name", "weapon_type", "engine_class", "tags", "source_reference",
                  "description", "sort_order", "active"]
WEAPON_TYPES = ("PISTOL", "SHOTGUN", "SMG", "ASSAULT_RIFLE")
CLASS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TAG_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
RULES = {"sharedBy": ["PLAYER", "AGENTS", "HOSTILES"],
         "agentPreferredWeapon": "ONE_RANDOMIZED_PER_AGENT_DESIGN_LATER"}
OPEN_ITEMS = {
    "WPN-OPEN-01": "Engine class names for each weapon.",
    "WPN-OPEN-02": "More pistols, shotguns and one or two assault rifles; weapon statistics and balance values.",
    "WPN-OPEN-03": "Tactical gear catalog, agent weapon proficiency, and how loadout weights mission dice.",
}


def validate_weapons(root, res):
    rows = net.read_table(root / "data_authoring" / "source" / WEAPONS_FILE, WEAPON_COLUMNS, "weapons", res) or []
    seen, classes, items = set(), set(), []
    for r in rows:
        ctx = f"[weapons] Line {r['_line']}"
        wid = r["weapon_id"]
        if not wid or wid in seen:
            res.errors.append(f"{ctx}: blank or duplicate weapon_id '{wid}'")
            continue
        seen.add(wid)
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        wtype = r["weapon_type"].upper()
        if wtype not in WEAPON_TYPES:
            res.errors.append(f"{ctx}: weapon_type must be one of {', '.join(WEAPON_TYPES)}")
        active = net._bool(r["active"], ctx, res)
        ec = r["engine_class"]
        if ec:
            if not CLASS_RE.match(ec):
                res.errors.append(f"{ctx}: engine_class must be a class name (letters, digits and underscore)")
            elif ec.casefold() in classes:
                res.errors.append(f"{ctx}: duplicate engine_class '{ec}'")
            classes.add(ec.casefold())
        elif active:
            res.warnings.append(f"{ctx}: active weapon '{wid}' has no engine_class yet")
        tags = [t.strip() for t in r["tags"].split(";") if t.strip()]
        for t in tags:
            if not TAG_RE.match(t):
                res.errors.append(f"{ctx}: tags must be uppercase words separated by ';' (got '{t}')")
        if len(set(tags)) != len(tags):
            res.errors.append(f"{ctx}: tags has repeats")
        items.append({"weaponId": wid, "displayName": r["display_name"], "weaponType": wtype,
                      "engineClass": ec or None, "tags": tags, "sourceReference": r["source_reference"] or None,
                      "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active})
    return {"weapons": sorted(items, key=lambda x: (x["sortOrder"] or 0, x["weaponId"]))}


def export(root):
    res = net.Result()
    data = validate_weapons(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "weapon_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "doda.weapon_catalog", "toolVersion": TOOL_VERSION,
               "generatedAtUtc": datetime.now(timezone.utc).isoformat(), **data,
               "rules": RULES, "openItems": OPEN_ITEMS, "runtimeImplemented": False}
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv=None):
    p = argparse.ArgumentParser(description="DoDA weapons catalog: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else net.find_project_root(Path(__file__).parent)
    out = None
    if a.command == "validate":
        res = net.Result()
        validate_weapons(root, res)
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
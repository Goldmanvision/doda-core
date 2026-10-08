#!/usr/bin/env python3
r"""
DoDA Content Workbench - Care services catalog (authoring slice).

Authoring, validation, and export only. No runtime behaviour, prices,
durations, healing amounts, or effects (deferred balancing).

Settled decisions encoded here (2026-10-07):
  * CARE-01: Medical care and therapy are not player-staffed services. They
    have no capability staffing rules or staffing qualifications.
  * CARE-02: Emergency medical care is automated and free of cost.
  * CARE-03: Agents may deliver medical attention through a skill/training
    competency; that is not facility staffing.
  * CARE-04: The player assigns an agent to therapy; the provider is handled
    automatically.
  * CARE-05: Care services live in their own catalog, separate from
    capabilities and staffing rules.
  * CARE-06: The catalog holds medical and therapy services only. Personal care
    (eating, resting, off duty, decompression) belongs with personnel work.
  * CARE-07: Emergency services are free. Non-emergency medical care and both
    physical and psychological therapy have costs; amounts are undecided.
  * CARE-08: Basic Medical Care, Advanced Medical Care, and Therapy Services are
    places where care services can happen (care location features), not
    staffed capabilities. A service may happen at a place with ANY of its
    linked features.
  * CARE-09: Emergency Medical Transport happens at no place; it brings
    incapacitated agents to a hospital for Advanced Medical Care. A service's
    destination_feature_id names where it delivers the agent, and its
    follow-up service must be offered at that destination.

Source files:
  data_authoring/source/care_services.csv
  (follow_up_care_service_id references another row in the same table)
  data_authoring/source/care_location_features.csv
  data_authoring/source/care_service_locations.csv
  (links care_services to care_location_features)
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

TOOL_VERSION = "0.3.0"

CARE_FILE = "care_services.csv"
FEATURES_FILE = "care_location_features.csv"
LINKS_FILE = "care_service_locations.csv"

CARE_COLUMNS = ["care_service_id", "display_name", "care_category", "recipient_assignment",
                "provider_mode", "cost_policy", "duration_minutes", "follow_up_care_service_id",
                "destination_feature_id", "source_reference", "description", "sort_order", "active"]

FEATURE_COLUMNS = ["feature_id", "display_name", "description", "source_reference", "sort_order", "active"]
LINK_COLUMNS = ["care_service_id", "feature_id", "sort_order", "active"]

CARE_CATEGORIES = ("EMERGENCY_MEDICAL", "MEDICAL", "THERAPY")
RECIPIENT_ASSIGNMENTS = ("AUTOMATIC", "PLAYER_ASSIGNED")
PROVIDER_MODES = ("AUTOMATIC", "AUTOMATIC_OR_AGENT_SKILL", "NONE")
COST_POLICIES = ("FREE", "COSTED")

OPEN_ITEMS = {
    "CARE-OPEN-01": "Cost amounts for COSTED services.",
    "CARE-OPEN-02": "Durations, healing amounts, and recovery effects for every service.",
    "CARE-OPEN-03": "Which agent skill level allows delivering medical attention (CARE-03).",
    "CARE-OPEN-04": "How Recovery relates to ordinary rest in the personnel slice.",
    "CARE-OPEN-05": "Which facilities or external locations provide each care location feature.",
}


def validate_care(root: Path, res: net.Result) -> dict[str, Any]:
    src = root / "data_authoring" / "source"
    rows = net.read_table(src / CARE_FILE, CARE_COLUMNS, "care_services", res)
    services: dict[str, dict[str, Any]] = {}
    if rows is None:
        return {"services": [], "locationFeatures": [], "serviceLocations": []}

    for r in rows:
        ctx = f"[care_services] Line {r['_line']}"
        sid = r["care_service_id"]
        if not sid or sid in services:
            res.errors.append(f"{ctx}: blank or duplicate care_service_id '{sid}'")
            continue
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        cat = r["care_category"].upper()
        assign = r["recipient_assignment"].upper()
        provider = r["provider_mode"].upper()
        cost = r["cost_policy"].upper()
        if cat not in CARE_CATEGORIES:
            res.errors.append(f"{ctx}: care_category must be one of {', '.join(CARE_CATEGORIES)}")
        if assign not in RECIPIENT_ASSIGNMENTS:
            res.errors.append(f"{ctx}: recipient_assignment must be AUTOMATIC or PLAYER_ASSIGNED")
        if provider not in PROVIDER_MODES:
            res.errors.append(f"{ctx}: provider_mode must be one of {', '.join(PROVIDER_MODES)}")
        if cost not in COST_POLICIES:
            res.errors.append(f"{ctx}: cost_policy must be FREE or COSTED")

        # Settled decisions.
        if cat == "EMERGENCY_MEDICAL":
            if cost and cost != "FREE":
                res.errors.append(f"{ctx}: emergency medical care is free (CARE-02/CARE-07)")
            if assign and assign != "AUTOMATIC":
                res.errors.append(f"{ctx}: emergency medical care is automated (CARE-02)")
            if provider and provider != "AUTOMATIC":
                res.errors.append(f"{ctx}: emergency medical care uses an automatic provider (CARE-02)")
        elif cat in ("MEDICAL", "THERAPY") and cost == "FREE":
            res.errors.append(f"{ctx}: non-emergency care and therapy have costs (CARE-07)")
        if cat == "THERAPY":
            if assign and assign != "PLAYER_ASSIGNED":
                res.errors.append(f"{ctx}: the player assigns agents to therapy (CARE-04)")
            if provider and provider != "AUTOMATIC":
                res.errors.append(f"{ctx}: therapy providers are handled automatically (CARE-04)")

        duration = None
        if r["duration_minutes"]:
            duration = net._int(r["duration_minutes"], ctx, "duration_minutes", res)
            if duration is not None and duration < 1:
                res.errors.append(f"{ctx}: duration_minutes must be at least 1, or blank while undecided")

        services[sid] = {"careServiceId": sid, "displayName": r["display_name"], "careCategory": cat,
                         "recipientAssignment": assign, "providerMode": provider, "costPolicy": cost,
                         "durationMinutes": duration,
                         "followUpCareServiceId": r["follow_up_care_service_id"] or None,
                         "destinationFeatureId": r["destination_feature_id"] or None,
                         "sourceReference": r["source_reference"] or None,
                         "description": r["description"],
                         "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                         "active": net._bool(r["active"], ctx, res), "_ctx": ctx}

    for s in services.values():
        ctx, follow = s["_ctx"], s["followUpCareServiceId"]
        if follow is None:
            continue
        if follow == s["careServiceId"]:
            res.errors.append(f"{ctx}: a service cannot be its own follow-up")
        elif follow not in services:
            res.errors.append(f"{ctx}: unknown follow_up_care_service_id '{follow}'")
        elif s["active"] and not services[follow]["active"]:
            res.errors.append(f"{ctx}: active service follows up with inactive service '{follow}'")

    # Follow-up chains must end; a loop would send an agent through care forever.
    reported: set[frozenset[str]] = set()
    for start in services:
        path: list[str] = []
        current = start
        while current in services:
            if current in path:
                loop = path[path.index(current):]
                if frozenset(loop) not in reported:
                    reported.add(frozenset(loop))
                    res.errors.append(f"[care_services] Follow-up loop: {' -> '.join(loop + [current])}")
                break
            path.append(current)
            current = services[current]["followUpCareServiceId"]

    for s in services.values():
        if s["active"] and s["durationMinutes"] is None:
            res.warnings.append(f"{s['_ctx']}: active service '{s['careServiceId']}' has no duration yet")

    features = _validate_features(src, res)
    links = _validate_links(src, services, features, res)

    for s in services.values():
        ctx, dest, follow = s["_ctx"], s["destinationFeatureId"], s["followUpCareServiceId"]
        if dest is None:
            continue
        if dest not in features:
            res.errors.append(f"{ctx}: unknown destination_feature_id '{dest}'")
            continue
        if s["active"] and not features[dest]["active"]:
            res.errors.append(f"{ctx}: active service delivers to inactive location feature '{dest}'")
        if follow in services and not any(l["careServiceId"] == follow and l["featureId"] == dest
                                          for l in links):
            res.errors.append(f"{ctx}: follow-up '{follow}' is not offered at destination '{dest}'")

    out = [{k: v for k, v in s.items() if k != "_ctx"} for s in services.values()]
    feats = [{k: v for k, v in f.items() if k != "_ctx"} for f in features.values()]
    return {"services": sorted(out, key=lambda x: (x["sortOrder"] or 0, x["careServiceId"])),
            "locationFeatures": sorted(feats, key=lambda x: (x["sortOrder"] or 0, x["featureId"])),
            "serviceLocations": links}


def _validate_features(src: Path, res: net.Result) -> dict[str, dict[str, Any]]:
    rows = net.read_table(src / FEATURES_FILE, FEATURE_COLUMNS, "care_location_features", res) or []
    features: dict[str, dict[str, Any]] = {}
    for r in rows:
        ctx = f"[care_location_features] Line {r['_line']}"
        fid = r["feature_id"]
        if not fid or fid in features:
            res.errors.append(f"{ctx}: blank or duplicate feature_id '{fid}'")
            continue
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        features[fid] = {"featureId": fid, "displayName": r["display_name"],
                         "description": r["description"], "sourceReference": r["source_reference"] or None,
                         "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                         "active": net._bool(r["active"], ctx, res), "_ctx": ctx}
    return features


def _validate_links(src: Path, services: dict[str, dict[str, Any]],
                    features: dict[str, dict[str, Any]], res: net.Result) -> list[dict[str, Any]]:
    rows = net.read_table(src / LINKS_FILE, LINK_COLUMNS, "care_service_locations", res) or []
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for r in rows:
        ctx = f"[care_service_locations] Line {r['_line']}"
        sid, fid = r["care_service_id"], r["feature_id"]
        if (sid, fid) in seen:
            res.errors.append(f"{ctx}: duplicate link {sid} -> {fid}")
            continue
        seen.add((sid, fid))
        active = net._bool(r["active"], ctx, res)
        service, feature = services.get(sid), features.get(fid)
        if service is None:
            res.errors.append(f"{ctx}: unknown care_service_id '{sid}'")
        if feature is None:
            res.errors.append(f"{ctx}: unknown feature_id '{fid}'")
        if active and service is not None and not service["active"]:
            res.errors.append(f"{ctx}: active link uses inactive service '{sid}'")
        if active and feature is not None and not feature["active"]:
            res.errors.append(f"{ctx}: active link uses inactive location feature '{fid}'")
        out.append({"careServiceId": sid, "featureId": fid,
                    "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res), "active": active})
    for f in features.values():
        if f["active"] and not any(l["featureId"] == f["featureId"] and l["active"] for l in out):
            res.warnings.append(f"{f['_ctx']}: active location feature '{f['featureId']}' hosts no active services")
    return sorted(out, key=lambda x: (x["sortOrder"] or 0, x["careServiceId"], x["featureId"]))


def export(root: Path) -> tuple[net.Result, Path | None]:
    res = net.Result()
    data = validate_care(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "care_services_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "doda.care_services_catalog", "toolVersion": TOOL_VERSION,
               "generatedAtUtc": datetime.now(timezone.utc).isoformat(), **data,
               "openItems": OPEN_ITEMS, "runtimeImplemented": False}
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="DoDA care services catalog: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else net.find_project_root(Path(__file__).parent)
    if a.command == "validate":
        res = net.Result(); validate_care(root, res); out = None
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

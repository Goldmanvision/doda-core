#!/usr/bin/env python3
r"""
DoDA Content Workbench - Personnel traits and training catalogs (authoring slice).

Authored definitions only. Each agent's actual trait and training values are
campaign/save state owned by the native simulation.

Settled decisions encoded here (2026-10-07):
  * PERS-13: Traits, training (skills), qualifications, and conditions stay in
    separate catalogs (handoff spec: they must not be collapsed).
  * PERS-14: TrainingCat IDs (TRAIN_*) are canonical for training. The
    duplicate *_TRAINING rows in TraitDefsCat are not imported. Loyalty stays a
    condition stat (PERS-03) and is not a trait.
  * PERS-06 applies: any agent value authored in the Workbench may count toward
    the Health average, with a formula. Traits and training default to not
    counting.
  * PERS-10 applies: each value states how it starts on agent/analyst creation.

Source files:
  data_authoring/source/personnel_traits.csv
  data_authoring/source/training_catalog.csv
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import doda_network_rules as net

TOOL_VERSION = "0.1.0"

TRAITS_FILE = "personnel_traits.csv"
TRAINING_FILE = "training_catalog.csv"

HEALTH_FORMULAS = ("NORMALIZED", "PERCENT_OF_REFERENCE")
CREATION_RULES = ("DEFAULT", "RANDOM_IN_RANGE")
TRAIT_CATEGORIES = ("PERSONALITY", "ATTRIBUTE", "SPECIAL_APTITUDE")
TRAINING_CATEGORIES = ("TACTICAL", "INVESTIGATIVE", "MEDICAL", "RESEARCH", "ADMINISTRATIVE")


def _columns(id_col: str, cat_col: str) -> list[str]:
    return [id_col, "display_name", cat_col, "minimum_value", "maximum_value", "default_value",
            "creation_rule", "can_change_over_time", "contributes_to_health", "health_formula",
            "health_reference_id", "primary_uses", "related_systems", "source_reference",
            "description", "sort_order", "active"]


TRAIT_COLUMNS = _columns("trait_id", "trait_category")
TRAINING_COLUMNS = _columns("training_id", "training_category")


@dataclass(frozen=True)
class AttributeTable:
    name: str
    filename: str
    id_col: str
    cat_col: str
    categories: tuple[str, ...]
    columns: list[str]


TABLES = (
    AttributeTable("personnel_traits", TRAITS_FILE, "trait_id", "trait_category", TRAIT_CATEGORIES,
                   TRAIT_COLUMNS),
    AttributeTable("training_catalog", TRAINING_FILE, "training_id", "training_category",
                   TRAINING_CATEGORIES, TRAINING_COLUMNS),
)

OPEN_ITEMS = {
    "PERS-OPEN-07": "How traits and training affect tasks, events, stress, and compliance (values and formulas).",
    "PERS-OPEN-08": "How training improves over time, and training thresholds used by qualifications.",
    "PERS-OPEN-09": "RemedyCat TRAINED_* flags (MEDIC, CULINARY, HOSPITALITY, SURVIVALIST, MAGIC): map to training thresholds or qualifications.",
}


def _opt_int(value: str, ctx: str, field: str, res: net.Result) -> int | None:
    return net._int(value, ctx, field, res) if value else None


def _validate_table(src: Path, t: AttributeTable, res: net.Result) -> list[dict[str, Any]]:
    rows = net.read_table(src / t.filename, t.columns, t.name, res)
    if rows is None:
        return []
    items: dict[str, dict[str, Any]] = {}
    for r in rows:
        ctx = f"[{t.name}] Line {r['_line']}"
        iid = r[t.id_col]
        if not iid or iid in items:
            res.errors.append(f"{ctx}: blank or duplicate {t.id_col} '{iid}'")
            continue
        if not r["display_name"]:
            res.errors.append(f"{ctx}: display_name is required")
        cat = r[t.cat_col].upper()
        if cat not in t.categories:
            res.errors.append(f"{ctx}: {t.cat_col} must be one of {', '.join(t.categories)}")
        lo = _opt_int(r["minimum_value"], ctx, "minimum_value", res)
        hi = _opt_int(r["maximum_value"], ctx, "maximum_value", res)
        default = _opt_int(r["default_value"], ctx, "default_value", res)
        if lo is None or hi is None:
            res.errors.append(f"{ctx}: minimum_value and maximum_value are required")
        elif lo >= hi:
            res.errors.append(f"{ctx}: minimum_value must be below maximum_value")
        if default is not None and lo is not None and hi is not None and not lo <= default <= hi:
            res.errors.append(f"{ctx}: default_value is outside the range")
        creation = r["creation_rule"].upper()
        if creation not in CREATION_RULES:
            res.errors.append(f"{ctx}: creation_rule must be one of {', '.join(CREATION_RULES)}")
        if creation == "DEFAULT" and default is None:
            res.errors.append(f"{ctx}: DEFAULT needs a default_value")
        if creation == "RANDOM_IN_RANGE" and default is not None:
            res.errors.append(f"{ctx}: default_value is unused by RANDOM_IN_RANGE; leave it blank")
        contributes = net._bool(r["contributes_to_health"], ctx, res)
        formula, ref = r["health_formula"].upper(), r["health_reference_id"]
        if contributes:
            if formula not in HEALTH_FORMULAS:
                res.errors.append(f"{ctx}: a Health contributor needs a health_formula "
                                  f"({', '.join(HEALTH_FORMULAS)})")
            if formula == "PERCENT_OF_REFERENCE" and not ref:
                res.errors.append(f"{ctx}: PERCENT_OF_REFERENCE needs health_reference_id")
            if formula != "PERCENT_OF_REFERENCE" and ref:
                res.errors.append(f"{ctx}: health_reference_id is only used by PERCENT_OF_REFERENCE")
        elif formula or ref:
            res.errors.append(f"{ctx}: health_formula and reference are only set when the value counts toward Health")
        items[iid] = {"id": iid, "displayName": r["display_name"], "category": cat,
                      "minimumValue": lo, "maximumValue": hi, "defaultValue": default,
                      "creationRule": creation or None,
                      "canChangeOverTime": net._bool(r["can_change_over_time"], ctx, res),
                      "contributesToHealth": contributes, "healthFormula": formula or None,
                      "healthReferenceId": ref or None, "primaryUses": r["primary_uses"],
                      "relatedSystems": r["related_systems"],
                      "sourceReference": r["source_reference"] or None, "description": r["description"],
                      "sortOrder": net._int(r["sort_order"], ctx, "sort_order", res),
                      "active": net._bool(r["active"], ctx, res), "_ctx": ctx}

    for it in items.values():
        ref = it["healthReferenceId"]
        if not (it["contributesToHealth"] and it["healthFormula"] == "PERCENT_OF_REFERENCE" and ref):
            continue
        target = items.get(ref)
        if target is None:
            res.errors.append(f"{it['_ctx']}: unknown health_reference_id '{ref}' (must be in {t.name})")
        elif ref == it["id"]:
            res.errors.append(f"{it['_ctx']}: a value cannot be its own Health reference")
        elif target["minimumValue"] is None or target["minimumValue"] < 1:
            res.errors.append(f"{it['_ctx']}: reference '{ref}' needs a minimum of at least 1 (it is divided by)")
        elif it["active"] and not target["active"]:
            res.errors.append(f"{it['_ctx']}: active value uses inactive Health reference '{ref}'")

    out = [{k: v for k, v in it.items() if k != "_ctx"} for it in items.values()]
    return sorted(out, key=lambda x: (x["sortOrder"] or 0, x["id"]))


def validate_attributes(root: Path, res: net.Result) -> dict[str, Any]:
    src = root / "data_authoring" / "source"
    data = {t.name: _validate_table(src, t, res) for t in TABLES}
    ids: dict[str, str] = {}
    for t in TABLES:
        for it in data[t.name]:
            if it["id"] in ids:
                res.errors.append(f"[{t.name}] ID '{it['id']}' is also used in {ids[it['id']]}")
            ids[it["id"]] = t.name
    return {"traits": data["personnel_traits"], "training": data["training_catalog"]}


def export(root: Path) -> tuple[net.Result, Path | None]:
    res = net.Result()
    data = validate_attributes(root, res)
    if not res.valid:
        return res, None
    out = root / "generated" / "data" / "personnel_attributes_catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "doda.personnel_attributes_catalog", "toolVersion": TOOL_VERSION,
               "generatedAtUtc": datetime.now(timezone.utc).isoformat(), **data,
               "openItems": OPEN_ITEMS, "runtimeImplemented": False}
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)
    return res, out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="DoDA personnel traits and training: validate or export.")
    p.add_argument("command", choices=["validate", "export"])
    p.add_argument("--root", type=Path, default=None)
    a = p.parse_args(argv)
    root = a.root.resolve() if a.root else net.find_project_root(Path(__file__).parent)
    if a.command == "validate":
        res = net.Result(); validate_attributes(root, res); out = None
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

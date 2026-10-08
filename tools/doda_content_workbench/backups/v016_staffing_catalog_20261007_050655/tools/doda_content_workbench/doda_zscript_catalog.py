"""Generate a read-only ZScript catalog from validated Workbench exports.

Option B bridge (stopgap): display/lookup data only, no simulation rules.
Inputs : generated/data/network_transfer_rules.json, generated/data/equipment_catalog.json,
         generated/data/department_content.json (facilities, capabilities, links, tracks)
Output : DoDA/Generated/WorkbenchCatalog.zs (plus expected-dump text for comparison)

ZScript features used (local docs, ZDoom_Documentation):
  03.02 Constant Definitions (int const), switch statement, 05.03.02 Console.PrintF,
  05.04.02 EventHandler / 05.04.08 NetworkProcess, 05.04.01 ConsoleEvent.Name.
String static const arrays are avoided because local docs only show int arrays.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

GENERATOR_VERSION = "0.2.0"
NETWORK_JSON = Path("generated/data/network_transfer_rules.json")
EQUIPMENT_JSON = Path("generated/data/equipment_catalog.json")
DEPARTMENT_JSON = Path("generated/data/department_content.json")
OUTPUT_ZS = Path("DoDA/Generated/WorkbenchCatalog.zs")
EXPECTED_DUMP = Path("generated/data/workbench_catalog_expected_dump.txt")
INCLUDE_LINE = '#include "DoDA/Generated/WorkbenchCatalog.zs"'
DUMP_EVENT = "DoDA_CatalogDump"


def find_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "zscript.txt").exists() and (p / "data_authoring").exists():
            return p
    raise SystemExit("ERROR: doda-core root not found")


def zs_str(value) -> str:
    s = "" if value is None else str(value)
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\r", " ").replace("\n", " ")
    return '"' + s + '"'


def _active(rows):
    return [r for r in rows if r.get("active", True)]


def _sorted(rows, key):
    return sorted(rows, key=lambda r: (r.get("sortOrder", 0), r[key]))


def string_lookup(name: str, values: list[str]) -> str:
    lines = [f"    static String {name}(int i)", "    {", "        switch (i)", "        {"]
    for i, v in enumerate(values):
        lines.append(f"        case {i}: return {zs_str(v)};")
    lines += ["        default: return \"\";", "        }", "    }", ""]
    return "\n".join(lines)


def int_lookup(name: str, values: list[int]) -> str:
    """None -> -1 (not applicable); out-of-range index -> -2."""
    lines = [f"    static int {name}(int i)", "    {", "        switch (i)", "        {"]
    for i, v in enumerate(values):
        lines.append(f"        case {i}: return {-1 if v is None else int(v)};")
    lines += ["        default: return -2;", "        }", "    }", ""]
    return "\n".join(lines)


def find_fn(name: str, count_const: str, id_fn: str) -> str:
    return "\n".join([
        f"    static int {name}(String id)",
        "    {",
        f"        for (int i = 0; i < {count_const}; i++)",
        "        {",
        f"            if ({id_fn}(i) == id) return i;",
        "        }",
        "        return -1;",
        "    }",
        "",
    ])


def load(root: Path):
    net_p, eq_p = root / NETWORK_JSON, root / EQUIPMENT_JSON
    for p in (net_p, eq_p):
        if not p.exists():
            raise ValueError(f"Missing export {p}; run Export All first")
    net, eq = json.loads(net_p.read_bytes()), json.loads(eq_p.read_bytes())
    p = root / DEPARTMENT_JSON
    if not p.exists():
        raise ValueError(f"Missing export {p}; run Export All first")
    dept = json.loads(p.read_bytes())
    return net, eq, content_hash(net), content_hash(eq), dept


def department_catalog(dept):
    """Project only this slice. Reject dangling active links before any write."""
    tables = dept["tables"]
    facilities = _sorted(_active(tables["facilities"]), "facility_id")
    capabilities = _sorted(_active(tables["capabilities"]), "capability_id")
    tracks = {r["track_id"]: r for r in _active(tables["department_tracks"])}
    links = sorted(_active(tables["facility_capabilities"]),
                   key=lambda r: (r["facility_id"], r["sort_order"], r["capability_id"]))
    # Department CSVs use snake_case sort order.
    capabilities.sort(key=lambda r: (r["sort_order"], r["capability_id"]))
    facility_ids = {r["facility_id"] for r in facilities}
    capability_ids = {r["capability_id"] for r in capabilities}
    seen = set()
    for row in facilities:
        if row["track_id"] not in tracks:
            raise ValueError(f"Unknown active track: {row['track_id']}")
    for row in links:
        pair = (row["facility_id"], row["capability_id"])
        if pair in seen or pair[0] not in facility_ids or pair[1] not in capability_ids:
            raise ValueError(f"Invalid/duplicate active facility-capability link: {pair}")
        seen.add(pair)
    projected = dict(facilities=facilities, capabilities=capabilities, links=links,
                     tracks=sorted(tracks.values(), key=lambda r: r["track_id"]))
    return facilities, capabilities, links, tracks, content_hash(projected)


def department_lookups(facilities, capabilities, links, tracks):
    parts = []
    def strings(prefix, rows, columns):
        for suffix, key in columns:
            parts.append(string_lookup(prefix + suffix, [r[key] for r in rows]))
    strings("Facility", facilities, [
        ("Id", "facility_id"), ("DisplayName", "display_name"),
        ("Description", "description"), ("TrackId", "track_id"),
        ("ZoneId", "hq_zone_id"), ("InitialTier", "initial_tier_id")])
    parts.append(string_lookup("FacilityTrackName", [
        tracks[r["track_id"]]["display_name"] for r in facilities]))
    parts.append(int_lookup("FacilityCapacity", [r["personnel_capacity"] for r in facilities]))
    parts.append(find_fn("FindFacility", "FACILITY_COUNT", "FacilityId"))
    strings("Capability", capabilities, [
        ("Id", "capability_id"), ("DisplayName", "display_name"),
        ("Description", "description"), ("StandingLabel", "standing_operation_label")])
    parts.append(find_fn("FindCapability", "CAPABILITY_COUNT", "CapabilityId"))
    strings("FacilityCapability", links, [
        ("FacilityId", "facility_id"), ("CapabilityId", "capability_id"),
        ("InitialTier", "initial_tier_id")])
    names = {r["capability_id"]: r["display_name"] for r in capabilities}
    parts.append(string_lookup("FacilityCapabilityDisplayName", [
        r["display_name_override"] or names[r["capability_id"]] for r in links]))
    parts.append(int_lookup("FacilityCapabilityCapacity", [
        r["max_concurrent_personnel"] for r in links]))
    return "\n".join(parts)


def content_hash(doc: dict) -> str:
    """Stable fingerprint: ignores export timestamps so unchanged data keeps the same hash."""
    stable = {k: v for k, v in doc.items() if k != "generatedAtUtc"}
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build(net, eq, net_hash, eq_hash, dept):
    tiers = _sorted(_active(net["tiers"]), "tierId")
    hw = _sorted(_active(net["hardwareModels"]), "modelId")
    fams = _sorted(_active(eq["families"]), "familyId")
    models = _sorted(_active(eq["models"]), "modelId")
    facilities, capabilities, links, tracks, dept_hash = department_catalog(dept)

    out = [
        "/*//////////////////////////|",
        "// DoDA/Generated/WorkbenchCatalog.zs",
        "*///////////////////////////|",
        "// GENERATED FILE - DO NOT EDIT. Regenerate with",
        "//   tools/doda_content_workbench/doda_zscript_catalog.py",
        f"// Generator {GENERATOR_VERSION}; network content sha256 {net_hash}",
        f"// equipment content sha256 {eq_hash}",
        f"// department catalog content sha256 {dept_hash}",
        "// Read-only display/lookup catalog (Option B stopgap). No simulation rules.",
        "",
        "class DoDAWorkbenchCatalog : Object",
        "{",
        f"    const TIER_COUNT = {len(tiers)};",
        f"    const HARDWARE_COUNT = {len(hw)};",
        f"    const FAMILY_COUNT = {len(fams)};",
        f"    const MODEL_COUNT = {len(models)};",
        f"    const FACILITY_COUNT = {len(facilities)};",
        f"    const CAPABILITY_COUNT = {len(capabilities)};",
        f"    const FACILITY_CAPABILITY_COUNT = {len(links)};",
        f"    const TOTAL_PERSONAL_DEVICE_LIMIT = {int(eq['totalPersonalDeviceLimit'])};",
        "",
        f"    static String GeneratorVersion() {{ return {zs_str(GENERATOR_VERSION)}; }}",
        f"    static String NetworkSourceHash() {{ return {zs_str(net_hash[:16])}; }}",
        f"    static String EquipmentSourceHash() {{ return {zs_str(eq_hash[:16])}; }}",
        f"    static String DepartmentSourceHash() {{ return {zs_str(dept_hash[:16])}; }}",
        "",
        "    // Network tiers",
        string_lookup("TierId", [t["tierId"] for t in tiers]),
        string_lookup("TierDisplayName", [t["displayName"] for t in tiers]),
        string_lookup("TierNetworkType", [t["networkType"] for t in tiers]),
        int_lookup("TierGeneration", [t["generation"] for t in tiers]),
        find_fn("FindTier", "TIER_COUNT", "TierId"),
        "    // Network hardware (modems / routers)",
        string_lookup("HardwareId", [h["modelId"] for h in hw]),
        string_lookup("HardwareDisplayName", [h["displayName"] for h in hw]),
        string_lookup("HardwareKind", [h["hardwareKind"] for h in hw]),
        string_lookup("HardwareTierId", [h["tierId"] for h in hw]),
        find_fn("FindHardware", "HARDWARE_COUNT", "HardwareId"),
        "    // Equipment families",
        string_lookup("FamilyId", [f["familyId"] for f in fams]),
        string_lookup("FamilyDisplayName", [f["displayName"] for f in fams]),
        string_lookup("FamilyOwnership", [f["ownership"] for f in fams]),
        string_lookup("FamilyStorageKind", [f["storageKind"] for f in fams]),
        string_lookup("FamilyConnectionKind", [f["connectionKind"] for f in fams]),
        int_lookup("FamilyPerTaskLimit", [f["perTaskLimit"] for f in fams]),
        find_fn("FindFamily", "FAMILY_COUNT", "FamilyId"),
        "    // Equipment models",
        string_lookup("ModelId", [m["modelId"] for m in models]),
        string_lookup("ModelDisplayName", [m["displayName"] for m in models]),
        string_lookup("ModelFamilyId", [m["familyId"] for m in models]),
        string_lookup("ModelPhoneLineKind", [m.get("phoneLineKind") for m in models]),
        string_lookup("ModelNetworkTierId", [m.get("networkTierId") for m in models]),
        string_lookup("ModelConnectionOverride", [m.get("connectionOverride") for m in models]),
        int_lookup("ModelGeneration", [m["generationOrder"] for m in models]),
        find_fn("FindModel", "MODEL_COUNT", "ModelId"),
        "    // Authored facilities/capabilities. Initial tiers are NOT campaign status.",
        department_lookups(facilities, capabilities, links, tracks),
        "}",
        "",
        "// Console: netevent " + DUMP_EVENT,
        "class DoDAWorkbenchCatalogProbe : EventHandler",
        "{",
        "    override void NetworkProcess(ConsoleEvent e)",
        "    {",
        f"        if (e.Name != {zs_str(DUMP_EVENT)}) return;",
        '        Console.PrintF("DODA_CATALOG BEGIN gen=%s net=%s eq=%s dept=%s", DoDAWorkbenchCatalog.GeneratorVersion(), DoDAWorkbenchCatalog.NetworkSourceHash(), DoDAWorkbenchCatalog.EquipmentSourceHash(), DoDAWorkbenchCatalog.DepartmentSourceHash());',
        '        Console.PrintF("DODA_CATALOG COUNTS tiers=%d hardware=%d families=%d models=%d limit=%d", DoDAWorkbenchCatalog.TIER_COUNT, DoDAWorkbenchCatalog.HARDWARE_COUNT, DoDAWorkbenchCatalog.FAMILY_COUNT, DoDAWorkbenchCatalog.MODEL_COUNT, DoDAWorkbenchCatalog.TOTAL_PERSONAL_DEVICE_LIMIT);',
        "        for (int t = 0; t < DoDAWorkbenchCatalog.TIER_COUNT; t++)",
        '            Console.PrintF("DODA_CATALOG TIER %s", DoDAWorkbenchCatalog.TierId(t));',
        "        for (int h = 0; h < DoDAWorkbenchCatalog.HARDWARE_COUNT; h++)",
        '            Console.PrintF("DODA_CATALOG HW %s %s", DoDAWorkbenchCatalog.HardwareId(h), DoDAWorkbenchCatalog.HardwareTierId(h));',
        "        for (int f = 0; f < DoDAWorkbenchCatalog.FAMILY_COUNT; f++)",
        '            Console.PrintF("DODA_CATALOG FAMILY %s", DoDAWorkbenchCatalog.FamilyId(f));',
        "        for (int m = 0; m < DoDAWorkbenchCatalog.MODEL_COUNT; m++)",
        '            Console.PrintF("DODA_CATALOG MODEL %s %s", DoDAWorkbenchCatalog.ModelId(m), DoDAWorkbenchCatalog.ModelFamilyId(m));',
        '        Console.PrintF("DODA_CATALOG DEPARTMENT facilities=%d capabilities=%d links=%d", DoDAWorkbenchCatalog.FACILITY_COUNT, DoDAWorkbenchCatalog.CAPABILITY_COUNT, DoDAWorkbenchCatalog.FACILITY_CAPABILITY_COUNT);',
        "        for (int fi = 0; fi < DoDAWorkbenchCatalog.FACILITY_COUNT; fi++)",
        '            Console.PrintF("DODA_CATALOG FACILITY %s", DoDAWorkbenchCatalog.FacilityId(fi));',
        "        for (int ca = 0; ca < DoDAWorkbenchCatalog.CAPABILITY_COUNT; ca++)",
        '            Console.PrintF("DODA_CATALOG CAPABILITY %s", DoDAWorkbenchCatalog.CapabilityId(ca));',
        "        for (int li = 0; li < DoDAWorkbenchCatalog.FACILITY_CAPABILITY_COUNT; li++)",
        '            Console.PrintF("DODA_CATALOG LINK %s %s", DoDAWorkbenchCatalog.FacilityCapabilityFacilityId(li), DoDAWorkbenchCatalog.FacilityCapabilityCapabilityId(li));',
        '        Console.PrintF("DODA_CATALOG END");',
        "    }",
        "}",
        "",
    ]
    dump = [f"DODA_CATALOG BEGIN gen={GENERATOR_VERSION} net={net_hash[:16]} eq={eq_hash[:16]} dept={dept_hash[:16]}",
            f"DODA_CATALOG COUNTS tiers={len(tiers)} hardware={len(hw)} families={len(fams)} "
            f"models={len(models)} limit={int(eq['totalPersonalDeviceLimit'])}"]
    dump += [f"DODA_CATALOG TIER {t['tierId']}" for t in tiers]
    dump += [f"DODA_CATALOG HW {h['modelId']} {h['tierId']}" for h in hw]
    dump += [f"DODA_CATALOG FAMILY {f['familyId']}" for f in fams]
    dump += [f"DODA_CATALOG MODEL {m['modelId']} {m['familyId']}" for m in models]
    dump += [f"DODA_CATALOG DEPARTMENT facilities={len(facilities)} capabilities={len(capabilities)} links={len(links)}"]
    dump += [f"DODA_CATALOG FACILITY {r['facility_id']}" for r in facilities]
    dump += [f"DODA_CATALOG CAPABILITY {r['capability_id']}" for r in capabilities]
    dump += [f"DODA_CATALOG LINK {r['facility_id']} {r['capability_id']}" for r in links]
    dump.append("DODA_CATALOG END")
    return "\n".join(out), "\n".join(dump) + "\n"


def generate(root: Path) -> tuple[Path, str, bool]:
    """Write catalog + expected dump. Returns (path, sha256, include_present)."""
    zs, dump = build(*load(root))
    target = root / OUTPUT_ZS
    included = INCLUDE_LINE in (root / "zscript.txt").read_text(encoding="utf-8", errors="replace")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(zs, encoding="utf-8", newline="\n")
    (root / EXPECTED_DUMP).write_text(dump, encoding="utf-8", newline="\n")
    return target, hashlib.sha256(zs.encode()).hexdigest(), included


def is_current(root: Path) -> bool:
    zs, _ = build(*load(root))
    target = root / OUTPUT_ZS
    return target.exists() and target.read_text(encoding="utf-8") == zs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--check", action="store_true", help="fail if generated file is stale; write nothing")
    a = ap.parse_args(argv)
    root = a.root or find_root(Path(__file__).resolve().parent)
    if a.check:
        ok = is_current(root)
        print("RESULT: " + ("PASS (catalog current)" if ok else "FAIL (catalog stale or missing)"))
        return 0 if ok else 1
    target, sha, included = generate(root)
    print(f"Wrote {target} sha256 {sha}")
    print(f"Wrote {root / EXPECTED_DUMP}")
    print("zscript.txt include present: " + ("yes" if included else "NO - add manually"))
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

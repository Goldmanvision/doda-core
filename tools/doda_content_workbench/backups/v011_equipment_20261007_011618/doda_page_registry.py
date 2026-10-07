"""
DoDA Content Workbench - central page registry and shared table metadata.

One place that says which pages exist, which navigation group they belong to,
and (for migrated tables) what their fields are. The grouped sidebar, the View
menu, and the network editors all read from here.

Migration status: only the network tables use TABLE_METADATA so far. Older
editors keep their own field definitions until migrated one at a time.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import doda_network_rules as network_rules


@dataclass(frozen=True)
class PageSpec:
    page_id: str
    group: str
    label: str
    tab_text_prefix: str          # matched against the notebook tab text
    tables: tuple[str, ...] = ()


GROUP_ORDER = (
    "Overview",
    "Department",
    "Facilities and Staffing",
    "Tasks",
    "Network and Transfers",
    "Content",
    "Administration",
)

PAGES: tuple[PageSpec, ...] = (
    PageSpec("dashboard", "Overview", "Dashboard", "Dashboard"),
    PageSpec("tracks", "Department", "Department Tracks", "Department Tracks", ("department_tracks",)),
    PageSpec("metrics", "Department", "Metrics", "Metrics", ("metrics",)),
    PageSpec("metric_tiers", "Department", "Metric Tiers", "Metric Tiers", ("metric_tiers",)),
    PageSpec("facilities", "Facilities and Staffing", "Facilities", "Facilities —", ("facilities",)),
    PageSpec("facility_capabilities", "Facilities and Staffing", "Facility Capabilities",
             "Facility Capabilities", ("facility_capabilities",)),
    PageSpec("capabilities", "Facilities and Staffing", "Capabilities", "Capabilities —", ("capabilities",)),
    PageSpec("capability_staffing_rules", "Facilities and Staffing", "Capability Staffing Rules",
             "Capability Staffing Rules", ("capability_staffing_rules",)),
    PageSpec("staffing_overrides", "Facilities and Staffing", "Facility Staffing Overrides",
             "Facility Staffing Overrides", ("facility_capability_staffing_overrides",)),
    PageSpec("qualifications", "Facilities and Staffing", "Qualifications", "Qualifications",
             ("qualification_catalog",)),
    PageSpec("task_templates", "Tasks", "Task Templates", "Task Templates", ("task_templates",)),
    PageSpec("network_tiers", "Network and Transfers", "Network Tiers", "Network Tiers", ("network_tiers",)),
    PageSpec("network_hardware", "Network and Transfers", "Modems and Routers", "Modems and Routers",
             ("network_hardware_models",)),
    PageSpec("transfer_rules", "Network and Transfers", "Transfer and Interruption Rules",
             "Transfer and Interruption Rules"),
    PageSpec("flavor_text", "Content", "Flavor Text", "Flavor Text", ("flavor_text",)),
    PageSpec("enum_catalog", "Administration", "Enum Catalog", "Enum Catalog", ("enum_catalog",)),
    PageSpec("activity_log", "Administration", "Activity Log", "Activity Log"),
)


@dataclass(frozen=True)
class FieldSpec:
    name: str
    label: str
    kind: str = "text"            # text | int | bool | choice | ref
    required: bool = True
    choices: tuple[str, ...] = ()
    ref_table: str = ""           # for kind == "ref": table whose key supplies choices
    multiline: bool = False


@dataclass(frozen=True)
class TableSpec:
    table: str
    filename: str
    key: str
    fields: tuple[FieldSpec, ...] = field(default_factory=tuple)

    @property
    def columns(self) -> list[str]:
        return [f.name for f in self.fields]


TABLE_METADATA: dict[str, TableSpec] = {
    "network_tiers": TableSpec(
        "network_tiers", network_rules.TIERS_FILE, "tier_id", (
            FieldSpec("tier_id", "Tier ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("network_type", "Network Type"),
            FieldSpec("generation", "Generation"),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "network_hardware_models": TableSpec(
        "network_hardware_models", network_rules.HARDWARE_FILE, "model_id", (
            FieldSpec("model_id", "Model ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("hardware_kind", "Hardware Kind", kind="choice",
                      choices=tuple(sorted(network_rules.HARDWARE_KINDS))),
            FieldSpec("tier_id", "Tier", kind="ref", ref_table="network_tiers"),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
}


def page_for_tab_text(text: str) -> PageSpec | None:
    """Longest matching prefix wins, so 'Facility Capabilities' beats 'Facilities'."""
    best: PageSpec | None = None
    for page in PAGES:
        if text.startswith(page.tab_text_prefix):
            if best is None or len(page.tab_text_prefix) > len(best.tab_text_prefix):
                best = page
    return best


def check_registry() -> list[str]:
    """Consistency checks used by tests: metadata must agree with the validator."""
    problems: list[str] = []
    ids = [p.page_id for p in PAGES]
    if len(ids) != len(set(ids)):
        problems.append("Duplicate page_id in PAGES")
    for p in PAGES:
        if p.group not in GROUP_ORDER:
            problems.append(f"Page {p.page_id} has unknown group {p.group}")
    if TABLE_METADATA["network_tiers"].columns != network_rules.TIER_COLUMNS:
        problems.append("network_tiers metadata columns differ from validator")
    if TABLE_METADATA["network_hardware_models"].columns != network_rules.HARDWARE_COLUMNS:
        problems.append("network_hardware_models metadata columns differ from validator")
    return problems

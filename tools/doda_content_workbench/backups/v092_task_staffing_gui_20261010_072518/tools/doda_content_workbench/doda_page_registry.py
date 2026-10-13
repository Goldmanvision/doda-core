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
import doda_resource_rules as resource_rules
import doda_task_flow_rules as task_flow_rules
import doda_equipment_rules as equipment_rules
import doda_care_rules as care_rules
import doda_condition_rules as condition_rules
import doda_agent_attribute_rules as attribute_rules
import doda_personal_care_rules as personal_care_rules
import doda_time_rules as time_rules
import doda_recreation_content_rules as rc_rules
import doda_sobriety_rules as sobriety_rules
import doda_territory_rules as territory_rules
import doda_congressional_support_rules as congressional_support_rules
import doda_weapon_rules as weapon_rules
import doda_hostile_rules as hostile_rules
import doda_progression_identity_rules as progression_identity_rules
import doda_authored_mission_rules as authored_mission_rules


@dataclass(frozen=True)
class PageSpec:
    page_id: str
    group: str
    label: str
    tab_text_prefix: str          # matched against the notebook tab text
    tables: tuple[str, ...] = ()
    subgroup: str = ""


GROUP_ORDER = (
    "Overview",
    "Department",
    "Facilities and Staffing",
    "Tasks",
    "Territory and Missions",
    "Personnel and Care",
    "Equipment",
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
    PageSpec("care_services", "Personnel and Care", "Care Services", "Care Services",
             ("care_services",)),
    PageSpec("care_location_features", "Personnel and Care", "Care Locations", "Care Locations",
             ("care_location_features",)),
    PageSpec("care_service_locations", "Personnel and Care", "Care Service Locations",
             "Care Service Locations", ("care_service_locations",)),
    PageSpec("condition_stats", "Personnel and Care", "Condition Stats", "Condition Stats",
             ("condition_stats",)),
    PageSpec("condition_bands", "Personnel and Care", "Condition Bands", "Condition Bands",
             ("condition_bands",)),
    PageSpec("personnel_traits", "Personnel and Care", "Traits", "Traits", ("personnel_traits",)),
    PageSpec("training_catalog", "Personnel and Care", "Training", "Training", ("training_catalog",)),
    PageSpec("personal_care_actions", "Personnel and Care", "Personal Care", "Personal Care —",
             ("personal_care_actions",)),
    PageSpec("personal_care_features", "Personnel and Care", "Personal Care Places",
             "Personal Care Places", ("personal_care_features",)),
    PageSpec("personal_care_locations", "Personnel and Care", "Personal Care Place Links",
             "Personal Care Place Links", ("personal_care_locations",)),
    PageSpec("personal_care_trainings", "Personnel and Care", "Personal Care Trainings",
             "Personal Care Trainings", ("personal_care_trainings",)),
    PageSpec("personal_care_place_types", "Personnel and Care", "Place Types", "Place Types —",
             ("personal_care_place_types",)),
    PageSpec("personal_care_place_type_features", "Personnel and Care", "Place Type Features",
             "Place Type Features", ("personal_care_place_type_features",)),
    PageSpec("recreation_activities", "Personnel and Care", "Recreation Activities",
             "Recreation Activities", ("recreation_activities",)),
    PageSpec("personal_care_during_care", "Personnel and Care", "Personal Care During Care",
             "Personal Care During Care", ("personal_care_during_care",)),
    PageSpec("time_settings", "Administration", "Time Settings", "Time Settings",
             ("time_settings",)),
    PageSpec("sobriety_stages", "Personnel and Care", "Sobriety Stages", "Sobriety Stages",
             ("sobriety_stages",)),
    PageSpec("sobriety_settings", "Personnel and Care", "Sobriety Settings", "Sobriety Settings",
             ("sobriety_settings",)),
    PageSpec("sobriety_shift_rules", "Personnel and Care", "Sobriety Shift Rules", "Sobriety Shift Rules",
             ("sobriety_shift_rules",)),
    PageSpec("greater_territories", "Territory and Missions", "Greater Territories", "Greater Territories", ("greater_territories",)),
    PageSpec("greater_territory_tags", "Territory and Missions", "Greater Territory Tags", "Greater Territory Tags", ("greater_territory_tags",)),
    PageSpec("greater_territory_tag_links", "Territory and Missions", "Greater Territory Tag Links", "Greater Territory Tag Links", ("greater_territory_tag_links",)),
    PageSpec("territories", "Territory and Missions", "Territories", "Territories", ("territories",)),
    PageSpec("territory_settings", "Territory and Missions", "Territory Settings", "Territory Settings", ("territory_settings",)),
    PageSpec("mission_tiers", "Territory and Missions", "Mission Tiers", "Mission Tiers", ("mission_tiers",)),
    PageSpec("map_formats", "Territory and Missions", "Map Formats", "Map Formats", ("map_formats",)),
    PageSpec("maps", "Territory and Missions", "Maps", "Maps", ("maps",)),
    PageSpec("weapons", "Territory and Missions", "Weapons", "Weapons", ("weapons",)),
    PageSpec("hostiles", "Territory and Missions", "Hostiles", "Hostiles", ("hostiles",)),
    PageSpec("upgrades", "Territory and Missions", "Upgrades", "Upgrades", ("upgrades",)),
    PageSpec("plot_milestones", "Territory and Missions", "Plot Milestones", "Plot Milestones", ("plot_milestones",)),
    PageSpec("plot_items", "Territory and Missions", "Plot Items", "Plot Items", ("plot_items",)),
    PageSpec("mission_tier_requirements", "Territory and Missions", "Mission Tier Requirements", "Mission Tier Requirements", ("mission_tier_requirements",)),
    PageSpec("congressional_support_inputs", "Territory and Missions", "Congressional Support Inputs", "Congressional Support Inputs", ("congressional_support_inputs",)),
    PageSpec("congressional_support_levels", "Territory and Missions", "Congressional Support Levels", "Congressional Support Levels", ("congressional_support_levels",)),
    PageSpec("authored_missions", "Territory and Missions", "Authored Missions", "Authored Missions", ("authored_missions",)),
    PageSpec("authored_mission_objectives", "Territory and Missions", "Mission Objectives", "Mission Objectives", ("authored_mission_objectives",)),
    PageSpec("effect_levels", "Personnel and Care", "Effect Levels", "Effect Levels",
             ("effect_levels",)),
    PageSpec("book_titles", "Personnel and Care", "Book Titles", "Book Titles",
             ("book_titles",)),
    PageSpec("equipment_families", "Equipment", "Equipment Families", "Equipment Families",
             ("equipment_families",)),
    PageSpec("equipment_models", "Equipment", "Equipment Models", "Equipment Models", ("equipment_models",)),
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

    @property
    def key_columns(self) -> tuple[str, ...]:
        """Composite keys are written as 'a+b'."""
        return tuple(self.key.split("+"))


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
    "equipment_families": TableSpec(
        "equipment_families", equipment_rules.FAMILIES_FILE, "family_id", (
            FieldSpec("family_id", "Family ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("ownership", "Ownership", kind="choice", choices=equipment_rules.OWNERSHIP),
            FieldSpec("per_task_limit", "Per-Task Limit (personal only)", required=False),
            FieldSpec("storage_kind", "Storage", kind="choice", choices=equipment_rules.STORAGE_KINDS),
            FieldSpec("connection_kind", "Connection", kind="choice", choices=equipment_rules.CONNECTION_KINDS),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "equipment_models": TableSpec(
        "equipment_models", equipment_rules.MODELS_FILE, "model_id", (
            FieldSpec("model_id", "Model ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("family_id", "Family", kind="ref", ref_table="equipment_families"),
            FieldSpec("phone_line_kind", "Phone Line Kind", kind="choice", required=False,
                      choices=("",) + equipment_rules.PHONE_LINE_KINDS),
            FieldSpec("network_tier_id", "Network Tier", kind="ref", required=False, ref_table="network_tiers"),
            FieldSpec("connection_override", "Connection Override", kind="choice", required=False,
                      choices=("",) + equipment_rules.CONNECTION_OVERRIDES),
            FieldSpec("generation_order", "Generation Order", kind="int"),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "care_services": TableSpec(
        "care_services", care_rules.CARE_FILE, "care_service_id", (
            FieldSpec("care_service_id", "Care Service ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("care_category", "Category", kind="choice", choices=care_rules.CARE_CATEGORIES),
            FieldSpec("recipient_assignment", "Patient Assignment", kind="choice",
                      choices=care_rules.RECIPIENT_ASSIGNMENTS),
            FieldSpec("provider_mode", "Provider", kind="choice", choices=care_rules.PROVIDER_MODES),
            FieldSpec("cost_policy", "Cost Policy", kind="choice", choices=care_rules.COST_POLICIES),
            FieldSpec("duration_minutes", "Duration (minutes, blank = undecided)", required=False),
            FieldSpec("follow_up_care_service_id", "Follow-Up Service", kind="ref", required=False,
                      ref_table="care_services"),
            FieldSpec("destination_feature_id", "Delivers Agent To", kind="ref", required=False,
                      ref_table="care_location_features"),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "care_location_features": TableSpec(
        "care_location_features", care_rules.FEATURES_FILE, "feature_id", (
            FieldSpec("feature_id", "Feature ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "care_service_locations": TableSpec(
        "care_service_locations", care_rules.LINKS_FILE, "care_service_id+feature_id", (
            FieldSpec("care_service_id", "Care Service", kind="ref", ref_table="care_services"),
            FieldSpec("feature_id", "Location Feature", kind="ref", ref_table="care_location_features"),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "condition_stats": TableSpec(
        "condition_stats", condition_rules.STATS_FILE, "stat_id", (
            FieldSpec("stat_id", "Stat ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("stat_category", "Category", kind="choice", choices=condition_rules.STAT_CATEGORIES),
            FieldSpec("minimum_value", "Minimum", kind="int"),
            FieldSpec("maximum_value", "Maximum (blank = undecided)", required=False),
            FieldSpec("default_value", "Default (blank = undecided)", required=False),
            FieldSpec("creation_rule", "Starting Value Rule", kind="choice", required=False,
                      choices=condition_rules.CREATION_RULES),
            FieldSpec("creation_source_stat_id", "Copy Starting Value From", kind="ref", required=False,
                      ref_table="condition_stats"),
            FieldSpec("direction", "Direction", kind="choice", choices=condition_rules.DIRECTIONS),
            FieldSpec("storage_model", "Storage", kind="choice", choices=condition_rules.STORAGE_MODELS),
            FieldSpec("derivation", "Derivation", kind="choice", required=False,
                      choices=condition_rules.DERIVATIONS),
            FieldSpec("contributes_to_health", "Counts Toward Health", kind="bool"),
            FieldSpec("health_formula", "Health Formula", kind="choice", required=False,
                      choices=condition_rules.HEALTH_FORMULAS),
            FieldSpec("health_reference_stat_id", "Health Reference Stat", kind="ref", required=False,
                      ref_table="condition_stats"),
            FieldSpec("player_visibility", "Visibility", kind="choice", choices=condition_rules.VISIBILITIES),
            FieldSpec("high_value_meaning", "High Value Means", required=False),
            FieldSpec("low_value_meaning", "Low Value Means", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "condition_bands": TableSpec(
        "condition_bands", condition_rules.BANDS_FILE, "band_id", (
            FieldSpec("band_id", "Band ID"),
            FieldSpec("stat_id", "Stat", kind="ref", ref_table="condition_stats"),
            FieldSpec("band_trigger", "Shown When", kind="choice", choices=condition_rules.BAND_TRIGGERS),
            FieldSpec("minimum_value", "Minimum (RANGE only)", kind="int", required=False),
            FieldSpec("maximum_value", "Maximum (RANGE only)", kind="int", required=False),
            FieldSpec("display_name", "Label"),
            FieldSpec("severity", "Severity", kind="choice", choices=condition_rules.SEVERITIES),
            FieldSpec("assignment_effect", "Assignment Effect", kind="choice",
                      choices=condition_rules.ASSIGNMENT_EFFECTS),
            FieldSpec("forced_off_duty", "Forced Off Duty", kind="bool"),
            FieldSpec("suggested_action", "Suggested Action", required=False),
            FieldSpec("suggested_care_service_id", "Suggested Care Service", kind="ref", required=False,
                      ref_table="care_services"),
            FieldSpec("foims_warning", "FOIMS Warning", required=False),
            FieldSpec("ui_color", "Colour (#RRGGBB)", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "personnel_traits": TableSpec(
        "personnel_traits", attribute_rules.TRAITS_FILE, "trait_id", (
            FieldSpec("trait_id", "Trait ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("trait_category", "Category", kind="choice", choices=attribute_rules.TRAIT_CATEGORIES),
            FieldSpec("minimum_value", "Minimum", kind="int"),
            FieldSpec("maximum_value", "Maximum", kind="int"),
            FieldSpec("default_value", "Default (DEFAULT rule only)", kind="int", required=False),
            FieldSpec("creation_rule", "Starting Value Rule", kind="choice",
                      choices=attribute_rules.CREATION_RULES),
            FieldSpec("can_change_over_time", "Can Change Over Time", kind="bool"),
            FieldSpec("contributes_to_health", "Counts Toward Health", kind="bool"),
            FieldSpec("health_formula", "Health Formula", kind="choice", required=False,
                      choices=attribute_rules.HEALTH_FORMULAS),
            FieldSpec("health_reference_id", "Health Reference", kind="ref", required=False,
                      ref_table="personnel_traits"),
            FieldSpec("primary_uses", "Primary Uses", required=False),
            FieldSpec("related_systems", "Related Systems", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "training_catalog": TableSpec(
        "training_catalog", attribute_rules.TRAINING_FILE, "training_id", (
            FieldSpec("training_id", "Training ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("training_category", "Category", kind="choice",
                      choices=attribute_rules.TRAINING_CATEGORIES),
            FieldSpec("eligible_at_creation", "Can Appear on New Hire Dossier", kind="bool"),
            FieldSpec("primary_uses", "Primary Uses", required=False),
            FieldSpec("related_systems", "Related Systems", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "effect_levels": TableSpec(
        "effect_levels", rc_rules.LEVELS_FILE, "scale_id+level_id", (
            FieldSpec("scale_id", "Scale", kind="choice", choices=rc_rules.SCALES),
            FieldSpec("level_id", "Level ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("value", "Value (blank = not set)", required=False),
            FieldSpec("unit", "Unit", kind="choice", choices=rc_rules.UNITS),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "book_titles": TableSpec(
        "book_titles", rc_rules.BOOKS_FILE, "book_id", (
            FieldSpec("book_id", "Book ID"),
            FieldSpec("title", "Title"),
            FieldSpec("author", "Author"),
            FieldSpec("notes", "Notes", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "sobriety_stages": TableSpec(
        "sobriety_stages", sobriety_rules.STAGES_FILE, "stage_id", (
            FieldSpec("stage_id", "Stage", kind="choice", choices=sobriety_rules.STAGE_IDS),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("min_intoxication", "Starts At (intoxication points)"),
            FieldSpec("skill_multiplier", "Skill Multiplier (blank if unconscious)", required=False),
            FieldSpec("can_drive", "Can Drive", kind="bool"),
            FieldSpec("unconscious", "Unconscious", kind="bool"),
            FieldSpec("driving_note", "Driving Note", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "sobriety_settings": TableSpec(
        "sobriety_settings", sobriety_rules.SETTINGS_FILE, "setting_id", (
            FieldSpec("setting_id", "Setting", kind="choice", choices=tuple(sobriety_rules.SETTING_UNITS)),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("value", "Value (decimal, up to 4 places)"),
            FieldSpec("unit", "Unit", kind="choice", choices=tuple(sobriety_rules.SETTING_UNITS.values())),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "sobriety_shift_rules": TableSpec(
        "sobriety_shift_rules", sobriety_rules.SHIFT_RULES_FILE, "rule_id", (
            FieldSpec("rule_id", "Rule ID"),
            FieldSpec("loyalty_min", "Loyalty From (0 to 100)"),
            FieldSpec("max_stage_id", "Most Intoxicated Arrival", kind="choice",
                      choices=sobriety_rules.STAGE_IDS[:-1]),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
        "greater_territories": TableSpec(
            "greater_territories", territory_rules.GREATER_TERRITORIES_FILE, "greater_territory_id", (
                FieldSpec("greater_territory_id", "Greater Territory ID"),
                FieldSpec("display_name", "Display Name"),
                FieldSpec("source_reference", "Source Reference", required=False),
                FieldSpec("description", "Description", required=False, multiline=True),
                FieldSpec("sort_order", "Sort Order", kind="int"),
                FieldSpec("active", "Active", kind="bool"),
            )),
        "greater_territory_tags": TableSpec(
            "greater_territory_tags", territory_rules.TAGS_FILE, "tag_id", (
                FieldSpec("tag_id", "Tag ID"),
                FieldSpec("category", "Category", kind="choice", choices=territory_rules.TAG_CATEGORIES),
                FieldSpec("display_name", "Display Name"),
                FieldSpec("source_reference", "Source Reference", required=False),
                FieldSpec("description", "Description", required=False, multiline=True),
                FieldSpec("sort_order", "Sort Order", kind="int"),
                FieldSpec("active", "Active", kind="bool"),
            )),
        "greater_territory_tag_links": TableSpec(
            "greater_territory_tag_links", territory_rules.TAG_LINKS_FILE, "link_id", (
                FieldSpec("link_id", "Link ID"),
                FieldSpec("greater_territory_id", "Greater Territory", kind="ref", ref_table="greater_territories"),
                FieldSpec("tag_id", "Tag", kind="ref", ref_table="greater_territory_tags"),
                FieldSpec("source_reference", "Source Reference", required=False),
                FieldSpec("sort_order", "Sort Order", kind="int"),
                FieldSpec("active", "Active", kind="bool"),
            )),
        "territories": TableSpec(
        "territories", territory_rules.TERRITORIES_FILE, "territory_id", (
            FieldSpec("territory_id", "Territory ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("locality", "Locality", required=False),
            FieldSpec("region", "Greater Territory", kind="ref", ref_table="greater_territories", required=False),
            FieldSpec("kind", "Kind", kind="choice", choices=territory_rules.KINDS),
            FieldSpec("hq_name", "HQ Name", required=False),
            FieldSpec("agents_allowed", "Agents Can Be Directed Here", kind="bool"),
            FieldSpec("population", "Population (whole number)", kind="int", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "territory_settings": TableSpec(
        "territory_settings", territory_rules.SETTINGS_FILE, "setting_id", (
            FieldSpec("setting_id", "Setting", kind="choice", choices=tuple(territory_rules.SETTING_UNITS)),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("value", "Value (blank = undecided)", required=False),
            FieldSpec("unit", "Unit", kind="choice", choices=tuple(dict.fromkeys(territory_rules.SETTING_UNITS.values()))),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "mission_tiers": TableSpec(
        "mission_tiers", territory_rules.TIERS_FILE, "tier_id", (
            FieldSpec("tier_id", "Tier ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("min_lifetime_admissible_evidence", "Starts At Lifetime Admissible Evidence (blank = undecided)", kind="int", required=False),
            FieldSpec("authored_content", "Authored End-Game Content", kind="bool"),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "map_formats": TableSpec(
        "map_formats", territory_rules.FORMATS_FILE, "format_id", (
            FieldSpec("format_id", "Format ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("role", "Role", kind="choice", choices=territory_rules.FORMAT_ROLES),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "maps": TableSpec(
        "maps", territory_rules.MAPS_FILE, "map_id", (
            FieldSpec("map_id", "Map ID"),
            FieldSpec("format_id", "Map Format", kind="ref", ref_table="map_formats"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("has_objective", "Has an Objective", kind="bool"),
            FieldSpec("agent_deployable", "Agents Can Be Deployed", kind="bool"),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "weapons": TableSpec(
        "weapons", weapon_rules.WEAPONS_FILE, "weapon_id", (
            FieldSpec("weapon_id", "Weapon ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("weapon_type", "Weapon Type", kind="choice", choices=weapon_rules.WEAPON_TYPES),
            FieldSpec("engine_class", "Engine Class (optional)", required=False),
            FieldSpec("tags", "Tags (separate with ;)", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "hostiles": TableSpec(
        "hostiles", hostile_rules.HOSTILES_FILE, "hostile_id", (
            FieldSpec("hostile_id", "Hostile ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("engine_class", "Engine Class (optional)", required=False),
            FieldSpec("weapon_id", "Weapon (optional)", kind="ref", ref_table="weapons", required=False),
            FieldSpec("tier_id", "Mission Tier (blank for authored-only)", kind="ref", ref_table="mission_tiers", required=False),
            FieldSpec("authored_only", "Authored Mission Areas Only", kind="bool"),
            FieldSpec("placeholder", "Placeholder (to be replaced)", kind="bool"),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "upgrades": TableSpec(
        "upgrades", progression_identity_rules.UPGRADES_FILE, "upgrade_id", (
            FieldSpec("upgrade_id", "Upgrade ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("track_id", "Department Track", kind="track_ref", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "plot_milestones": TableSpec(
        "plot_milestones", progression_identity_rules.MILESTONES_FILE, "milestone_id", (
            FieldSpec("milestone_id", "Milestone ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "plot_items": TableSpec(
        "plot_items", progression_identity_rules.ITEMS_FILE, "plot_item_id", (
            FieldSpec("plot_item_id", "Plot Item ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "mission_tier_requirements": TableSpec(
        "mission_tier_requirements", progression_identity_rules.REQUIREMENTS_FILE, "requirement_id", (
            FieldSpec("requirement_id", "Requirement ID"),
            FieldSpec("tier_id", "Target Mission Tier", kind="ref", ref_table="mission_tiers"),
            FieldSpec("upgrade_id", "Upgrade Acquired (choose ONE reference)", kind="ref", ref_table="upgrades", required=False),
            FieldSpec("milestone_id", "Milestone Completed", kind="ref", ref_table="plot_milestones", required=False),
            FieldSpec("plot_item_id", "Plot Item Held", kind="ref", ref_table="plot_items", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "congressional_support_inputs": TableSpec(
        "congressional_support_inputs", congressional_support_rules.INPUTS_FILE, "input_id", (
            FieldSpec("input_id", "Input ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("source_type", "Source", kind="choice", choices=congressional_support_rules.SOURCE_TYPES),
            FieldSpec("metric_id", "Metric ID (METRIC inputs only)", required=False),
            FieldSpec("scale", "Scale", kind="choice", choices=congressional_support_rules.SCALES),
            FieldSpec("floor_value", "Floor (score is 0 at or below; blank = undecided)", kind="int", required=False),
            FieldSpec("cap_value", "Cap (score is 100 at or above; blank = undecided)", kind="int", required=False),
            FieldSpec("weight", "Weight (whole number; blank = undecided)", kind="int", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "congressional_support_levels": TableSpec(
        "congressional_support_levels", congressional_support_rules.LEVELS_FILE, "level_id", (
            FieldSpec("level_id", "Level ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("min_score", "Minimum Combined Score 0-100 (blank = undecided)", kind="int", required=False),
            FieldSpec("grant_funding", "Recurring Budget Per Cycle While This Level Is Held (FUNDING_UNITS; blank = undecided)", kind="int", required=False),
            FieldSpec("grant_territories", "New Operational Territories On First Reaching This Level (permanent; blank = undecided)", kind="int", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "authored_missions": TableSpec(
        "authored_missions", authored_mission_rules.MISSIONS_FILE, "mission_id", (
            FieldSpec("mission_id", "Mission ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("kind", "Kind", kind="choice", choices=authored_mission_rules.KINDS),
            FieldSpec("chain_id", "Chain ID"),
            FieldSpec("chain_position", "Chain Position (1 = first)", kind="int"),
            FieldSpec("tier_id", "Mission Tier", kind="ref", ref_table="mission_tiers", required=False),
            FieldSpec("unlocks_tier_id", "Unlocks Tier (final mission only)", kind="ref", ref_table="mission_tiers", required=False),
            FieldSpec("territory_id", "Territory", kind="ref", ref_table="territories", required=False),
            FieldSpec("map_id", "Map (blank until authored)", kind="ref", ref_table="maps", required=False),
            FieldSpec("player_only", "Player Only", kind="bool"),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "authored_mission_objectives": TableSpec(
        "authored_mission_objectives", authored_mission_rules.OBJECTIVES_FILE, "objective_id", (
            FieldSpec("objective_id", "Objective ID"),
            FieldSpec("mission_id", "Mission", kind="ref", ref_table="authored_missions"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("required", "Required For Completion", kind="bool"),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "time_settings": TableSpec(
        "time_settings", time_rules.SETTINGS_FILE, "setting_id", (
            FieldSpec("setting_id", "Setting ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("category", "Category", kind="choice", choices=time_rules.CATEGORIES),
            FieldSpec("value", "Value (decimal, up to 4 places)"),
            FieldSpec("unit", "Unit", kind="choice", choices=time_rules.UNITS),
            FieldSpec("editable", "Editable", kind="bool"),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "personal_care_actions": TableSpec(
        "personal_care_actions", personal_care_rules.ACTIONS_FILE, "action_id", (
            FieldSpec("action_id", "Action ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("initiation", "Who Starts It", kind="choice", choices=personal_care_rules.INITIATIONS),
            FieldSpec("off_duty_required", "Requires Off Duty", kind="bool"),
            FieldSpec("follow_up_action_id", "Follow-Up Action", kind="ref", required=False,
                      ref_table="personal_care_actions"),
            FieldSpec("workbook_status", "Workbook Status", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "personal_care_features": TableSpec(
        "personal_care_features", personal_care_rules.FEATURES_FILE, "feature_id", (
            FieldSpec("feature_id", "Feature ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "personal_care_locations": TableSpec(
        "personal_care_locations", personal_care_rules.LOCATIONS_FILE, "action_id+feature_id", (
            FieldSpec("action_id", "Personal-Care Action", kind="ref", ref_table="personal_care_actions"),
            FieldSpec("feature_id", "Place Feature", kind="ref", ref_table="personal_care_features"),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "personal_care_place_types": TableSpec(
        "personal_care_place_types", personal_care_rules.PLACE_TYPES_FILE, "place_type_id", (
            FieldSpec("place_type_id", "Place Type ID"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("serves_as_home", "Serves as a Home", kind="bool"),
            FieldSpec("agent_owned", "Owned by an Agent", kind="bool"),
            FieldSpec("occupancy_rule", "Occupancy Limit", kind="choice",
                      choices=personal_care_rules.OCCUPANCY_RULES),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "personal_care_place_type_features": TableSpec(
        "personal_care_place_type_features", personal_care_rules.PLACE_TYPE_FEATURES_FILE,
        "place_type_id+feature_id", (
            FieldSpec("place_type_id", "Place Type", kind="ref", ref_table="personal_care_place_types"),
            FieldSpec("feature_id", "Offers Feature", kind="ref", ref_table="personal_care_features"),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "recreation_activities": TableSpec(
        "recreation_activities", personal_care_rules.ACTIVITIES_FILE, "activity_id", (
            FieldSpec("activity_id", "Activity ID"),
            FieldSpec("place_type_id", "Place Type", kind="ref", ref_table="personal_care_place_types"),
            FieldSpec("display_name", "Display Name"),
            FieldSpec("description", "Description", required=False, multiline=True),
            FieldSpec("duration_minutes", "Time Cost (minutes)", kind="int", required=False),
            FieldSpec("duration_label", "Duration Label (e.g. Overnight)", required=False),
            FieldSpec("company_options", "Company (ALONE; FRIENDS; STRANGERS)", required=False),
            FieldSpec("stress_reduction_per_tick", "Stress Reduction per Tick", required=False),
            FieldSpec("fatigue_cost_per_tick", "Fatigue Cost per Tick (energy used)", required=False),
            FieldSpec("energy_required_to_start", "Energy Required to Start (0-100)", required=False),
            FieldSpec("hunger_reduction_per_tick", "Hunger Reduction per Tick", required=False),
            FieldSpec("source_reference", "Source Reference", required=False),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "personal_care_during_care": TableSpec(
        "personal_care_during_care", personal_care_rules.DURING_CARE_FILE, "care_service_id+action_id", (
            FieldSpec("care_service_id", "Care Service", kind="ref", ref_table="care_services"),
            FieldSpec("action_id", "Provides Personal Care", kind="ref", ref_table="personal_care_actions"),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
    "personal_care_trainings": TableSpec(
        "personal_care_trainings", personal_care_rules.TRAININGS_FILE, "action_id+training_id", (
            FieldSpec("action_id", "Personal-Care Action", kind="ref", ref_table="personal_care_actions"),
            FieldSpec("training_id", "Training (do it anywhere)", kind="ref", ref_table="training_catalog"),
            FieldSpec("sort_order", "Sort Order", kind="int"),
            FieldSpec("active", "Active", kind="bool"),
        )),
}


import dataclasses as _dc

TABLE_METADATA["recreation_activities"] = _dc.replace(
    TABLE_METADATA["recreation_activities"],
    fields=TABLE_METADATA["recreation_activities"].fields + (
        FieldSpec("duration_step_minutes", "Duration Step (minutes, variable length)", kind="int", required=False),
        FieldSpec("duration_max_minutes", "Duration Maximum (minutes, variable length)", kind="int", required=False),
        FieldSpec("stress_reduction_level_id", "Stress Reduction Level", required=False),
        FieldSpec("fatigue_cost_level_id", "Fatigue Cost Level", required=False),
        FieldSpec("fatigue_cost_level_id_cafe", "Fatigue Cost Level (with cafe)", required=False),
        FieldSpec("hunger_restore_level_id", "Hunger Restore Level (on finish)", required=False),
        FieldSpec("hunger_restore_level_id_cafe", "Hunger Restore Level (with cafe)", required=False),
        FieldSpec("energy_restore_level_id", "Energy Restore Level (on finish)", required=False),
        FieldSpec("stress_gain_level_id", "Stress Gain Level (after delay)", required=False),
        FieldSpec("stress_gain_delay_min_minutes", "Stress Gain Delay Minimum (minutes)", kind="int",
                  required=False),
        FieldSpec("stress_gain_delay_max_minutes", "Stress Gain Delay Maximum (minutes)", kind="int",
                  required=False),
        FieldSpec("intoxication_gain_level_id", "Intoxication Gain Level (on finish)", required=False),
        FieldSpec("off_duty_only", "Off Duty Only", kind="bool", required=False),
        FieldSpec("hunger_loss_level_id", "Hunger Loss Level (on finish)", required=False),
    ))
TABLE_METADATA["personal_care_place_types"] = _dc.replace(
    TABLE_METADATA["personal_care_place_types"],
    fields=TABLE_METADATA["personal_care_place_types"].fields + (
        FieldSpec("cafe_possible", "Cafe Possible", kind="bool"),
    ))


PAGE_SUBGROUPS = {
    "care_services": "Medical Care",
    "care_location_features": "Medical Care",
    "care_service_locations": "Medical Care",
    "condition_stats": "Conditions",
    "condition_bands": "Conditions",
    "personnel_traits": "Traits and Training",
    "training_catalog": "Traits and Training",
    "personal_care_actions": "Personal Care Actions",
    "personal_care_trainings": "Personal Care Actions",
    "personal_care_during_care": "Personal Care Actions",
    "personal_care_features": "Places",
    "personal_care_locations": "Places",
    "personal_care_place_types": "Places",
    "personal_care_place_type_features": "Places",
    "recreation_activities": "Recreation",
    "effect_levels": "Recreation",
    "book_titles": "Recreation",
    "sobriety_stages": "Recreation",
    "sobriety_settings": "Recreation",
    "sobriety_shift_rules": "Recreation",
}
PAGES = tuple(_dc.replace(p, subgroup=PAGE_SUBGROUPS.get(p.page_id, "")) for p in PAGES)



PAGES += (
    PageSpec("resources", "Department", "Resources", "Resources", ("resources",)),
)
TABLE_METADATA["resources"] = TableSpec(
    "resources", resource_rules.RESOURCES_FILE, "resource_id", (
        FieldSpec("resource_id", "Resource ID"),
        FieldSpec("display_name", "Display Name"),
        FieldSpec("description", "Description", multiline=True),
        FieldSpec("resource_kind", "Resource Kind", kind="choice",
                  choices=resource_rules.RESOURCE_KINDS),
        FieldSpec("tracks_lifetime", "Tracks Lifetime", kind="bool"),
        FieldSpec("sort_order", "Sort Order", kind="int"),
        FieldSpec("active", "Active", kind="bool"),
    ),
)


PAGES += (
    PageSpec("task_template_flows", "Tasks", "Task Resource Flows",
             "Task Resource Flows", ("task_template_flows",)),
)
TABLE_METADATA["task_template_flows"] = TableSpec(
    "task_template_flows", task_flow_rules.FLOWS_FILE,
    "task_template_id+direction+resource_id", (
        FieldSpec("task_template_id", "Task Template", kind="task_ref"),
        FieldSpec("direction", "Direction", kind="choice",
                  choices=task_flow_rules.DIRECTIONS),
        FieldSpec("resource_id", "Resource", kind="ref", ref_table="resources"),
        FieldSpec("flow_mode", "Flow Mode", kind="choice",
                  choices=task_flow_rules.FLOW_MODES),
        FieldSpec("amount", "Amount (blank unconfigured)", kind="int", required=False),
        FieldSpec("weight", "Relative Weight (weighted outputs)", kind="int", required=False),
        FieldSpec("sort_order", "Sort Order", kind="int"),
        FieldSpec("active", "Active", kind="bool"),
    ),
)

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
    if TABLE_METADATA["task_template_flows"].columns != task_flow_rules.FLOW_COLUMNS:
        problems.append("task_template_flows metadata differs from validator")
    if TABLE_METADATA["resources"].columns != resource_rules.RESOURCE_COLUMNS:
        problems.append("resources metadata columns differ from validator")
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
    if TABLE_METADATA["equipment_families"].columns != equipment_rules.FAMILY_COLUMNS:
        problems.append("equipment_families metadata columns differ from validator")
    if TABLE_METADATA["equipment_models"].columns != equipment_rules.MODEL_COLUMNS:
        problems.append("equipment_models metadata columns differ from validator")
    if TABLE_METADATA["care_services"].columns != care_rules.CARE_COLUMNS:
        problems.append("care_services metadata columns differ from validator")
    if TABLE_METADATA["care_location_features"].columns != care_rules.FEATURE_COLUMNS:
        problems.append("care_location_features metadata columns differ from validator")
    if TABLE_METADATA["care_service_locations"].columns != care_rules.LINK_COLUMNS:
        problems.append("care_service_locations metadata columns differ from validator")
    if TABLE_METADATA["condition_stats"].columns != condition_rules.STAT_COLUMNS:
        problems.append("condition_stats metadata columns differ from validator")
    if TABLE_METADATA["condition_bands"].columns != condition_rules.BAND_COLUMNS:
        problems.append("condition_bands metadata columns differ from validator")
    if TABLE_METADATA["personnel_traits"].columns != attribute_rules.TRAIT_COLUMNS:
        problems.append("personnel_traits metadata columns differ from validator")
    if TABLE_METADATA["training_catalog"].columns != attribute_rules.TRAINING_COLUMNS:
        problems.append("training_catalog metadata columns differ from validator")
    for name, cols in (("personal_care_actions", personal_care_rules.ACTION_COLUMNS),
                       ("personal_care_features", personal_care_rules.FEATURE_COLUMNS),
                       ("personal_care_locations", personal_care_rules.LOCATION_COLUMNS),
                       ("personal_care_trainings", personal_care_rules.TRAINING_LINK_COLUMNS),
                       ("personal_care_place_types", personal_care_rules.PLACE_TYPE_COLUMNS),
                       ("personal_care_place_type_features", personal_care_rules.PLACE_TYPE_FEATURE_COLUMNS),
                       ("recreation_activities", personal_care_rules.ACTIVITY_COLUMNS),
                       ("personal_care_during_care", personal_care_rules.DURING_CARE_COLUMNS)):
        if TABLE_METADATA[name].columns != cols:
            problems.append(f"{name} metadata columns differ from validator")
    for name, cols in (("sobriety_stages", sobriety_rules.STAGE_COLUMNS),
                       ("sobriety_settings", sobriety_rules.SETTING_COLUMNS),
                       ("sobriety_shift_rules", sobriety_rules.SHIFT_COLUMNS)):
        if TABLE_METADATA[name].columns != cols:
            problems.append(f"{name} metadata columns differ from validator")
    for name, cols in (("territories", territory_rules.TERRITORY_COLUMNS),
                       ("territory_settings", territory_rules.SETTING_COLUMNS),
                       ("mission_tiers", territory_rules.TIER_COLUMNS),
                       ("map_formats", territory_rules.FORMAT_COLUMNS),
                       ("maps", territory_rules.MAP_COLUMNS),
                       ("weapons", weapon_rules.WEAPON_COLUMNS),
                       ("hostiles", hostile_rules.HOSTILE_COLUMNS),
                       ("upgrades", progression_identity_rules.UPGRADE_COLUMNS),
                       ("plot_milestones", progression_identity_rules.MILESTONE_COLUMNS),
                       ("plot_items", progression_identity_rules.ITEM_COLUMNS),
                       ("mission_tier_requirements", progression_identity_rules.REQUIREMENT_COLUMNS),
                       ("authored_missions", authored_mission_rules.MISSION_COLUMNS),
                       ("authored_mission_objectives", authored_mission_rules.OBJECTIVE_COLUMNS),
        ("greater_territories", territory_rules.GREATER_TERRITORY_COLUMNS),
        ("greater_territory_tags", territory_rules.TAG_COLUMNS),
        ("greater_territory_tag_links", territory_rules.TAG_LINK_COLUMNS),
        ("congressional_support_inputs", congressional_support_rules.INPUT_COLUMNS),
        ("congressional_support_levels", congressional_support_rules.LEVEL_COLUMNS)):
        if TABLE_METADATA[name].columns != cols:
            problems.append(f"{name} metadata columns differ from validator")
    if TABLE_METADATA["effect_levels"].columns != rc_rules.LEVEL_COLUMNS:
        problems.append("effect_levels metadata columns differ from validator")
    if TABLE_METADATA["book_titles"].columns != rc_rules.BOOK_COLUMNS:
        problems.append("book_titles metadata columns differ from validator")
    if TABLE_METADATA["time_settings"].columns != time_rules.SETTING_COLUMNS:
        problems.append("time_settings metadata columns differ from validator")
    for spec in TABLE_METADATA.values():
        for k in spec.key_columns:
            if k not in spec.columns:
                problems.append(f"{spec.table} key column {k} is not a field")
    return problems

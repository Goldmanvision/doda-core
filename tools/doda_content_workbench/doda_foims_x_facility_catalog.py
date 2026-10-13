"""Read-only facility catalog projection; no simulation mutations."""
from copy import deepcopy
import textwrap

def status(row):
    return "ACTIVE" if str(row.get("active", "false")).strip().lower() == "true" else "DRAFT"

def order(row, key):
    try:
        number = int(row.get("sort_order", ""))
    except (ValueError, TypeError):
        number = 999999
    return number, str(row.get(key, ""))

class FacilityCatalog:
    def __init__(self, tables):
        self.tables = deepcopy(tables)

    def facilities(self):
        return deepcopy(sorted(
            self.tables.get("facilities", []),
            key=lambda row: order(row, "facility_id")
        ))

    def describe(self, facility_id):
        matches = [r for r in self.facilities() if r.get("facility_id") == facility_id]
        if not matches:
            return ["Facility no longer present in catalog."]
        if len(matches) != 1:
            return ["Duplicate facility ID; run Workbench validation."]
        facility = matches[0]
        lines = [
            facility.get("display_name") or facility_id,
            "ID: " + facility_id,
            "Authoring status: " + status(facility),
            "CATALOG ONLY - not live construction/staffing state."
        ]
        for key, value in facility.items():
            if key not in ("facility_id", "display_name", "active", "sort_order"):
                lines.append(
                    key.replace("_", " ") + ": "
                    + (str(value).strip() or "UNCONFIGURED")
                )
        installations = sorted(
            [r for r in self.tables.get("facility_capabilities", [])
             if r.get("facility_id") == facility_id],
            key=lambda row: order(row, "capability_id")
        )
        lines += ["", "LINKED CAPABILITIES"]
        if not installations:
            lines.append("No capability links authored for this facility.")
        for link in installations:
            cid = link.get("capability_id", "")
            definitions = [
                r for r in self.tables.get("capabilities", [])
                if r.get("capability_id") == cid
            ]
            capability = definitions[0] if len(definitions) == 1 else {}
            name = (
                link.get("display_name_override")
                or capability.get("display_name") or cid
            )
            lines += [
                "", name + " / " + cid,
                "Link: " + status(link) + " | Definition: "
                + (status(capability) if capability else "MISSING OR DUPLICATE")
            ]
            for key, value in link.items():
                if key not in (
                    "facility_id", "capability_id", "display_name_override",
                    "active", "sort_order"
                ):
                    lines.append(
                        "Installation " + key.replace("_", " ") + ": "
                        + (str(value).strip() or "UNCONFIGURED")
                    )
            for key, value in capability.items():
                if key not in ("capability_id", "display_name", "active", "sort_order"):
                    lines.append(
                        "Capability " + key.replace("_", " ") + ": "
                        + (str(value).strip() or "UNCONFIGURED")
                    )
            baseline = [
                r for r in self.tables.get("capability_staffing_rules", [])
                if r.get("capability_id") == cid
            ]
            overrides = [
                r for r in self.tables.get("facility_capability_staffing_overrides", [])
                if r.get("facility_id") == facility_id
                and r.get("capability_id") == cid
            ]
            for title, rules in (
                ("GLOBAL STAFFING BASELINES", baseline),
                ("FACILITY-SPECIFIC OVERRIDES", overrides)
            ):
                lines.append(title)
                if not rules:
                    lines.append("None authored.")
                for rule in sorted(rules, key=lambda row: order(row, "qualification_id")):
                    qid = rule.get("qualification_id", "")
                    qualifications = [
                        r for r in self.tables.get("qualification_catalog", [])
                        if r.get("qualification_id") == qid
                    ]
                    qualification = qualifications[0] if len(qualifications) == 1 else {}
                    qname = qualification.get("display_name") or qid
                    counts = [
                        str(rule.get(key, "")).strip() or "?"
                        for key in (
                            "min_contributors", "preferred_contributors",
                            "max_contributors"
                        )
                    ]
                    lines.append(qname + " / " + qid + " [" + status(rule) + "]")
                    lines.append("Contributors min/preferred/max: " + "/".join(counts))
                    lines.append(
                        "Qualification: "
                        + (status(qualification) if qualification else "MISSING OR DUPLICATE")
                    )
        return lines

    def pages(self, facility_id, width=52, page_size=23):
        if width < 1 or page_size < 1:
            raise ValueError("page dimensions must be positive")
        wrapped = []
        for line in self.describe(facility_id):
            wrapped.extend(textwrap.wrap(line, width=width) or [""])
        return [
            wrapped[i:i + page_size]
            for i in range(0, len(wrapped), page_size)
        ] or [[]]

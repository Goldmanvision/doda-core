"""Read-only task and qualification catalog projections."""
from copy import deepcopy
from doda_foims_x_facility_catalog import FacilityCatalog, order, status

def fields(row, identity):
    lines = [
        row.get("display_name") or row.get(identity, ""),
        "ID: " + row.get(identity, ""),
        "Authoring status: " + status(row),
        "CATALOG ONLY - not live personnel or task state."
    ]
    for key, value in row.items():
        if key not in (identity, "display_name", "active", "sort_order"):
            lines.append(
                key.replace("_", " ") + ": "
                + (str(value).strip() or "UNCONFIGURED")
            )
    return lines

def unique(tables, table, key, value):
    rows = [r for r in tables.get(table, []) if r.get(key) == value]
    return rows[0] if len(rows) == 1 else None

def reference_label(tables, table, key, value):
    row = unique(tables, table, key, value)
    if row is None:
        return (value or "BLANK") + " [MISSING OR DUPLICATE]"
    return (row.get("display_name") or value) + " / " + value + " [" + status(row) + "]"

def staffing_line(row):
    counts = [
        str(row.get(k, "")).strip() or "?"
        for k in (
            "min_contributors", "preferred_contributors", "max_contributors"
        )
    ]
    return "Contributors min/preferred/max: " + "/".join(counts) + " [" + status(row) + "]"

class ReferenceCatalog(FacilityCatalog):
    table = ""
    identity = ""

    def facilities(self):
        rows = sorted(
            self.tables.get(self.table, []),
            key=lambda row: order(row, self.identity)
        )
        result = []
        for row in rows:
            item = deepcopy(row)
            item["facility_id"] = item.get(self.identity, "")
            result.append(item)
        return result

    def selected(self, identity):
        return unique(self.tables, self.table, self.identity, identity)

class TaskCatalog(ReferenceCatalog):
    table = "task_templates"
    identity = "task_template_id"

    def describe(self, identity):
        row = self.selected(identity)
        if row is None:
            return ["Task template missing or duplicated; run Workbench validation."]
        lines = fields(row, self.identity)
        lines += [
            "Tasks are work assignments; they have no deadlines.",
            "Auto-allocation belongs to department/personnel scheduling policy.",
            "", "CAPABILITY"
        ]
        cid = row.get("capability_id", "")
        lines.append(reference_label(
            self.tables, "capabilities", "capability_id", cid
        ))
        capability = unique(self.tables, "capabilities", "capability_id", cid)
        if capability:
            lines.append(capability.get("description") or "No capability description authored.")

        lines += ["", "QUALIFICATIONS VIA GLOBAL STAFFING RULES"]
        rules = sorted(
            [r for r in self.tables.get("capability_staffing_rules", [])
             if r.get("capability_id") == cid],
            key=lambda r: order(r, "qualification_id")
        )
        if not rules:
            lines.append("No staffing rules authored for this capability.")
        for rule in rules:
            qid = rule.get("qualification_id", "")
            lines.append(reference_label(
                self.tables, "qualification_catalog", "qualification_id", qid
            ))
            lines.append(staffing_line(rule))

        lines += ["", "AUTHORED FACILITY CAPABILITY LINKS"]
        links = sorted(
            [r for r in self.tables.get("facility_capabilities", [])
             if r.get("capability_id") == cid],
            key=lambda r: order(r, "facility_id")
        )
        if not links:
            lines.append("No facility links authored for this capability.")
        for link in links:
            fid = link.get("facility_id", "")
            lines.append(reference_label(
                self.tables, "facilities", "facility_id", fid
            ))
            lines.append("Capability link: " + status(link))
        lines.append("Links do not prove construction, staffing or task readiness.")
        return lines

class QualificationCatalog(ReferenceCatalog):
    table = "qualification_catalog"
    identity = "qualification_id"

    def describe(self, identity):
        row = self.selected(identity)
        if row is None:
            return ["Qualification missing or duplicated; run Workbench validation."]
        lines = fields(row, self.identity)
        lines += ["", "GLOBAL CAPABILITY STAFFING REFERENCES"]
        rules = sorted(
            [r for r in self.tables.get("capability_staffing_rules", [])
             if r.get("qualification_id") == identity],
            key=lambda r: order(r, "capability_id")
        )
        if not rules:
            lines.append("No global staffing references authored.")
        capability_ids = set()
        for rule in rules:
            cid = rule.get("capability_id", "")
            capability_ids.add(cid)
            lines.append(reference_label(
                self.tables, "capabilities", "capability_id", cid
            ))
            lines.append(staffing_line(rule))

        lines += ["", "FACILITY-SPECIFIC STAFFING OVERRIDES"]
        overrides = sorted(
            [r for r in self.tables.get("facility_capability_staffing_overrides", [])
             if r.get("qualification_id") == identity],
            key=lambda r: (r.get("facility_id", ""), order(r, "capability_id"))
        )
        if not overrides:
            lines.append("No facility-specific overrides authored.")
        for override in overrides:
            fid, cid = override.get("facility_id", ""), override.get("capability_id", "")
            capability_ids.add(cid)
            lines.append(reference_label(
                self.tables, "facilities", "facility_id", fid
            ))
            lines.append(reference_label(
                self.tables, "capabilities", "capability_id", cid
            ))
            lines.append(staffing_line(override))

        lines += ["", "RELATED TASKS VIA CAPABILITY STAFFING"]
        tasks = sorted(
            [r for r in self.tables.get("task_templates", [])
             if r.get("capability_id") in capability_ids],
            key=lambda r: order(r, "task_template_id")
        )
        if not tasks:
            lines.append("No related task templates authored.")
        for task in tasks:
            lines.append(
                (task.get("display_name") or task.get("task_template_id", ""))
                + " / " + task.get("task_template_id", "")
                + " [" + status(task) + "]"
            )
        lines.append("Indirect references are not a live eligibility check.")
        return lines

"""Projection of sandbox task instances for the FOIMS-X catalog browser."""
from datetime import timedelta
from doda_foims_x_facility_catalog import order
from doda_foims_x_reference_catalog import (
    ReferenceCatalog, reference_label, staffing_line
)
from doda_foims_x_sandbox import EPOCH

def stamp(minute):
    return (EPOCH + timedelta(minutes=minute)).strftime("%Y-%m-%d %H:%M")

class TasksCatalog(ReferenceCatalog):
    table = "sandbox_tasks"
    identity = "instance_id"

    def __init__(self, tables, board, now_fn):
        super().__init__(tables)
        board.tables = tables
        self.board = board
        self.now_fn = now_fn

    def _view(self):
        return self.board.view(self.now_fn())

    def facilities(self):
        return [
            {
                "facility_id": row["instance_id"],
                "instance_id": row["instance_id"],
                "display_name": row["instance_id"] + " " + row["state"],
                "active": "TRUE",
            }
            for row in self._view()
        ]

    def selected(self, identity):
        return next(
            (r for r in self._view() if r["instance_id"] == identity), None
        )

    def describe(self, identity):
        row = self.selected(identity)
        if row is None:
            return ["Task instance missing; spawn one from the Debug Panel."]
        remaining = row["remaining_minutes"]
        if row["state"] == "CANCELLED":
            timing = "Cancelled; deadline no longer applies."
        elif row["state"] == "OVERDUE":
            timing = "OVERDUE by %d strategic minutes" % (-remaining)
        else:
            timing = "Remaining: %d strategic minutes" % remaining
        lines = [
            row["display_name"],
            "ID: " + row["instance_id"],
            "State: " + row["state"],
            "SANDBOX ONLY - not authored data and not assigned.",
            "", "TIMING",
            "Created: minute %d (%s)" % (
                row["created_minute"], stamp(row["created_minute"])),
            "Deadline: minute %d (%s)" % (
                row["deadline_minute"], stamp(row["deadline_minute"])),
            timing,
            "Target effort: %d minutes (work effort, not completion time)"
            % row["target_effort_minutes"],
            "Overdue is flagged only; the task stays open.",
            "", "TEMPLATE",
            reference_label(
                self.tables, "task_templates", "task_template_id",
                row["template_id"]),
            "Priority: " + (row["priority"] or "UNCONFIGURED"),
            "", "CAPABILITY",
            reference_label(
                self.tables, "capabilities", "capability_id",
                row["capability_id"]),
            "", "QUALIFICATIONS VIA GLOBAL STAFFING RULES",
        ]
        rules = sorted(
            [r for r in self.tables.get("capability_staffing_rules", [])
             if r.get("capability_id") == row["capability_id"]],
            key=lambda r: order(r, "qualification_id")
        )
        if not rules:
            lines.append("No staffing rules authored for this capability.")
        for rule in rules:
            lines.append(reference_label(
                self.tables, "qualification_catalog", "qualification_id",
                rule.get("qualification_id", "")))
            lines.append(staffing_line(rule))
        return lines

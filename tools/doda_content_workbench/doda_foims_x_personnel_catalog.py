"""Projection of the sandbox roster for the FOIMS-X catalog browser."""
from doda_foims_x_facility_catalog import order, status
from doda_foims_x_reference_catalog import (
    ReferenceCatalog, reference_label, staffing_line
)
from doda_foims_x_roster import AVAILABLE

class PersonnelCatalog(ReferenceCatalog):
    table = "sandbox_roster"
    identity = "agent_id"

    def __init__(self, tables, roster):
        super().__init__(tables)
        roster.tables = tables
        self.roster = roster

    def facilities(self):
        rows = []
        for agent in self.roster.agents():
            marker = "AVAIL" if agent.availability == AVAILABLE else "OFF"
            rows.append({
                "facility_id": agent.agent_id,
                "agent_id": agent.agent_id,
                "display_name": agent.display_name + " / " + marker,
                "active": "TRUE",
            })
        return rows

    def selected(self, identity):
        return self.roster.get(identity)

    def describe(self, identity):
        agent = self.roster.get(identity)
        if agent is None:
            return ["Agent missing; reset the roster."]
        lines = [
            agent.display_name,
            "ID: " + agent.agent_id,
            "Availability: " + agent.availability,
            "SANDBOX ONLY - not authored data and not an assignment.",
            "", "QUALIFICATIONS",
        ]
        if not agent.qualifications:
            lines.append("None.")
        for qid in agent.qualifications:
            lines.append(reference_label(
                self.tables, "qualification_catalog", "qualification_id", qid
            ))
        issues = [i for i in self.roster.audit()
                  if i.startswith(agent.agent_id + ":")]
        if issues:
            lines += ["", "AUDIT"] + issues

        lines += ["", "STAFFING ROLES THIS AGENT MATCHES"]
        rules = sorted(
            [r for r in self.tables.get("capability_staffing_rules", [])
             if r.get("qualification_id") in agent.qualifications],
            key=lambda r: order(r, "capability_id")
        )
        capability_ids = set()
        if not rules:
            lines.append("No global staffing rules reference these qualifications.")
        for rule in rules:
            cid = rule.get("capability_id", "")
            capability_ids.add(cid)
            lines.append(reference_label(
                self.tables, "capabilities", "capability_id", cid
            ))
            lines.append(staffing_line(rule))

        lines += ["", "TASK TEMPLATES USING THOSE CAPABILITIES"]
        tasks = sorted(
            [r for r in self.tables.get("task_templates", [])
             if r.get("capability_id") in capability_ids],
            key=lambda r: order(r, "task_template_id")
        )
        if not tasks:
            lines.append("None authored.")
        for task in tasks:
            lines.append(
                (task.get("display_name") or task.get("task_template_id", ""))
                + " / " + task.get("task_template_id", "")
                + " [" + status(task) + "]"
            )
        lines.append("Matching a role is not an assignment or readiness check.")
        return lines

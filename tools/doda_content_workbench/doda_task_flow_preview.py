"""Read-only task resource-flow preview; no execution or balance writes."""
import argparse
import csv
from fractions import Fraction
from pathlib import Path


def build_preview(template, flows, resources):
    tid = template["task_template_id"]
    selected = [dict(r) for r in flows if r["taskTemplateId"] == tid]
    names = {r["resource_id"]: r.get("display_name", r["resource_id"]) for r in resources}
    active_weighted = [r for r in selected if r["active"] and r["direction"] == "OUT" and r["flowMode"] == "WEIGHTED"]
    weighted_ready = bool(active_weighted) and all(
        isinstance(r["weight"], int) and r["weight"] > 0 for r in active_weighted
    )
    total = sum(r["weight"] for r in active_weighted) if weighted_ready else 0
    for row in selected:
        row["resourceName"] = names.get(row["resourceId"], row["resourceId"])
        row["probability"] = (
            Fraction(row["weight"], total)
            if weighted_ready and row in active_weighted else None
        )
    return {"template": dict(template), "flows": selected,
            "runtimeImplemented": False, "activeWeightedTotal": total or None}


def render_preview(preview):
    template = preview["template"]
    lines = [template.get("display_name", template["task_template_id"]),
             "Template: " + template["task_template_id"],
             "Template active: " + template.get("active", "unknown"),
             "READ ONLY: no task execution, selection, or balance changes."]
    for field in ("priority", "target_type", "target_family_id", "loop_task",
                  "time_to_complete_minutes", "reward_mode", "payout_count"):
        lines.append(field + ": " + (template.get(field) or "not configured / not specified"))
    for title, predicate in (
        ("FIXED INPUTS", lambda r: r["direction"] == "IN"),
        ("FIXED OUTPUTS", lambda r: r["direction"] == "OUT" and r["flowMode"] == "FIXED"),
        ("WEIGHTED OUTPUT CHOICES", lambda r: r["direction"] == "OUT" and r["flowMode"] == "WEIGHTED"),
    ):
        lines.extend(["", title])
        group = [r for r in preview["flows"] if predicate(r)]
        if not group:
            lines.append("  No authored rows.")
        for row in group:
            amount = str(row["amount"]) if row["amount"] is not None else "UNCONFIGURED"
            state = "ACTIVE DEFINITION" if row["active"] else "INACTIVE DRAFT"
            text = f"  {row['resourceName']} [{row['resourceId']}]: amount={amount}; {state}"
            if row["flowMode"] == "WEIGHTED":
                weight = str(row["weight"]) if row["weight"] is not None else "UNCONFIGURED"
                p = row["probability"]
                chance = f"{p} ({float(p)*100:.2f}%)" if p is not None else "not calculated"
                text += f"; relative weight={weight}; active-choice share={chance}"
            lines.append(text)
    lines.extend(staffing_lines(preview))
    lines.extend(["", "Weighted amount is TOTAL units selected per credit event, not units for each choice.",
                  "One resource type is selected per unit. Inactive rows are excluded from active-choice shares.",
                  "Credit timing belongs to task execution. No timing or throughput is inferred here.",
                  "Shares describe configured active definitions only; this preview never draws outcomes."])
    return "\n".join(lines)



def attach_staffing(previews, rules):
    result = []
    for model in previews:
        item = dict(model)
        tid = model["template"]["task_template_id"]
        item["staffingRules"] = [
            dict(rule) for rule in rules if rule["taskTemplateId"] == tid
        ]
        result.append(item)
    return result


def staffing_lines(model):
    lines = ["", "TASK-SPECIFIC STAFFING"]
    if "staffingRules" not in model:
        lines.append("  Staffing was not loaded for this preview model.")
        return lines
    rules = model["staffingRules"]
    if not rules:
        lines.append("  No authored task-specific staffing rules.")
        lines.append("  This does not establish that no personnel are required.")
        return lines
    for rule in rules:
        minimum = rule["minContributors"]
        preferred = rule["preferredContributors"]
        maximum = rule["maxContributors"]
        state = "ACTIVE DEFINITION" if rule["active"] else "INACTIVE DRAFT"
        lines.append(
            "  " + rule["personnelRole"] +
            ": minimum=" + (str(minimum) if minimum is not None else "UNCONFIGURED") +
            "; preferred=" + (str(preferred) if preferred is not None else "UNSPECIFIED") +
            "; maximum=" + (str(maximum) if maximum is not None else "UNSPECIFIED") +
            "; " + state
        )
    lines.append("  An unspecified maximum is not confirmation of unlimited staffing.")
    lines.append("  These are authored role counts, not a live eligibility or allocation check.")
    lines.append("  Capability staffing, training, qualifications and equipment remain separate.")
    return lines


def load_previews(root):
    import doda_network_rules as net
    import doda_task_flow_rules as rules
    root = Path(root)
    result = net.Result()
    data = rules.validate_flows(root, result)
    if not result.valid:
        raise ValueError("\n".join(result.errors))
    source = root / "data_authoring/source"
    def read(name):
        with (source / name).open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    templates = read("task_templates.csv")
    resources = read("resources.csv")
    import doda_task_staffing_rules as staffing
    staffing_result = staffing.Result()
    staffing_data = staffing.validate_staffing(root, staffing_result)
    if not staffing_result.valid:
        raise ValueError("\n".join(staffing_result.errors))
    models = [build_preview(t, data["flows"], resources) for t in templates]
    models = attach_staffing(models, staffing_data["staffingRules"])
    return models, result.warnings + staffing_result.warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--template", help="Print one template instead of opening the window")
    args = parser.parse_args(argv)
    previews, warnings = load_previews(args.root)
    if args.template:
        matches = [p for p in previews if p["template"]["task_template_id"] == args.template]
        if not matches:
            parser.error("Unknown template ID: " + args.template)
        print(render_preview(matches[0]))
        return 0
    import tkinter as tk
    from tkinter import ttk
    app = tk.Tk()
    app.title("DoDA - Task Resource Flow Preview (Read Only)")
    app.geometry("1100x740")
    app.columnconfigure(0, weight=1)
    app.rowconfigure(1, weight=1)
    selector = ttk.Combobox(app, state="readonly", values=[
        p["template"]["task_template_id"] for p in previews])
    selector.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
    frame = ttk.Frame(app)
    frame.grid(row=1, column=0, sticky="nsew", padx=12)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    text = tk.Text(frame, wrap="word", font=("Consolas", 11))
    text.grid(row=0, column=0, sticky="nsew")
    scroll = ttk.Scrollbar(frame, command=text.yview)
    scroll.grid(row=0, column=1, sticky="ns")
    text.configure(yscrollcommand=scroll.set)
    def refresh(event=None):
        index = selector.current()
        if index < 0:
            return
        text.configure(state="normal")
        text.delete("1.0", "end")
        text.insert("1.0", render_preview(previews[index]))
        text.configure(state="disabled")
    selector.bind("<<ComboboxSelected>>", refresh)
    ttk.Label(app, text=f"Validated source snapshot: {len(previews)} templates; {len(warnings)} draft warnings. Close and reopen to refresh.").grid(row=2, column=0, sticky="w", padx=12, pady=12)
    if previews:
        selector.current(0)
        refresh()
    app.mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

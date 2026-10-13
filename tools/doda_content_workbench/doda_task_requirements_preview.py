"""Saved task staffing and prerequisite definitions; no live eligibility or writes."""
from copy import deepcopy
import hashlib
import re
from pathlib import Path
import doda_task_schema as schema
from doda_task_flow_preview import staffing_lines

FILES = ("task_templates.csv", "task_staffing_rules.csv", "task_prerequisites.csv")


def source_hashes(source):
    return {
        name: hashlib.sha256((source / name).read_bytes()).hexdigest()
        for name in FILES
    }


def build_preview(template, staffing, prerequisites):
    tid = template["task_template_id"]
    return {
        "template": deepcopy(template),
        "staffingRules": deepcopy([
            r for r in staffing if r["taskTemplateId"] == tid
        ]),
        "prerequisites": deepcopy([
            r for r in prerequisites if r["taskTemplateId"] == tid
        ]),
        "savedSourceOnly": True,
        "runtimeImplemented": False,
        "inventoryChecked": False,
        "eligibilityChecked": False,
        "allocationImplemented": False,
    }


def render_preview(model):
    template = model["template"]
    lines = [
        template.get("display_name") or template["task_template_id"],
        "Template: " + template["task_template_id"],
        "Template active: " + template["active"],
        "SAVED SOURCE ONLY - unsaved form/list changes are not included.",
        "READ ONLY - no live eligibility, inventory, assignment or execution checks.",
    ]
    for field in ("capability_id", "target_type", "target_family_id"):
        lines.append(
            field + ": " + (template.get(field) or "UNCONFIGURED / NOT SPECIFIED")
        )
    lines.extend(staffing_lines(model))

    for scope, title in (
        ("PER_ASSIGNED_AGENT", "PER-ASSIGNED-AGENT PREREQUISITES"),
        ("TASK", "TASK-WIDE PREREQUISITES"),
    ):
        lines.extend(["", title])
        rows = [r for r in model["prerequisites"] if r["scope"] == scope]
        if not rows:
            lines.append(
                "  No authored rows for this scope; absence is not confirmation of no requirements."
            )
        for row in rows:
            quantity = (
                "UNCONFIGURED" if row["minQuantity"] is None
                else str(row["minQuantity"])
            )
            state = "ACTIVE DEFINITION" if row["active"] else "INACTIVE DRAFT"
            lines.append(
                "  " + row["prerequisiteId"] + ": " + row["requirementKind"]
                + "; minimum=" + quantity + "; " + state
            )
            lines.append(
                "    scope=" + scope
                + "; role=" + (row["personnelRole"] or "NOT APPLICABLE")
                + "; value=" + (row["requirementValue"] or "GENERIC / NOT SPECIFIED")
            )
            lines.append("    Authored description: " + row["description"])

    lines.extend([
        "", "INTERPRETATION BOUNDARIES",
        "Per-agent minimum applies separately to EACH assigned agent; no total is calculated here.",
        "Task-wide minimum applies once to the task assignment, not once per agent.",
        "Applicable receptacle means a receptacle model matching the evidence category, not a collection device.",
        "Vehicle quantity is not team capacity. Vehicle capacity does not change task staffing limits.",
        "No vehicle type, owned quantity, equipment availability or multiple-vehicle policy is inferred.",
        "Inactive definitions are displayed as drafts, not executable requirements.",
        "Capability staffing, skills, training, qualifications and other task configuration remain separate.",
        "Definition validation is not proof that this task is configured or can run.",
    ])
    return "\n".join(lines)


def build_report(model, warnings):
    lines = [
        "=== SAVED TASK REQUIREMENTS REPORT ===",
        "Snapshot loaded when the preview opened; reopen to refresh.",
        "Unsaved drafts are excluded. No live eligibility or inventory checks.",
        "", render_preview(model),
        "", "SNAPSHOT DEFINITION WARNINGS (ALL LOADED TEMPLATES)",
    ]
    lines.extend("  " + warning for warning in warnings)
    if not warnings:
        lines.append("  None.")
    return "\n".join(lines) + "\n"


def copy_requirements_report(owner, model, warnings):
    report = build_report(model, warnings)
    owner.clipboard_clear()
    owner.clipboard_append(report)
    owner.update_idletasks()
    owner.log("Copied saved Task Requirements Preview: "
              + model["template"]["task_template_id"])
    return report


def load_previews(root):
    import doda_network_rules as net
    import doda_task_staffing_rules as staffing
    import doda_task_prerequisite_rules as prerequisites

    source = Path(root) / "data_authoring/source"
    before = source_hashes(source)
    result = net.Result()
    templates = staffing.read_rows(
        source / FILES[0], list(schema.COLUMNS), result
    )
    seen = set()
    for row in templates:
        tid = row["task_template_id"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", tid) or tid in seen:
            result.errors.append(
                "task_templates.csv: invalid or duplicate template ID " + tid
            )
        seen.add(tid)
        try:
            schema.boolean(row["active"])
        except ValueError:
            result.errors.append("task_templates.csv: invalid active field " + tid)

    staff = staffing.validate_staffing(Path(root), result)
    required = prerequisites.validate_prerequisites(Path(root), result)

    if before != source_hashes(source):
        raise ValueError(
            "Source changed while loading. Close and reopen the preview."
        )
    if not result.valid:
        raise ValueError("\n".join(result.errors))

    models = [
        build_preview(t, staff["staffingRules"], required["prerequisites"])
        for t in sorted(templates, key=lambda row: row["task_template_id"])
    ]
    return models, list(result.warnings)


def initial_index(models, template_id):
    if not template_id:
        return 0 if models else -1
    for index, model in enumerate(models):
        if model["template"]["task_template_id"] == template_id:
            return index
    raise ValueError("Template is not in saved source: " + template_id)


def open_task_requirements_preview(owner, template_id=None):
    import tkinter as tk
    from tkinter import ttk, messagebox

    try:
        models, warnings = load_previews(owner.project_root)
        index = initial_index(models, template_id)
    except Exception as error:
        owner.log("Task requirements preview blocked: " + str(error))
        messagebox.showerror(
            "Saved Task Requirements Preview", str(error), parent=owner
        )
        return None

    previous = getattr(owner, "task_requirements_preview_window", None)
    if previous is not None and previous.winfo_exists():
        previous.destroy()

    window = tk.Toplevel(owner)
    owner.task_requirements_preview_window = window
    window.title("DoDA - Saved Task Requirements Preview (Read Only)")
    window.geometry("1100x760")
    window.minsize(760, 500)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(2, weight=1)

    ttk.Label(
        window,
        text="SAVED SOURCE ONLY - unsaved drafts are excluded. Reopen to refresh.",
    ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 0))

    selector = ttk.Combobox(
        window, state="readonly",
        values=[m["template"]["task_template_id"] for m in models],
    )
    selector.grid(row=1, column=0, sticky="ew", padx=12, pady=12)

    frame = ttk.Frame(window)
    frame.grid(row=2, column=0, sticky="nsew", padx=12)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    text = tk.Text(
        frame, wrap="word", font=("Consolas", 11),
        background="#0d1117", foreground="#e6edf3", state="disabled",
    )
    text.grid(row=0, column=0, sticky="nsew")
    scroll = ttk.Scrollbar(frame, command=text.yview)
    scroll.grid(row=0, column=1, sticky="ns")
    text.configure(yscrollcommand=scroll.set)

    def refresh(event=None):
        selected = selector.current()
        if selected < 0:
            return
        text.configure(state="normal")
        text.delete("1.0", "end")
        text.insert("1.0", render_preview(models[selected]))
        text.configure(state="disabled")

    selector.bind("<<ComboboxSelected>>", refresh)
    ttk.Label(
        window,
        text=(
            str(len(models)) + " saved templates; " + str(len(warnings))
            + " definition warnings. Not full project validation or live task eligibility."
        ),
    ).grid(row=3, column=0, sticky="w", padx=12, pady=12)
    def copy_current():
        selected = selector.current()
        if selected < 0:
            messagebox.showwarning(
                "Saved Task Requirements Preview",
                "No saved template is selected.", parent=window,
            )
            return
        try:
            copy_requirements_report(owner, models[selected], warnings)
        except tk.TclError as error:
            owner.log("Task requirements report copy failed: " + str(error))
            messagebox.showerror(
                "Saved Task Requirements Preview",
                "Clipboard copy failed: " + str(error), parent=window,
            )

    actions = ttk.Frame(window)
    actions.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 12))
    ttk.Button(
        actions, text="Copy Requirements Report", command=copy_current,
    ).pack(side="left")
    ttk.Button(
        actions, text="Close", command=window.destroy,
    ).pack(side="right")
    window.bind("<Escape>", lambda event: window.destroy())

    if index >= 0:
        selector.current(index)
        refresh()

    owner.log(
        "Opened saved-source Task Requirements Preview"
        + (": " + template_id if template_id else ".")
    )
    return window

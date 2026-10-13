from __future__ import annotations

import doda_task_schema as task_schema
import csv
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from uuid import uuid4

from doda_content_workbench import TABLE_SPECS
from doda_row_selection import selection_display, set_form_state, require_single
from doda_task_requirements_preview import open_task_requirements_preview


FIELDS = (
    "task_template_id", "display_name", "description", "capability_id",
    "priority", "target_type", "target_family_id", "loop_task",
    "time_to_complete_minutes", "reward_mode", "payout_count", "sort_order", "active",
)
FILES = tuple(spec["filename"] for spec in TABLE_SPECS.values())
FILES = tuple(FILES) + ("equipment_families.csv",)
FILES = tuple(dict.fromkeys(tuple(FILES) + ("resources.csv", "task_template_flows.csv")))
FILES = tuple(dict.fromkeys(tuple(FILES) + ("task_staffing_rules.csv",)))
FILES = tuple(dict.fromkeys(tuple(FILES) + ("collection_receptacles.csv",)))
FILES = tuple(dict.fromkeys(tuple(FILES) + ("collection_device_types.csv", "collection_models.csv")))
FILES = tuple(dict.fromkeys(tuple(FILES) + ("evidence_type_instances.csv",)))
FILES = tuple(dict.fromkeys(tuple(FILES) + ("task_prerequisites.csv",)))
FILES = tuple(dict.fromkeys(tuple(FILES) + ("vehicle_types.csv",)))


class TaskTemplatesEditor:
    def __init__(self, app):
        self.app = app
        self.editing_id = None
        self.snapshot_hash = None
        self.loaded_rows = []
        self.dirty = False
        self.loaded_path = None
        self.status = tk.StringVar(master=app, value="Source not loaded.")
        self.vars = {
            field: tk.StringVar(master=app)
            for field in FIELDS
            if field != "description"
        }
        self.widgets = {}
        self.build()

    def source_path(self):
        return self.app.source_directory / "task_templates.csv"

    def backup_directory(self):
        return (
            self.app.project_root / "data_authoring"
            / "backups" / "task_templates"
        )

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def choices(self, field):
        if field == "capability_id":
            return [""] + sorted({r["capability_id"] for r in self.app.tables.get("capabilities", [])})
        if field == "priority":
            rows = [r for r in self.app.tables.get("enum_catalog", [])
                    if r.get("enum_group") == "TASK_PRIORITY" and r.get("active", "").upper() == "TRUE"]
            return [r["enum_value"] for r in sorted(rows, key=lambda r: int(r["sort_order"]))]
        if field == "target_type":
            return list(task_schema.TARGET_TYPES)
        if field == "reward_mode":
            return list(task_schema.REWARD_MODES)
        if field == "target_family_id":
            path = self.app.source_directory / "equipment_families.csv"
            if not path.is_file():
                return [""]
            with path.open(encoding="utf-8-sig", newline="") as handle:
                return [""] + sorted(r["family_id"] for r in csv.DictReader(handle)
                                     if r.get("ownership", "").upper() == "LOCATION")
        return []

    def build(self):
        tab = self.app.task_templates_tab
        for child in tab.winfo_children():
            child.destroy()
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)

        left = ttk.LabelFrame(tab, text="Task Templates", padding=8)
        right = ttk.LabelFrame(tab, text="Task Template Editor", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right.grid(row=0, column=1, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        right.columnconfigure(1, weight=1)

        columns = ("task_template_id", "display_name", "priority",
                   "target_type", "loop_task")
        self.tree = ttk.Treeview(
            left, columns=columns, show="headings", selectmode="extended"
        )
        for field, title in zip(
            columns, ("Template ID", "Name", "Priority", "Target", "Loop")
        ):
            self.tree.heading(field, text=title)
            self.tree.column(field, width=140, minwidth=60)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(left, command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(
            left, orient="horizontal", command=self.tree.xview
        )
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(
            yscrollcommand=vertical.set, xscrollcommand=horizontal.set
        )
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        labels = (
            "Template ID", "Display Name", "Description", "Capability",
            "Priority", "Target Type", "Station Family (optional draft)", "Loop Task",
            "Time To Complete (minutes; optional)", "Reward Mode", "Payout Count", "Sort Order", "Active",
        )
        for index, (field, label) in enumerate(zip(FIELDS, labels)):
            ttk.Label(right, text=label + ":").grid(
                row=index, column=0, sticky="nw", padx=(0, 8), pady=4
            )
            if field == "description":
                widget = tk.Text(
                    right, height=4, wrap="word",
                    background="#0d1117", foreground="#e6edf3",
                    insertbackground="#e6edf3"
                )
                self.description = widget
            elif field in {"capability_id", "priority", "target_type", "target_family_id", "reward_mode"}:
                widget = ttk.Combobox(
                    right, textvariable=self.vars[field], state="readonly"
                )
            elif field in {"active", "loop_task"}:
                widget = ttk.Checkbutton(
                    right, variable=self.vars[field],
                    onvalue="TRUE", offvalue="FALSE"
                )
            else:
                widget = ttk.Entry(right, textvariable=self.vars[field])
            widget.grid(row=index, column=1, sticky="ew", pady=4)
            self.widgets[field] = widget

        buttons = ttk.Frame(right)
        buttons.grid(row=len(FIELDS), column=0, columnspan=2, sticky="ew", pady=8)
        for index, (text, command) in enumerate((
            ("New Template", self.new),
            ("Apply to List", self.apply_record),
            ("Save to Source", self.save),
            ("Delete from List", self.remove),
            ("Revert Form", self.revert),
            ("Revert Draft", self.revert_source),
            ("Open Backups", self.open_backups),
            ("Preview Saved Requirements", lambda: open_task_requirements_preview(
                self.app, self.vars["task_template_id"].get().strip() or None)),
        )):
            ttk.Button(buttons, text=text, command=command).grid(
                row=index // 3, column=index % 3, padx=3, pady=3, sticky="ew"
            )

        ttk.Label(
            right,
            text=(
                "IDs are immutable. Blank completion time means open-ended. "
                "Drafts may retain unconfigured requirements. Active tasks "
                "require an active capability installation. Apply changes the draft; "
                "Save to Source validates "
                "the complete candidate project before replacing the CSV."
            ),
            wraplength=380, foreground="#9da7b3"
        ).grid(row=len(FIELDS) + 1, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Label(right, textvariable=self.status, wraplength=380,
                  foreground="#9da7b3").grid(
            row=len(FIELDS) + 2, column=0, columnspan=2, sticky="ew", pady=4
        )
        self.new()

    def update(self, force=False):
        path = self.source_path()
        if self.dirty and not force:
            if self.loaded_path is not None and path.resolve() != self.loaded_path:
                raise ValueError("Task Templates draft belongs to another project. Save or revert it before changing projects.")
            self._set_status("Unsaved Task Templates draft kept; source refresh skipped.")
            return
        before = self.digest(path)
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = [dict(row) for row in csv.DictReader(handle) if any(row.values())]
        if before != self.digest(path):
            raise ValueError("Task CSV changed during refresh. Refresh again.")
        choices = {field: self.choices(field) for field in (
            "capability_id", "priority", "target_type", "target_family_id", "reward_mode"
        )}
        for field, values in choices.items():
            self.widgets[field].configure(values=values)
        self.loaded_rows = rows
        self.snapshot_hash = before
        self.loaded_path = path.resolve()
        self.dirty = False
        self._render_draft()
        if self.editing_id and self.tree.exists(self.editing_id):
            self.tree.selection_set(self.editing_id)
            self.on_select()
        else:
            self.new()
        self._set_status(f"{len(rows)} templates loaded from source.")

    def new(self):
        self._multi_selection = False
        set_form_state(self, False)
        self.tree.selection_remove(*self.tree.selection())
        self.editing_id = None
        self.widgets["task_template_id"].configure(state="normal")
        for variable in self.vars.values():
            variable.set("")
        self.description.delete("1.0", "end")
        self.vars["priority"].set("NORMAL" if "NORMAL" in self.choices("priority") else "")
        self.vars["target_type"].set("TERRITORY")
        self.vars["reward_mode"].set("CONTINUOUS")
        self.vars["loop_task"].set("FALSE")
        self.vars["payout_count"].set("0")
        self.vars["active"].set("FALSE")
        self.vars["sort_order"].set(str(max(
            (int(r["sort_order"]) for r in self.loaded_rows), default=0
        ) + 1))

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            if getattr(self, "_multi_selection", False):
                self.new()
            return
        if len(selected) > 1:
            self._multi_selection = True
            self.editing_id = None
            selected_rows = [
                row for row in self.loaded_rows
                if row["task_template_id"] in selected
            ]
            set_form_state(self, False)
            for field, variable in self.vars.items():
                variable.set(selection_display(selected_rows, field))
            self.description.delete("1.0", "end")
            self.description.insert(
                "1.0", selection_display(selected_rows, "description")
            )
            set_form_state(self, True)
            return
        was_multiple = getattr(self, "_multi_selection", False)
        self._multi_selection = False
        set_form_state(self, False)
        if _event is not None and not was_multiple and selected[0] == self.editing_id:
            return
        row = next(
            (r for r in self.loaded_rows
             if r["task_template_id"] == selected[0]), None
        )
        if row is None:
            return
        self.editing_id = row["task_template_id"]
        for field, variable in self.vars.items():
            variable.set(row[field])
        self.description.delete("1.0", "end")
        self.description.insert("1.0", row["description"])
        self.widgets["task_template_id"].configure(state="disabled")

    def revert(self):
        if self.editing_id and self.tree.exists(self.editing_id):
            self.tree.selection_set(self.editing_id)
            self.on_select()
        else:
            self.new()

    def record(self):
        row = {field: var.get().strip() for field, var in self.vars.items()}
        row["description"] = self.description.get("1.0", "end").strip()
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", row["task_template_id"]):
            raise ValueError("Template ID must be uppercase letters/digits/underscores, starting with a letter.")
        problems = task_schema.errors(row, set(self.choices("priority")))
        if row["capability_id"] and row["capability_id"] not in self.choices("capability_id"):
            problems.append("unknown capability_id")
        if row["target_family_id"] not in self.choices("target_family_id"):
            problems.append("unknown LOCATION station family")
        if problems:
            raise ValueError("; ".join(problems))
        return row

    def candidate_valid(self, candidate):
        with tempfile.TemporaryDirectory(prefix="doda-task-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)
            for filename in FILES:
                shutil.copy2(
                    candidate if filename == "task_templates.csv"
                    else self.app.source_directory / filename,
                    destination / filename
                )
            done = subprocess.run(
                [sys.executable, str(self.app.validator_path),
                 "--root", str(root), "validate"],
                cwd=root, text=True, encoding="utf-8",
                errors="replace", capture_output=True
            )
            return done.returncode == 0, done.stdout + "\n" + done.stderr

    def commit(self, rows):
        path = self.source_path()
        if self.loaded_path is not None and path.resolve() != self.loaded_path:
            raise ValueError("Task Templates project changed. Draft retained; save blocked.")
        if self.snapshot_hash is None or self.digest(path) != self.snapshot_hash:
            raise ValueError("Task CSV changed externally. Draft retained. Revert Draft to reload before reapplying edits.")
        temporary = path.with_name(f".tasks-{uuid4().hex}.tmp.csv")
        try:
            with temporary.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(sorted(rows, key=lambda row: (int(row["sort_order"]), row["task_template_id"])))
            valid, output = self.candidate_valid(temporary)
            self.app.log(output)
            if not valid:
                raise ValueError("Candidate validation failed. Draft retained; CSV unchanged. See Activity Log.")
            if self.digest(path) != self.snapshot_hash:
                raise ValueError("Task CSV changed during validation. Draft retained; CSV unchanged.")
            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)
            backup = folder / ("task_templates_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".csv")
            shutil.copy2(path, backup)
            if self.digest(path) != self.snapshot_hash:
                raise ValueError("Task CSV changed while preparing the backup. Draft retained; save blocked.")
            os.replace(temporary, path)
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError as error:
                self.app.log(f"Task Templates temporary-file cleanup warning: {error}")
        self.snapshot_hash = self.digest(path)
        self.loaded_path = path.resolve()
        self.dirty = False
        self.app.log(f"Task Templates saved. Backup: {backup}")
        self._set_status("Task Templates saved to source.")
        self.app.refresh_all(False)
        messagebox.showinfo("Task Templates", f"Candidate validation passed.\nBackup: {backup}", parent=self.app)

    def save(self):
        if not self.dirty:
            self._set_status("No applied draft changes to save. Use Apply to List first.")
            return
        try:
            self.commit(self.loaded_rows)
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            self.app.log(f"Task Templates save blocked; draft retained: {error}")
            self._set_status("Save blocked; draft retained. See Activity Log.")
            messagebox.showerror("Task Templates", str(error), parent=self.app)

    def remove(self):
        if not require_single(self, "Delete from List", messagebox):
            return
        if not self.editing_id:
            messagebox.showwarning("Task Templates", "Select a template first.", parent=self.app)
            return
        key = self.editing_id
        if not messagebox.askyesno("Delete from Draft?", f"Remove '{key}' from the draft?\nSource changes only after Save to Source.",
                                 default=messagebox.NO, icon="warning", parent=self.app):
            return
        candidate = [dict(row) for row in self.loaded_rows if row["task_template_id"] != key]
        if len(candidate) == len(self.loaded_rows):
            self._set_status("Selected template is no longer present in the draft.")
            return
        try:
            self._validate_rows(candidate)
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            self.app.log(f"Task Templates delete blocked; draft retained: {error}")
            messagebox.showerror("Task Templates", str(error), parent=self.app)
            return
        self.loaded_rows = candidate
        self.dirty = True
        self.editing_id = None
        self._render_draft()
        self.new()
        self._set_status("Template removed from draft. UNSAVED CHANGES.")

    def _set_status(self, text):
        self.status.set(text)

    def _render_draft(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in sorted(self.loaded_rows, key=lambda r: (int(r["sort_order"]), r["task_template_id"])):
            self.tree.insert("", "end", iid=row["task_template_id"], values=tuple(row[field] for field in self.tree["columns"]))

    def _validate_rows(self, rows):
        with tempfile.TemporaryDirectory(prefix="doda-task-draft-") as folder:
            candidate = Path(folder) / "task_templates.csv"
            with candidate.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            valid, output = self.candidate_valid(candidate)
        self.app.log(output)
        if not valid:
            raise ValueError("Draft candidate validation failed; no draft rows changed. See Activity Log.")

    def apply_record(self):
        if not require_single(self, "Apply to List", messagebox):
            return
        try:
            row = self.record()
            key = row["task_template_id"]
            if self.editing_id and key != self.editing_id:
                raise ValueError("Template ID cannot change after creation.")
            if not self.editing_id and any(r["task_template_id"] == key for r in self.loaded_rows):
                raise ValueError("Template ID already exists.")
            candidate = [dict(r) for r in self.loaded_rows if r["task_template_id"] != key] + [row]
            self._validate_rows(candidate)
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            self.app.log(f"Task Templates Apply blocked; draft retained: {error}")
            messagebox.showerror("Task Templates", str(error), parent=self.app)
            return
        self.loaded_rows = candidate
        self.editing_id = key
        self.dirty = True
        self._render_draft()
        self.tree.selection_set(key)
        self.on_select()
        self._set_status("Template applied to draft. UNSAVED CHANGES.")

    def revert_source(self):
        if self.dirty and not messagebox.askyesno("Revert Task Templates Draft?", "Discard applied Task Templates draft changes and reload source?", parent=self.app):
            return
        try:
            self.update(force=True)
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            self.app.log(f"Task Templates reload failed; draft retained: {error}")
            messagebox.showerror("Task Templates", str(error), parent=self.app)

    def open_backups(self):
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_task_templates_editor(app):
    app.task_templates_editor = TaskTemplatesEditor(app)

from __future__ import annotations

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


FIELDS = (
    "task_template_id", "display_name", "description", "capability_id",
    "priority", "default_target_effort_minutes", "default_deadline_minutes",
    "auto_allocate", "sort_order", "active",
)
FILES = tuple(spec["filename"] for spec in TABLE_SPECS.values())


class TaskTemplatesEditor:
    def __init__(self, app):
        self.app = app
        self.editing_id = None
        self.snapshot_hash = None
        self.loaded_rows = []
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
            return sorted({
                row["capability_id"]
                for row in self.app.tables.get("capabilities", [])
                if row.get("active", "").upper() == "TRUE"
            })
        if field == "priority":
            rows = [
                row for row in self.app.tables.get("enum_catalog", [])
                if row.get("enum_group") == "TASK_PRIORITY"
                and row.get("active", "").upper() == "TRUE"
            ]
            return [
                row["enum_value"]
                for row in sorted(rows, key=lambda row: int(row["sort_order"]))
            ]
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
                   "default_target_effort_minutes", "default_deadline_minutes")
        self.tree = ttk.Treeview(
            left, columns=columns, show="headings", selectmode="browse"
        )
        for field, title in zip(
            columns, ("Template ID", "Name", "Priority", "Effort", "Deadline")
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
            "Priority", "Target Effort (minutes)", "Deadline (minutes)",
            "Auto Allocate", "Sort Order", "Active",
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
            elif field in {"capability_id", "priority"}:
                widget = ttk.Combobox(
                    right, textvariable=self.vars[field], state="readonly"
                )
            elif field in {"active", "auto_allocate"}:
                widget = ttk.Checkbutton(
                    right, variable=self.vars[field],
                    onvalue="TRUE", offvalue="FALSE"
                )
            else:
                widget = ttk.Entry(right, textvariable=self.vars[field])
            widget.grid(row=index, column=1, sticky="ew", pady=4)
            self.widgets[field] = widget

        buttons = ttk.Frame(right)
        buttons.grid(row=10, column=0, columnspan=2, sticky="ew", pady=8)
        for index, (text, command) in enumerate((
            ("New Template", self.new),
            ("Save Template", self.save),
            ("Remove Template", self.remove),
            ("Revert Form", self.revert),
            ("Open Backups", self.open_backups),
        )):
            ttk.Button(buttons, text=text, command=command).grid(
                row=index // 3, column=index % 3, padx=3, pady=3, sticky="ew"
            )

        ttk.Label(
            right,
            text=(
                "IDs are immutable after creation. Effort and deadline must "
                "each be positive; effort may exceed deadline. Active tasks "
                "require an active capability installation. Saves validate "
                "the complete candidate project before replacing the CSV."
            ),
            wraplength=380, foreground="#9da7b3"
        ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=8)
        self.new()

    def update(self):
        path = self.source_path()
        before = self.digest(path)
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = [
                dict(row) for row in csv.DictReader(handle)
                if any(row.values())
            ]
        if before != self.digest(path):
            raise ValueError("Task CSV changed during refresh. Refresh again.")
        self.loaded_rows = rows
        self.snapshot_hash = before
        for field in ("capability_id", "priority"):
            self.widgets[field].configure(values=self.choices(field))
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in sorted(rows, key=lambda r: (
            int(r["sort_order"]), r["task_template_id"]
        )):
            self.tree.insert(
                "", "end", iid=row["task_template_id"],
                values=tuple(row[field] for field in self.tree["columns"])
            )
        if self.editing_id and self.tree.exists(self.editing_id):
            self.tree.selection_set(self.editing_id)

    def new(self):
        self.tree.selection_remove(*self.tree.selection())
        self.editing_id = None
        self.widgets["task_template_id"].configure(state="normal")
        for variable in self.vars.values():
            variable.set("")
        self.description.delete("1.0", "end")
        for field in ("capability_id", "priority"):
            choices = self.choices(field)
            self.vars[field].set(
                "NORMAL" if field == "priority" and "NORMAL" in choices
                else choices[0] if choices else ""
            )
        self.vars["default_target_effort_minutes"].set("1")
        self.vars["default_deadline_minutes"].set("1")
        self.vars["sort_order"].set(str(max(
            (int(row["sort_order"]) for row in self.loaded_rows), default=0
        ) + 1))
        self.vars["auto_allocate"].set("TRUE")
        self.vars["active"].set("TRUE")

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
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
        for field in ("display_name", "description"):
            if not row[field]:
                raise ValueError(f"{field} is required.")
        for field in ("capability_id", "priority"):
            if row[field] not in self.choices(field):
                raise ValueError(f"Select a valid {field}.")
        for field in (
            "default_target_effort_minutes", "default_deadline_minutes",
            "sort_order",
        ):
            if int(row[field]) < 1:
                raise ValueError(f"{field} must be an integer of at least 1.")
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
        if self.snapshot_hash is None or self.digest(path) != self.snapshot_hash:
            raise ValueError("Task CSV changed externally. Refresh before saving.")
        temporary = path.with_name(f".tasks-{uuid4().hex}.tmp.csv")
        try:
            with temporary.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle, fieldnames=FIELDS, lineterminator="\n"
                )
                writer.writeheader()
                writer.writerows(sorted(rows, key=lambda row: (
                    int(row["sort_order"]), row["task_template_id"]
                )))
            valid, output = self.candidate_valid(temporary)
            self.app.log(output)
            if not valid:
                raise ValueError("Candidate validation failed. CSV unchanged; see Activity Log.")
            if self.digest(path) != self.snapshot_hash:
                raise ValueError("Task CSV changed during validation. CSV unchanged.")
            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)
            backup = folder / (
                "task_templates_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )
            shutil.copy2(path, backup)
            os.replace(temporary, path)
            self.app.log(f"Task Templates saved. Backup: {backup}")
            self.app.refresh_all(False)
            messagebox.showinfo(
                "Task Templates", f"Candidate validation passed.\nBackup: {backup}",
                parent=self.app
            )
        finally:
            if temporary.exists():
                temporary.unlink()

    def save(self):
        try:
            row = self.record()
            key = row["task_template_id"]
            if self.editing_id and key != self.editing_id:
                raise ValueError("Template ID cannot change after creation.")
            if not self.editing_id and any(
                r["task_template_id"] == key for r in self.loaded_rows
            ):
                raise ValueError("Template ID already exists.")
            rows = [
                dict(r) for r in self.loaded_rows
                if r["task_template_id"] != key
            ] + [row]
            self.commit(rows)
            self.editing_id = key
            self.tree.selection_set(key)
            self.on_select()
        except (OSError, ValueError) as error:
            messagebox.showerror("Task Templates", str(error), parent=self.app)

    def remove(self):
        if not self.editing_id:
            messagebox.showwarning(
                "Task Templates", "Select a template first.", parent=self.app
            )
            return
        key = self.editing_id
        if not messagebox.askyesno(
            "Remove Template?", f"Remove '{key}'?\nA CSV backup will be created.",
            default=messagebox.NO, icon="warning", parent=self.app
        ):
            return
        try:
            self.commit([
                dict(row) for row in self.loaded_rows
                if row["task_template_id"] != key
            ])
            self.new()
        except (OSError, ValueError) as error:
            messagebox.showerror("Task Templates", str(error), parent=self.app)

    def open_backups(self):
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_task_templates_editor(app):
    app.task_templates_editor = TaskTemplatesEditor(app)
from __future__ import annotations

import csv
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from uuid import uuid4

from doda_row_selection import MULTIPLE_VALUES, selection_display
from doda_task_templates_editor import FILES as VALIDATION_FILES

FIELDS = (
    "facility_id", "capability_id", "qualification_id", "min_contributors",
    "preferred_contributors", "max_contributors", "sort_order", "active",
)
IDENTITY = FIELDS[:3]
EDITABLE = FIELDS[3:]
FILES = tuple(VALIDATION_FILES)
ERRORS = (OSError, UnicodeError, csv.Error, ValueError)


def row_key(row):
    return row["facility_id"], row["capability_id"], row["qualification_id"]


def row_iid(row):
    return "::".join(row_key(row))


class FacilityCapabilityStaffingOverridesEditor:
    title = "Facility Staffing Overrides"

    def __init__(self, app):
        self.app = app
        self.editing_key = None
        self.loaded_rows = []
        self.loaded_path = None
        self.snapshot_hash = None
        self.dirty = False
        self.vars = {field: tk.StringVar(master=app) for field in FIELDS}
        self.status = tk.StringVar(master=app, value="Source not loaded.")
        self.widgets = {}
        self.installation_choice = tk.StringVar(master=app)
        self.baseline_text = tk.StringVar(master=app)
        self._loading = False
        self._session = ()
        self._original = []
        self._changes = {}
        self.build()
        for field in EDITABLE:
            self.vars[field].trace_add("write", lambda *_args, f=field: self.changed(f))
        self.widgets["active"].bind(
            "<<ComboboxSelected>>", lambda _event: self.changed("active")
        )

    def source_path(self):
        return self.app.source_directory / "facility_capability_staffing_overrides.csv"

    def backup_directory(self):
        return self.app.project_root / "data_authoring" / "backups" / "facility_capability_staffing_overrides"

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def rows(self):
        return [dict(row) for row in self.loaded_rows]

    def active_installations(self):
        facilities = {
            r["facility_id"] for r in self.app.tables.get("facilities", [])
            if r.get("facility_id") and r.get("active", "").upper() == "TRUE"
        }
        capabilities = {
            r["capability_id"] for r in self.app.tables.get("capabilities", [])
            if r.get("capability_id") and r.get("active", "").upper() == "TRUE"
        }
        return sorted({
            (r["facility_id"], r["capability_id"])
            for r in self.app.tables.get("facility_capabilities", [])
            if r.get("facility_id") in facilities
            and r.get("capability_id") in capabilities
            and r.get("active", "").upper() == "TRUE"
        })

    def global_rules(self):
        qualifications = {
            r["qualification_id"] for r in self.app.tables.get("qualification_catalog", [])
            if r.get("qualification_id") and r.get("active", "").upper() == "TRUE"
        }
        capabilities = {
            r["capability_id"] for r in self.app.tables.get("capabilities", [])
            if r.get("capability_id") and r.get("active", "").upper() == "TRUE"
        }
        return {
            (r["capability_id"], r["qualification_id"]): r
            for r in self.app.tables.get("capability_staffing_rules", [])
            if r.get("capability_id") in capabilities
            and r.get("qualification_id") in qualifications
            and r.get("active", "").upper() == "TRUE"
        }

    def choices(self, field):
        if field == "facility_id":
            return sorted({f for f, _c in self.active_installations()})
        if field == "capability_id":
            facility = self.vars["facility_id"].get()
            return sorted({c for f, c in self.active_installations() if f == facility})
        capability = self.vars["capability_id"].get()
        return sorted({q for c, q in self.global_rules() if c == capability})

    def build(self):
        tab = self.app.staffing_overrides_tab
        for child in tab.winfo_children():
            child.destroy()
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)
        left = ttk.LabelFrame(tab, text=self.title, padding=8)
        right = ttk.LabelFrame(tab, text="Staffing Override Editor", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right.grid(row=0, column=1, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        right.columnconfigure(1, weight=1)
        self.tree = ttk.Treeview(left, columns=FIELDS, show="headings", selectmode="extended")
        labels = ("Facility", "Capability", "Qualification", "Min", "Preferred", "Max", "Sort", "Active")
        for field, label in zip(FIELDS, labels):
            self.tree.heading(field, text=label)
            self.tree.column(field, width=165 if field in IDENTITY else 80, minwidth=50)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(left, command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(left, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        ttk.Label(right, text="Installation:").grid(row=0, column=0, sticky="w")
        self.installation_combo = ttk.Combobox(
            right, textvariable=self.installation_choice, state="readonly"
        )
        self.installation_combo.grid(row=0, column=1, sticky="ew", pady=4)
        self.installation_combo.bind("<<ComboboxSelected>>", self.on_installation_changed)
        for index, (field, label) in enumerate(zip(FIELDS, labels), 1):
            ttk.Label(right, text=label + ":").grid(row=index, column=0, sticky="w", pady=4)
            if field in ("facility_id", "capability_id"):
                widget = ttk.Combobox(right, textvariable=self.vars[field], state="disabled")
            elif field in ("qualification_id", "active"):
                widget = ttk.Combobox(right, textvariable=self.vars[field], state="readonly")
                if field == "active":
                    widget.configure(values=("TRUE", "FALSE"))
                else:
                    widget.bind("<<ComboboxSelected>>", lambda _e: self.refresh_reference())
            else:
                widget = ttk.Entry(right, textvariable=self.vars[field])
                widget.bind("<FocusIn>", lambda _e, f=field: self.select_placeholder(f))
                widget.bind("<ButtonRelease-1>", lambda _e, f=field: self.select_placeholder(f))
            widget.grid(row=index, column=1, sticky="ew", pady=4)
            self.widgets[field] = widget
        buttons = ttk.Frame(right)
        buttons.grid(row=len(FIELDS) + 1, column=0, columnspan=2, sticky="ew", pady=8)
        for index, (label, command) in enumerate((
            ("New Override", self.new), ("Apply to List", self.apply_record),
            ("Save to Source", self.save), ("Delete from List", self.remove),
            ("Revert Form", self.revert), ("Revert Draft", self.revert_source),
            ("Open Backups", self.open_backups),
        )):
            ttk.Button(buttons, text=label, command=command).grid(
                row=index // 3, column=index % 3, sticky="ew", padx=3, pady=3
            )
        ttk.Label(right, textvariable=self.baseline_text, wraplength=390).grid(
            row=len(FIELDS) + 2, column=0, columnspan=2, sticky="ew", pady=6
        )
        ttk.Label(
            right, wraplength=390,
            text="Identity is immutable. Overrides require an active installation and "
                 "active global rule. Global baseline is reference only. "
                 "Apply changes the draft; Save validates and writes source. "
                 "Validate/Export use saved source."
        ).grid(row=len(FIELDS) + 3, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(right, textvariable=self.status, wraplength=390).grid(
            row=len(FIELDS) + 4, column=0, columnspan=2, sticky="ew"
        )
        self.new()

    def _set_status(self, text):
        self.status.set(text)

    def _end_session(self):
        self._session = ()
        self._original = []
        self._changes = {}

    def changed(self, field):
        if self._loading or len(self._session) < 2 or field not in EDITABLE:
            return
        self._changes[field] = self.vars[field].get()
        self._set_status(
            f"{len(self._session)} rules selected; {len(self._changes)} edited field(s) ready for Apply."
        )

    def select_placeholder(self, field):
        if len(self._session) < 2 or field in self._changes:
            return

        def select():
            if (
                len(self._session) >= 2 and field not in self._changes
                and self.vars[field].get() == MULTIPLE_VALUES
            ):
                self.widgets[field].selection_range(0, "end")
                self.widgets[field].icursor("end")

        self.widgets[field].after_idle(select)

    def _render_draft(self):
        selected = tuple(self.tree.selection())
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in sorted(
            self.loaded_rows,
            key=lambda r: (r["facility_id"], r["capability_id"], int(r["sort_order"]), r["qualification_id"])
        ):
            self.tree.insert(
                "", "end", iid=row_iid(row), values=tuple(row[f] for f in FIELDS)
            )
        kept = [iid for iid in selected if self.tree.exists(iid)]
        if kept:
            self.tree.selection_set(*kept)

    def update(self, force=False):
        path = self.source_path()
        if self.dirty and not force:
            if self.loaded_path is not None and path.resolve() != self.loaded_path:
                raise ValueError("Facility Staffing Overrides draft belongs to another project. Save or revert first.")
            self._set_status("Unsaved Facility Staffing Overrides draft retained; refresh skipped.")
            return
        before = self.digest(path)
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(FIELDS):
                raise ValueError("Facility Staffing Overrides CSV header does not match the current schema.")
            rows = [dict(row) for row in reader if any(row.values())]
        self.validate_rows(rows)
        if before != self.digest(path):
            raise ValueError("Facility Staffing Overrides CSV changed during refresh; draft retained.")
        for field in IDENTITY:
            self.widgets[field].configure(values=self.choices(field))
        self._end_session()
        self.loaded_rows = rows
        self.loaded_path = path.resolve()
        self.snapshot_hash = before
        self.dirty = False
        self._render_draft()
        if self.tree.selection():
            self.on_select(force=True)
        else:
            self.new()
        self._set_status(f"{len(rows)} staffing rules loaded from source.")

    def _draft_new(self):
        self._end_session()
        self.editing_key = None
        self._loading = True
        try:
            self.tree.selection_remove(*self.tree.selection())
            for field in IDENTITY:
                values = self.choices(field)
                self.widgets[field].configure(state="readonly", values=values)
                self.vars[field].set(values[0] if values else "")
            defaults = dict(
                min_contributors="0", preferred_contributors="1",
                max_contributors="1", sort_order="1", active="TRUE"
            )
            capability = self.vars["capability_id"].get()
            defaults["sort_order"] = str(max(
                (int(r["sort_order"]) for r in self.loaded_rows
                 if r["capability_id"] == capability), default=0
            ) + 1)
            self.widgets["active"].configure(values=("TRUE", "FALSE"))
            for field in EDITABLE:
                self.vars[field].set(defaults[field])
        finally:
            self._loading = False

    def _draft_on_select(self, _event=None, force=False):
        selected = tuple(self.tree.selection())
        if not selected:
            was_multiple = len(self._session) > 1
            self._end_session()
            if was_multiple:
                self.new()
            return
        if not force and selected == self._session and self.loaded_rows == self._original:
            return
        by_id = {row_iid(row): row for row in self.loaded_rows}
        if len(selected) != len(set(selected)) or any(iid not in by_id for iid in selected):
            self._set_status("Selection no longer matches draft. Reselect rows.")
            return
        rows = [by_id[iid] for iid in selected]
        self._loading = True
        try:
            self._session = selected
            self._original = self.rows()
            self._changes = {}
            self.editing_key = row_key(rows[0]) if len(rows) == 1 else None
            for field in FIELDS:
                self.vars[field].set(selection_display(rows, field, show_common=True))
            for field in IDENTITY:
                self.widgets[field].configure(state="disabled")
            self.widgets["active"].configure(values=("TRUE", "FALSE"))
        finally:
            self._loading = False
        if len(rows) > 1:
            self._set_status(f"{len(rows)} rules selected. Untouched fields are preserved.")

    def revert(self):
        if self.tree.selection():
            self.on_select(force=True)
        else:
            self.new()

    def validate_rows(self, rows):
        installations = set(self.active_installations())
        rules = self.global_rules()
        seen = set()
        for row in rows:
            if set(row) != set(FIELDS) or any(not isinstance(row[f], str) for f in FIELDS):
                raise ValueError("Malformed override row.")
            if any(row[f].strip() == MULTIPLE_VALUES for f in FIELDS):
                raise ValueError("Mixed-value placeholder cannot be applied as data.")
            key = row_key(row)
            if key in seen:
                raise ValueError("Duplicate Facility + Capability + Qualification.")
            seen.add(key)
            if key[:2] not in installations:
                raise ValueError("Override requires an active Facility Capability installation.")
            if key[1:] not in rules:
                raise ValueError("Override qualification requires an active global staffing rule.")
            minimum, preferred, maximum = (int(row[f]) for f in FIELDS[3:6])
            if not 0 <= minimum <= preferred <= maximum:
                raise ValueError("Counts require 0 <= Min <= Preferred <= Max.")
            if int(row["sort_order"]) < 1:
                raise ValueError("Sort Order must be at least 1.")
            if row["active"] not in ("TRUE", "FALSE"):
                raise ValueError("Active must be TRUE or FALSE.")

    def write(self, path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(sorted(
                rows, key=lambda r: (r["facility_id"], r["capability_id"], int(r["sort_order"]), r["qualification_id"])
            ))

    def candidate_valid(self, candidate):
        with tempfile.TemporaryDirectory(prefix="doda-capability-staffing-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)
            for filename in FILES:
                shutil.copy2(
                    candidate if filename == "facility_capability_staffing_overrides.csv"
                    else self.app.source_directory / filename,
                    destination / filename
                )
            completed = subprocess.run(
                [sys.executable, str(self.app.validator_path), "--root", str(root), "validate"],
                cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True
            )
            return completed.returncode == 0, completed.stdout + "\n" + completed.stderr

    def _validate_rows(self, rows):
        self.validate_rows(rows)
        with tempfile.TemporaryDirectory(prefix="doda-capability-staffing-draft-") as temporary:
            candidate = Path(temporary) / "facility_capability_staffing_overrides.csv"
            self.write(candidate, rows)
            valid, output = self.candidate_valid(candidate)
        self.app.log(output)
        if not valid:
            raise ValueError("Candidate project validation failed. Draft and CSV unchanged; see Activity Log.")

    def _check_project(self):
        if self.loaded_path is None or self.source_path().resolve() != self.loaded_path:
            raise ValueError("Source project changed or is not loaded. Draft retained.")

    def apply_record(self):
        try:
            self._check_project()
            before = self.rows()
            selected = tuple(self.tree.selection())
            if len(selected) > 1:
                if selected != self._session or before != self._original:
                    raise ValueError("Draft or selection changed. Reselect before applying.")
                if not self._changes:
                    self._set_status("No deliberately edited fields. Draft unchanged.")
                    return False
                if any(field not in EDITABLE for field in self._changes):
                    raise ValueError("Identity cannot be batch-edited.")
                changes = {field: value.strip() for field, value in self._changes.items()}
                candidate = [
                    {**row, **changes} if row_iid(row) in selected else dict(row)
                    for row in before
                ]
            else:
                row = {field: self.vars[field].get().strip() for field in FIELDS}
                key = row_key(row)
                if self.editing_key is not None and key != self.editing_key:
                    raise ValueError("Facility + Capability + Qualification cannot change after creation.")
                if self.editing_key is None and any(row_key(r) == key for r in before):
                    raise ValueError("Facility + Capability + Qualification already exists.")
                if self.editing_key is not None and not any(row_key(r) == key for r in before):
                    raise ValueError("Selected rule is no longer in the draft.")
                candidate = [dict(r) for r in before if row_key(r) != key] + [row]
            self._validate_rows(candidate)
            self._check_project()
            if self.loaded_rows != before or tuple(self.tree.selection()) != selected:
                raise ValueError("Draft or selection changed during validation. Nothing applied.")
            self.loaded_rows = candidate
            self.dirty = True
            if len(selected) > 1:
                by_id = {row_iid(r): r for r in candidate}
                for iid in selected:
                    self.tree.item(iid, values=tuple(by_id[iid][f] for f in FIELDS))
            else:
                self._render_draft()
                self.tree.selection_set(row_iid(row))
            self.on_select(force=True)
            self._set_status("Applied to draft. UNSAVED CHANGES.")
            return True
        except ERRORS as error:
            self.blocked("Apply", error)
            return False

    def blocked(self, action, error):
        self.app.log(f"Facility Staffing Overrides {action} blocked; draft retained: {error}")
        self._set_status(f"{action} blocked: {str(error).splitlines()[0]}")
        messagebox.showerror(self.title, str(error), parent=self.app)

    def remove(self):
        selected = tuple(self.tree.selection())
        if len(selected) != 1 or self.editing_key is None:
            messagebox.showwarning(
                self.title, "Delete from List requires one selected existing rule.", parent=self.app
            )
            return
        if not messagebox.askyesno(
            self.title, "Delete selected rule from draft? Source changes only after Save to Source.",
            default=messagebox.NO, parent=self.app
        ):
            return
        try:
            self._check_project()
            before = self.rows()
            candidate = [r for r in before if row_iid(r) != selected[0]]
            if len(candidate) == len(before):
                raise ValueError("Selected rule is no longer in the draft.")
            self._validate_rows(candidate)
            self._check_project()
            if self.loaded_rows != before or tuple(self.tree.selection()) != selected:
                raise ValueError("Draft or selection changed during validation.")
            self.loaded_rows = candidate
            self.dirty = True
            self._render_draft()
            self.new()
            self._set_status("Rule deleted from draft. UNSAVED CHANGES.")
        except ERRORS as error:
            self.blocked("Delete", error)

    def commit(self, rows):
        self._check_project()
        path = self.source_path()
        expected = self.snapshot_hash
        if expected is None or self.digest(path) != expected:
            raise ValueError("CSV changed externally. Draft retained; Revert Draft before reapplying edits.")
        original = self.rows()
        candidate_rows = [dict(row) for row in rows]
        temporary = path.with_name(".capability-staffing-" + uuid4().hex + ".tmp.csv")
        try:
            self.validate_rows(candidate_rows)
            self.write(temporary, candidate_rows)
            valid, output = self.candidate_valid(temporary)
            self.app.log(output)
            if not valid:
                raise ValueError("Candidate project validation failed. Draft retained; CSV unchanged.")
            self._check_project()
            if self.loaded_rows != original or self.digest(path) != expected:
                raise ValueError("Draft or CSV changed during validation. Save blocked.")
            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)
            backup = folder / (
                "capability_staffing_rules_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".csv"
            )
            shutil.copy2(path, backup)
            if self.digest(backup) != expected or self.digest(path) != expected:
                raise ValueError("CSV changed while preparing backup. Save blocked.")
            self._check_project()
            os.replace(temporary, path)
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError as error:
                self.app.log(f"Facility Staffing Overrides temporary cleanup warning: {error}")
        self.snapshot_hash = self.digest(path)
        self.dirty = False
        self.app.log(f"Facility Staffing Overrides saved. Backup: {backup}")
        self._set_status("Facility Staffing Overrides saved to source.")
        self.app.refresh_all(False)
        messagebox.showinfo(
            self.title, f"Candidate validation passed.\nBackup: {backup}", parent=self.app
        )

    def save(self):
        if not self.dirty:
            self._set_status("No applied changes. Use Apply to List first.")
            return
        try:
            self.commit(self.loaded_rows)
        except ERRORS as error:
            self.blocked("Save", error)

    def revert_source(self):
        if self.dirty and not messagebox.askyesno(
            self.title, "Discard applied Facility Staffing Overrides draft changes and reload source?",
            default=messagebox.NO, parent=self.app
        ):
            return
        try:
            self.update(force=True)
        except ERRORS as error:
            self.blocked("Revert Draft", error)

    def open_backups(self):
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


    def new(self):
        self._draft_new()
        for field in ("facility_id", "capability_id"):
            self.widgets[field].configure(state="disabled")
        pair = (self.vars["facility_id"].get(), self.vars["capability_id"].get())
        self.installation_combo.configure(
            state="readonly", values=["::".join(p) for p in self.active_installations()]
        )
        self.installation_choice.set("::".join(pair) if all(pair) else "")
        self.vars["sort_order"].set(str(max(
            (int(r["sort_order"]) for r in self.loaded_rows
             if (r["facility_id"], r["capability_id"]) == pair), default=0
        ) + 1))
        self.refresh_reference()

    def on_installation_changed(self, _event=None):
        if self.editing_key is not None or self._session:
            return
        pairs = {"::".join(p): p for p in self.active_installations()}
        pair = pairs.get(self.installation_choice.get(), ("", ""))
        self._loading = True
        try:
            self.vars["facility_id"].set(pair[0])
            self.vars["capability_id"].set(pair[1])
            qualifications = self.choices("qualification_id")
            self.vars["qualification_id"].set(qualifications[0] if qualifications else "")
            self.vars["sort_order"].set(str(max(
                (int(r["sort_order"]) for r in self.loaded_rows
                 if (r["facility_id"], r["capability_id"]) == pair), default=0
            ) + 1))
        finally:
            self._loading = False
        self.refresh_reference()

    def on_select(self, _event=None, force=False):
        self._draft_on_select(_event, force)
        self.refresh_reference()

    def refresh_reference(self):
        selected = tuple(self.tree.selection())
        by_id = {row_iid(r): r for r in self.loaded_rows}
        rows = [by_id[iid] for iid in selected if iid in by_id]
        rules = self.global_rules()
        if rows:
            pairs = [(r["facility_id"], r["capability_id"]) for r in rows]
            value = "::".join(pairs[0]) if all(p == pairs[0] for p in pairs) else MULTIPLE_VALUES
            self.installation_choice.set(value)
            self.installation_combo.configure(state="disabled")
            baselines = [rules.get((r["capability_id"], r["qualification_id"])) for r in rows]
        else:
            self.installation_combo.configure(
                state="readonly", values=["::".join(p) for p in self.active_installations()]
            )
            self.widgets["qualification_id"].configure(
                state="readonly", values=self.choices("qualification_id")
            )
            baselines = [rules.get((
                self.vars["capability_id"].get(), self.vars["qualification_id"].get()
            ))]
        values = [
            tuple(rule.get(f, "") for f in ("min_contributors", "preferred_contributors", "max_contributors"))
            if rule is not None else None
            for rule in baselines
        ]
        if not values or any(value is None for value in values):
            text = "No active global staffing baseline is available."
        elif all(value == values[0] for value in values):
            minimum, preferred, maximum = values[0]
            text = f"Global baseline: Min {minimum}, Preferred {preferred}, Max {maximum}."
        else:
            text = "Multiple global baselines. Each selected override retains its own reference rule."
        self.baseline_text.set(text)


def install_facility_capability_staffing_overrides_editor(app):
    app.facility_capability_staffing_overrides_editor = FacilityCapabilityStaffingOverridesEditor(app)
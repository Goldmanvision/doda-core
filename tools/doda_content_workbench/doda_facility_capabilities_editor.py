from __future__ import annotations

import csv
import hashlib
import json
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
    "facility_id", "capability_id", "display_name_override",
    "max_concurrent_personnel", "initial_tier_id", "foims_panel_id",
    "sort_order", "active",
)
IDENTITY = FIELDS[:2]
EDITABLE = FIELDS[2:]
FILES = tuple(VALIDATION_FILES)
ERRORS = (OSError, UnicodeError, csv.Error, ValueError)


def row_key(row):
    return row["facility_id"], row["capability_id"]


def row_iid(row):
    # Do not split compound IDs on a delimiter that might occur in an ID.
    return json.dumps(row_key(row), separators=(",", ":"), ensure_ascii=True)


def sort_key(row):
    return row["facility_id"], int(row["sort_order"]), row["capability_id"]


class FacilityCapabilitiesEditor:
    title = "Facility Capabilities"

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
        self._loading = False
        self._session = ()
        self._original = []
        self._changes = {}
        self._validated_dependencies = {}
        self.build()
        for field in EDITABLE:
            self.vars[field].trace_add("write", lambda *_args, f=field: self.changed(f))
        self.vars["facility_id"].trace_add("write", lambda *_args: self.on_facility_changed())
        for field in ("initial_tier_id", "active"):
            self.widgets[field].bind(
                "<<ComboboxSelected>>", lambda _e, f=field: self.changed(f)
            )

    def source_path(self):
        return self.app.source_directory / "facility_capabilities.csv"

    def backup_directory(self):
        return self.app.project_root / "data_authoring" / "backups" / "facility_capabilities"

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def active_facility_rows(self):
        return sorted(
            (row for row in self.app.tables.get("facilities", [])
             if row.get("facility_id") and row.get("active", "").upper() == "TRUE"),
            key=lambda row: row["facility_id"],
        )

    def active_capability_rows(self):
        return sorted(
            (row for row in self.app.tables.get("capabilities", [])
             if row.get("capability_id") and row.get("active", "").upper() == "TRUE"),
            key=lambda row: (self.integer_or_default(row.get("sort_order"), 999999),
                             row["capability_id"]),
        )

    def facility_ids(self):
        return [row["facility_id"] for row in self.active_facility_rows()]

    def capability_ids(self):
        return [row["capability_id"] for row in self.active_capability_rows()]

    def facility_tiers(self):
        rows = [
            row for row in self.app.tables.get("enum_catalog", [])
            if row.get("enum_group") == "FACILITY_TIER" and row.get("enum_value")
            and row.get("active", "").upper() == "TRUE"
        ]
        return [row["enum_value"] for row in sorted(
            rows, key=lambda row: (self.integer_or_default(row.get("sort_order"), 999999),
                                  row["enum_value"])
        )]

    @staticmethod
    def integer_or_default(value, default):
        try:
            return int((value or "").strip())
        except ValueError:
            return default

    def build(self):
        tab = self.app.facility_capabilities_tab
        for child in tab.winfo_children():
            child.destroy()
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)
        left = ttk.LabelFrame(tab, text=self.title, padding=8)
        right = ttk.LabelFrame(tab, text="Facility Capability Editor", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right.grid(row=0, column=1, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        right.columnconfigure(1, weight=1)
        self.tree = ttk.Treeview(left, columns=FIELDS, show="headings", selectmode="extended")
        labels = (
            "Facility", "Capability", "Display Override", "Max Personnel",
            "Initial Tier", "FOIMS Panel ID", "Sort Order", "Active",
        )
        for field, label in zip(FIELDS, labels):
            self.tree.heading(field, text=label)
            self.tree.column(field, width=170 if field in IDENTITY else 125, minwidth=60)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(left, command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(left, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        for index, (field, label) in enumerate(zip(FIELDS, labels)):
            ttk.Label(right, text=label + ":").grid(row=index, column=0, sticky="nw", pady=4)
            if field in IDENTITY or field in ("initial_tier_id", "active"):
                widget = ttk.Combobox(right, textvariable=self.vars[field], state="readonly")
            else:
                widget = ttk.Entry(right, textvariable=self.vars[field])
                widget.bind("<FocusIn>", lambda _e, f=field: self.select_placeholder(f), add="+")
                widget.bind("<ButtonRelease-1>", lambda _e, f=field: self.select_placeholder(f), add="+")
            widget.grid(row=index, column=1, sticky="ew", pady=4)
            self.widgets[field] = widget
        self.facility_hint = ttk.Label(right, wraplength=390, foreground="#9da7b3")
        self.facility_hint.grid(row=len(FIELDS), column=0, columnspan=2, sticky="ew", pady=6)
        buttons = ttk.Frame(right)
        buttons.grid(row=len(FIELDS) + 1, column=0, columnspan=2, sticky="ew", pady=8)
        for index, (label, command) in enumerate((
            ("New Installation", self.new), ("Apply to List", self.apply_record),
            ("Save to Source", self.save), ("Delete from List", self.remove),
            ("Revert Form", self.revert), ("Revert Draft", self.revert_source),
            ("Open Backups", self.open_backups),
        )):
            ttk.Button(buttons, text=label, command=command).grid(
                row=index // 3, column=index % 3, sticky="ew", padx=3, pady=3
            )
        ttk.Label(
            right, wraplength=390,
            text="Facility + Capability are immutable after creation. Display Override is optional. "
                 "Apply changes only the draft; Save to Source validates and creates a backup. "
                 "Untouched fields are preserved when editing multiple rows.",
        ).grid(row=len(FIELDS) + 2, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Label(right, textvariable=self.status, wraplength=390).grid(
            row=len(FIELDS) + 3, column=0, columnspan=2, sticky="ew"
        )
        self.new()

    def refresh_choices(self):
        for field, choices in (
            ("facility_id", self.facility_ids()),
            ("capability_id", self.capability_ids()),
            ("initial_tier_id", self.facility_tiers()),
            ("active", ("TRUE", "FALSE")),
        ):
            self.widgets[field].configure(values=tuple(choices))

    def next_sort_order(self, facility_id):
        return max(
            (int(row["sort_order"]) for row in self.loaded_rows
             if row["facility_id"] == facility_id), default=0
        ) + 1

    def on_facility_changed(self):
        if self._loading:
            return
        if not self._session:
            self.vars["sort_order"].set(str(self.next_sort_order(self.vars["facility_id"].get())))
        self.update_facility_hint()

    def update_facility_hint(self):
        if len(self._session) > 1:
            text = "Multiple installations selected. Personnel limits are checked against each row's own facility."
        else:
            selected = self.vars["facility_id"].get()
            facility = next((r for r in self.active_facility_rows() if r["facility_id"] == selected), None)
            text = (
                f"{selected}: {facility.get('display_name', '')}\n"
                f"Personnel capacity: {facility.get('personnel_capacity', '')}."
                if facility else "Select an active Facility."
            )
        self.facility_hint.configure(text=text)

    def _set_status(self, text):
        self.status.set(text)

    def _end_session(self):
        self._session = ()
        self._original = []
        self._changes = {}
        self.editing_key = None

    def new(self):
        self._loading = True
        try:
            self._end_session()
            self.tree.selection_remove(*self.tree.selection())
            self.refresh_choices()
            facilities, capabilities, tiers = self.facility_ids(), self.capability_ids(), self.facility_tiers()
            defaults = {
                "facility_id": facilities[0] if facilities else "",
                "capability_id": capabilities[0] if capabilities else "",
                "display_name_override": "", "max_concurrent_personnel": "1",
                "initial_tier_id": "UNBUILT" if "UNBUILT" in tiers else (tiers[0] if tiers else ""),
                "foims_panel_id": "", "active": "TRUE",
            }
            defaults["sort_order"] = str(self.next_sort_order(defaults["facility_id"]))
            for field in FIELDS:
                self.vars[field].set(defaults[field])
            for field in IDENTITY:
                self.widgets[field].configure(state="readonly")
        finally:
            self._loading = False
        self.update_facility_hint()

    def rows(self):
        return [dict(row) for row in self.loaded_rows]

    def validate_rows(self, rows):
        facilities = {row["facility_id"]: row for row in self.active_facility_rows()}
        capabilities, tiers = set(self.capability_ids()), set(self.facility_tiers())
        seen = set()
        for row in rows:
            if set(row) != set(FIELDS) or any(not isinstance(row[f], str) for f in FIELDS):
                raise ValueError("Malformed Facility Capability row.")
            if any(row[f].strip() == MULTIPLE_VALUES for f in FIELDS):
                raise ValueError("Mixed-value placeholder cannot be applied as data.")
            key = row_key(row)
            if key in seen:
                raise ValueError("Duplicate Facility + Capability installation.")
            seen.add(key)
            facility = facilities.get(row["facility_id"])
            if facility is None:
                raise ValueError("Select a valid active Facility.")
            if row["capability_id"] not in capabilities:
                raise ValueError("Select a valid active Capability.")
            if row["initial_tier_id"] not in tiers:
                raise ValueError("Select a valid active Facility Tier.")
            if not row["foims_panel_id"].strip():
                raise ValueError("FOIMS Panel ID is required.")
            maximum = int(row["max_concurrent_personnel"])
            capacity = int(facility["personnel_capacity"])
            if maximum < 1:
                raise ValueError("Max Concurrent Personnel must be at least 1.")
            if maximum > capacity:
                raise ValueError(
                    f"{row['facility_id']}/{row['capability_id']}: Max Concurrent Personnel "
                    f"cannot exceed this Facility's capacity of {capacity}."
                )
            if int(row["sort_order"]) < 1:
                raise ValueError("Sort Order must be at least 1.")
            if row["active"] not in ("TRUE", "FALSE"):
                raise ValueError("Active must be TRUE or FALSE.")
        # Aggregate overcommit is intentionally not rejected here.

    def changed(self, field):
        if self._loading or len(self._session) < 2 or field not in EDITABLE:
            return
        self._changes[field] = self.vars[field].get()
        self._set_status(
            f"{len(self._session)} installations selected; {len(self._changes)} edited field(s) ready for Apply."
        )

    def select_placeholder(self, field):
        if len(self._session) < 2 or field in self._changes:
            return

        def select():
            if (len(self._session) > 1 and field not in self._changes
                    and self.vars[field].get() == MULTIPLE_VALUES):
                self.widgets[field].selection_range(0, "end")
                self.widgets[field].icursor("end")
        self.widgets[field].after_idle(select)

    def _render_draft(self):
        selected, focused = tuple(self.tree.selection()), self.tree.focus()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in sorted(self.loaded_rows, key=sort_key):
            self.tree.insert("", "end", iid=row_iid(row), values=tuple(row[f] for f in self.tree["columns"]))
        kept = [iid for iid in selected if self.tree.exists(iid)]
        if kept:
            self.tree.selection_set(*kept)
        if focused and self.tree.exists(focused):
            self.tree.focus(focused)

    def update(self, force=False):
        path = self.source_path()
        if self.dirty and not force:
            self._check_project()
            self._set_status("Unsaved Facility Capabilities draft retained; refresh skipped.")
            return
        before = self.digest(path)
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(FIELDS):
                raise ValueError("Facility Capabilities CSV header does not match the current schema.")
            rows = [dict(row) for row in reader if any(row.values())]
        self.validate_rows(rows)
        if before != self.digest(path):
            raise ValueError("Facility Capabilities CSV changed during refresh; draft retained.")
        self._end_session()
        self.loaded_rows = rows
        self.loaded_path = path.resolve()
        self.snapshot_hash = before
        self.dirty = False
        self._render_draft()
        self.refresh_choices()
        if self.tree.selection():
            self.on_select(force=True)
        else:
            self.new()
        self._set_status(f"{len(rows)} installations loaded from source.")

    def on_select(self, _event=None, force=False):
        selected = tuple(self.tree.selection())
        if not selected:
            if self._session:
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
            self.refresh_choices()
            for field in FIELDS:
                self.vars[field].set(selection_display(rows, field, show_common=True))
            for field in IDENTITY:
                self.widgets[field].configure(state="disabled")
        finally:
            self._loading = False
        self.update_facility_hint()
        self._set_status(
            f"{len(rows)} installation(s) selected. Untouched fields are preserved."
            + (" UNSAVED CHANGES." if self.dirty else "")
        )

    def revert(self):
        if self.tree.selection():
            self.on_select(force=True)
        else:
            self.new()

    def write(self, path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(sorted(rows, key=sort_key))

    def candidate_valid(self, candidate):
        self._validated_dependencies = {}
        dependencies = {}
        with tempfile.TemporaryDirectory(prefix="doda-facility-capabilities-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)
            for filename in FILES:
                source = candidate if filename == "facility_capabilities.csv" else self.app.source_directory / filename
                before = self.digest(source)
                shutil.copy2(source, destination / filename)
                if before != self.digest(source) or before != self.digest(destination / filename):
                    raise ValueError(f"Validation input changed during copy: {filename}")
                dependencies[source.resolve()] = before
            completed = subprocess.run(
                [sys.executable, str(self.app.validator_path), "--root", str(root), "validate"],
                cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True,
            )
            for source, expected in dependencies.items():
                if self.digest(source) != expected:
                    raise ValueError(f"Validation input changed during validation: {source.name}")
            self._validated_dependencies = {
                path: digest for path, digest in dependencies.items()
                if path != candidate.resolve()
            }
            return completed.returncode == 0, completed.stdout + "\n" + completed.stderr

    def _validate_rows(self, rows):
        self.validate_rows(rows)
        with tempfile.TemporaryDirectory(prefix="doda-facility-capabilities-draft-") as temporary:
            candidate = Path(temporary) / "facility_capabilities.csv"
            self.write(candidate, rows)
            valid, output = self.candidate_valid(candidate)
        self.app.log(output)
        if not valid:
            raise ValueError("Candidate project validation failed. Draft and CSV unchanged; see Activity Log.")

    def _check_project(self):
        if self.loaded_path is None or self.source_path().resolve() != self.loaded_path:
            raise ValueError("Source project changed or is not loaded. Draft retained.")

    def _check_session(self, before, selected):
        if selected and (selected != self._session or before != self._original):
            raise ValueError("Draft or selection changed. Reselect before applying.")
        if not selected and self._session:
            raise ValueError("Selection cleared. Start a new installation before applying.")

    def apply_record(self):
        try:
            self._check_project()
            before, selected = self.rows(), tuple(self.tree.selection())
            self._check_session(before, selected)
            if len(selected) > 1:
                if not self._changes:
                    self._set_status("No deliberately edited fields. Draft unchanged.")
                    return False
                if any(field not in EDITABLE for field in self._changes):
                    raise ValueError("Facility and Capability identity cannot be batch-edited.")
                changes = {field: value.strip() for field, value in self._changes.items()}
                candidate = [
                    {**row, **changes} if row_iid(row) in selected else dict(row)
                    for row in before
                ]
            else:
                row = {field: self.vars[field].get().strip() for field in FIELDS}
                key = row_key(row)
                if selected and self.editing_key is None:
                    raise ValueError("Reselect the installation before applying.")
                if self.editing_key is not None:
                    if key != self.editing_key:
                        raise ValueError("Facility + Capability cannot change after creation.")
                    if not any(row_key(r) == key for r in before):
                        raise ValueError("Selected installation is no longer in the draft.")
                    candidate = [row if row_key(r) == key else dict(r) for r in before]
                else:
                    if any(row_key(r) == key for r in before):
                        raise ValueError("This Facility + Capability installation already exists.")
                    candidate = before + [row]
            if candidate == before:
                self._set_status("No changed values. Draft unchanged.")
                return False
            self._validate_rows(candidate)
            self._check_project()
            if self.loaded_rows != before or tuple(self.tree.selection()) != selected:
                raise ValueError("Draft or selection changed during validation. Nothing applied.")
            self.loaded_rows = candidate
            self.dirty = True
            if len(selected) > 1:
                by_id = {row_iid(r): r for r in candidate}
                for iid in selected:
                    self.tree.item(iid, values=tuple(by_id[iid][f] for f in self.tree["columns"]))
            else:
                self._render_draft()
                self.tree.selection_set(row_iid(row))
                self.tree.focus(row_iid(row))
            self.on_select(force=True)
            self._set_status("Applied to draft. UNSAVED CHANGES.")
            return True
        except ERRORS as error:
            self.blocked("Apply", error)
            return False

    def blocked(self, action, error):
        self.app.log(f"Facility Capabilities {action} blocked; draft retained: {error}")
        self._set_status(f"{action} blocked: {str(error).splitlines()[0]}")
        messagebox.showerror(self.title, str(error), parent=self.app)

    def remove(self):
        selected = tuple(self.tree.selection())
        if len(selected) != 1 or self.editing_key is None:
            messagebox.showwarning(self.title, "Delete from List requires one selected existing installation.", parent=self.app)
            return False
        if not messagebox.askyesno(
            self.title, "Delete selected installation from draft? Source changes only after Save to Source.",
            default=messagebox.NO, parent=self.app,
        ):
            return False
        try:
            self._check_project()
            before = self.rows()
            self._check_session(before, selected)
            candidate = [r for r in before if row_iid(r) != selected[0]]
            if len(candidate) == len(before):
                raise ValueError("Selected installation is no longer in the draft.")
            self._validate_rows(candidate)
            self._check_project()
            if self.loaded_rows != before or tuple(self.tree.selection()) != selected:
                raise ValueError("Draft or selection changed during validation.")
            self.loaded_rows = candidate
            self.dirty = True
            self._render_draft()
            self.new()
            self._set_status("Installation deleted from draft. UNSAVED CHANGES.")
            return True
        except ERRORS as error:
            self.blocked("Delete", error)
            return False

    def commit(self, rows):
        self._check_project()
        path, expected = self.source_path(), self.snapshot_hash
        if expected is None or self.digest(path) != expected:
            raise ValueError("CSV changed externally. Draft retained; Revert Draft before reapplying edits.")
        original = self.rows()
        candidate_rows = [dict(row) for row in rows]
        temporary = path.with_name(".facility-capabilities-" + uuid4().hex + ".tmp.csv")
        try:
            self.validate_rows(candidate_rows)
            self.write(temporary, candidate_rows)
            candidate_hash = self.digest(temporary)
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
                "facility_capabilities_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".csv"
            )
            shutil.copy2(path, backup)
            if self.digest(backup) != expected or self.digest(path) != expected:
                raise ValueError("CSV changed while preparing backup. Save blocked.")
            self._check_project()
            if self.loaded_rows != original or self.digest(temporary) != candidate_hash:
                raise ValueError("Draft or candidate changed while preparing backup. Save blocked.")
            for source, dependency_hash in self._validated_dependencies.items():
                if self.digest(source) != dependency_hash:
                    raise ValueError(f"Validation dependency changed before save: {source.name}")
            os.replace(temporary, path)
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError as error:
                self.app.log(f"Facility Capabilities temporary cleanup warning: {error}")
        self.snapshot_hash = self.digest(path)
        self.dirty = False
        self.app.log(f"Facility Capabilities saved. Backup: {backup}")
        self._set_status("Facility Capabilities saved to source.")
        self.app.refresh_all(False)
        messagebox.showinfo(self.title, f"Candidate validation passed.\nBackup: {backup}", parent=self.app)

    def save(self):
        if not self.dirty:
            self._set_status("No applied changes. Use Apply to List first.")
            return False
        try:
            self.commit(self.loaded_rows)
            return True
        except ERRORS as error:
            self.blocked("Save", error)
            return False

    def revert_source(self):
        if self.dirty and not messagebox.askyesno(
            self.title, "Discard applied Facility Capabilities draft changes and reload source?",
            default=messagebox.NO, parent=self.app,
        ):
            return False
        try:
            self.update(force=True)
            return True
        except ERRORS as error:
            self.blocked("Revert Draft", error)
            return False

    def open_backups(self):
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_facility_capabilities_editor(app):
    app.facility_capabilities_editor = FacilityCapabilitiesEditor(app)

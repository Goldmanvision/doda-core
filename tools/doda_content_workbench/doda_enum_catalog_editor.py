from __future__ import annotations

import csv
import json
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

from doda_row_selection import MULTIPLE_VALUES, selection_display
from doda_task_templates_editor import FILES as VALIDATION_FILES

FIELDS = ("enum_group", "enum_value", "display_label", "description", "sort_order", "active")
IDENTITY = FIELDS[:2]
EDITABLE = FIELDS[2:]
FILES = tuple(VALIDATION_FILES)
ERRORS = (OSError, UnicodeError, csv.Error, ValueError)


def row_key(row):
    return row["enum_group"], row["enum_value"]


def row_iid(row):
    return json.dumps(row_key(row), separators=(",", ":"), ensure_ascii=True)


def sort_key(row):
    return row["enum_group"], int(row["sort_order"]), row["enum_value"]


def clean_value(field, value):
    if not isinstance(value, str):
        raise ValueError("Form values must be text.")
    return value if field == "description" else value.strip()


def display_values(row):
    return tuple(row[f] for f in (
        "enum_group", "enum_value", "display_label", "sort_order", "active"
    ))


class EnumCatalogEditor:
    title = "Enum Catalog"

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
        self._description_seen = ""
        self.catalog_group_filter = tk.StringVar(master=app, value="All Groups")
        self._visible_filter = "All Groups"
        self._new_form_values = {}
        self.build()
        for field in EDITABLE:
            self.vars[field].trace_add("write", lambda *_args, f=field: self.changed(f))
        self.vars["enum_group"].trace_add("write", lambda *_args: self.on_group_changed())
        self.widgets["active"].bind(
            "<<ComboboxSelected>>", lambda _event: self.changed("active")
        )

    def source_path(self):
        return self.app.source_directory / "enum_catalog.csv"

    def backup_directory(self):
        return self.app.project_root / "data_authoring" / "backups" / "enum_catalog"

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def build(self):
        self.tab = tab = ttk.Frame(self.app.notebook, padding=10)
        self.app.notebook.add(tab, text="Enum Catalog — Admin")
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)
        left = ttk.LabelFrame(tab, text=self.title, padding=8)
        right = ttk.LabelFrame(tab, text="Enum Catalog Editor", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right.grid(row=0, column=1, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        right.columnconfigure(1, weight=1)
        right.rowconfigure(3, weight=1)
        filters = ttk.Frame(left)
        filters.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(filters, text="Enum Group:").pack(side="left", padx=(0, 6))
        self.catalog_group_combo = ttk.Combobox(
            filters, textvariable=self.catalog_group_filter,
            values=("All Groups",), state="readonly", width=28,
        )
        self.catalog_group_combo.pack(side="left")
        self.catalog_group_combo.bind(
            "<<ComboboxSelected>>", self.on_catalog_group_filter_changed
        )
        columns = ("enum_group", "enum_value", "display_label", "sort_order", "active")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="extended")
        for field, label, width in (
            ("enum_group", "Enum Group", 170), ("enum_value", "Enum Value", 200),
            ("display_label", "Display Label", 230), ("sort_order", "Sort", 65),
            ("active", "Active", 75),
        ):
            self.tree.heading(field, text=label)
            self.tree.column(field, width=width, minwidth=60)
        self.tree.grid(row=1, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(left, command=self.tree.yview)
        vertical.grid(row=1, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(left, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=2, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        labels = ("Enum Group", "Enum Value", "Display Label", "Description", "Sort Order", "Active")
        for index, (field, label) in enumerate(zip(FIELDS, labels)):
            ttk.Label(right, text=label + ":").grid(row=index, column=0, sticky="nw", pady=4)
            if field == "description":
                widget = tk.Text(
                    right, height=7, wrap="word", background="#0d1117",
                    foreground="#e6edf3", insertbackground="#e6edf3",
                )
                self.description = widget
                widget.bind("<<Modified>>", self.description_modified)
                scrollbar = ttk.Scrollbar(right, command=widget.yview)
                scrollbar.grid(row=index, column=2, sticky="ns", pady=4)
                widget.configure(yscrollcommand=scrollbar.set)
            elif field in IDENTITY:
                widget = ttk.Combobox(right, textvariable=self.vars[field], state="normal")
            elif field == "active":
                widget = ttk.Combobox(
                    right, textvariable=self.vars[field], state="readonly",
                    values=("TRUE", "FALSE"),
                )
            else:
                widget = ttk.Entry(right, textvariable=self.vars[field])
            if field in EDITABLE and field != "active":
                widget.bind("<FocusIn>", lambda _e, f=field: self.select_placeholder(f), add="+")
                widget.bind("<ButtonRelease-1>", lambda _e, f=field: self.select_placeholder(f), add="+")
            widget.grid(row=index, column=1, sticky="nsew" if field == "description" else "ew", pady=4)
            self.widgets[field] = widget
        self.group_combo = self.widgets["enum_group"]
        self.value_combo = self.widgets["enum_value"]
        self.group_combo.bind("<<ComboboxSelected>>", self.refresh_value_choices)
        self.group_combo.bind("<FocusOut>", self.refresh_value_choices)
        buttons = ttk.Frame(right)
        buttons.grid(row=len(FIELDS), column=0, columnspan=3, sticky="ew", pady=8)
        for index, (label, command) in enumerate((
            ("New Enum Value", self.new), ("Apply to List", self.apply_record),
            ("Save to Source", self.save), ("Delete from List", self.remove),
            ("Revert Form", self.revert), ("Revert Draft", self.revert_source),
            ("Open Backups", self.open_backups),
        )):
            ttk.Button(buttons, text=label, command=command).grid(
                row=index // 3, column=index % 3, sticky="ew", padx=3, pady=3
            )
        ttk.Label(
            right, wraplength=390,
            text="Group + Value are immutable after creation. Label and Description are required. "
                 "Sort Order is a whole number of at least zero. Apply/Delete change only the draft. "
                 "Save validates authored dependencies and creates a backup. "
                 "Apply or Revert Form before changing the group filter.",
        ).grid(row=len(FIELDS) + 1, column=0, columnspan=3, sticky="ew", pady=8)
        ttk.Label(right, textvariable=self.status, wraplength=390).grid(
            row=len(FIELDS) + 2, column=0, columnspan=3, sticky="ew"
        )
        self.new()

    def refresh_choices(self):
        self.group_combo.configure(values=tuple(self.groups()))
        self.refresh_value_choices()
        self.widgets["active"].configure(values=("TRUE", "FALSE"))
        self.catalog_group_combo.configure(values=tuple(self.catalog_groups()))

    def groups(self):
        return sorted({row["enum_group"] for row in self.loaded_rows})

    def values_for_group(self, group):
        return [
            row["enum_value"] for row in sorted(self.loaded_rows, key=sort_key)
            if row["enum_group"] == group
        ]

    def refresh_value_choices(self, _event=None):
        self.value_combo.configure(values=tuple(self.values_for_group(self.vars["enum_group"].get())))

    def on_group_changed(self):
        if not self._loading:
            self.refresh_value_choices()

    def catalog_groups(self):
        return ["All Groups", *self.groups()]

    def visible_rows(self):
        group = self.catalog_group_filter.get()
        return [
            dict(row) for row in self.loaded_rows
            if group == "All Groups" or row["enum_group"] == group
        ]

    def refresh_catalog_group_filter(self):
        groups = self.catalog_groups()
        self.catalog_group_combo.configure(values=tuple(groups))
        if self.catalog_group_filter.get() not in groups:
            self.catalog_group_filter.set("All Groups")
        self._visible_filter = self.catalog_group_filter.get()

    def next_sort_order(self, group):
        return max(
            (int(row["sort_order"]) for row in self.loaded_rows if row["enum_group"] == group),
            default=-1,
        ) + 1

    def _has_pending_form(self):
        self.flush_description()
        current = {field: self.vars[field].get() for field in FIELDS}
        if not self._session:
            return current != self._new_form_values
        original = {row_iid(row): row for row in self._original}
        if any(iid not in original for iid in self._session):
            return True
        rows = [original[iid] for iid in self._session]
        return any(
            current[field] != selection_display(rows, field, show_common=True)
            for field in FIELDS
        )

    def on_catalog_group_filter_changed(self, _event=None):
        requested = self.catalog_group_filter.get()
        if requested == self._visible_filter:
            return True
        try:
            if requested not in self.catalog_groups():
                raise ValueError("Select an existing catalog group or All Groups.")
            if self._has_pending_form():
                raise ValueError("Apply to List or Revert Form before changing the group filter. Pending form retained.")
            self._render_draft()
            if self.tree.selection():
                self.on_select(force=True)
            else:
                self.new()
            return True
        except ERRORS as error:
            self.catalog_group_filter.set(self._visible_filter)
            self.blocked("Filter", error)
            return False

    def new(self):
        self._loading = True
        try:
            self._end_session()
            self.tree.selection_remove(*self.tree.selection())
            self.refresh_choices()
            groups = self.groups()
            selected = self.catalog_group_filter.get()
            group = selected if selected in groups else groups[0] if groups else ""
            for field in FIELDS:
                self.vars[field].set("")
            self.vars["enum_group"].set(group)
            self.vars["sort_order"].set(str(self.next_sort_order(group)))
            self.vars["active"].set("TRUE")
            for field in IDENTITY:
                self.widgets[field].configure(state="normal")
            self.refresh_value_choices()
            self._load_description()
            self._new_form_values = {field: self.vars[field].get() for field in FIELDS}
        finally:
            self._loading = False

    def validate_rows(self, rows):
        seen = set()
        for row in rows:
            if set(row) != set(FIELDS) or any(not isinstance(row[f], str) for f in FIELDS):
                raise ValueError("Malformed Enum Catalog row.")
            if any(row[f].strip() == MULTIPLE_VALUES for f in FIELDS):
                raise ValueError("Mixed-value placeholder cannot be applied as data.")
            key = row_key(row)
            for field in IDENTITY:
                if not re.fullmatch(r"[A-Z][A-Z0-9_]*", row[field]):
                    raise ValueError("Enum Group and Enum Value must start with an uppercase letter and use uppercase letters, digits, or underscores.")
            if key in seen:
                raise ValueError("Duplicate Enum Group + Enum Value pair.")
            seen.add(key)
            for field in ("display_label", "description"):
                if not row[field].strip():
                    raise ValueError(field.replace("_", " ").title() + " is required.")
            if int(row["sort_order"]) < 0:
                raise ValueError("Sort Order must be a whole number of at least zero.")
            if row["active"] not in ("TRUE", "FALSE"):
                raise ValueError("Active must be TRUE or FALSE.")

    def update(self, force=False):
        path = self.source_path()
        if self.dirty and not force:
            self._check_project()
            self._set_status("Unsaved Enum Catalog draft retained; refresh skipped.")
            return
        before = self.digest(path)
        if (
            not force and self.loaded_path == path.resolve()
            and self.snapshot_hash == before
        ):
            self.refresh_choices()
            return
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(FIELDS):
                raise ValueError("Enum Catalog CSV header does not match the current schema.")
            rows = [dict(row) for row in reader if any(row.values())]
        self.validate_rows(rows)
        if before != self.digest(path):
            raise ValueError("Enum Catalog CSV changed during refresh; draft retained.")
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
        self._set_status(f"{len(rows)} enum records loaded from source.")

    def _load_description(self):
        previous = self._loading
        self._loading = True
        try:
            self.description.delete("1.0", "end")
            self.description.insert("1.0", self.vars["description"].get())
            self._description_seen = self.description.get("1.0", "end-1c")
            self.description.edit_modified(False)
        finally:
            self._loading = previous

    def description_modified(self, _event=None):
        if not self.description.edit_modified():
            return
        self.description.edit_modified(False)
        self.flush_description()

    def flush_description(self):
        current = self.description.get("1.0", "end-1c")
        if not self._loading and current != self._description_seen:
            self.vars["description"].set(current)
            self.changed("description")
        self._description_seen = current

    def on_select(self, _event=None, force=False):
        selected = tuple(self.tree.selection())
        if not force and selected == self._session and self.loaded_rows == self._original:
            return
        self._draft_on_select(_event, force)
        self._load_description()
        self.refresh_choices()

    def apply_record(self):
        self.flush_description()
        return self._draft_apply_record()

    def select_placeholder(self, field):
        if len(self._session) < 2 or field in self._changes:
            return

        def select():
            if len(self._session) < 2 or field in self._changes:
                return
            value = (
                self.description.get("1.0", "end-1c")
                if field == "description" else self.vars[field].get()
            )
            if value != MULTIPLE_VALUES:
                return
            if field == "description":
                self.description.tag_add("sel", "1.0", "end-1c")
                self.description.mark_set("insert", "end-1c")
            else:
                self.widgets[field].selection_range(0, "end")
                self.widgets[field].icursor("end")
        self.widgets[field].after_idle(select)





    def _set_status(self, text):
        self.status.set(text)

    def _end_session(self):
        self._session = ()
        self._original = []
        self._changes = {}
        self.editing_key = None

    def rows(self):
        return [dict(row) for row in self.loaded_rows]

    def changed(self, field):
        if self._loading or len(self._session) < 2 or field not in EDITABLE:
            return
        self._changes[field] = self.vars[field].get()
        self._set_status(
            f"{len(self._session)} tracks selected; {len(self._changes)} edited field(s) ready for Apply."
        )

    def _render_draft(self):
        selected, focused = tuple(self.tree.selection()), self.tree.focus()
        self.refresh_catalog_group_filter()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in sorted(self.visible_rows(), key=sort_key):
            self.tree.insert("", "end", iid=row_iid(row), values=display_values(row))
        kept = [iid for iid in selected if self.tree.exists(iid)]
        if kept:
            self.tree.selection_set(*kept)
        if focused and self.tree.exists(focused):
            self.tree.focus(focused)

    def _draft_on_select(self, _event=None, force=False):
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

        self._set_status(
            f"{len(rows)} enum record(s) selected. Untouched fields are preserved."
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
            writer.writerows(rows)

    def candidate_valid(self, candidate):
        self._validated_dependencies = {}
        dependencies = {}
        with tempfile.TemporaryDirectory(prefix="doda-enum-catalog-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)
            for filename in FILES:
                source = candidate if filename == "enum_catalog.csv" else self.app.source_directory / filename
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
        with tempfile.TemporaryDirectory(prefix="doda-enum-catalog-draft-") as temporary:
            candidate = Path(temporary) / "enum_catalog.csv"
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
            raise ValueError("Selection cleared. Start a new enum value before applying.")

    def _draft_apply_record(self):
        try:
            self._check_project()
            before, selected = self.rows(), tuple(self.tree.selection())
            self._check_session(before, selected)
            if len(selected) > 1:
                if not self._changes:
                    self._set_status("No deliberately edited fields. Draft unchanged.")
                    return False
                if any(field not in EDITABLE for field in self._changes):
                    raise ValueError("Enum Group + Enum Value cannot be batch-edited.")
                changes = {field: clean_value(field, value) for field, value in self._changes.items()}
                candidate = [
                    {**row, **changes} if row_iid(row) in selected else dict(row)
                    for row in before
                ]
            else:
                row = {field: clean_value(field, self.vars[field].get()) for field in FIELDS}
                key = row_key(row)
                if selected and self.editing_key is None:
                    raise ValueError("Reselect the enum value before applying.")
                if self.editing_key is not None:
                    if key != self.editing_key:
                        raise ValueError("Enum Group + Enum Value cannot change after creation.")
                    if not any(row_key(r) == key for r in before):
                        raise ValueError("Selected enum value is no longer in the draft.")
                    candidate = [row if row_key(r) == key else dict(r) for r in before]
                else:
                    if any(row_key(r) == key for r in before):
                        raise ValueError("This Enum Group + Enum Value installation already exists.")
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
                    self.tree.item(iid, values=display_values(by_id[iid]))
            else:
                if self.catalog_group_filter.get() not in ("All Groups", row["enum_group"]):
                    self.catalog_group_filter.set(row["enum_group"])
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
        self.app.log(f"Enum Catalog {action} blocked; draft retained: {error}")
        self._set_status(f"{action} blocked: {str(error).splitlines()[0]}")
        messagebox.showerror(self.title, str(error), parent=self.app)

    def remove(self):
        selected = tuple(self.tree.selection())
        if len(selected) != 1 or self.editing_key is None:
            messagebox.showwarning(self.title, "Delete from List requires one selected existing facility.", parent=self.app)
            return False
        if not messagebox.askyesno(
            self.title, "Delete selected facility from draft? Source changes only after Save to Source.",
            default=messagebox.NO, parent=self.app,
        ):
            return False
        try:
            self._check_project()
            before = self.rows()
            self._check_session(before, selected)
            candidate = [r for r in before if row_iid(r) != selected[0]]
            if len(candidate) == len(before):
                raise ValueError("Selected enum value is no longer in the draft.")
            self._validate_rows(candidate)
            self._check_project()
            if self.loaded_rows != before or tuple(self.tree.selection()) != selected:
                raise ValueError("Draft or selection changed during validation.")
            self.loaded_rows = candidate
            self.dirty = True
            self._render_draft()
            self.new()
            self._set_status("Track deleted from draft. UNSAVED CHANGES.")
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
        temporary = path.with_name(".enum-catalog-" + uuid4().hex + ".tmp.csv")
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
                "enum_catalog_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".csv"
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
                self.app.log(f"Enum Catalog temporary cleanup warning: {error}")
        self.snapshot_hash = self.digest(path)
        self.dirty = False
        self.app.log(f"Enum Catalog saved. Backup: {backup}")
        self._set_status("Enum Catalog saved to source.")
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
            self.title, "Discard applied Enum Catalog draft changes and reload source?",
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


def install_enum_catalog_editor(app):
    editor = EnumCatalogEditor(app)
    app.enum_catalog_editor = editor
    app.update_enum_catalog = editor.update
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

from doda_row_selection import MULTIPLE_VALUES, selection_display
from doda_task_templates_editor import FILES as VALIDATION_FILES

FIELDS = ("flavor_text_id", "category", "title", "body", "active")
IDENTITY = FIELDS[:1]
EDITABLE = FIELDS[1:]
FILES = tuple(VALIDATION_FILES)
ERRORS = (OSError, UnicodeError, csv.Error, ValueError)


def row_key(row):
    return row["flavor_text_id"]


def row_iid(row):
    return row_key(row)


def sort_key(row):
    return row["category"], row["flavor_text_id"]


def clean_value(field, value):
    if not isinstance(value, str):
        raise ValueError("Form values must be text.")
    return value if field == "body" else value.strip()


def display_values(row):
    title = " ".join(row["title"].split())
    if len(title) > 70:
        title = title[:67] + "..."
    return row["flavor_text_id"], row["category"], title, row["active"]


class FlavorTextEditor:
    title = "Flavor Text"

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
        self._body_seen = ""
        self.build()
        for field in EDITABLE:
            self.vars[field].trace_add("write", lambda *_args, f=field: self.changed(f))
        for field in ("category", "active"):
            self.widgets[field].bind(
                "<<ComboboxSelected>>", lambda _event, f=field: self.changed(f)
            )

    def source_path(self):
        return self.app.source_directory / "flavor_text.csv"

    def backup_directory(self):
        return self.app.project_root / "data_authoring" / "backups" / "flavor_text"

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def build(self):
        tab = self.app.flavor_tab
        for child in tab.winfo_children():
            child.destroy()
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)
        left = ttk.LabelFrame(tab, text=self.title, padding=8)
        right = ttk.LabelFrame(tab, text="Flavor Text Editor", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right.grid(row=0, column=1, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        right.columnconfigure(1, weight=1)
        right.rowconfigure(3, weight=1)
        columns = ("flavor_text_id", "category", "title", "active")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="extended")
        for field, label, width in (
            ("flavor_text_id", "Flavor Text ID", 260), ("category", "Category", 130),
            ("title", "Title", 280), ("active", "Active", 80),
        ):
            self.tree.heading(field, text=label)
            self.tree.column(field, width=width, minwidth=60)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(left, command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(left, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        labels = ("Flavor Text ID", "Category", "Title", "Body", "Active")
        for index, (field, label) in enumerate(zip(FIELDS, labels)):
            ttk.Label(right, text=label + ":").grid(row=index, column=0, sticky="nw", pady=4)
            if field == "body":
                widget = tk.Text(
                    right, height=12, wrap="word", background="#0d1117",
                    foreground="#e6edf3", insertbackground="#e6edf3",
                )
                self.body = widget
                widget.bind("<<Modified>>", self.body_modified)
                scrollbar = ttk.Scrollbar(right, command=widget.yview)
                scrollbar.grid(row=index, column=2, sticky="ns", pady=4)
                widget.configure(yscrollcommand=scrollbar.set)
            elif field == "category":
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
            widget.grid(row=index, column=1, sticky="nsew" if field == "body" else "ew", pady=4)
            self.widgets[field] = widget
        buttons = ttk.Frame(right)
        buttons.grid(row=len(FIELDS), column=0, columnspan=3, sticky="ew", pady=8)
        for index, (label, command) in enumerate((
            ("New Flavor Text", self.new), ("Apply to List", self.apply_record),
            ("Save to Source", self.save), ("Delete from List", self.remove),
            ("Revert Form", self.revert), ("Revert Draft", self.revert_source),
            ("Open Backups", self.open_backups),
        )):
            ttk.Button(buttons, text=label, command=command).grid(
                row=index // 3, column=index % 3, sticky="ew", padx=3, pady=3
            )
        ttk.Label(
            right, wraplength=390,
            text="IDs are immutable. Category, Title, and Body are required. "
                 "Apply/Delete change only the draft. Save validates and creates a backup. "
                 "Metric Tier references remain protected. Validate/Export use saved source.",
        ).grid(row=len(FIELDS) + 1, column=0, columnspan=3, sticky="ew", pady=8)
        ttk.Label(right, textvariable=self.status, wraplength=390).grid(
            row=len(FIELDS) + 2, column=0, columnspan=3, sticky="ew"
        )
        self.new()

    def refresh_choices(self):
        self.widgets["category"].configure(values=tuple(self.categories()))
        self.widgets["active"].configure(values=("TRUE", "FALSE"))

    def categories(self):
        return sorted({
            row["category"].strip() for row in self.loaded_rows
            if row["category"].strip()
        })

    def new(self):
        self._loading = True
        try:
            self._end_session()
            self.tree.selection_remove(*self.tree.selection())
            self.refresh_choices()
            categories = self.categories()
            for field in FIELDS:
                self.vars[field].set("")
            self.vars["category"].set(categories[0] if categories else "")
            self.vars["active"].set("TRUE")
            self.widgets["flavor_text_id"].configure(state="normal")
            self._load_body()
        finally:
            self._loading = False

    def validate_rows(self, rows):
        seen = set()
        for row in rows:
            if set(row) != set(FIELDS) or any(not isinstance(row[f], str) for f in FIELDS):
                raise ValueError("Malformed Flavor Text row.")
            if any(row[f].strip() == MULTIPLE_VALUES for f in FIELDS):
                raise ValueError("Mixed-value placeholder cannot be applied as data.")
            key = row_key(row)
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
                raise ValueError("Flavor Text ID must start with an uppercase letter and use uppercase letters, digits, or underscores.")
            if key in seen:
                raise ValueError("Duplicate Flavor Text ID.")
            seen.add(key)
            for field in ("category", "title", "body"):
                if not row[field].strip():
                    raise ValueError(field.title() + " is required.")
            if row["active"] not in ("TRUE", "FALSE"):
                raise ValueError("Active must be TRUE or FALSE.")

    def update(self, force=False):
        path = self.source_path()
        if self.dirty and not force:
            self._check_project()
            self._set_status("Unsaved Flavor Text draft retained; refresh skipped.")
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
                raise ValueError("Flavor Text CSV header does not match the current schema.")
            rows = [dict(row) for row in reader if any(row.values())]
        self.validate_rows(rows)
        if before != self.digest(path):
            raise ValueError("Flavor Text CSV changed during refresh; draft retained.")
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
        self._set_status(f"{len(rows)} flavor records loaded from source.")

    def _load_body(self):
        previous = self._loading
        self._loading = True
        try:
            self.body.delete("1.0", "end")
            self.body.insert("1.0", self.vars["body"].get())
            self._body_seen = self.body.get("1.0", "end-1c")
            self.body.edit_modified(False)
        finally:
            self._loading = previous

    def body_modified(self, _event=None):
        if not self.body.edit_modified():
            return
        self.body.edit_modified(False)
        self.flush_body()

    def flush_body(self):
        current = self.body.get("1.0", "end-1c")
        if not self._loading and current != self._body_seen:
            self.vars["body"].set(current)
            self.changed("body")
        self._body_seen = current

    def on_select(self, _event=None, force=False):
        selected = tuple(self.tree.selection())
        if not force and selected == self._session and self.loaded_rows == self._original:
            return
        self._draft_on_select(_event, force)
        self._load_body()

    def apply_record(self):
        self.flush_body()
        return self._draft_apply_record()

    def select_placeholder(self, field):
        if len(self._session) < 2 or field in self._changes:
            return

        def select():
            if len(self._session) < 2 or field in self._changes:
                return
            value = (
                self.body.get("1.0", "end-1c")
                if field == "body" else self.vars[field].get()
            )
            if value != MULTIPLE_VALUES:
                return
            if field == "body":
                self.body.tag_add("sel", "1.0", "end-1c")
                self.body.mark_set("insert", "end-1c")
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
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in sorted(self.loaded_rows, key=sort_key):
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
            f"{len(rows)} facility record(s) selected. Untouched fields are preserved."
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
        with tempfile.TemporaryDirectory(prefix="doda-flavor-text-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)
            for filename in FILES:
                source = candidate if filename == "flavor_text.csv" else self.app.source_directory / filename
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
        with tempfile.TemporaryDirectory(prefix="doda-flavor-text-draft-") as temporary:
            candidate = Path(temporary) / "flavor_text.csv"
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
            raise ValueError("Selection cleared. Start a new facility before applying.")

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
                    raise ValueError("Flavor Text ID cannot be batch-edited.")
                changes = {field: clean_value(field, value) for field, value in self._changes.items()}
                candidate = [
                    {**row, **changes} if row_iid(row) in selected else dict(row)
                    for row in before
                ]
            else:
                row = {field: clean_value(field, self.vars[field].get()) for field in FIELDS}
                key = row_key(row)
                if selected and self.editing_key is None:
                    raise ValueError("Reselect the facility before applying.")
                if self.editing_key is not None:
                    if key != self.editing_key:
                        raise ValueError("Flavor Text ID cannot change after creation.")
                    if not any(row_key(r) == key for r in before):
                        raise ValueError("Selected facility is no longer in the draft.")
                    candidate = [row if row_key(r) == key else dict(r) for r in before]
                else:
                    if any(row_key(r) == key for r in before):
                        raise ValueError("This Flavor Text ID installation already exists.")
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
        self.app.log(f"Flavor Text {action} blocked; draft retained: {error}")
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
                raise ValueError("Selected facility is no longer in the draft.")
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
        temporary = path.with_name(".flavor-text-" + uuid4().hex + ".tmp.csv")
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
                "flavor_text_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".csv"
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
                self.app.log(f"Flavor Text temporary cleanup warning: {error}")
        self.snapshot_hash = self.digest(path)
        self.dirty = False
        self.app.log(f"Flavor Text saved. Backup: {backup}")
        self._set_status("Flavor Text saved to source.")
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
            self.title, "Discard applied Flavor Text draft changes and reload source?",
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


def install_flavor_text_editor(app):
    editor = FlavorTextEditor(app)
    app.flavor_text_editor = editor
    app.update_flavor_text = editor.update
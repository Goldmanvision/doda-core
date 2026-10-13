from __future__ import annotations

import csv
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
from typing import Any
from uuid import uuid4

FIELDS = (
    "enum_group",
    "enum_value",
    "display_label",
    "description",
    "sort_order",
    "active",
)

FILES = (
    "enum_catalog.csv",
    "department_tracks.csv",
    "metrics.csv",
    "metric_tiers.csv",
    "facilities.csv",
    "flavor_text.csv",
    "qualification_catalog.csv",
    "capabilities.csv",
    "facility_capabilities.csv",
    "capability_staffing_rules.csv",
    "facility_capability_staffing_overrides.csv",
    "task_templates.csv",
)
FILES = tuple(FILES) + ("equipment_families.csv",)

ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")


class EnumCatalogEditor:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.editing_key: tuple[str, str] | None = None

        self.catalog_group_filter = tk.StringVar(value="All Groups")

        self.enum_group = tk.StringVar()
        self.enum_value = tk.StringVar()
        self.display_label = tk.StringVar()
        self.sort_order = tk.StringVar()
        self.active = tk.BooleanVar(value=True)

        self.build()

    def source_path(self) -> Path:
        return self.app.source_directory / "enum_catalog.csv"

    def backup_directory(self) -> Path:
        return self.app.project_root / "data_authoring" / "backups" / "enum_catalog"

    def rows(self) -> list[dict[str, str]]:
        return [dict(row) for row in self.app.tables.get("enum_catalog", [])]

    def groups(self) -> list[str]:
        source_path = self.app.source_directory / "enum_catalog.csv"

        if not source_path.is_file():
            return []

        groups: set[str] = set()

        try:
            with source_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as source_file:
                reader = csv.DictReader(source_file)

                for row in reader:
                    if row is None:
                        continue

                    group = (row.get("enum_group") or "").strip()

                    if group:
                        groups.add(group)

        except (OSError, csv.Error):
            return []

        return sorted(groups)

    def values_for_group(self, group: str) -> list[str]:
        source_path = self.app.source_directory / "enum_catalog.csv"

        if not source_path.is_file() or not group:
            return []

        rows: list[tuple[int, str]] = []

        try:
            with source_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as source_file:
                reader = csv.DictReader(source_file)

                for row in reader:
                    if row is None:
                        continue

                    if (row.get("enum_group") or "").strip() != group:
                        continue

                    value = (row.get("enum_value") or "").strip()

                    if not value:
                        continue

                    try:
                        sort_order = int(
                            (row.get("sort_order") or "999999").strip()
                        )
                    except ValueError:
                        sort_order = 999999

                    rows.append((sort_order, value))

        except (OSError, csv.Error):
            return []

        return [
            value
            for _, value in sorted(
                rows,
                key=lambda item: (item[0], item[1]),
            )
        ]

    def refresh_value_choices(self, _event: object = None) -> None:
        group = self.enum_group.get().strip()
        current_value = self.enum_value.get().strip()

        self.value_combo.configure(values=self.values_for_group(group))

        if current_value:
            self.enum_value.set(current_value)
    def catalog_groups(self) -> list[str]:
        groups = sorted(
            {
                (row.get("enum_group") or "").strip()
                for row in self.rows()
                if (row.get("enum_group") or "").strip()
            }
        )

        return ["All Groups", *groups]

    def visible_rows(self) -> list[dict[str, str]]:
        selected_group = self.catalog_group_filter.get().strip()

        if not selected_group or selected_group == "All Groups":
            return self.rows()

        return [
            row
            for row in self.rows()
            if (row.get("enum_group") or "").strip() == selected_group
        ]

    def refresh_catalog_group_filter(self) -> None:
        groups = self.catalog_groups()
        current = self.catalog_group_filter.get().strip()

        self.catalog_group_combo.configure(values=groups)

        if current in groups:
            self.catalog_group_filter.set(current)
        else:
            self.catalog_group_filter.set("All Groups")

    def on_catalog_group_filter_changed(self, _event: Any = None) -> None:
        self.update()
    def build(self) -> None:
        self.tab = ttk.Frame(self.app.notebook, padding=10)
        self.app.notebook.add(self.tab, text="Enum Catalog — Admin")

        self.tab.columnconfigure(0, weight=3)
        self.tab.columnconfigure(1, weight=2)
        self.tab.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(self.tab, text="Enum Catalog", padding=8)
        editor_frame = ttk.LabelFrame(self.tab, text="Enum Catalog Editor", padding=10)

        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        editor_frame.grid(row=0, column=1, sticky=tk.NSEW)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)

        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(0, 8),
        )

        ttk.Label(
            filter_frame,
            text="Enum Group:",
            style="Section.TLabel",
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.catalog_group_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.catalog_group_filter,
            values=self.catalog_groups(),
            state="readonly",
            width=28,
        )
        self.catalog_group_combo.pack(side=tk.LEFT)
        self.catalog_group_combo.bind(
            "<<ComboboxSelected>>",
            self.on_catalog_group_filter_changed,
        )
        self.tree = ttk.Treeview(
            list_frame,
            columns=("group", "value", "label", "sort", "active"),
            show="headings",
            selectmode="browse",
        )

        columns = (
            ("group", "Enum Group", 170),
            ("value", "Enum Value", 200),
            ("label", "Display Label", 230),
            ("sort", "Sort", 60),
            ("active", "Active", 70),
        )

        for key, title, width in columns:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, anchor=tk.W)

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )

        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=1, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=1, column=1, sticky=tk.NS)

        list_frame.rowconfigure(1, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        def label(text: str, row: int) -> None:
            ttk.Label(
                editor_frame,
                text=text,
                style="Section.TLabel",
            ).grid(
                row=row,
                column=0,
                sticky=tk.NW,
                padx=(0, 8),
                pady=(0, 8),
            )

        label("Enum Group:", 0)

        self.group_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.enum_group,
            values=self.groups(),
            state="normal",
        )

        self.group_combo.grid(
            row=0,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )
        self.group_combo.bind(
            "<<ComboboxSelected>>",
            self.refresh_value_choices,
        )

        self.group_combo.bind(
            "<FocusOut>",
            self.refresh_value_choices,
        )

        label("Enum Value:", 1)
        self.value_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.enum_value,
            values=self.values_for_group(self.enum_group.get()),
            state="normal",
        )

        self.value_combo.grid(
            row=1,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        ttk.Label(
            editor_frame,
            text="Group + Value are immutable after creation.",
            foreground="#9da7b3",
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
        )

        label("Display Label:", 3)

        ttk.Entry(
            editor_frame,
            textvariable=self.display_label,
        ).grid(
            row=3,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Description:", 4)

        self.description = tk.Text(
            editor_frame,
            height=7,
            wrap=tk.WORD,
            background="#0d1117",
            foreground="#e6edf3",
            insertbackground="#e6edf3",
            highlightbackground="#3b4754",
            highlightcolor="#58a6ff",
        )

        self.description.grid(
            row=4,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Sort Order:", 5)

        ttk.Entry(
            editor_frame,
            textvariable=self.sort_order,
            width=10,
        ).grid(
            row=5,
            column=1,
            sticky=tk.W,
            pady=(0, 8),
        )

        label("Active:", 6)

        ttk.Checkbutton(
            editor_frame,
            text="This enum value is active",
            variable=self.active,
        ).grid(
            row=6,
            column=1,
            sticky=tk.W,
            pady=(0, 8),
        )

        buttons = ttk.Frame(editor_frame)
        buttons.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(8, 0),
        )

        ttk.Button(
            buttons,
            text="Add Enum Value",
            command=self.new,
        ).pack(side=tk.LEFT)

        ttk.Button(
            buttons,
            text="Save Enum Value",
            command=self.save,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Remove Enum Value",
            command=self.remove,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Revert Form",
            command=self.revert,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Open Backups",
            command=self.open_backups,
        ).pack(side=tk.RIGHT)

        ttk.Label(
            editor_frame,
            text=(
                "Administrative editor. Candidate validation blocks deletion "
                "or deactivation when authored data depends on this value."
            ),
            foreground="#9da7b3",
            wraplength=390,
        ).grid(
            row=8,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(12, 0),
        )

        self.new()

    def update(self) -> None:
        selected = self.editing_key

        current_group = self.enum_group.get()

        self.group_combo.configure(values=self.groups())
        self.refresh_value_choices()

        if current_group and current_group in self.groups():
            self.enum_group.set(current_group)

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.refresh_catalog_group_filter()

        rows = sorted(
            self.visible_rows(),
            key=lambda row: (
                row.get("enum_group", ""),
                int(row.get("sort_order", "999999")),
                row.get("enum_value", ""),
            ),
        )

        for row in rows:
            group = row.get("enum_group", "")
            value = row.get("enum_value", "")
            key = f"{group}::{value}"

            self.tree.insert(
                "",
                tk.END,
                iid=key,
                values=(
                    group,
                    value,
                    row.get("display_label", ""),
                    row.get("sort_order", ""),
                    row.get("active", ""),
                ),
            )

        if selected:
            key = f"{selected[0]}::{selected[1]}"

            if self.tree.exists(key):
                self.tree.selection_set(key)
                self.tree.focus(key)

    def next_sort_order(self, group: str) -> int:
        values: list[int] = []

        for row in self.rows():
            if row.get("enum_group") != group:
                continue

            try:
                values.append(int(row.get("sort_order", "")))
            except ValueError:
                pass

        return max(values, default=-1) + 1

    def new(self) -> None:
        self.editing_key = None

        self.group_combo.configure(state=tk.NORMAL)
        self.value_combo.configure(state="normal")

        groups = self.groups()

        self.enum_group.set(groups[0] if groups else "")
        self.enum_value.set("")
        self.refresh_value_choices()
        self.display_label.set("")
        self.description.delete("1.0", tk.END)
        self.sort_order.set(
            str(self.next_sort_order(self.enum_group.get()))
            if self.enum_group.get()
            else "0"
        )
        self.active.set(True)

        self.value_combo.focus_set()

    def on_select(self, _event: Any = None) -> None:
        selection = self.tree.selection()

        if not selection:
            return

        group, value = selection[0].split("::", 1)

        row = next(
            (
                item
                for item in self.rows()
                if item.get("enum_group") == group
                and item.get("enum_value") == value
            ),
            None,
        )

        if row is None:
            return

        self.editing_key = (group, value)

        self.group_combo.configure(state=tk.NORMAL)
        self.group_combo.set(group)
        self.group_combo.configure(state=tk.DISABLED)

        self.value_combo.configure(state="normal")
        self.enum_value.set(value)
        self.value_combo.configure(state=tk.DISABLED)

        self.display_label.set(row.get("display_label", ""))
        self.sort_order.set(row.get("sort_order", ""))
        self.active.set(row.get("active", "").upper() == "TRUE")

        self.description.delete("1.0", tk.END)
        self.description.insert("1.0", row.get("description", ""))

    def revert(self) -> None:
        if self.editing_key:
            key = f"{self.editing_key[0]}::{self.editing_key[1]}"

            if self.tree.exists(key):
                self.tree.selection_set(key)
                self.on_select()
                return

        self.new()

    def record(self) -> dict[str, str] | None:
        row = {
            "enum_group": self.enum_group.get().strip(),
            "enum_value": self.enum_value.get().strip(),
            "display_label": self.display_label.get().strip(),
            "description": self.description.get("1.0", tk.END).strip(),
            "sort_order": self.sort_order.get().strip(),
            "active": "TRUE" if self.active.get() else "FALSE",
        }

        errors: list[str] = []

        if not ID_PATTERN.fullmatch(row["enum_group"]):
            errors.append(
                "Enum Group must begin with an uppercase letter and use only "
                "uppercase letters, digits, or underscores."
            )

        if not ID_PATTERN.fullmatch(row["enum_value"]):
            errors.append(
                "Enum Value must begin with an uppercase letter and use only "
                "uppercase letters, digits, or underscores."
            )

        if not row["display_label"]:
            errors.append("Display Label is required.")

        if not row["description"]:
            errors.append("Description is required.")

        try:
            sort_order = int(row["sort_order"])

            if sort_order < 0:
                errors.append("Sort Order cannot be negative.")

        except ValueError:
            errors.append("Sort Order must be an integer.")

        if errors:
            messagebox.showerror(
                "DoDA Content Workbench",
                "Correct before saving:\n\n- " + "\n- ".join(errors),
            )

            return None

        return row

    def write(self, path: Path, rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=FIELDS,
                lineterminator="\n",
            )

            writer.writeheader()

            for row in rows:
                writer.writerow(
                    {
                        field: row.get(field, "")
                        for field in FIELDS
                    }
                )

    def candidate_valid(self, candidate: Path) -> tuple[bool, str]:
        with tempfile.TemporaryDirectory(prefix="doda-enum-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)

            for filename in FILES:
                source = (
                    candidate
                    if filename == "enum_catalog.csv"
                    else self.app.source_directory / filename
                )

                shutil.copy2(source, destination / filename)

            command = [
                sys.executable,
                str(self.app.validator_path),
                "--root",
                str(root),
                "validate",
            ]

            completed = subprocess.run(
                command,
                cwd=root,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            output = (
                completed.stdout
                + ("\n" if completed.stdout and completed.stderr else "")
                + completed.stderr
            ).strip()

            return completed.returncode == 0, output

    def post_validate(self) -> tuple[bool, str]:
        command = [
            sys.executable,
            str(self.app.validator_path),
            "--root",
            str(self.app.project_root),
            "validate",
        ]

        completed = subprocess.run(
            command,
            cwd=self.app.project_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        output = (
            completed.stdout
            + ("\n" if completed.stdout and completed.stderr else "")
            + completed.stderr
        ).strip()

        return completed.returncode == 0, output

    def save(self) -> None:
        row = self.record()

        if row is None:
            return

        rows = self.rows()

        if self.editing_key:
            if (
                row["enum_group"] != self.editing_key[0]
                or row["enum_value"] != self.editing_key[1]
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Enum Group and Enum Value cannot change after creation.",
                )
                return

            rows = [
                row
                if (
                    item.get("enum_group") == self.editing_key[0]
                    and item.get("enum_value") == self.editing_key[1]
                )
                else item
                for item in rows
            ]

            action = "updated"

        else:
            if any(
                item.get("enum_group") == row["enum_group"]
                and item.get("enum_value") == row["enum_value"]
                for item in rows
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "This Enum Group and Enum Value combination already exists.",
                )
                return

            rows.append(row)
            action = "added"

        temporary = self.app.source_directory / (
            f".enum-catalog-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log("Enum Catalog candidate validation output:")

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Enum Catalog candidate validation failed. Source CSV "
                        "was unchanged.\n\nReview Activity Log for details."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "enum_catalog_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_key = (
                row["enum_group"],
                row["enum_value"],
            )

            self.app.log(f"Created Enum Catalog backup: {backup}")
            self.app.log(
                f"Enum Catalog {action}: "
                f"{row['enum_group']} / {row['enum_value']}"
            )

            self.app.refresh_all(False)

            valid, output = self.post_validate()

            for line in output.splitlines():
                self.app.log(" " + line)

            self.app.refresh_all(False)

            if valid:
                messagebox.showinfo(
                    "DoDA Content Workbench",
                    (
                        f"Enum Value '{row['enum_group']} / {row['enum_value']}' "
                        f"{action}.\n\nBackup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Enum Catalog {action}, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"ENUM CATALOG SAVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to save Enum Catalog value.\n\n{error}",
            )

        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def remove(self) -> None:
        if not self.editing_key:
            messagebox.showwarning(
                "DoDA Content Workbench",
                "Select an existing Enum Value before using Remove Enum Value.",
            )
            return

        group, value = self.editing_key

        confirmed = messagebox.askyesno(
            "Remove Enum Value?",
            (
                f"ARE YOU SURE you want to remove '{group} / {value}'?\n\n"
                "Removal is blocked when authored data still depends on it."
            ),
            icon="warning",
            default=messagebox.NO,
        )

        if not confirmed:
            self.app.log(
                f"Remove Enum Value cancelled for '{group} / {value}'."
            )
            return

        rows = [
            row
            for row in self.rows()
            if not (
                row.get("enum_group") == group
                and row.get("enum_value") == value
            )
        ]

        temporary = self.app.source_directory / (
            f".enum-catalog-remove-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                "Enum Catalog removal candidate validation output "
                f"for '{group} / {value}':"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Removal was blocked by validation.\n\n"
                        "The enum value is still referenced by authored data. "
                        "Source CSV was unchanged."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "enum_catalog_before_remove_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_key = None

            self.app.log(
                f"Created pre-removal Enum Catalog backup: {backup}"
            )

            self.app.log(f"Removed Enum Value: {group} / {value}")

            self.app.refresh_all(False)
            self.new()

            valid, output = self.post_validate()

            for line in output.splitlines():
                self.app.log(" " + line)

            self.app.refresh_all(False)

            if valid:
                messagebox.showinfo(
                    "DoDA Content Workbench",
                    (
                        f"Enum Value '{group} / {value}' removed.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        "Enum Value removed, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"ENUM CATALOG REMOVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to remove Enum Value.\n\n{error}",
            )

        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def open_backups(self) -> None:
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_enum_catalog_editor(app: Any) -> None:
    editor = EnumCatalogEditor(app)

    app.enum_catalog_editor = editor

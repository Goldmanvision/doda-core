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
    "capability_id",
    "display_name",
    "description",
    "standing_operation_label",
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


class CapabilitiesEditor:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.editing_id: str | None = None

        self.capability_id = tk.StringVar()
        self.display_name = tk.StringVar()
        self.standing_operation_label = tk.StringVar()
        self.sort_order = tk.StringVar()
        self.active = tk.BooleanVar(value=True)

        self.build()

    def source_path(self) -> Path:
        return self.app.source_directory / "capabilities.csv"

    def backup_directory(self) -> Path:
        return (
            self.app.project_root
            / "data_authoring"
            / "backups"
            / "capabilities"
        )

    def rows(self) -> list[dict[str, str]]:
        return [
            dict(row)
            for row in self.app.tables.get("capabilities", [])
        ]

    def build(self) -> None:
        for child in self.app.capabilities_tab.winfo_children():
            child.destroy()

        tab = self.app.capabilities_tab
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(tab, text="Capabilities", padding=8)
        editor_frame = ttk.LabelFrame(
            tab,
            text="Capability Editor",
            padding=10,
        )

        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        editor_frame.grid(row=0, column=1, sticky=tk.NSEW)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("id", "name", "operation", "sort", "active"),
            show="headings",
            selectmode="browse",
        )

        columns = (
            ("id", "Capability ID", 180),
            ("name", "Display Name", 205),
            ("operation", "Standing Operation", 185),
            ("sort", "Sort", 55),
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
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
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

        label("Capability ID:", 0)

        self.id_entry = ttk.Entry(
            editor_frame,
            textvariable=self.capability_id,
        )
        self.id_entry.grid(
            row=0,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        ttk.Label(
            editor_frame,
            text="Uppercase ID; immutable after creation.",
            foreground="#9da7b3",
        ).grid(
            row=1,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
        )

        label("Display Name:", 2)

        ttk.Entry(
            editor_frame,
            textvariable=self.display_name,
        ).grid(
            row=2,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Description:", 3)

        self.description = tk.Text(
            editor_frame,
            height=5,
            wrap=tk.WORD,
            background="#0d1117",
            foreground="#e6edf3",
            insertbackground="#e6edf3",
            highlightbackground="#3b4754",
            highlightcolor="#58a6ff",
        )
        self.description.grid(
            row=3,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Standing Operation:", 4)

        ttk.Entry(
            editor_frame,
            textvariable=self.standing_operation_label,
        ).grid(
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
            text="This capability is active",
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
            text="Add Capability",
            command=self.new,
        ).pack(side=tk.LEFT)

        ttk.Button(
            buttons,
            text="Save Capability",
            command=self.save,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Remove Capability",
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
                "Candidate validation blocks deletion or changes that would "
                "break facility, staffing-rule, override, or task references."
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
        selected = self.editing_id

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = sorted(
            self.rows(),
            key=lambda row: (
                int(row.get("sort_order", "999999")),
                row.get("capability_id", ""),
            ),
        )

        for row in rows:
            capability_id = row.get("capability_id", "")

            self.tree.insert(
                "",
                tk.END,
                iid=capability_id,
                values=(
                    capability_id,
                    row.get("display_name", ""),
                    row.get("standing_operation_label", ""),
                    row.get("sort_order", ""),
                    row.get("active", ""),
                ),
            )

        if selected and self.tree.exists(selected):
            self.tree.selection_set(selected)
            self.tree.focus(selected)

    def next_sort_order(self) -> int:
        values: list[int] = []

        for row in self.rows():
            try:
                values.append(int(row.get("sort_order", "")))
            except ValueError:
                pass

        return max(values, default=0) + 1

    def new(self) -> None:
        self.editing_id = None
        self.id_entry.configure(state=tk.NORMAL)

        self.capability_id.set("")
        self.display_name.set("")
        self.standing_operation_label.set("")
        self.sort_order.set(str(self.next_sort_order()))
        self.active.set(True)

        self.description.delete("1.0", tk.END)
        self.id_entry.focus_set()

    def on_select(self, _event: Any = None) -> None:
        selection = self.tree.selection()

        if not selection:
            return

        row = next(
            (
                item
                for item in self.rows()
                if item.get("capability_id") == selection[0]
            ),
            None,
        )

        if row is None:
            return

        self.editing_id = row["capability_id"]

        self.id_entry.configure(state=tk.NORMAL)
        self.capability_id.set(row.get("capability_id", ""))
        self.id_entry.configure(state=tk.DISABLED)

        self.display_name.set(row.get("display_name", ""))
        self.standing_operation_label.set(
            row.get("standing_operation_label", "")
        )
        self.sort_order.set(row.get("sort_order", ""))
        self.active.set(row.get("active", "").upper() == "TRUE")

        self.description.delete("1.0", tk.END)
        self.description.insert("1.0", row.get("description", ""))

    def revert(self) -> None:
        if self.editing_id and self.tree.exists(self.editing_id):
            self.tree.selection_set(self.editing_id)
            self.on_select()
        else:
            self.new()

    def record(self) -> dict[str, str] | None:
        row = {
            "capability_id": self.capability_id.get().strip(),
            "display_name": self.display_name.get().strip(),
            "description": self.description.get("1.0", tk.END).strip(),
            "standing_operation_label": (
                self.standing_operation_label.get().strip()
            ),
            "sort_order": self.sort_order.get().strip(),
            "active": "TRUE" if self.active.get() else "FALSE",
        }

        errors: list[str] = []

        if not ID_PATTERN.fullmatch(row["capability_id"]):
            errors.append(
                "Capability ID must begin with an uppercase letter and use only "
                "uppercase letters, digits, or underscores."
            )

        if not row["display_name"]:
            errors.append("Display Name is required.")

        if not row["description"]:
            errors.append("Description is required.")

        if not row["standing_operation_label"]:
            errors.append("Standing Operation Label is required.")

        try:
            sort_order = int(row["sort_order"])

            if sort_order < 1:
                errors.append("Sort Order must be at least 1.")
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
        with tempfile.TemporaryDirectory(
            prefix="doda-capability-"
        ) as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)

            for filename in FILES:
                source = (
                    candidate
                    if filename == "capabilities.csv"
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

        if self.editing_id:
            if row["capability_id"] != self.editing_id:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Capability ID cannot change after creation.",
                )
                return

            rows = [
                row
                if item.get("capability_id") == self.editing_id
                else item
                for item in rows
            ]
            action = "updated"
        else:
            if any(
                item.get("capability_id") == row["capability_id"]
                for item in rows
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Capability ID already exists.",
                )
                return

            rows.append(row)
            action = "added"

        rows.sort(
            key=lambda item: (
                int(item.get("sort_order", "999999")),
                item.get("capability_id", ""),
            )
        )

        temporary = self.app.source_directory / (
            f".capabilities-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log("Capability candidate validation output:")

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Capability candidate validation failed. Source CSV "
                        "was unchanged.\n\nReview Activity Log for details."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "capabilities_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_id = row["capability_id"]

            self.app.log(f"Created capability backup: {backup}")
            self.app.log(f"Capability {action}: {row['capability_id']}")

            self.app.refresh_all(False)

            valid, output = self.post_validate()

            for line in output.splitlines():
                self.app.log(" " + line)

            self.app.refresh_all(False)

            if valid:
                messagebox.showinfo(
                    "DoDA Content Workbench",
                    (
                        f"Capability '{row['capability_id']}' {action}.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Capability {action}, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"CAPABILITY SAVE ERROR: {error}")
            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to save capability.\n\n{error}",
            )
        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def remove(self) -> None:
        if not self.editing_id:
            messagebox.showwarning(
                "DoDA Content Workbench",
                "Select an existing capability before using Remove.",
            )
            return

        capability_id = self.editing_id

        confirmed = messagebox.askyesno(
            "Remove Capability?",
            (
                f"ARE YOU SURE you want to remove '{capability_id}'?\n\n"
                "Removal will be blocked if the capability is referenced by "
                "Facility Capabilities, staffing rules, overrides, or tasks."
            ),
            icon="warning",
            default=messagebox.NO,
        )

        if not confirmed:
            self.app.log(
                f"Remove Capability cancelled for '{capability_id}'."
            )
            return

        rows = [
            row
            for row in self.rows()
            if row.get("capability_id") != capability_id
        ]

        temporary = self.app.source_directory / (
            f".capabilities-remove-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                "Capability removal candidate validation output "
                f"for '{capability_id}':"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Capability removal was blocked by validation.\n\n"
                        "Source CSV was unchanged."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "capabilities_before_remove_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_id = None

            self.app.log(
                f"Created pre-removal capability backup: {backup}"
            )
            self.app.log(f"Removed capability: {capability_id}")

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
                        f"Capability '{capability_id}' removed.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Capability '{capability_id}' removed, but post-save "
                        f"validation failed.\n\nBackup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"CAPABILITY REMOVE ERROR: {error}")
            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to remove capability.\n\n{error}",
            )
        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def open_backups(self) -> None:
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_capabilities_editor(app: Any) -> None:
    editor = CapabilitiesEditor(app)
    app.capabilities_editor = editor

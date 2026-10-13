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
    "flavor_text_id",
    "category",
    "title",
    "body",
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


class FlavorTextEditor:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.editing_id: str | None = None

        self.flavor_id = tk.StringVar()
        self.category = tk.StringVar()
        self.title = tk.StringVar()
        self.active = tk.BooleanVar(value=True)

        self.build()

    def source_path(self) -> Path:
        return self.app.source_directory / "flavor_text.csv"

    def backup_directory(self) -> Path:
        return self.app.project_root / "data_authoring" / "backups" / "flavor_text"

    def rows(self) -> list[dict[str, str]]:
        return [dict(row) for row in self.app.tables.get("flavor_text", [])]

    def categories(self) -> list[str]:
        return sorted(
            {
                row.get("category", "").strip()
                for row in self.rows()
                if row.get("category", "").strip()
            }
        )

    def build(self) -> None:
        for child in self.app.flavor_tab.winfo_children():
            child.destroy()

        tab = self.app.flavor_tab
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(tab, text="Flavor Text", padding=8)
        editor_frame = ttk.LabelFrame(tab, text="Flavor Text Editor", padding=10)

        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        editor_frame.grid(row=0, column=1, sticky=tk.NSEW)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)
        editor_frame.rowconfigure(4, weight=1)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("id", "category", "title", "active"),
            show="headings",
            selectmode="browse",
        )

        columns = (
            ("id", "Flavor Text ID", 250),
            ("category", "Category", 150),
            ("title", "Title", 280),
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

        label("Flavor Text ID:", 0)

        self.id_entry = ttk.Entry(
            editor_frame,
            textvariable=self.flavor_id,
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

        label("Category:", 2)

        self.category_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.category,
            values=self.categories(),
        )

        self.category_combo.grid(
            row=2,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Title:", 3)

        ttk.Entry(
            editor_frame,
            textvariable=self.title,
        ).grid(
            row=3,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Body:", 4)

        self.body = tk.Text(
            editor_frame,
            height=12,
            wrap=tk.WORD,
            background="#0d1117",
            foreground="#e6edf3",
            insertbackground="#e6edf3",
            highlightbackground="#3b4754",
            highlightcolor="#58a6ff",
        )

        self.body.grid(
            row=4,
            column=1,
            sticky=tk.NSEW,
            pady=(0, 8),
        )

        label("Active:", 5)

        ttk.Checkbutton(
            editor_frame,
            text="This flavor text is active",
            variable=self.active,
        ).grid(
            row=5,
            column=1,
            sticky=tk.W,
            pady=(0, 8),
        )

        buttons = ttk.Frame(editor_frame)
        buttons.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(8, 0),
        )

        ttk.Button(
            buttons,
            text="Add Flavor Text",
            command=self.new,
        ).pack(side=tk.LEFT)

        ttk.Button(
            buttons,
            text="Save Flavor Text",
            command=self.save,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Remove Flavor Text",
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
                "Removal is blocked when Metric Tiers reference the selected "
                "Flavor Text ID."
            ),
            foreground="#9da7b3",
            wraplength=390,
        ).grid(
            row=7,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(12, 0),
        )

        self.new()

    def update(self) -> None:
        selected = self.editing_id

        self.category_combo.configure(values=self.categories())

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = sorted(
            self.rows(),
            key=lambda row: (
                row.get("category", ""),
                row.get("flavor_text_id", ""),
            ),
        )

        for row in rows:
            flavor_id = row.get("flavor_text_id", "")
            title = " ".join(row.get("title", "").split())

            if len(title) > 70:
                title = title[:67] + "..."

            self.tree.insert(
                "",
                tk.END,
                iid=flavor_id,
                values=(
                    flavor_id,
                    row.get("category", ""),
                    title,
                    row.get("active", ""),
                ),
            )

        if selected and self.tree.exists(selected):
            self.tree.selection_set(selected)
            self.tree.focus(selected)

    def new(self) -> None:
        self.editing_id = None

        self.id_entry.configure(state=tk.NORMAL)

        categories = self.categories()

        self.flavor_id.set("")
        self.category.set(categories[0] if categories else "")
        self.title.set("")
        self.active.set(True)

        self.body.delete("1.0", tk.END)
        self.id_entry.focus_set()

    def on_select(self, _event: Any = None) -> None:
        selection = self.tree.selection()

        if not selection:
            return

        row = next(
            (
                item
                for item in self.rows()
                if item.get("flavor_text_id") == selection[0]
            ),
            None,
        )

        if row is None:
            return

        self.editing_id = row["flavor_text_id"]

        self.id_entry.configure(state=tk.NORMAL)
        self.flavor_id.set(row.get("flavor_text_id", ""))
        self.id_entry.configure(state=tk.DISABLED)

        self.category.set(row.get("category", ""))
        self.title.set(row.get("title", ""))
        self.active.set(row.get("active", "").upper() == "TRUE")

        self.body.delete("1.0", tk.END)
        self.body.insert("1.0", row.get("body", ""))

    def revert(self) -> None:
        if self.editing_id and self.tree.exists(self.editing_id):
            self.tree.selection_set(self.editing_id)
            self.on_select()
        else:
            self.new()

    def record(self) -> dict[str, str] | None:
        row = {
            "flavor_text_id": self.flavor_id.get().strip(),
            "category": self.category.get().strip(),
            "title": self.title.get().strip(),
            "body": self.body.get("1.0", tk.END).strip(),
            "active": "TRUE" if self.active.get() else "FALSE",
        }

        errors: list[str] = []

        if not ID_PATTERN.fullmatch(row["flavor_text_id"]):
            errors.append(
                "Flavor Text ID must begin with an uppercase letter and use "
                "only uppercase letters, digits, or underscores."
            )

        if not row["category"]:
            errors.append("Category is required.")

        if not row["title"]:
            errors.append("Title is required.")

        if not row["body"]:
            errors.append("Body is required.")

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
        with tempfile.TemporaryDirectory(prefix="doda-flavor-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)

            for filename in FILES:
                source = (
                    candidate
                    if filename == "flavor_text.csv"
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
            if row["flavor_text_id"] != self.editing_id:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Flavor Text ID cannot change after creation.",
                )
                return

            rows = [
                row
                if item.get("flavor_text_id") == self.editing_id
                else item
                for item in rows
            ]

            action = "updated"

        else:
            if any(
                item.get("flavor_text_id") == row["flavor_text_id"]
                for item in rows
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Flavor Text ID already exists.",
                )
                return

            rows.append(row)
            action = "added"

        temporary = self.app.source_directory / (
            f".flavor-text-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log("Flavor Text candidate validation output:")

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Flavor Text candidate validation failed. Source CSV "
                        "was unchanged.\n\nReview Activity Log for details."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "flavor_text_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_id = row["flavor_text_id"]

            self.app.log(f"Created Flavor Text backup: {backup}")
            self.app.log(
                f"Flavor Text {action}: {row['flavor_text_id']}"
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
                        f"Flavor Text '{row['flavor_text_id']}' {action}.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Flavor Text {action}, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"FLAVOR TEXT SAVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to save Flavor Text.\n\n{error}",
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
                "Select existing Flavor Text before using Remove Flavor Text.",
            )
            return

        flavor_id = self.editing_id

        confirmed = messagebox.askyesno(
            "Remove Flavor Text?",
            (
                f"ARE YOU SURE you want to remove '{flavor_id}'?\n\n"
                "Removal is blocked if Metric Tiers still reference this ID."
            ),
            icon="warning",
            default=messagebox.NO,
        )

        if not confirmed:
            self.app.log(
                f"Remove Flavor Text cancelled for '{flavor_id}'."
            )
            return

        rows = [
            row
            for row in self.rows()
            if row.get("flavor_text_id") != flavor_id
        ]

        temporary = self.app.source_directory / (
            f".flavor-text-remove-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                f"Flavor Text removal candidate validation output for '{flavor_id}':"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Removal was blocked by validation.\n\n"
                        "Metric Tier references must be updated first. "
                        "Source CSV was unchanged."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "flavor_text_before_remove_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_id = None

            self.app.log(
                f"Created pre-removal Flavor Text backup: {backup}"
            )

            self.app.log(f"Removed Flavor Text: {flavor_id}")

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
                        f"Flavor Text '{flavor_id}' removed.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        "Flavor Text removed, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"FLAVOR TEXT REMOVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to remove Flavor Text.\n\n{error}",
            )

        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def open_backups(self) -> None:
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_flavor_text_editor(app: Any) -> None:
    editor = FlavorTextEditor(app)

    app.flavor_text_editor = editor
    app.update_flavor_text = editor.update

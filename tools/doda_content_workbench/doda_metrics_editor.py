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
    "metric_id",
    "display_name",
    "description",
    "owner_system",
    "internal_min",
    "internal_max",
    "default_value",
    "polarity",
    "ui_display_mode",
    "update_notes",
    "active",
)

FILES = (
    "enum_catalog.csv",
    "department_tracks.csv",
    "metrics.csv",
    "metric_tiers.csv",
    "facilities.csv",
    "flavor_text.csv",
)

ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")


class MetricsEditor:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.editing_id: str | None = None

        self.metric_id = tk.StringVar()
        self.display_name = tk.StringVar()
        self.owner_system = tk.StringVar()
        self.internal_min = tk.StringVar()
        self.internal_max = tk.StringVar()
        self.default_value = tk.StringVar()
        self.polarity = tk.StringVar()
        self.display_mode = tk.StringVar()
        self.active = tk.BooleanVar(value=True)

        self.build()

    def source_path(self) -> Path:
        return self.app.source_directory / "metrics.csv"

    def backup_directory(self) -> Path:
        return self.app.project_root / "data_authoring" / "backups" / "metrics"

    def rows(self) -> list[dict[str, str]]:
        return [dict(row) for row in self.app.tables.get("metrics", [])]

    def enum_values(self, group: str) -> list[str]:
        source_path = self.app.source_directory / "enum_catalog.csv"

        if not source_path.is_file():
            return []

        values: list[tuple[int, str]] = []

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

                    if (
                        (row.get("enum_group") or "").strip() != group
                        or (row.get("active") or "").strip().upper() != "TRUE"
                    ):
                        continue

                    enum_value = (row.get("enum_value") or "").strip()

                    if not enum_value:
                        continue

                    try:
                        sort_order = int(
                            (row.get("sort_order") or "999999").strip()
                        )
                    except ValueError:
                        sort_order = 999999

                    values.append((sort_order, enum_value))

        except (OSError, csv.Error):
            return []

        return [
            enum_value
            for _, enum_value in sorted(
                values,
                key=lambda item: (item[0], item[1]),
            )
        ]

    def build(self) -> None:
        for child in self.app.metrics_tab.winfo_children():
            child.destroy()

        tab = self.app.metrics_tab
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(tab, text="Department Metrics", padding=8)
        editor_frame = ttk.LabelFrame(tab, text="Metric Editor", padding=10)

        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        editor_frame.grid(row=0, column=1, sticky=tk.NSEW)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("metric_id", "display_name", "min", "max", "default", "polarity"),
            show="headings",
            selectmode="browse",
        )

        columns = (
            ("metric_id", "Metric ID", 180),
            ("display_name", "Display Name", 220),
            ("min", "Min", 60),
            ("max", "Max", 60),
            ("default", "Default", 70),
            ("polarity", "Polarity", 145),
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

        label("Metric ID:", 0)

        self.metric_id_entry = ttk.Entry(
            editor_frame,
            textvariable=self.metric_id,
        )

        self.metric_id_entry.grid(
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

        label("Owner System:", 4)

        ttk.Entry(
            editor_frame,
            textvariable=self.owner_system,
        ).grid(
            row=4,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        range_frame = ttk.Frame(editor_frame)
        range_frame.grid(
            row=5,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        ttk.Label(
            editor_frame,
            text="Range / Default:",
            style="Section.TLabel",
        ).grid(
            row=5,
            column=0,
            sticky=tk.NW,
            padx=(0, 8),
            pady=(0, 8),
        )

        ttk.Label(range_frame, text="Min").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(
            range_frame,
            textvariable=self.internal_min,
            width=9,
        ).grid(row=0, column=1, padx=(4, 10))

        ttk.Label(range_frame, text="Max").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(
            range_frame,
            textvariable=self.internal_max,
            width=9,
        ).grid(row=0, column=3, padx=(4, 10))

        ttk.Label(range_frame, text="Default").grid(row=0, column=4, sticky=tk.W)
        ttk.Entry(
            range_frame,
            textvariable=self.default_value,
            width=9,
        ).grid(row=0, column=5, padx=(4, 0))

        label("Polarity:", 6)

        self.polarity_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.polarity,
            state="readonly",
            values=self.enum_values("METRIC_POLARITY"),
        )

        self.polarity_combo.grid(
            row=6,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("UI Display Mode:", 7)

        self.display_mode_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.display_mode,
            state="readonly",
            values=self.enum_values("METRIC_DISPLAY_MODE"),
        )

        self.display_mode_combo.grid(
            row=7,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Update Notes:", 8)

        self.update_notes = tk.Text(
            editor_frame,
            height=4,
            wrap=tk.WORD,
            background="#0d1117",
            foreground="#e6edf3",
            insertbackground="#e6edf3",
            highlightbackground="#3b4754",
            highlightcolor="#58a6ff",
        )

        self.update_notes.grid(
            row=8,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Active:", 9)

        ttk.Checkbutton(
            editor_frame,
            text="This metric is active",
            variable=self.active,
        ).grid(
            row=9,
            column=1,
            sticky=tk.W,
            pady=(0, 8),
        )

        buttons = ttk.Frame(editor_frame)
        buttons.grid(
            row=10,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(8, 0),
        )

        ttk.Button(
            buttons,
            text="Add Metric",
            command=self.new,
        ).pack(side=tk.LEFT)

        ttk.Button(
            buttons,
            text="Save Metric",
            command=self.save,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Remove Metric",
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
                "Save validates a complete isolated candidate before replacing "
                "metrics.csv. Remove is blocked when tier records still reference "
                "the selected metric."
            ),
            foreground="#9da7b3",
            wraplength=390,
        ).grid(
            row=11,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(12, 0),
        )

        self.new()

    def update(self) -> None:
        selected = self.editing_id

        polarity_values = self.enum_values("METRIC_POLARITY")
        self.polarity_combo.configure(values=polarity_values)

        display_values = self.enum_values("METRIC_DISPLAY_MODE")
        self.display_mode_combo.configure(values=display_values)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self.rows():
            metric_id = row.get("metric_id", "")

            self.tree.insert(
                "",
                tk.END,
                iid=metric_id,
                values=(
                    metric_id,
                    row.get("display_name", ""),
                    row.get("internal_min", ""),
                    row.get("internal_max", ""),
                    row.get("default_value", ""),
                    row.get("polarity", ""),
                ),
            )

        if selected and self.tree.exists(selected):
            self.tree.selection_set(selected)
            self.tree.focus(selected)

    def new(self) -> None:
        self.editing_id = None

        self.metric_id_entry.configure(state=tk.NORMAL)

        self.metric_id.set("")
        self.display_name.set("")
        self.owner_system.set("NativeStrategicCore")
        self.internal_min.set("0")
        self.internal_max.set("1000")
        self.default_value.set("0")
        self.active.set(True)

        polarity_values = self.enum_values("METRIC_POLARITY")
        self.polarity_combo.configure(values=polarity_values)

        display_values = self.enum_values("METRIC_DISPLAY_MODE")
        self.display_mode_combo.configure(values=display_values)

        self.polarity.set(
            "HIGHER_IS_BETTER"
            if "HIGHER_IS_BETTER" in polarity_values
            else (polarity_values[0] if polarity_values else "")
        )

        self.display_mode.set(
            "TIERED_BAR"
            if "TIERED_BAR" in display_values
            else (display_values[0] if display_values else "")
        )

        self.description.delete("1.0", tk.END)
        self.update_notes.delete("1.0", tk.END)

        self.tree.selection_remove(*self.tree.selection())
        self.metric_id_entry.focus_set()

    def on_select(self, _event: Any = None) -> None:
        selection = self.tree.selection()

        if not selection:
            return

        row = next(
            (
                item
                for item in self.rows()
                if item.get("metric_id") == selection[0]
            ),
            None,
        )

        if row is None:
            return

        self.editing_id = row["metric_id"]

        self.metric_id_entry.configure(state=tk.NORMAL)
        self.metric_id.set(row.get("metric_id", ""))
        self.metric_id_entry.configure(state=tk.DISABLED)

        self.display_name.set(row.get("display_name", ""))
        self.owner_system.set(row.get("owner_system", ""))
        self.internal_min.set(row.get("internal_min", ""))
        self.internal_max.set(row.get("internal_max", ""))
        self.default_value.set(row.get("default_value", ""))
        self.polarity.set(row.get("polarity", ""))
        self.display_mode.set(row.get("ui_display_mode", ""))
        self.active.set(row.get("active", "").upper() == "TRUE")

        self.description.delete("1.0", tk.END)
        self.description.insert("1.0", row.get("description", ""))

        self.update_notes.delete("1.0", tk.END)
        self.update_notes.insert("1.0", row.get("update_notes", ""))

    def revert(self) -> None:
        if self.editing_id and self.tree.exists(self.editing_id):
            self.tree.selection_set(self.editing_id)
            self.on_select()
        else:
            self.new()

    def record(self) -> dict[str, str] | None:
        row = {
            "metric_id": self.metric_id.get().strip(),
            "display_name": self.display_name.get().strip(),
            "description": self.description.get("1.0", tk.END).strip(),
            "owner_system": self.owner_system.get().strip(),
            "internal_min": self.internal_min.get().strip(),
            "internal_max": self.internal_max.get().strip(),
            "default_value": self.default_value.get().strip(),
            "polarity": self.polarity.get().strip(),
            "ui_display_mode": self.display_mode.get().strip(),
            "update_notes": self.update_notes.get("1.0", tk.END).strip(),
            "active": "TRUE" if self.active.get() else "FALSE",
        }

        errors: list[str] = []

        if not ID_PATTERN.fullmatch(row["metric_id"]):
            errors.append(
                "Metric ID must begin with an uppercase letter and use only "
                "uppercase letters, digits, or underscores."
            )

        if not row["display_name"]:
            errors.append("Display Name is required.")

        if not row["description"]:
            errors.append("Description is required.")

        if not row["owner_system"]:
            errors.append("Owner System is required.")

        try:
            minimum = int(row["internal_min"])
            maximum = int(row["internal_max"])
            default = int(row["default_value"])

            if minimum > maximum:
                errors.append("Internal Minimum cannot exceed Internal Maximum.")

            if not minimum <= default <= maximum:
                errors.append(
                    "Default Value must be inside the inclusive internal range."
                )

        except ValueError:
            errors.append(
                "Internal Minimum, Internal Maximum, and Default Value must all be integers."
            )

        if row["polarity"] not in ("HIGHER_IS_BETTER", "LOWER_IS_BETTER"):
            errors.append("Select a valid Metric Polarity.")

        if row["ui_display_mode"] not in ("TIERED_BAR",):
            errors.append("Select a valid UI Display Mode.")

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
        with tempfile.TemporaryDirectory(prefix="doda-metric-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)

            for filename in FILES:
                source = (
                    candidate
                    if filename == "metrics.csv"
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
            if row["metric_id"] != self.editing_id:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Metric ID cannot change after creation.",
                )
                return

            rows = [
                row if item.get("metric_id") == self.editing_id else item
                for item in rows
            ]

            action = "updated"

        else:
            if any(
                item.get("metric_id") == row["metric_id"]
                for item in rows
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Metric ID already exists.",
                )
                return

            rows.append(row)
            action = "added"

        temporary = self.app.source_directory / (
            f".metrics-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log("Metric candidate validation output:")

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Metric candidate validation failed. Source CSV was "
                        "unchanged.\n\nReview Activity Log for details."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "metrics_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_id = row["metric_id"]

            self.app.log(f"Created metric backup: {backup}")
            self.app.log(f"Metric {action}: {row['metric_id']}")

            self.app.refresh_all(False)

            valid, output = self.post_validate()

            self.app.log(
                f"Post-save metric validation exit code: {0 if valid else 1}"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            self.app.refresh_all(False)

            if valid:
                messagebox.showinfo(
                    "DoDA Content Workbench",
                    (
                        f"Metric '{row['metric_id']}' {action}.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Metric {action}, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"METRIC SAVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to save metric.\n\n{error}",
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
                "Select an existing metric before using Remove Metric.",
            )
            return

        metric_id = self.editing_id

        confirmed = messagebox.askyesno(
            "Remove Department Metric?",
            (
                f"ARE YOU SURE you want to remove '{metric_id}'?\n\n"
                "Removal is blocked if metric tiers still reference this metric."
            ),
            icon="warning",
            default=messagebox.NO,
        )

        if not confirmed:
            self.app.log(f"Remove Metric cancelled for '{metric_id}'.")
            return

        rows = [
            row
            for row in self.rows()
            if row.get("metric_id") != metric_id
        ]

        temporary = self.app.source_directory / (
            f".metrics-remove-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                f"Metric removal candidate validation output for '{metric_id}':"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        f"Removal of '{metric_id}' was blocked by validation.\n\n"
                        "Metric tier references or other source relationships "
                        "must be removed first.\n\n"
                        "Source CSV was unchanged."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "metrics_before_remove_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_id = None

            self.app.log(f"Created metric pre-removal backup: {backup}")
            self.app.log(f"Removed metric: {metric_id}")

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
                        f"Metric '{metric_id}' removed.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Metric '{metric_id}' removed, but post-save validation "
                        f"failed.\n\nBackup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"METRIC REMOVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to remove metric.\n\n{error}",
            )

        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def open_backups(self) -> None:
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_metrics_editor(app: Any) -> None:
    editor = MetricsEditor(app)

    app.metrics_editor = editor

    if str(app.metrics_tab) not in app.notebook.tabs():
        app.notebook.add(
            app.metrics_tab,
            text="Metrics - Editor",
        )
    else:
        app.notebook.tab(
            app.metrics_tab,
            text="Metrics - Editor",
        )

    app.update_metrics = editor.update





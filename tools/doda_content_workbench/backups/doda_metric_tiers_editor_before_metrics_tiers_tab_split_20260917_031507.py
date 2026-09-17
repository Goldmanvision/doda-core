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
    "tier_id",
    "min_inclusive",
    "max_inclusive",
    "display_label",
    "short_status",
    "ui_color_key",
    "flavor_text_id",
    "sort_order",
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


class MetricTiersEditor:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.editing_key: tuple[str, str] | None = None

        self.metric_id = tk.StringVar()
        self.tier_id = tk.StringVar()
        self.minimum = tk.StringVar()
        self.maximum = tk.StringVar()
        self.display_label = tk.StringVar()
        self.short_status = tk.StringVar()
        self.color_key = tk.StringVar()
        self.flavor_text_id = tk.StringVar()
        self.sort_order = tk.StringVar()

        self.build()

    def source_path(self) -> Path:
        return self.app.source_directory / "metric_tiers.csv"

    def backup_directory(self) -> Path:
        return self.app.project_root / "data_authoring" / "backups" / "metric_tiers"

    def rows(self) -> list[dict[str, str]]:
        return [dict(row) for row in self.app.tables.get("metric_tiers", [])]

    def metric_ids(self) -> list[str]:
        return sorted(
            row.get("metric_id", "")
            for row in self.app.tables.get("metrics", [])
            if row.get("metric_id", "")
        )

    def flavor_ids(self) -> list[str]:
        return sorted(
            row.get("flavor_text_id", "")
            for row in self.app.tables.get("flavor_text", [])
            if row.get("flavor_text_id", "")
        )

    def build(self) -> None:
        for child in self.app.metrics_tab.winfo_children():
            child.destroy()

        tab = self.app.metrics_tab
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(tab, text="Metric Tiers", padding=8)
        editor_frame = ttk.LabelFrame(tab, text="Metric Tier Editor", padding=10)

        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        editor_frame.grid(row=0, column=1, sticky=tk.NSEW)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("metric", "tier", "range", "label", "sort"),
            show="headings",
            selectmode="browse",
        )

        columns = (
            ("metric", "Metric", 165),
            ("tier", "Tier ID", 145),
            ("range", "Inclusive Range", 130),
            ("label", "Display Label", 190),
            ("sort", "Sort", 55),
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

        label("Metric:", 0)

        self.metric_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.metric_id,
            state="readonly",
            values=self.metric_ids(),
        )

        self.metric_combo.grid(
            row=0,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Tier ID:", 1)

        self.tier_entry = ttk.Entry(
            editor_frame,
            textvariable=self.tier_id,
        )

        self.tier_entry.grid(
            row=1,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        ttk.Label(
            editor_frame,
            text="Metric + Tier ID are immutable after creation.",
            foreground="#9da7b3",
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
        )

        label("Inclusive Range:", 3)

        range_frame = ttk.Frame(editor_frame)
        range_frame.grid(
            row=3,
            column=1,
            sticky=tk.W,
            pady=(0, 8),
        )

        ttk.Label(range_frame, text="Min").grid(row=0, column=0)
        ttk.Entry(
            range_frame,
            textvariable=self.minimum,
            width=10,
        ).grid(row=0, column=1, padx=(4, 12))

        ttk.Label(range_frame, text="Max").grid(row=0, column=2)
        ttk.Entry(
            range_frame,
            textvariable=self.maximum,
            width=10,
        ).grid(row=0, column=3, padx=(4, 0))

        label("Display Label:", 4)

        ttk.Entry(
            editor_frame,
            textvariable=self.display_label,
        ).grid(
            row=4,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Short Status:", 5)

        self.short_status_text = tk.Text(
            editor_frame,
            height=3,
            wrap=tk.WORD,
            background="#0d1117",
            foreground="#e6edf3",
            insertbackground="#e6edf3",
            highlightbackground="#3b4754",
            highlightcolor="#58a6ff",
        )

        self.short_status_text.grid(
            row=5,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("UI Color Key:", 6)

        ttk.Entry(
            editor_frame,
            textvariable=self.color_key,
        ).grid(
            row=6,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Flavor Text:", 7)

        self.flavor_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.flavor_text_id,
            state="readonly",
            values=self.flavor_ids(),
        )

        self.flavor_combo.grid(
            row=7,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Sort Order:", 8)

        ttk.Entry(
            editor_frame,
            textvariable=self.sort_order,
            width=10,
        ).grid(
            row=8,
            column=1,
            sticky=tk.W,
            pady=(0, 8),
        )

        buttons = ttk.Frame(editor_frame)
        buttons.grid(
            row=9,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(8, 0),
        )

        ttk.Button(
            buttons,
            text="Add Tier",
            command=self.new,
        ).pack(side=tk.LEFT)

        ttk.Button(
            buttons,
            text="Save Tier",
            command=self.save,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Remove Tier",
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
                "Candidate validation enforces complete metric coverage, "
                "contiguous ranges, no gaps, and no overlaps."
            ),
            foreground="#9da7b3",
            wraplength=390,
        ).grid(
            row=10,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(12, 0),
        )

        self.new()

    def update(self) -> None:
        selected = self.editing_key

        self.metric_combo.configure(values=self.metric_ids())
        self.flavor_combo.configure(values=self.flavor_ids())

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = sorted(
            self.rows(),
            key=lambda row: (
                row.get("metric_id", ""),
                int(row.get("sort_order", "999999")),
                row.get("tier_id", ""),
            ),
        )

        for row in rows:
            metric_id = row.get("metric_id", "")
            tier_id = row.get("tier_id", "")
            key = f"{metric_id}::{tier_id}"

            self.tree.insert(
                "",
                tk.END,
                iid=key,
                values=(
                    metric_id,
                    tier_id,
                    (
                        f"{row.get('min_inclusive', '')}"
                        f" - {row.get('max_inclusive', '')}"
                    ),
                    row.get("display_label", ""),
                    row.get("sort_order", ""),
                ),
            )

        if selected:
            key = f"{selected[0]}::{selected[1]}"

            if self.tree.exists(key):
                self.tree.selection_set(key)
                self.tree.focus(key)

    def next_sort_order(self, metric_id: str) -> int:
        values: list[int] = []

        for row in self.rows():
            if row.get("metric_id") != metric_id:
                continue

            try:
                values.append(int(row.get("sort_order", "")))
            except ValueError:
                pass

        return max(values, default=0) + 1

    def new(self) -> None:
        self.editing_key = None

        self.metric_combo.configure(state="readonly")
        self.tier_entry.configure(state=tk.NORMAL)

        metric_ids = self.metric_ids()

        self.metric_id.set(metric_ids[0] if metric_ids else "")
        self.tier_id.set("")
        self.minimum.set("")
        self.maximum.set("")
        self.display_label.set("")
        self.color_key.set("STATUS_GRAY")
        self.flavor_text_id.set("")
        self.sort_order.set(
            str(self.next_sort_order(self.metric_id.get()))
            if self.metric_id.get()
            else "1"
        )

        self.short_status_text.delete("1.0", tk.END)
        self.tier_entry.focus_set()

    def on_select(self, _event: Any = None) -> None:
        selection = self.tree.selection()

        if not selection:
            return

        metric_id, tier_id = selection[0].split("::", 1)

        row = next(
            (
                item
                for item in self.rows()
                if item.get("metric_id") == metric_id
                and item.get("tier_id") == tier_id
            ),
            None,
        )

        if row is None:
            return

        self.editing_key = (metric_id, tier_id)

        self.metric_combo.configure(state=tk.DISABLED)
        self.tier_entry.configure(state=tk.NORMAL)

        self.metric_id.set(metric_id)
        self.tier_id.set(tier_id)

        self.tier_entry.configure(state=tk.DISABLED)

        self.minimum.set(row.get("min_inclusive", ""))
        self.maximum.set(row.get("max_inclusive", ""))
        self.display_label.set(row.get("display_label", ""))
        self.color_key.set(row.get("ui_color_key", ""))
        self.flavor_text_id.set(row.get("flavor_text_id", ""))
        self.sort_order.set(row.get("sort_order", ""))

        self.short_status_text.delete("1.0", tk.END)
        self.short_status_text.insert(
            "1.0",
            row.get("short_status", ""),
        )

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
            "metric_id": self.metric_id.get().strip(),
            "tier_id": self.tier_id.get().strip(),
            "min_inclusive": self.minimum.get().strip(),
            "max_inclusive": self.maximum.get().strip(),
            "display_label": self.display_label.get().strip(),
            "short_status": self.short_status_text.get("1.0", tk.END).strip(),
            "ui_color_key": self.color_key.get().strip(),
            "flavor_text_id": self.flavor_text_id.get().strip(),
            "sort_order": self.sort_order.get().strip(),
        }

        errors: list[str] = []

        if row["metric_id"] not in self.metric_ids():
            errors.append("Select a valid Metric.")

        if not ID_PATTERN.fullmatch(row["tier_id"]):
            errors.append(
                "Tier ID must begin with an uppercase letter and use only "
                "uppercase letters, digits, or underscores."
            )

        if not row["display_label"]:
            errors.append("Display Label is required.")

        if not row["short_status"]:
            errors.append("Short Status is required.")

        if not row["ui_color_key"]:
            errors.append("UI Color Key is required.")

        if row["flavor_text_id"] not in self.flavor_ids():
            errors.append("Select a valid Flavor Text ID.")

        try:
            minimum = int(row["min_inclusive"])
            maximum = int(row["max_inclusive"])

            if minimum > maximum:
                errors.append("Minimum cannot exceed Maximum.")

        except ValueError:
            errors.append("Minimum and Maximum must be integers.")

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
        with tempfile.TemporaryDirectory(prefix="doda-tier-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)

            for filename in FILES:
                source = (
                    candidate
                    if filename == "metric_tiers.csv"
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
                row["metric_id"] != self.editing_key[0]
                or row["tier_id"] != self.editing_key[1]
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Metric ID and Tier ID cannot change after creation.",
                )
                return

            rows = [
                row
                if (
                    item.get("metric_id") == self.editing_key[0]
                    and item.get("tier_id") == self.editing_key[1]
                )
                else item
                for item in rows
            ]

            action = "updated"

        else:
            if any(
                item.get("metric_id") == row["metric_id"]
                and item.get("tier_id") == row["tier_id"]
                for item in rows
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "This Metric ID and Tier ID combination already exists.",
                )
                return

            rows.append(row)
            action = "added"

        temporary = self.app.source_directory / (
            f".metric-tiers-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log("Metric Tier candidate validation output:")

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Metric Tier candidate validation failed. Source CSV "
                        "was unchanged.\n\nReview Activity Log for details."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "metric_tiers_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_key = (
                row["metric_id"],
                row["tier_id"],
            )

            self.app.log(f"Created Metric Tier backup: {backup}")
            self.app.log(
                f"Metric Tier {action}: "
                f"{row['metric_id']} / {row['tier_id']}"
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
                        f"Metric Tier '{row['metric_id']} / {row['tier_id']}' "
                        f"{action}.\n\nBackup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Metric Tier {action}, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"METRIC TIER SAVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to save Metric Tier.\n\n{error}",
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
                "Select an existing Metric Tier before using Remove Tier.",
            )
            return

        metric_id, tier_id = self.editing_key

        confirmed = messagebox.askyesno(
            "Remove Metric Tier?",
            (
                f"ARE YOU SURE you want to remove '{metric_id} / {tier_id}'?\n\n"
                "Removal will be blocked if it leaves incomplete metric coverage."
            ),
            icon="warning",
            default=messagebox.NO,
        )

        if not confirmed:
            self.app.log(
                f"Remove Metric Tier cancelled for '{metric_id} / {tier_id}'."
            )
            return

        rows = [
            row
            for row in self.rows()
            if not (
                row.get("metric_id") == metric_id
                and row.get("tier_id") == tier_id
            )
        ]

        temporary = self.app.source_directory / (
            f".metric-tiers-remove-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                "Metric Tier removal candidate validation output "
                f"for '{metric_id} / {tier_id}':"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Removal was blocked by validation.\n\n"
                        "A metric must retain complete contiguous tier coverage. "
                        "Source CSV was unchanged."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "metric_tiers_before_remove_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_key = None

            self.app.log(f"Created pre-removal Metric Tier backup: {backup}")
            self.app.log(
                f"Removed Metric Tier: {metric_id} / {tier_id}"
            )

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
                        f"Metric Tier '{metric_id} / {tier_id}' removed.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        "Metric Tier removed, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"METRIC TIER REMOVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to remove Metric Tier.\n\n{error}",
            )

        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def open_backups(self) -> None:
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_metric_tiers_editor(app: Any) -> None:
    editor = MetricTiersEditor(app)

    app.metric_tiers_editor = editor
    app.update_metrics = editor.update

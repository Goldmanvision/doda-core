from __future__ import annotations

import csv
import os
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
    "qualification_id",
    "min_contributors",
    "preferred_contributors",
    "max_contributors",
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


class CapabilityStaffingRulesEditor:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.editing_key: tuple[str, str] | None = None

        self.capability_id = tk.StringVar()
        self.qualification_id = tk.StringVar()
        self.minimum = tk.StringVar()
        self.preferred = tk.StringVar()
        self.maximum = tk.StringVar()
        self.sort_order = tk.StringVar()
        self.active = tk.BooleanVar(value=True)

        self.build()

    def source_path(self) -> Path:
        return self.app.source_directory / "capability_staffing_rules.csv"

    def backup_directory(self) -> Path:
        return (
            self.app.project_root
            / "data_authoring"
            / "backups"
            / "capability_staffing_rules"
        )

    def rows(self) -> list[dict[str, str]]:
        return [
            dict(row)
            for row in self.app.tables.get("capability_staffing_rules", [])
        ]

    @staticmethod
    def integer_or_default(value: str, default: int) -> int:
        try:
            return int((value or "").strip())
        except ValueError:
            return default

    def active_capability_rows(self) -> list[dict[str, str]]:
        return sorted(
            (
                row
                for row in self.app.tables.get("capabilities", [])
                if row.get("capability_id", "")
                and row.get("active", "").upper() == "TRUE"
            ),
            key=lambda row: (
                self.integer_or_default(row.get("sort_order", ""), 999999),
                row.get("capability_id", ""),
            ),
        )

    def capability_ids(self) -> list[str]:
        return [
            row.get("capability_id", "")
            for row in self.active_capability_rows()
        ]

    def active_qualification_rows(self) -> list[dict[str, str]]:
        return sorted(
            (
                row
                for row in self.app.tables.get("qualification_catalog", [])
                if row.get("qualification_id", "")
                and row.get("active", "").upper() == "TRUE"
            ),
            key=lambda row: (
                self.integer_or_default(row.get("sort_order", ""), 999999),
                row.get("qualification_id", ""),
            ),
        )

    def qualification_ids(self) -> list[str]:
        return [
            row.get("qualification_id", "")
            for row in self.active_qualification_rows()
        ]

    def capability_display_values(self) -> dict[str, str]:
        return {
            row.get("capability_id", ""): (
                f"{row.get('capability_id', '')} — {row.get('display_name', '')}"
            )
            for row in self.active_capability_rows()
        }

    def qualification_display_values(self) -> dict[str, str]:
        return {
            row.get("qualification_id", ""): (
                f"{row.get('qualification_id', '')} — {row.get('display_name', '')}"
            )
            for row in self.active_qualification_rows()
        }

    def build(self) -> None:
        for child in self.app.capability_staffing_rules_tab.winfo_children():
            child.destroy()

        tab = self.app.capability_staffing_rules_tab
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(
            tab,
            text="Capability Staffing Rules",
            padding=8,
        )
        editor_frame = ttk.LabelFrame(
            tab,
            text="Staffing Rule Editor",
            padding=10,
        )

        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        editor_frame.grid(row=0, column=1, sticky=tk.NSEW)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)

        self.tree = ttk.Treeview(
            list_frame,
            columns=(
                "capability",
                "qualification",
                "minimum",
                "preferred",
                "maximum",
                "sort",
                "active",
            ),
            show="headings",
            selectmode="browse",
        )

        columns = (
            ("capability", "Capability", 190),
            ("qualification", "Qualification", 175),
            ("minimum", "Min", 55),
            ("preferred", "Preferred", 80),
            ("maximum", "Max", 55),
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

        label("Capability:", 0)

        self.capability_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.capability_id,
            state="readonly",
            values=self.capability_ids(),
        )
        self.capability_combo.grid(
            row=0,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )
        self.capability_combo.bind(
            "<<ComboboxSelected>>",
            self.on_capability_changed,
        )

        label("Qualification:", 1)

        self.qualification_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.qualification_id,
            state="readonly",
            values=self.qualification_ids(),
        )
        self.qualification_combo.grid(
            row=1,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        ttk.Label(
            editor_frame,
            text="Capability + Qualification are immutable after creation.",
            foreground="#9da7b3",
            wraplength=360,
        ).grid(
            row=2,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
        )

        label("Contributor Range:", 3)

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
            width=8,
        ).grid(row=0, column=1, padx=(4, 10))

        ttk.Label(range_frame, text="Preferred").grid(row=0, column=2)
        ttk.Entry(
            range_frame,
            textvariable=self.preferred,
            width=8,
        ).grid(row=0, column=3, padx=(4, 10))

        ttk.Label(range_frame, text="Max").grid(row=0, column=4)
        ttk.Entry(
            range_frame,
            textvariable=self.maximum,
            width=8,
        ).grid(row=0, column=5, padx=(4, 0))

        ttk.Label(
            editor_frame,
            text="Required range: 0 ≤ Min ≤ Preferred ≤ Max.",
            foreground="#9da7b3",
        ).grid(
            row=4,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
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
            text="This staffing rule is active",
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
            text="Add Rule",
            command=self.new,
        ).pack(side=tk.LEFT)

        ttk.Button(
            buttons,
            text="Save Rule",
            command=self.save,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Remove Rule",
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
                "Candidate validation requires every active Capability to retain "
                "at least one active global staffing rule. Removal can also be "
                "blocked by Facility Capability staffing overrides."
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

        self.capability_combo.configure(values=self.capability_ids())
        self.qualification_combo.configure(values=self.qualification_ids())

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = sorted(
            self.rows(),
            key=lambda row: (
                row.get("capability_id", ""),
                self.integer_or_default(row.get("sort_order", ""), 999999),
                row.get("qualification_id", ""),
            ),
        )

        for row in rows:
            capability_id = row.get("capability_id", "")
            qualification_id = row.get("qualification_id", "")
            key = f"{capability_id}::{qualification_id}"

            self.tree.insert(
                "",
                tk.END,
                iid=key,
                values=(
                    capability_id,
                    qualification_id,
                    row.get("min_contributors", ""),
                    row.get("preferred_contributors", ""),
                    row.get("max_contributors", ""),
                    row.get("sort_order", ""),
                    row.get("active", ""),
                ),
            )

        if selected:
            key = f"{selected[0]}::{selected[1]}"

            if self.tree.exists(key):
                self.tree.selection_set(key)
                self.tree.focus(key)

    def next_sort_order(self, capability_id: str) -> int:
        values: list[int] = []

        for row in self.rows():
            if row.get("capability_id", "") != capability_id:
                continue

            try:
                values.append(int(row.get("sort_order", "")))
            except ValueError:
                pass

        return max(values, default=0) + 1

    def on_capability_changed(self, _event: Any = None) -> None:
        capability_id = self.capability_id.get().strip()

        if capability_id:
            self.sort_order.set(str(self.next_sort_order(capability_id)))

    def new(self) -> None:
        self.editing_key = None

        self.capability_combo.configure(state="readonly")
        self.qualification_combo.configure(state="readonly")

        capabilities = self.capability_ids()
        qualifications = self.qualification_ids()

        self.capability_id.set(capabilities[0] if capabilities else "")
        self.qualification_id.set(
            qualifications[0] if qualifications else ""
        )
        self.minimum.set("0")
        self.preferred.set("1")
        self.maximum.set("1")
        self.sort_order.set(
            str(self.next_sort_order(self.capability_id.get()))
            if self.capability_id.get()
            else "1"
        )
        self.active.set(True)

        self.capability_combo.focus_set()

    def on_select(self, _event: Any = None) -> None:
        selection = self.tree.selection()

        if not selection:
            return

        capability_id, qualification_id = selection[0].split("::", 1)

        row = next(
            (
                item
                for item in self.rows()
                if item.get("capability_id", "") == capability_id
                and item.get("qualification_id", "") == qualification_id
            ),
            None,
        )

        if row is None:
            return

        self.editing_key = (capability_id, qualification_id)

        self.capability_combo.configure(state=tk.DISABLED)
        self.qualification_combo.configure(state=tk.DISABLED)

        self.capability_id.set(capability_id)
        self.qualification_id.set(qualification_id)
        self.minimum.set(row.get("min_contributors", ""))
        self.preferred.set(row.get("preferred_contributors", ""))
        self.maximum.set(row.get("max_contributors", ""))
        self.sort_order.set(row.get("sort_order", ""))
        self.active.set(row.get("active", "").upper() == "TRUE")

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
            "capability_id": self.capability_id.get().strip(),
            "qualification_id": self.qualification_id.get().strip(),
            "min_contributors": self.minimum.get().strip(),
            "preferred_contributors": self.preferred.get().strip(),
            "max_contributors": self.maximum.get().strip(),
            "sort_order": self.sort_order.get().strip(),
            "active": "TRUE" if self.active.get() else "FALSE",
        }

        errors: list[str] = []

        if row["capability_id"] not in self.capability_ids():
            errors.append("Select a valid active Capability.")

        if row["qualification_id"] not in self.qualification_ids():
            errors.append("Select a valid active Qualification.")

        try:
            minimum = int(row["min_contributors"])
            preferred = int(row["preferred_contributors"])
            maximum = int(row["max_contributors"])

            if not 0 <= minimum <= preferred <= maximum:
                errors.append(
                    "Contributor counts must satisfy "
                    "0 ≤ Min ≤ Preferred ≤ Max."
                )
        except ValueError:
            errors.append(
                "Min, Preferred, and Max Contributors must be whole numbers."
            )

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
            prefix="doda-capability-staffing-"
        ) as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)

            for filename in FILES:
                source = (
                    candidate
                    if filename == "capability_staffing_rules.csv"
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
                row["capability_id"] != self.editing_key[0]
                or row["qualification_id"] != self.editing_key[1]
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Capability ID and Qualification ID cannot change "
                        "after creation."
                    ),
                )
                return

            rows = [
                row
                if (
                    item.get("capability_id", "") == self.editing_key[0]
                    and item.get("qualification_id", "") == self.editing_key[1]
                )
                else item
                for item in rows
            ]
            action = "updated"
        else:
            if any(
                item.get("capability_id", "") == row["capability_id"]
                and item.get("qualification_id", "") == row["qualification_id"]
                for item in rows
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "This Capability and Qualification staffing rule "
                        "already exists."
                    ),
                )
                return

            rows.append(row)
            action = "added"

        rows.sort(
            key=lambda item: (
                item.get("capability_id", ""),
                self.integer_or_default(item.get("sort_order", ""), 999999),
                item.get("qualification_id", ""),
            )
        )

        temporary = self.app.source_directory / (
            f".capability-staffing-rules-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                "Capability Staffing Rule candidate validation output:"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Capability Staffing Rule candidate validation failed. "
                        "Source CSV was unchanged.\n\nReview Activity Log for "
                        "details."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "capability_staffing_rules_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_key = (
                row["capability_id"],
                row["qualification_id"],
            )

            self.app.log(
                f"Created Capability Staffing Rule backup: {backup}"
            )
            self.app.log(
                "Capability Staffing Rule "
                f"{action}: {row['capability_id']} / "
                f"{row['qualification_id']}"
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
                        "Capability Staffing Rule "
                        f"'{row['capability_id']} / "
                        f"{row['qualification_id']}' {action}.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        "Capability Staffing Rule "
                        f"{action}, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(
                f"CAPABILITY STAFFING RULE SAVE ERROR: {error}"
            )
            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to save Capability Staffing Rule.\n\n{error}",
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
                (
                    "Select an existing Capability Staffing Rule before using "
                    "Remove Rule."
                ),
            )
            return

        capability_id, qualification_id = self.editing_key

        confirmed = messagebox.askyesno(
            "Remove Capability Staffing Rule?",
            (
                "ARE YOU SURE you want to remove this global staffing rule?\n\n"
                f"Capability: {capability_id}\n"
                f"Qualification: {qualification_id}\n\n"
                "Removal will be blocked if it leaves an active Capability "
                "without an active global rule or breaks a staffing override."
            ),
            icon="warning",
            default=messagebox.NO,
        )

        if not confirmed:
            self.app.log(
                "Remove Capability Staffing Rule cancelled for "
                f"'{capability_id} / {qualification_id}'."
            )
            return

        rows = [
            row
            for row in self.rows()
            if not (
                row.get("capability_id", "") == capability_id
                and row.get("qualification_id", "") == qualification_id
            )
        ]

        temporary = self.app.source_directory / (
            f".capability-staffing-rules-remove-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                "Capability Staffing Rule removal candidate validation output "
                f"for '{capability_id} / {qualification_id}':"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Capability Staffing Rule removal was blocked by "
                        "validation.\n\nSource CSV was unchanged."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "capability_staffing_rules_before_remove_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_key = None

            self.app.log(
                "Created pre-removal Capability Staffing Rule backup: "
                f"{backup}"
            )
            self.app.log(
                "Removed Capability Staffing Rule: "
                f"{capability_id} / {qualification_id}"
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
                        "Capability Staffing Rule "
                        f"'{capability_id} / {qualification_id}' removed.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        "Capability Staffing Rule removed, but post-save "
                        f"validation failed.\n\nBackup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(
                f"CAPABILITY STAFFING RULE REMOVE ERROR: {error}"
            )
            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to remove Capability Staffing Rule.\n\n{error}",
            )
        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def open_backups(self) -> None:
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_capability_staffing_rules_editor(app: Any) -> None:
    editor = CapabilityStaffingRulesEditor(app)
    app.capability_staffing_rules_editor = editor
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
    "facility_id",
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
FILES = tuple(FILES) + ("equipment_families.csv",)


class FacilityCapabilityStaffingOverridesEditor:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.editing_key: tuple[str, str, str] | None = None

        self.installation_choice = tk.StringVar()
        self.qualification_id = tk.StringVar()
        self.minimum = tk.StringVar()
        self.preferred = tk.StringVar()
        self.maximum = tk.StringVar()
        self.sort_order = tk.StringVar()
        self.active = tk.BooleanVar(value=True)
        self.baseline_text = tk.StringVar(
            value="Select an installation and qualification to view its global baseline."
        )

        self.build()

    def source_path(self) -> Path:
        return (
            self.app.source_directory
            / "facility_capability_staffing_overrides.csv"
        )

    def backup_directory(self) -> Path:
        return (
            self.app.project_root
            / "data_authoring"
            / "backups"
            / "facility_capability_staffing_overrides"
        )

    def rows(self) -> list[dict[str, str]]:
        return [
            dict(row)
            for row in self.app.tables.get(
                "facility_capability_staffing_overrides",
                [],
            )
        ]

    @staticmethod
    def integer_or_default(value: str, default: int) -> int:
        try:
            return int((value or "").strip())
        except ValueError:
            return default

    def active_facility_ids(self) -> set[str]:
        return {
            row.get("facility_id", "")
            for row in self.app.tables.get("facilities", [])
            if row.get("facility_id", "")
            and row.get("active", "").upper() == "TRUE"
        }

    def active_capability_ids(self) -> set[str]:
        return {
            row.get("capability_id", "")
            for row in self.app.tables.get("capabilities", [])
            if row.get("capability_id", "")
            and row.get("active", "").upper() == "TRUE"
        }

    def active_qualification_ids(self) -> set[str]:
        return {
            row.get("qualification_id", "")
            for row in self.app.tables.get("qualification_catalog", [])
            if row.get("qualification_id", "")
            and row.get("active", "").upper() == "TRUE"
        }

    def active_installations(self) -> list[dict[str, str]]:
        active_facilities = self.active_facility_ids()
        active_capabilities = self.active_capability_ids()

        rows = [
            row
            for row in self.app.tables.get("facility_capabilities", [])
            if row.get("facility_id", "") in active_facilities
            and row.get("capability_id", "") in active_capabilities
            and row.get("active", "").upper() == "TRUE"
        ]

        return sorted(
            rows,
            key=lambda row: (
                row.get("facility_id", ""),
                self.integer_or_default(row.get("sort_order", ""), 999999),
                row.get("capability_id", ""),
            ),
        )

    def installation_key(self, facility_id: str, capability_id: str) -> str:
        return f"{facility_id}::{capability_id}"

    def selected_installation_parts(self) -> tuple[str, str]:
        value = self.installation_choice.get().strip()

        if "::" not in value:
            return "", ""

        return tuple(value.split("::", 1))

    def installation_choices(self) -> list[str]:
        return [
            self.installation_key(
                row.get("facility_id", ""),
                row.get("capability_id", ""),
            )
            for row in self.active_installations()
        ]

    def installation_labels(self) -> dict[str, str]:
        facility_names = {
            row.get("facility_id", ""): row.get("display_name", "")
            for row in self.app.tables.get("facilities", [])
        }
        capability_names = {
            row.get("capability_id", ""): row.get("display_name", "")
            for row in self.app.tables.get("capabilities", [])
        }

        labels: dict[str, str] = {}

        for row in self.active_installations():
            facility_id = row.get("facility_id", "")
            capability_id = row.get("capability_id", "")
            key = self.installation_key(facility_id, capability_id)

            labels[key] = (
                f"{facility_id} — {facility_names.get(facility_id, '')}"
                f"\n{capability_id} — {capability_names.get(capability_id, '')}"
            )

        return labels

    def active_global_rules(self) -> list[dict[str, str]]:
        active_capabilities = self.active_capability_ids()
        active_qualifications = self.active_qualification_ids()

        rows = [
            row
            for row in self.app.tables.get("capability_staffing_rules", [])
            if row.get("capability_id", "") in active_capabilities
            and row.get("qualification_id", "") in active_qualifications
            and row.get("active", "").upper() == "TRUE"
        ]

        return sorted(
            rows,
            key=lambda row: (
                row.get("capability_id", ""),
                self.integer_or_default(row.get("sort_order", ""), 999999),
                row.get("qualification_id", ""),
            ),
        )

    def rule_for(
        self,
        capability_id: str,
        qualification_id: str,
    ) -> dict[str, str] | None:
        return next(
            (
                row
                for row in self.active_global_rules()
                if row.get("capability_id", "") == capability_id
                and row.get("qualification_id", "") == qualification_id
            ),
            None,
        )

    def qualification_choices_for_selected_installation(self) -> list[str]:
        _, capability_id = self.selected_installation_parts()

        if not capability_id:
            return []

        return [
            row.get("qualification_id", "")
            for row in self.active_global_rules()
            if row.get("capability_id", "") == capability_id
        ]

    def qualification_display_values(self) -> dict[str, str]:
        return {
            row.get("qualification_id", ""): (
                f"{row.get('qualification_id', '')} — {row.get('display_name', '')}"
            )
            for row in self.app.tables.get("qualification_catalog", [])
            if row.get("qualification_id", "")
        }

    def installation_is_valid(
        self,
        facility_id: str,
        capability_id: str,
    ) -> bool:
        return any(
            row.get("facility_id", "") == facility_id
            and row.get("capability_id", "") == capability_id
            for row in self.active_installations()
        )

    def next_sort_order(self, facility_id: str, capability_id: str) -> int:
        values: list[int] = []

        for row in self.rows():
            if (
                row.get("facility_id", "") != facility_id
                or row.get("capability_id", "") != capability_id
            ):
                continue

            try:
                values.append(int(row.get("sort_order", "")))
            except ValueError:
                pass

        return max(values, default=0) + 1

    def build(self) -> None:
        for child in self.app.staffing_overrides_tab.winfo_children():
            child.destroy()

        tab = self.app.staffing_overrides_tab
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(
            tab,
            text="Facility Capability Staffing Overrides",
            padding=8,
        )
        editor_frame = ttk.LabelFrame(
            tab,
            text="Staffing Override Editor",
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
                "facility",
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
            ("facility", "Facility", 165),
            ("capability", "Capability", 180),
            ("qualification", "Qualification", 165),
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

        label("Installation:", 0)

        self.installation_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.installation_choice,
            state="readonly",
            values=self.installation_choices(),
        )
        self.installation_combo.grid(
            row=0,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )
        self.installation_combo.bind(
            "<<ComboboxSelected>>",
            self.on_installation_changed,
        )

        self.installation_hint = ttk.Label(
            editor_frame,
            text="Select an active Facility Capability installation.",
            foreground="#9da7b3",
            justify=tk.LEFT,
            wraplength=360,
        )
        self.installation_hint.grid(
            row=1,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
        )

        label("Qualification:", 2)

        self.qualification_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.qualification_id,
            state="readonly",
            values=[],
        )
        self.qualification_combo.grid(
            row=2,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )
        self.qualification_combo.bind(
            "<<ComboboxSelected>>",
            self.on_qualification_changed,
        )

        ttk.Label(
            editor_frame,
            text=(
                "Installation + Qualification are immutable after creation. "
                "Only global-rule qualifications are offered."
            ),
            foreground="#9da7b3",
            wraplength=360,
        ).grid(
            row=3,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
        )

        label("Global Baseline:", 4)

        ttk.Label(
            editor_frame,
            textvariable=self.baseline_text,
            foreground="#9da7b3",
            justify=tk.LEFT,
            wraplength=360,
        ).grid(
            row=4,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
        )

        label("Override Range:", 5)

        range_frame = ttk.Frame(editor_frame)
        range_frame.grid(
            row=5,
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
            row=6,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
        )

        label("Sort Order:", 7)

        ttk.Entry(
            editor_frame,
            textvariable=self.sort_order,
            width=10,
        ).grid(
            row=7,
            column=1,
            sticky=tk.W,
            pady=(0, 8),
        )

        label("Active:", 8)

        ttk.Checkbutton(
            editor_frame,
            text="This facility-specific override is active",
            variable=self.active,
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
            text="Add Override",
            command=self.new,
        ).pack(side=tk.LEFT)

        ttk.Button(
            buttons,
            text="Save Override",
            command=self.save,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Remove Override",
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
                "Overrides are optional. They must refer to an active Facility "
                "Capability installation and an active global staffing rule."
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

        self.installation_combo.configure(
            values=self.installation_choices()
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = sorted(
            self.rows(),
            key=lambda row: (
                row.get("facility_id", ""),
                row.get("capability_id", ""),
                self.integer_or_default(row.get("sort_order", ""), 999999),
                row.get("qualification_id", ""),
            ),
        )

        for row in rows:
            facility_id = row.get("facility_id", "")
            capability_id = row.get("capability_id", "")
            qualification_id = row.get("qualification_id", "")
            key = f"{facility_id}::{capability_id}::{qualification_id}"

            self.tree.insert(
                "",
                tk.END,
                iid=key,
                values=(
                    facility_id,
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
            key = f"{selected[0]}::{selected[1]}::{selected[2]}"

            if self.tree.exists(key):
                self.tree.selection_set(key)
                self.tree.focus(key)

        self.refresh_dependent_fields()

    def refresh_dependent_fields(self) -> None:
        facility_id, capability_id = self.selected_installation_parts()
        qualifications = self.qualification_choices_for_selected_installation()

        self.qualification_combo.configure(values=qualifications)

        if self.qualification_id.get().strip() not in qualifications:
            self.qualification_id.set(
                qualifications[0] if qualifications else ""
            )

        labels = self.installation_labels()
        selected_key = self.installation_choice.get().strip()

        if selected_key:
            self.installation_hint.configure(
                text=labels.get(selected_key, selected_key)
            )
        else:
            self.installation_hint.configure(
                text="Select an active Facility Capability installation."
            )

        rule = self.rule_for(
            capability_id,
            self.qualification_id.get().strip(),
        )

        if rule is None:
            self.baseline_text.set(
                "No active global staffing baseline is available."
            )
        else:
            self.baseline_text.set(
                "Global rule: "
                f"Min {rule.get('min_contributors', '')}, "
                f"Preferred {rule.get('preferred_contributors', '')}, "
                f"Max {rule.get('max_contributors', '')}."
            )

    def on_installation_changed(self, _event: Any = None) -> None:
        facility_id, capability_id = self.selected_installation_parts()

        self.qualification_id.set("")
        self.refresh_dependent_fields()

        if facility_id and capability_id:
            self.sort_order.set(
                str(self.next_sort_order(facility_id, capability_id))
            )

    def on_qualification_changed(self, _event: Any = None) -> None:
        self.refresh_dependent_fields()

    def new(self) -> None:
        self.editing_key = None

        self.installation_combo.configure(state="readonly")
        self.qualification_combo.configure(state="readonly")

        installations = self.installation_choices()

        self.installation_choice.set(
            installations[0] if installations else ""
        )
        self.qualification_id.set("")
        self.minimum.set("0")
        self.preferred.set("1")
        self.maximum.set("1")
        self.active.set(True)

        self.refresh_dependent_fields()

        facility_id, capability_id = self.selected_installation_parts()

        self.sort_order.set(
            str(self.next_sort_order(facility_id, capability_id))
            if facility_id and capability_id
            else "1"
        )

        self.installation_combo.focus_set()

    def on_select(self, _event: Any = None) -> None:
        selection = self.tree.selection()

        if not selection:
            return

        facility_id, capability_id, qualification_id = selection[0].split(
            "::",
            2,
        )

        row = next(
            (
                item
                for item in self.rows()
                if item.get("facility_id", "") == facility_id
                and item.get("capability_id", "") == capability_id
                and item.get("qualification_id", "") == qualification_id
            ),
            None,
        )

        if row is None:
            return

        self.editing_key = (
            facility_id,
            capability_id,
            qualification_id,
        )

        self.installation_combo.configure(state=tk.DISABLED)
        self.qualification_combo.configure(state=tk.DISABLED)

        self.installation_choice.set(
            self.installation_key(facility_id, capability_id)
        )
        self.qualification_id.set(qualification_id)
        self.minimum.set(row.get("min_contributors", ""))
        self.preferred.set(row.get("preferred_contributors", ""))
        self.maximum.set(row.get("max_contributors", ""))
        self.sort_order.set(row.get("sort_order", ""))
        self.active.set(row.get("active", "").upper() == "TRUE")

        self.refresh_dependent_fields()

    def revert(self) -> None:
        if self.editing_key:
            key = (
                f"{self.editing_key[0]}::{self.editing_key[1]}::"
                f"{self.editing_key[2]}"
            )

            if self.tree.exists(key):
                self.tree.selection_set(key)
                self.on_select()
                return

        self.new()

    def record(self) -> dict[str, str] | None:
        facility_id, capability_id = self.selected_installation_parts()

        row = {
            "facility_id": facility_id,
            "capability_id": capability_id,
            "qualification_id": self.qualification_id.get().strip(),
            "min_contributors": self.minimum.get().strip(),
            "preferred_contributors": self.preferred.get().strip(),
            "max_contributors": self.maximum.get().strip(),
            "sort_order": self.sort_order.get().strip(),
            "active": "TRUE" if self.active.get() else "FALSE",
        }

        errors: list[str] = []

        if not self.installation_is_valid(
            row["facility_id"],
            row["capability_id"],
        ):
            errors.append(
                "Select a valid active Facility Capability installation."
            )

        if row["qualification_id"] not in self.active_qualification_ids():
            errors.append("Select a valid active Qualification.")

        if self.rule_for(
            row["capability_id"],
            row["qualification_id"],
        ) is None:
            errors.append(
                "The selected Qualification has no active global staffing "
                "rule for the selected Capability."
            )

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
            prefix="doda-staffing-override-"
        ) as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)

            for filename in FILES:
                source = (
                    candidate
                    if filename == (
                        "facility_capability_staffing_overrides.csv"
                    )
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
                row["facility_id"] != self.editing_key[0]
                or row["capability_id"] != self.editing_key[1]
                or row["qualification_id"] != self.editing_key[2]
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Facility, Capability, and Qualification cannot "
                        "change after creation."
                    ),
                )
                return

            rows = [
                row
                if (
                    item.get("facility_id", "") == self.editing_key[0]
                    and item.get("capability_id", "") == self.editing_key[1]
                    and item.get("qualification_id", "") == self.editing_key[2]
                )
                else item
                for item in rows
            ]
            action = "updated"
        else:
            if any(
                item.get("facility_id", "") == row["facility_id"]
                and item.get("capability_id", "") == row["capability_id"]
                and item.get("qualification_id", "") == row["qualification_id"]
                for item in rows
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "This Facility Capability Qualification override already exists.",
                )
                return

            rows.append(row)
            action = "added"

        rows.sort(
            key=lambda item: (
                item.get("facility_id", ""),
                item.get("capability_id", ""),
                self.integer_or_default(item.get("sort_order", ""), 999999),
                item.get("qualification_id", ""),
            )
        )

        temporary = self.app.source_directory / (
            f".facility-capability-staffing-overrides-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                "Facility Capability Staffing Override candidate validation output:"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Staffing Override candidate validation failed. "
                        "Source CSV was unchanged.\n\nReview Activity Log for "
                        "details."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "facility_capability_staffing_overrides_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_key = (
                row["facility_id"],
                row["capability_id"],
                row["qualification_id"],
            )

            self.app.log(
                f"Created Facility Capability Staffing Override backup: {backup}"
            )
            self.app.log(
                "Facility Capability Staffing Override "
                f"{action}: {row['facility_id']} / "
                f"{row['capability_id']} / {row['qualification_id']}"
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
                        "Facility Capability Staffing Override "
                        f"'{row['facility_id']} / {row['capability_id']} / "
                        f"{row['qualification_id']}' {action}.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        "Staffing Override "
                        f"{action}, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"STAFFING OVERRIDE SAVE ERROR: {error}")
            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to save Staffing Override.\n\n{error}",
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
                "Select an existing Staffing Override before using Remove.",
            )
            return

        facility_id, capability_id, qualification_id = self.editing_key

        confirmed = messagebox.askyesno(
            "Remove Staffing Override?",
            (
                "ARE YOU SURE you want to remove this facility-specific "
                "staffing override?\n\n"
                f"Facility: {facility_id}\n"
                f"Capability: {capability_id}\n"
                f"Qualification: {qualification_id}\n\n"
                "A timestamped backup will be created before removal."
            ),
            icon="warning",
            default=messagebox.NO,
        )

        if not confirmed:
            self.app.log(
                "Remove Staffing Override cancelled for "
                f"'{facility_id} / {capability_id} / {qualification_id}'."
            )
            return

        rows = [
            row
            for row in self.rows()
            if not (
                row.get("facility_id", "") == facility_id
                and row.get("capability_id", "") == capability_id
                and row.get("qualification_id", "") == qualification_id
            )
        ]

        temporary = self.app.source_directory / (
            f".facility-capability-staffing-overrides-remove-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                "Facility Capability Staffing Override removal candidate "
                f"validation output for '{facility_id} / {capability_id} / "
                f"{qualification_id}':"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Staffing Override removal was blocked by validation.\n\n"
                        "Source CSV was unchanged."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "facility_capability_staffing_overrides_before_remove_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_key = None

            self.app.log(
                "Created pre-removal Facility Capability Staffing Override "
                f"backup: {backup}"
            )
            self.app.log(
                "Removed Facility Capability Staffing Override: "
                f"{facility_id} / {capability_id} / {qualification_id}"
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
                        "Facility Capability Staffing Override "
                        f"'{facility_id} / {capability_id} / "
                        f"{qualification_id}' removed.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        "Staffing Override removed, but post-save validation "
                        f"failed.\n\nBackup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"STAFFING OVERRIDE REMOVE ERROR: {error}")
            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to remove Staffing Override.\n\n{error}",
            )
        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def open_backups(self) -> None:
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_facility_capability_staffing_overrides_editor(app: Any) -> None:
    editor = FacilityCapabilityStaffingOverridesEditor(app)
    app.facility_capability_staffing_overrides_editor = editor

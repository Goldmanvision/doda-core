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
    "facility_id",
    "display_name",
    "track_id",
    "hq_zone_id",
    "description",
    "personnel_capacity",
    "initial_tier_id",
    "interaction_asset_id",
    "foims_panel_id",
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


class FacilitiesEditor:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.editing_id: str | None = None

        self.facility_id = tk.StringVar()
        self.display_name = tk.StringVar()
        self.track_id = tk.StringVar()
        self.hq_zone_id = tk.StringVar()
        self.personnel_capacity = tk.StringVar()
        self.initial_tier_id = tk.StringVar()
        self.interaction_asset_id = tk.StringVar()
        self.foims_panel_id = tk.StringVar()
        self.active = tk.BooleanVar(value=True)

        self.build()

    def source_path(self) -> Path:
        return self.app.source_directory / "facilities.csv"

    def backup_directory(self) -> Path:
        return self.app.project_root / "data_authoring" / "backups" / "facilities"

    def rows(self) -> list[dict[str, str]]:
        return [dict(row) for row in self.app.tables.get("facilities", [])]

    def track_ids(self) -> list[str]:
        return sorted(
            row.get("track_id", "")
            for row in self.app.tables.get("department_tracks", [])
            if row.get("track_id", "")
            and row.get("active", "").upper() == "TRUE"
        )

    def facility_tiers(self) -> list[str]:
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
                        (row.get("enum_group") or "").strip() != "FACILITY_TIER"
                        or (row.get("active") or "").strip().upper() != "TRUE"
                    ):
                        continue

                    value = (row.get("enum_value") or "").strip()

                    if not value:
                        continue

                    try:
                        order = int((row.get("sort_order") or "999999").strip())
                    except ValueError:
                        order = 999999

                    values.append((order, value))

        except (OSError, csv.Error):
            return []

        return [
            value
            for _, value in sorted(values, key=lambda item: (item[0], item[1]))
        ]

    def build(self) -> None:
        for child in self.app.facilities_tab.winfo_children():
            child.destroy()

        tab = self.app.facilities_tab
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(tab, text="Facilities", padding=8)
        editor_frame = ttk.LabelFrame(tab, text="Facility Editor", padding=10)

        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        editor_frame.grid(row=0, column=1, sticky=tk.NSEW)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("facility", "name", "track", "tier", "active"),
            show="headings",
            selectmode="browse",
        )

        columns = (
            ("facility", "Facility ID", 180),
            ("name", "Display Name", 220),
            ("track", "Track", 180),
            ("tier", "Initial Tier", 130),
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

        label("Facility ID:", 0)

        self.facility_id_entry = ttk.Entry(
            editor_frame,
            textvariable=self.facility_id,
        )

        self.facility_id_entry.grid(
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

        label("Department Track:", 3)

        self.track_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.track_id,
            state="readonly",
            values=self.track_ids(),
        )

        self.track_combo.grid(
            row=3,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("HQ Zone ID:", 4)

        ttk.Entry(
            editor_frame,
            textvariable=self.hq_zone_id,
        ).grid(
            row=4,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Description:", 5)

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
            row=5,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Personnel Capacity:", 6)

        ttk.Entry(
            editor_frame,
            textvariable=self.personnel_capacity,
        ).grid(
            row=6,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        ttk.Label(
            editor_frame,
            text="Whole number of personnel assigned to this facility.",
            foreground="#9da7b3",
        ).grid(
            row=7,
            column=1,
            sticky=tk.W,
            pady=(0, 10),
        )

        label("Initial Tier:", 8)

        self.tier_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.initial_tier_id,
            state="readonly",
            values=self.facility_tiers(),
        )

        self.tier_combo.grid(
            row=8,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Interaction Asset ID:", 9)

        ttk.Entry(
            editor_frame,
            textvariable=self.interaction_asset_id,
        ).grid(
            row=9,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("FOIMS Panel ID:", 10)

        ttk.Entry(
            editor_frame,
            textvariable=self.foims_panel_id,
        ).grid(
            row=10,
            column=1,
            sticky=tk.EW,
            pady=(0, 8),
        )

        label("Active:", 11)

        ttk.Checkbutton(
            editor_frame,
            text="This facility is active",
            variable=self.active,
        ).grid(
            row=11,
            column=1,
            sticky=tk.W,
            pady=(0, 8),
        )

        buttons = ttk.Frame(editor_frame)
        buttons.grid(
            row=12,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(8, 0),
        )

        ttk.Button(
            buttons,
            text="Add Facility",
            command=self.new,
        ).pack(side=tk.LEFT)

        ttk.Button(
            buttons,
            text="Save Facility",
            command=self.save,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Remove Facility",
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
                "Save validates the complete candidate project before replacing "
                "facilities.csv. Track and tier choices are controlled."
            ),
            foreground="#9da7b3",
            wraplength=390,
        ).grid(
            row=13,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(12, 0),
        )

        self.new()

    def update(self) -> None:
        selected = self.editing_id

        self.track_combo.configure(values=self.track_ids())
        self.tier_combo.configure(values=self.facility_tiers())

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self.rows():
            facility_id = row.get("facility_id", "")

            self.tree.insert(
                "",
                tk.END,
                iid=facility_id,
                values=(
                    facility_id,
                    row.get("display_name", ""),
                    row.get("track_id", ""),
                    row.get("initial_tier_id", ""),
                    row.get("active", ""),
                ),
            )

        if selected and self.tree.exists(selected):
            self.tree.selection_set(selected)
            self.tree.focus(selected)

    def new(self) -> None:
        self.editing_id = None

        self.facility_id_entry.configure(state=tk.NORMAL)

        tracks = self.track_ids()
        tiers = self.facility_tiers()

        self.facility_id.set("")
        self.display_name.set("")
        self.track_id.set(tracks[0] if tracks else "")
        self.hq_zone_id.set("")
        self.personnel_capacity.set("1")
        self.initial_tier_id.set(
            "UNBUILT" if "UNBUILT" in tiers else (tiers[0] if tiers else "")
        )
        self.interaction_asset_id.set("")
        self.foims_panel_id.set("")
        self.active.set(True)

        self.description.delete("1.0", tk.END)
        self.facility_id_entry.focus_set()

    def on_select(self, _event: Any = None) -> None:
        selection = self.tree.selection()

        if not selection:
            return

        row = next(
            (
                item
                for item in self.rows()
                if item.get("facility_id") == selection[0]
            ),
            None,
        )

        if row is None:
            return

        self.editing_id = row["facility_id"]

        self.facility_id_entry.configure(state=tk.NORMAL)
        self.facility_id.set(row.get("facility_id", ""))
        self.facility_id_entry.configure(state=tk.DISABLED)

        self.display_name.set(row.get("display_name", ""))
        self.track_id.set(row.get("track_id", ""))
        self.hq_zone_id.set(row.get("hq_zone_id", ""))
        self.personnel_capacity.set(row.get("personnel_capacity", ""))
        self.initial_tier_id.set(row.get("initial_tier_id", ""))
        self.interaction_asset_id.set(row.get("interaction_asset_id", ""))
        self.foims_panel_id.set(row.get("foims_panel_id", ""))
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
            "facility_id": self.facility_id.get().strip(),
            "display_name": self.display_name.get().strip(),
            "track_id": self.track_id.get().strip(),
            "hq_zone_id": self.hq_zone_id.get().strip(),
            "description": self.description.get("1.0", tk.END).strip(),
            "personnel_capacity": self.personnel_capacity.get().strip(),
            "initial_tier_id": self.initial_tier_id.get().strip(),
            "interaction_asset_id": self.interaction_asset_id.get().strip(),
            "foims_panel_id": self.foims_panel_id.get().strip(),
            "active": "TRUE" if self.active.get() else "FALSE",
        }

        errors: list[str] = []

        if not ID_PATTERN.fullmatch(row["facility_id"]):
            errors.append(
                "Facility ID must begin with an uppercase letter and use only "
                "uppercase letters, digits, or underscores."
            )

        if not row["display_name"]:
            errors.append("Display Name is required.")

        if row["track_id"] not in self.track_ids():
            errors.append("Select a valid Department Track.")

        if not row["hq_zone_id"]:
            errors.append("HQ Zone ID is required.")

        if not row["description"]:
            errors.append("Description is required.")

        try:
            personnel_capacity = int(row["personnel_capacity"])
        except ValueError:
            personnel_capacity = 0
            errors.append("Personnel Capacity must be a whole number of at least 1.")

        if personnel_capacity < 1 and not any(
            "Personnel Capacity must be" in error
            for error in errors
        ):
            errors.append("Personnel Capacity must be a whole number of at least 1.")

        if row["initial_tier_id"] not in self.facility_tiers():
            errors.append("Select a valid Initial Tier.")

        if not row["interaction_asset_id"]:
            errors.append("Interaction Asset ID is required.")

        if not row["foims_panel_id"]:
            errors.append("FOIMS Panel ID is required.")

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
        with tempfile.TemporaryDirectory(prefix="doda-facility-") as temporary:
            root = Path(temporary)
            destination = root / "data_authoring" / "source"
            destination.mkdir(parents=True)

            for filename in FILES:
                source = (
                    candidate
                    if filename == "facilities.csv"
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
            if row["facility_id"] != self.editing_id:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Facility ID cannot change after creation.",
                )
                return

            rows = [
                row if item.get("facility_id") == self.editing_id else item
                for item in rows
            ]

            action = "updated"

        else:
            if any(
                item.get("facility_id") == row["facility_id"]
                for item in rows
            ):
                messagebox.showerror(
                    "DoDA Content Workbench",
                    "Facility ID already exists.",
                )
                return

            rows.append(row)
            action = "added"

        temporary = self.app.source_directory / (
            f".facilities-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log("Facility candidate validation output:")

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Facility candidate validation failed. Source CSV was "
                        "unchanged.\n\nReview Activity Log for details."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "facilities_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_id = row["facility_id"]

            self.app.log(f"Created facility backup: {backup}")
            self.app.log(f"Facility {action}: {row['facility_id']}")

            self.app.refresh_all(False)

            valid, output = self.post_validate()

            for line in output.splitlines():
                self.app.log(" " + line)

            self.app.refresh_all(False)

            if valid:
                messagebox.showinfo(
                    "DoDA Content Workbench",
                    (
                        f"Facility '{row['facility_id']}' {action}.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Facility {action}, but post-save validation failed.\n\n"
                        f"Backup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"FACILITY SAVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to save facility.\n\n{error}",
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
                "Select an existing facility before using Remove Facility.",
            )
            return

        facility_id = self.editing_id

        confirmed = messagebox.askyesno(
            "Remove Facility?",
            (
                f"ARE YOU SURE you want to remove '{facility_id}'?\n\n"
                "A timestamped backup will be created before removal."
            ),
            icon="warning",
            default=messagebox.NO,
        )

        if not confirmed:
            self.app.log(f"Remove Facility cancelled for '{facility_id}'.")
            return

        rows = [
            row
            for row in self.rows()
            if row.get("facility_id") != facility_id
        ]

        temporary = self.app.source_directory / (
            f".facilities-remove-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                f"Facility removal candidate validation output for '{facility_id}':"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        "Facility removal was blocked by validation.\n\n"
                        "Source CSV was unchanged."
                    ),
                )
                return

            folder = self.backup_directory()
            folder.mkdir(parents=True, exist_ok=True)

            backup = folder / (
                "facilities_before_remove_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.source_path(), backup)
            os.replace(temporary, self.source_path())

            self.editing_id = None

            self.app.log(f"Created pre-removal facility backup: {backup}")
            self.app.log(f"Removed facility: {facility_id}")

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
                        f"Facility '{facility_id}' removed.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Facility '{facility_id}' removed, but post-save "
                        f"validation failed.\n\nBackup:\n{backup}"
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"FACILITY REMOVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to remove facility.\n\n{error}",
            )

        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()

    def open_backups(self) -> None:
        self.backup_directory().mkdir(parents=True, exist_ok=True)
        self.app.open_folder(self.backup_directory())


def install_facilities_editor(app: Any) -> None:
    editor = FacilitiesEditor(app)

    app.facilities_editor = editor
    app.update_facilities = editor.update

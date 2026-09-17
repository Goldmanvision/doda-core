#!/usr/bin/env python3
r"""
DoDA Content Workbench GUI v0.1.

Read-only content browser and safe CLI launcher for the DoDA authoring pipeline.

This version can:
- Show project and authoring-data status.
- Browse tracks, metrics, facilities, and flavor text.
- Run the validator.
- Run the content exporter.
- Open source, generated, report, and build folders.
- Display validation/export process output.

This version intentionally cannot edit CSV source data.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any


APP_TITLE = "DoDA Content Workbench"
APP_VERSION = "0.1.0"

SOURCE_FILES = {
    "enum_catalog": "enum_catalog.csv",
    "department_tracks": "department_tracks.csv",
    "metrics": "metrics.csv",
    "metric_tiers": "metric_tiers.csv",
    "facilities": "facilities.csv",
    "flavor_text": "flavor_text.csv",
}


def find_project_root(start: Path) -> Path:
    current = start.resolve()

    for candidate in (current, *current.parents):
        if (
            (candidate / "data_authoring").is_dir()
            and (candidate / "tools").is_dir()
            and (candidate / "DoDA").is_dir()
        ):
            return candidate

    raise FileNotFoundError(
        "Could not locate a DoDA project root. Choose the doda-core folder manually."
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as source_file:
        reader = csv.DictReader(source_file)
        rows: list[dict[str, str]] = []

        for raw_row in reader:
            if raw_row is None:
                continue

            row = {
                (key or "").strip(): (value or "").strip()
                for key, value in raw_row.items()
                if key is not None
            }

            if any(row.values()):
                rows.append(row)

        return rows


def truncate_text(value: str, maximum_length: int = 120) -> str:
    normalized = " ".join((value or "").split())

    if len(normalized) <= maximum_length:
        return normalized

    return normalized[: maximum_length - 3] + "..."


class ContentWorkbenchApp(tk.Tk):
    def __init__(self, project_root: Path) -> None:
        super().__init__()

        self.project_root = project_root.resolve()
        self.workbench_directory = (
            self.project_root / "tools" / "doda_content_workbench"
        )
        self.validator_path = (
            self.workbench_directory / "doda_content_workbench.py"
        )
        self.exporter_path = (
            self.workbench_directory / "doda_content_export.py"
        )

        self.source_directory = self.project_root / "data_authoring" / "source"
        self.generated_directory = self.project_root / "generated"
        self.report_directory = self.generated_directory / "reports"
        self.build_directory = self.project_root / "build"
        self.validation_report_path = (
            self.report_directory / "content_validation_report.json"
        )

        self.tables: dict[str, list[dict[str, str]]] = {}
        self.validation_report: dict[str, Any] = {}

        self.status_text = tk.StringVar(value="Ready.")
        self.project_text = tk.StringVar(value=str(self.project_root))
        self.validation_text = tk.StringVar(value="Validation status: unknown")
        self.export_text = tk.StringVar(value="Export status: unknown")

        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry("1280x800")
        self.minsize(1040, 650)

        self._configure_styles()
        self._build_menu()
        self._build_layout()
        self.refresh_all(show_message=False)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Status.TLabel", font=("Consolas", 9))
        style.configure("Treeview", rowheight=24)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(
            label="Choose Project Root...",
            command=self.choose_project_root,
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        actions_menu = tk.Menu(menu_bar, tearoff=False)
        actions_menu.add_command(
            label="Refresh Source Data",
            command=lambda: self.refresh_all(show_message=True),
        )
        actions_menu.add_command(
            label="Run Validation",
            command=self.run_validation,
        )
        actions_menu.add_command(
            label="Export Generated Content",
            command=self.run_export,
        )

        folders_menu = tk.Menu(menu_bar, tearoff=False)
        folders_menu.add_command(
            label="Open Source Data Folder",
            command=lambda: self.open_folder(self.source_directory),
        )
        folders_menu.add_command(
            label="Open Generated Output Folder",
            command=lambda: self.open_folder(self.generated_directory),
        )
        folders_menu.add_command(
            label="Open Validation Reports Folder",
            command=lambda: self.open_folder(self.report_directory),
        )
        folders_menu.add_command(
            label="Open Build Folder",
            command=lambda: self.open_folder(self.build_directory),
        )

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Actions", menu=actions_menu)
        menu_bar.add_cascade(label="Folders", menu=folders_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menu_bar)

    def _build_layout(self) -> None:
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(outer)
        header.pack(fill=tk.X)

        title_frame = ttk.Frame(header)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(
            title_frame,
            text=APP_TITLE,
            style="Title.TLabel",
        ).pack(anchor=tk.W)

        ttk.Label(
            title_frame,
            textvariable=self.project_text,
            foreground="#555555",
        ).pack(anchor=tk.W, pady=(2, 0))

        action_frame = ttk.Frame(header)
        action_frame.pack(side=tk.RIGHT, anchor=tk.NE)

        ttk.Button(
            action_frame,
            text="Refresh",
            command=lambda: self.refresh_all(show_message=True),
        ).grid(row=0, column=0, padx=(0, 6))

        ttk.Button(
            action_frame,
            text="Validate",
            command=self.run_validation,
        ).grid(row=0, column=1, padx=(0, 6))

        ttk.Button(
            action_frame,
            text="Export PK3",
            command=self.run_export,
        ).grid(row=0, column=2)

        status_frame = ttk.LabelFrame(
            outer,
            text="Project Status",
            padding=8,
        )
        status_frame.pack(fill=tk.X, pady=(12, 10))

        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Validation:", style="Section.TLabel").grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=(0, 8),
        )

        ttk.Label(
            status_frame,
            textvariable=self.validation_text,
            style="Status.TLabel",
        ).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(status_frame, text="Export:", style="Section.TLabel").grid(
            row=1,
            column=0,
            sticky=tk.W,
            padx=(0, 8),
            pady=(4, 0),
        )

        ttk.Label(
            status_frame,
            textvariable=self.export_text,
            style="Status.TLabel",
        ).grid(row=1, column=1, sticky=tk.W, pady=(4, 0))

        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.dashboard_tab = ttk.Frame(self.notebook, padding=10)
        self.tracks_tab = ttk.Frame(self.notebook, padding=10)
        self.metrics_tab = ttk.Frame(self.notebook, padding=10)
        self.facilities_tab = ttk.Frame(self.notebook, padding=10)
        self.flavor_tab = ttk.Frame(self.notebook, padding=10)
        self.activity_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.tracks_tab, text="Department Tracks")
        self.notebook.add(self.metrics_tab, text="Metrics")
        self.notebook.add(self.facilities_tab, text="Facilities")
        self.notebook.add(self.flavor_tab, text="Flavor Text")
        self.notebook.add(self.activity_tab, text="Activity Log")

        self._build_dashboard_tab()
        self._build_tracks_tab()
        self._build_metrics_tab()
        self._build_facilities_tab()
        self._build_flavor_tab()
        self._build_activity_tab()

        footer = ttk.Frame(outer)
        footer.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(
            footer,
            textvariable=self.status_text,
            style="Status.TLabel",
        ).pack(side=tk.LEFT)

        ttk.Label(
            footer,
            text="Read-only v0.1 — CSV editing is not enabled yet.",
            foreground="#666666",
        ).pack(side=tk.RIGHT)

    def _build_dashboard_tab(self) -> None:
        self.dashboard_tab.columnconfigure(0, weight=1)
        self.dashboard_tab.rowconfigure(1, weight=1)

        summary_frame = ttk.Frame(self.dashboard_tab)
        summary_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0, 10))

        self.dashboard_summary = ttk.Label(
            summary_frame,
            text="Loading project summary...",
            justify=tk.LEFT,
        )
        self.dashboard_summary.pack(anchor=tk.W)

        source_frame = ttk.LabelFrame(
            self.dashboard_tab,
            text="Authored Source Files",
            padding=8,
        )
        source_frame.grid(row=1, column=0, sticky=tk.NSEW)

        source_frame.columnconfigure(0, weight=1)
        source_frame.rowconfigure(0, weight=1)

        columns = ("table", "filename", "rows", "status", "modified")
        self.dashboard_tree = ttk.Treeview(
            source_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "table": "Table",
            "filename": "Source File",
            "rows": "Rows",
            "status": "Status",
            "modified": "Last Modified",
        }

        widths = {
            "table": 180,
            "filename": 250,
            "rows": 80,
            "status": 160,
            "modified": 180,
        }

        for column in columns:
            self.dashboard_tree.heading(column, text=headings[column])
            self.dashboard_tree.column(column, width=widths[column], anchor=tk.W)

        scrollbar = ttk.Scrollbar(
            source_frame,
            orient=tk.VERTICAL,
            command=self.dashboard_tree.yview,
        )
        self.dashboard_tree.configure(yscrollcommand=scrollbar.set)

        self.dashboard_tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        self.dashboard_tree.bind(
            "<<TreeviewSelect>>",
            self.on_dashboard_selection,
        )

    def _build_tracks_tab(self) -> None:
        self.tracks_tree, self.tracks_detail = self._build_browser(
            parent=self.tracks_tab,
            title="Department Tracks",
            columns=(
                ("track_id", "Track ID", 220),
                ("display_name", "Display Name", 260),
                ("active", "Active", 90),
            ),
            select_handler=self.on_track_selection,
        )

    def _build_metrics_tab(self) -> None:
        self.metrics_tree, self.metrics_detail = self._build_browser(
            parent=self.metrics_tab,
            title="Department Metrics",
            columns=(
                ("metric_id", "Metric ID", 210),
                ("display_name", "Display Name", 220),
                ("default_value", "Default", 90),
                ("polarity", "Polarity", 170),
            ),
            select_handler=self.on_metric_selection,
        )

    def _build_facilities_tab(self) -> None:
        self.facilities_tree, self.facilities_detail = self._build_browser(
            parent=self.facilities_tab,
            title="Facilities",
            columns=(
                ("facility_id", "Facility ID", 220),
                ("display_name", "Display Name", 220),
                ("track_id", "Track", 190),
                ("initial_tier_id", "Initial Tier", 150),
            ),
            select_handler=self.on_facility_selection,
        )

    def _build_flavor_tab(self) -> None:
        self.flavor_tree, self.flavor_detail = self._build_browser(
            parent=self.flavor_tab,
            title="Flavor Text",
            columns=(
                ("flavor_text_id", "Flavor Text ID", 280),
                ("category", "Category", 150),
                ("title", "Title", 320),
            ),
            select_handler=self.on_flavor_selection,
        )

    def _build_browser(
        self,
        parent: ttk.Frame,
        title: str,
        columns: tuple[tuple[str, str, int], ...],
        select_handler: Any,
    ) -> tuple[ttk.Treeview, tk.Text]:
        parent.columnconfigure(0, weight=3)
        parent.columnconfigure(1, weight=2)
        parent.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(parent, text=title, padding=8)
        detail_frame = ttk.LabelFrame(parent, text="Record Detail", padding=8)

        list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        detail_frame.grid(row=0, column=1, sticky=tk.NSEW)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        column_ids = tuple(column[0] for column in columns)

        tree = ttk.Treeview(
            list_frame,
            columns=column_ids,
            show="headings",
            selectmode="browse",
        )

        for column_id, heading, width in columns:
            tree.heading(column_id, text=heading)
            tree.column(column_id, width=width, anchor=tk.W)

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=tree.yview,
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        detail = tk.Text(
            detail_frame,
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            background="#f7f7f7",
            font=("Consolas", 10),
        )

        detail_scrollbar = ttk.Scrollbar(
            detail_frame,
            orient=tk.VERTICAL,
            command=detail.yview,
        )
        detail.configure(yscrollcommand=detail_scrollbar.set)

        detail.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        detail.configure(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", select_handler)

        return tree, detail

    def _build_activity_tab(self) -> None:
        self.activity_tab.columnconfigure(0, weight=1)
        self.activity_tab.rowconfigure(1, weight=1)

        action_row = ttk.Frame(self.activity_tab)
        action_row.grid(row=0, column=0, sticky=tk.EW, pady=(0, 8))

        ttk.Button(
            action_row,
            text="Clear Log",
            command=self.clear_activity_log,
        ).pack(side=tk.LEFT)

        ttk.Button(
            action_row,
            text="Open Reports Folder",
            command=lambda: self.open_folder(self.report_directory),
        ).pack(side=tk.LEFT, padx=(6, 0))

        self.activity_log = tk.Text(
            self.activity_tab,
            wrap=tk.WORD,
            background="#111111",
            foreground="#E5E5E5",
            insertbackground="#FFFFFF",
            font=("Consolas", 10),
        )

        activity_scrollbar = ttk.Scrollbar(
            self.activity_tab,
            orient=tk.VERTICAL,
            command=self.activity_log.yview,
        )
        self.activity_log.configure(yscrollcommand=activity_scrollbar.set)

        self.activity_log.grid(row=1, column=0, sticky=tk.NSEW)
        activity_scrollbar.grid(row=1, column=1, sticky=tk.NS)

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_log.see(tk.END)

    def clear_activity_log(self) -> None:
        self.activity_log.delete("1.0", tk.END)

    def set_detail(self, detail_widget: tk.Text, record: dict[str, str]) -> None:
        lines: list[str] = []

        for key, value in record.items():
            lines.append(f"{key}:")
            lines.append(f"  {value}")
            lines.append("")

        detail_widget.configure(state=tk.NORMAL)
        detail_widget.delete("1.0", tk.END)
        detail_widget.insert("1.0", "\n".join(lines).rstrip() + "\n")
        detail_widget.configure(state=tk.DISABLED)

    def refresh_all(self, show_message: bool = False) -> None:
        try:
            self.tables = {
                table_name: read_csv(self.source_directory / filename)
                for table_name, filename in SOURCE_FILES.items()
            }

            self.load_validation_report()
            self.update_dashboard()
            self.update_tracks()
            self.update_metrics()
            self.update_facilities()
            self.update_flavor_text()
            self.update_status_labels()

            self.status_text.set("Source data refreshed successfully.")
            self.log("Source data refreshed.")

            if show_message:
                messagebox.showinfo(
                    APP_TITLE,
                    "Source data was refreshed successfully.",
                )

        except Exception as error:
            self.status_text.set("Refresh failed.")
            self.log(f"REFRESH ERROR: {error}")
            messagebox.showerror(
                APP_TITLE,
                f"Unable to refresh source data.\n\n{error}",
            )

    def load_validation_report(self) -> None:
        self.validation_report = {}

        if not self.validation_report_path.is_file():
            return

        try:
            self.validation_report = json.loads(
                self.validation_report_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as error:
            self.log(f"Could not read validation report: {error}")

    def update_status_labels(self) -> None:
        if self.validation_report:
            valid = bool(self.validation_report.get("valid", False))
            error_count = self.validation_report.get("errorCount", "?")
            warning_count = self.validation_report.get("warningCount", "?")
            generated_at = self.validation_report.get("generatedAtUtc", "unknown")

            if valid:
                self.validation_text.set(
                    f"PASS — {error_count} error(s), {warning_count} warning(s), "
                    f"report: {generated_at}"
                )
            else:
                self.validation_text.set(
                    f"FAIL — {error_count} error(s), {warning_count} warning(s), "
                    f"report: {generated_at}"
                )
        else:
            self.validation_text.set(
                "UNKNOWN — no validation report has been generated yet."
            )

        pk3_path = self.build_directory / "doda-generated-content.pk3"

        if pk3_path.is_file():
            modified = datetime.fromtimestamp(
                pk3_path.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M:%S")

            self.export_text.set(
                f"READY — doda-generated-content.pk3, "
                f"{pk3_path.stat().st_size:,} bytes, built {modified}"
            )
        else:
            self.export_text.set(
                "NOT BUILT — no generated PK3 overlay exists yet."
            )

    def update_dashboard(self) -> None:
        for item in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(item)

        total_rows = 0
        source_files_present = 0

        for table_name, filename in SOURCE_FILES.items():
            path = self.source_directory / filename
            rows = self.tables.get(table_name, [])
            total_rows += len(rows)

            if path.is_file():
                source_files_present += 1
                modified = datetime.fromtimestamp(
                    path.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")
                status = "Available"
            else:
                modified = "—"
                status = "Missing"

            self.dashboard_tree.insert(
                "",
                tk.END,
                iid=table_name,
                values=(
                    table_name,
                    filename,
                    len(rows),
                    status,
                    modified,
                ),
            )

        validation_state = "unknown"

        if self.validation_report:
            validation_state = (
                "passed"
                if self.validation_report.get("valid", False)
                else "failed"
            )

        self.dashboard_summary.configure(
            text=(
                f"Authoring tables: {source_files_present}/{len(SOURCE_FILES)} "
                f"available\n"
                f"Total authored records: {total_rows}\n"
                f"Latest validation state: {validation_state}\n"
                f"Current mode: read-only browse, validate, export, and package."
            )
        )

    def update_tracks(self) -> None:
        for item in self.tracks_tree.get_children():
            self.tracks_tree.delete(item)

        for row in self.tables.get("department_tracks", []):
            track_id = row.get("track_id", "")
            self.tracks_tree.insert(
                "",
                tk.END,
                iid=track_id,
                values=(
                    track_id,
                    row.get("display_name", ""),
                    row.get("active", ""),
                ),
            )

        self.clear_detail(self.tracks_detail)

    def update_metrics(self) -> None:
        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)

        for row in self.tables.get("metrics", []):
            metric_id = row.get("metric_id", "")
            self.metrics_tree.insert(
                "",
                tk.END,
                iid=metric_id,
                values=(
                    metric_id,
                    row.get("display_name", ""),
                    row.get("default_value", ""),
                    row.get("polarity", ""),
                ),
            )

        self.clear_detail(self.metrics_detail)

    def update_facilities(self) -> None:
        for item in self.facilities_tree.get_children():
            self.facilities_tree.delete(item)

        for row in self.tables.get("facilities", []):
            facility_id = row.get("facility_id", "")
            self.facilities_tree.insert(
                "",
                tk.END,
                iid=facility_id,
                values=(
                    facility_id,
                    row.get("display_name", ""),
                    row.get("track_id", ""),
                    row.get("initial_tier_id", ""),
                ),
            )

        self.clear_detail(self.facilities_detail)

    def update_flavor_text(self) -> None:
        for item in self.flavor_tree.get_children():
            self.flavor_tree.delete(item)

        for row in self.tables.get("flavor_text", []):
            flavor_id = row.get("flavor_text_id", "")
            self.flavor_tree.insert(
                "",
                tk.END,
                iid=flavor_id,
                values=(
                    flavor_id,
                    row.get("category", ""),
                    truncate_text(row.get("title", ""), 80),
                ),
            )

        self.clear_detail(self.flavor_detail)

    def clear_detail(self, detail_widget: tk.Text) -> None:
        detail_widget.configure(state=tk.NORMAL)
        detail_widget.delete("1.0", tk.END)
        detail_widget.insert(
            "1.0",
            "Select a record from the list to inspect its authored fields.\n",
        )
        detail_widget.configure(state=tk.DISABLED)

    def find_row(
        self,
        table_name: str,
        key_name: str,
        key_value: str,
    ) -> dict[str, str] | None:
        for row in self.tables.get(table_name, []):
            if row.get(key_name) == key_value:
                return row

        return None

    def on_dashboard_selection(self, _event: Any) -> None:
        selection = self.dashboard_tree.selection()

        if not selection:
            return

        table_name = selection[0]
        filename = SOURCE_FILES.get(table_name, "")
        path = self.source_directory / filename
        row_count = len(self.tables.get(table_name, []))

        self.log(
            f"Selected source table '{table_name}' "
            f"({row_count} row(s), path: {path})."
        )

    def on_track_selection(self, _event: Any) -> None:
        selection = self.tracks_tree.selection()

        if not selection:
            return

        row = self.find_row(
            "department_tracks",
            "track_id",
            selection[0],
        )

        if row:
            self.set_detail(self.tracks_detail, row)

    def on_metric_selection(self, _event: Any) -> None:
        selection = self.metrics_tree.selection()

        if not selection:
            return

        row = self.find_row(
            "metrics",
            "metric_id",
            selection[0],
        )

        if row:
            self.set_detail(self.metrics_detail, row)

    def on_facility_selection(self, _event: Any) -> None:
        selection = self.facilities_tree.selection()

        if not selection:
            return

        row = self.find_row(
            "facilities",
            "facility_id",
            selection[0],
        )

        if row:
            self.set_detail(self.facilities_detail, row)

    def on_flavor_selection(self, _event: Any) -> None:
        selection = self.flavor_tree.selection()

        if not selection:
            return

        row = self.find_row(
            "flavor_text",
            "flavor_text_id",
            selection[0],
        )

        if row:
            self.set_detail(self.flavor_detail, row)

    def run_validation(self) -> None:
        if not self.validator_path.is_file():
            messagebox.showerror(
                APP_TITLE,
                f"Validator script was not found:\n{self.validator_path}",
            )
            return

        command = [
            sys.executable,
            str(self.validator_path),
            "--root",
            str(self.project_root),
            "validate",
        ]

        self.run_command(
            label="Validation",
            command=command,
            success_message="Validation completed successfully.",
        )

    def run_export(self) -> None:
        if not self.exporter_path.is_file():
            messagebox.showerror(
                APP_TITLE,
                f"Exporter script was not found:\n{self.exporter_path}",
            )
            return

        command = [
            sys.executable,
            str(self.exporter_path),
            "--root",
            str(self.project_root),
        ]

        self.run_command(
            label="Export",
            command=command,
            success_message="Export and PK3 build completed successfully.",
        )

    def run_command(
        self,
        label: str,
        command: list[str],
        success_message: str,
    ) -> None:
        self.config(cursor="watch")
        self.update_idletasks()

        self.log(f"Starting {label.lower()}: {' '.join(command)}")

        try:
            completed = subprocess.run(
                command,
                cwd=self.project_root,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            combined_output = (
                completed.stdout.rstrip()
                + ("\n" if completed.stdout and completed.stderr else "")
                + completed.stderr.rstrip()
            ).strip()

            if combined_output:
                self.log(f"{label} output:")
                for line in combined_output.splitlines():
                    self.log(f"  {line}")

            self.log(f"{label} process exit code: {completed.returncode}")

            self.refresh_all(show_message=False)

            if completed.returncode == 0:
                self.status_text.set(success_message)
                messagebox.showinfo(APP_TITLE, success_message)
            else:
                self.status_text.set(f"{label} failed.")
                messagebox.showerror(
                    APP_TITLE,
                    f"{label} failed with exit code {completed.returncode}.\n\n"
                    "Review the Activity Log tab for complete output.",
                )

        except OSError as error:
            self.status_text.set(f"{label} could not start.")
            self.log(f"{label} launch error: {error}")
            messagebox.showerror(
                APP_TITLE,
                f"Could not start {label.lower()}.\n\n{error}",
            )
        finally:
            self.config(cursor="")
            self.update_idletasks()

    def open_folder(self, folder: Path) -> None:
        if not folder.exists():
            messagebox.showerror(
                APP_TITLE,
                f"Folder does not exist:\n{folder}",
            )
            return

        try:
            if hasattr(os, "startfile"):
                os.startfile(str(folder))
            else:
                subprocess.run(["explorer", str(folder)], check=False)

            self.log(f"Opened folder: {folder}")

        except OSError as error:
            self.log(f"Could not open folder '{folder}': {error}")
            messagebox.showerror(
                APP_TITLE,
                f"Could not open folder.\n\n{folder}\n\n{error}",
            )

    def choose_project_root(self) -> None:
        selected = filedialog.askdirectory(
            title="Choose DoDA Project Root",
            initialdir=str(self.project_root),
        )

        if not selected:
            return

        candidate = Path(selected)

        try:
            verified_root = find_project_root(candidate)
        except FileNotFoundError as error:
            messagebox.showerror(APP_TITLE, str(error))
            return

        self.project_root = verified_root
        self.workbench_directory = (
            self.project_root / "tools" / "doda_content_workbench"
        )
        self.validator_path = (
            self.workbench_directory / "doda_content_workbench.py"
        )
        self.exporter_path = (
            self.workbench_directory / "doda_content_export.py"
        )
        self.source_directory = self.project_root / "data_authoring" / "source"
        self.generated_directory = self.project_root / "generated"
        self.report_directory = self.generated_directory / "reports"
        self.build_directory = self.project_root / "build"
        self.validation_report_path = (
            self.report_directory / "content_validation_report.json"
        )

        self.project_text.set(str(self.project_root))
        self.log(f"Project root changed to: {self.project_root}")
        self.refresh_all(show_message=True)

    def show_about(self) -> None:
        messagebox.showinfo(
            f"About {APP_TITLE}",
            (
                f"{APP_TITLE} v{APP_VERSION}\n\n"
                "A DoDA-specific content authoring, validation, export, and "
                "packaging workspace.\n\n"
                "Current version: read-only data browser with validation and "
                "PK3 export controls.\n\n"
                "Authoritative editable data remains in:\n"
                "data_authoring/source/\n\n"
                "Generated files must not be edited manually."
            ),
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doda_content_gui",
        description="Launch the DoDA Content Workbench GUI.",
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Path to the doda-core project root. Defaults to automatic discovery.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    arguments = parser.parse_args()

    try:
        project_root = (
            arguments.root.resolve()
            if arguments.root is not None
            else find_project_root(Path.cwd())
        )

    except FileNotFoundError as error:
        print(f"GUI STARTUP FAILED: {error}", file=sys.stderr)
        return 1

    app = ContentWorkbenchApp(project_root)
    app.mainloop()

    return 0


if __name__ == "__main__":
    sys.exit(main())


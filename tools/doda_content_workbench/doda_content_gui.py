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
from doda_task_flow_preview_ui import open_task_flow_preview
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any
from doda_track_editor import install_track_editor
from doda_metrics_editor import install_metrics_editor
from doda_metric_tiers_editor import install_metric_tiers_editor
from doda_metric_bundle_editor import open_metric_bundle_editor
from doda_facilities_editor import install_facilities_editor
from doda_facilities_draft_policy import allow_facilities_project_change, install_facilities_draft_close_guard
from doda_flavor_text_editor import install_flavor_text_editor
from doda_enum_catalog_editor import install_enum_catalog_editor
from doda_qualification_catalog_editor import install_qualification_catalog_editor
from doda_qualification_draft_policy import allow_qualification_project_change, install_qualification_draft_close_guard
from doda_capabilities_editor import install_capabilities_editor
from doda_capabilities_draft_policy import allow_capabilities_project_change, install_capabilities_draft_close_guard
from doda_facility_capabilities_editor import install_facility_capabilities_editor
from doda_facility_capabilities_draft_policy import allow_facility_capabilities_project_change, install_facility_capabilities_draft_close_guard
from doda_capability_staffing_rules_editor import install_capability_staffing_rules_editor
from doda_capability_staffing_draft_policy import allow_capability_staffing_project_change, install_capability_staffing_draft_close_guard
from doda_facility_capability_staffing_overrides_editor import install_facility_capability_staffing_overrides_editor
from doda_facility_staffing_overrides_draft_policy import allow_facility_staffing_overrides_project_change, install_facility_staffing_overrides_draft_close_guard
from doda_task_templates_editor import install_task_templates_editor
from doda_task_draft_policy import task_draft_dirty, allow_task_project_change, install_task_draft_close_guard
from doda_foims_x_preview import FoimsXPreview
from doda_network_editor import install_network_editor, network_editors_dirty
from doda_navigation import install_grouped_navigation
from doda_ui_enhancements import install_tree_autosize
import doda_network_rules
import doda_equipment_rules
import doda_care_rules
import doda_condition_rules
import doda_agent_attribute_rules
import doda_personal_care_rules
import doda_time_rules
import doda_recreation_content_rules
import doda_sobriety_rules
import doda_territory_rules
import doda_weapon_rules
import doda_hostile_rules
import doda_progression_identity_rules
import doda_authored_mission_rules
import doda_zscript_catalog
import doda_resource_rules
import doda_task_flow_rules
import doda_task_staffing_rules
import doda_collection_rules
import doda_collection_model_rules
import doda_evidence_instance_rules
import doda_task_prerequisite_rules
import doda_vehicle_rules


APP_TITLE = "DoDA Content Workbench"
APP_VERSION = "0.13.0"

SOURCE_FILES = {
    "enum_catalog": "enum_catalog.csv",
    "department_tracks": "department_tracks.csv",
    "metrics": "metrics.csv",
    "metric_tiers": "metric_tiers.csv",
    "facilities": "facilities.csv",
    "flavor_text": "flavor_text.csv",
    "qualification_catalog": "qualification_catalog.csv",
    "capabilities": "capabilities.csv",
    "facility_capabilities": "facility_capabilities.csv",
    "capability_staffing_rules": "capability_staffing_rules.csv",
    "facility_capability_staffing_overrides": (
        "facility_capability_staffing_overrides.csv"
    ),
    "task_templates": "task_templates.csv",
}


def enable_windows_dark_title_bar(window: tk.Tk) -> None:
    """Request a dark native Windows title bar for the top-level app frame."""

    if sys.platform != "win32":
        return

    try:
        import ctypes

        window.update_idletasks()

        user32 = ctypes.windll.user32
        dwm_api = ctypes.windll.dwmapi.DwmSetWindowAttribute

        user32.GetAncestor.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
        ]
        user32.GetAncestor.restype = ctypes.c_void_p

        dwm_api.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_uint,
        ]
        dwm_api.restype = ctypes.c_long

        # Tk exposes a client-area handle. DWM title-bar settings must target
        # the top-level frame window instead.
        GA_ROOT = 2
        client_handle = window.winfo_id()
        top_level_handle = user32.GetAncestor(
            ctypes.c_void_p(client_handle),
            GA_ROOT,
        )

        hwnd = top_level_handle or client_handle
        enabled = ctypes.c_int(1)

        # Attribute 20 is used by current Windows 10/11 releases.
        result = dwm_api(
            ctypes.c_void_p(hwnd),
            20,
            ctypes.byref(enabled),
            ctypes.sizeof(enabled),
        )

        if result != 0:
            # Attribute 19 is the Windows 10 1809–1909 compatibility value.
            dwm_api(
                ctypes.c_void_p(hwnd),
                19,
                ctypes.byref(enabled),
                ctypes.sizeof(enabled),
            )

    except (AttributeError, OSError, tk.TclError):
        # Unsupported Windows versions retain their standard system title bar.
        pass
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
        self.foims_preview: FoimsXPreview | None = None

        self.status_text = tk.StringVar(value="Ready.")
        self.project_text = tk.StringVar(value=str(self.project_root))
        self.validation_text = tk.StringVar(value="Validation status: unknown")
        self.export_text = tk.StringVar(value="Export status: unknown")

        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry("1280x800")
        self.minsize(1040, 650)

        self._configure_styles()

        self.after(250, lambda: enable_windows_dark_title_bar(self))
        self._build_menu()

        self.bind("<F11>", self.toggle_fullscreen)
        self.bind_all(
            "<Control-o>",
            self.open_foims_preview_from_shortcut,
        )
        self.bind_all(
            "<Control-O>",
            self.open_foims_preview_from_shortcut,
        )

        self._build_layout()
        install_track_editor(self)
        install_metrics_editor(self)
        install_metric_tiers_editor(self)
        install_facilities_editor(self)
        install_flavor_text_editor(self)
        install_enum_catalog_editor(self)
        install_qualification_catalog_editor(self)
        install_capabilities_editor(self)
        install_facility_capabilities_editor(self)
        install_capability_staffing_rules_editor(self)
        install_facility_capability_staffing_overrides_editor(self)
        install_task_templates_editor(self)
        install_network_editor(self)
        install_task_draft_close_guard(self, messagebox)
        install_capability_staffing_draft_close_guard(self, messagebox)
        install_facility_staffing_overrides_draft_close_guard(self, messagebox)
        install_qualification_draft_close_guard(self, messagebox)
        install_capabilities_draft_close_guard(self, messagebox)
        install_facility_capabilities_draft_close_guard(self, messagebox)
        install_facilities_draft_close_guard(self, messagebox)
        install_grouped_navigation(self)
        install_tree_autosize(self)
        self.refresh_all(show_message=False)

    def _configure_styles(self) -> None:
        """Apply the standard DoDA dark desktop theme."""

        palette = {
            "window": "#161b22",
            "surface": "#1f2933",
            "surface_alt": "#273340",
            "input": "#0d1117",
            "border": "#3b4754",
            "text": "#e6edf3",
            "muted": "#9da7b3",
            "accent": "#58a6ff",
            "accent_active": "#79c0ff",
            "selected": "#264f78",
            "selected_inactive": "#33475b",
        }

        self.configure(background=palette["window"])

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            ".",
            background=palette["window"],
            foreground=palette["text"],
            bordercolor=palette["border"],
            lightcolor=palette["surface"],
            darkcolor=palette["surface"],
            troughcolor=palette["input"],
            focuscolor=palette["accent"],
        )

        style.configure(
            "TFrame",
            background=palette["window"],
        )

        style.configure(
            "TLabel",
            background=palette["window"],
            foreground=palette["text"],
        )

        style.configure(
            "Title.TLabel",
            background=palette["window"],
            foreground=palette["text"],
            font=("Segoe UI", 16, "bold"),
        )

        style.configure(
            "Section.TLabel",
            background=palette["surface"],
            foreground=palette["text"],
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "Status.TLabel",
            background=palette["window"],
            foreground=palette["muted"],
            font=("Consolas", 9),
        )

        style.configure(
            "TLabelframe",
            background=palette["surface"],
            foreground=palette["text"],
            bordercolor=palette["border"],
            relief="solid",
        )

        style.configure(
            "TLabelframe.Label",
            background=palette["surface"],
            foreground=palette["accent_active"],
            font=("Segoe UI", 9, "bold"),
        )

        style.configure(
            "TButton",
            background=palette["surface_alt"],
            foreground=palette["text"],
            bordercolor=palette["border"],
            focuscolor=palette["accent"],
            padding=(10, 5),
        )

        style.map(
            "TButton",
            background=[
                ("active", palette["selected"]),
                ("pressed", palette["accent"]),
                ("disabled", palette["surface"]),
            ],
            foreground=[
                ("disabled", palette["muted"]),
            ],
        )

        style.configure(
            "TEntry",
            fieldbackground=palette["input"],
            background=palette["input"],
            foreground=palette["text"],
            insertcolor=palette["text"],
            bordercolor=palette["border"],
            lightcolor=palette["border"],
            darkcolor=palette["border"],
        )

        style.map(
            "TEntry",
            fieldbackground=[
                ("disabled", palette["surface"]),
                ("focus", palette["input"]),
            ],
            bordercolor=[
                ("focus", palette["accent"]),
            ],
        )

        style.configure(
            "TCombobox",
            fieldbackground=palette["input"],
            background=palette["surface_alt"],
            foreground=palette["text"],
            arrowcolor=palette["text"],
            bordercolor=palette["border"],
            lightcolor=palette["border"],
            darkcolor=palette["border"],
            padding=(6, 3),
        )

        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", palette["input"]),
                ("focus", palette["input"]),
                ("disabled", palette["surface"]),
            ],
            background=[
                ("readonly", palette["surface_alt"]),
                ("active", palette["selected"]),
            ],
            foreground=[
                ("readonly", palette["text"]),
                ("disabled", palette["muted"]),
            ],
            arrowcolor=[
                ("active", palette["text"]),
            ],
            bordercolor=[
                ("focus", palette["accent"]),
            ],
        )

        self.option_add("*TCombobox*Listbox.background", palette["input"])
        self.option_add("*TCombobox*Listbox.foreground", palette["text"])
        self.option_add("*TCombobox*Listbox.selectBackground", palette["selected"])
        self.option_add("*TCombobox*Listbox.selectForeground", palette["text"])
        self.option_add("*TCombobox*Listbox.font", ("Segoe UI", 9))
        style.configure(
            "TCheckbutton",
            background=palette["surface"],
            foreground=palette["text"],
            focuscolor=palette["accent"],
        )

        style.map(
            "TCheckbutton",
            background=[
                ("active", palette["surface"]),
            ],
            foreground=[
                ("disabled", palette["muted"]),
            ],
        )

        style.configure(
            "Treeview",
            background=palette["input"],
            fieldbackground=palette["input"],
            foreground=palette["text"],
            bordercolor=palette["border"],
            rowheight=25,
        )

        style.map(
            "Treeview",
            background=[
                ("selected", palette["selected"]),
                ("!focus", "selected", palette["selected_inactive"]),
            ],
            foreground=[
                ("selected", palette["text"]),
            ],
        )

        style.configure(
            "Treeview.Heading",
            background=palette["surface_alt"],
            foreground=palette["accent_active"],
            bordercolor=palette["border"],
            relief="flat",
            font=("Segoe UI", 9, "bold"),
        )

        style.map(
            "Treeview.Heading",
            background=[
                ("active", palette["selected"]),
            ],
            foreground=[
                ("active", palette["text"]),
            ],
        )

        style.configure(
            "TNotebook",
            background=palette["window"],
            bordercolor=palette["border"],
            tabmargins=(0, 0, 0, 0),
        )

        style.configure(
            "TNotebook.Tab",
            background=palette["surface_alt"],
            foreground=palette["muted"],
            bordercolor=palette["border"],
            padding=(12, 7),
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", palette["surface"]),
                ("active", palette["selected"]),
            ],
            foreground=[
                ("selected", palette["text"]),
                ("active", palette["text"]),
            ],
        )

        style.configure(
            "Vertical.TScrollbar",
            background=palette["surface_alt"],
            troughcolor=palette["input"],
            bordercolor=palette["border"],
            arrowcolor=palette["text"],
        )

        style.map(
            "Vertical.TScrollbar",
            background=[
                ("active", palette["selected"]),
            ],
        )
    def _build_menu(self) -> None:
        """Create dark drop-down menus without attaching a native Windows menu bar."""

        menu_options = {
            "tearoff": False,
            "background": "#1f2933",
            "foreground": "#e6edf3",
            "activebackground": "#264f78",
            "activeforeground": "#ffffff",
            "disabledforeground": "#6e7681",
            "borderwidth": 0,
            "relief": tk.FLAT,
        }

        self.file_menu = tk.Menu(self, **menu_options)
        self.file_menu.add_command(
            label="Choose Project Root...",
            command=self.choose_project_root,
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.request_close)

        self.actions_menu = tk.Menu(self, **menu_options)
        self.actions_menu.add_command(
            label="Refresh Source Data",
            command=lambda: self.refresh_all(show_message=True),
        )
        self.actions_menu.add_command(
            label="Validate All",
            command=self.run_validation,
        )
        self.actions_menu.add_command(
            label="Edit Metric and Tiers...",
            command=lambda: open_metric_bundle_editor(self),
        )
        self.actions_menu.add_command(
            label="Export All (Content, Rules, ZScript Catalog, PK3)",
            command=self.run_export,
        )
        self.actions_menu.add_separator()
        self.rules_only_menu = tk.Menu(self.actions_menu, **menu_options)
        self.rules_only_menu.add_command(
            label="Validate Network, Transfer, and Equipment Only",
            command=lambda: self.run_network_rules("validate", announce=True),
        )
        self.rules_only_menu.add_command(
            label="Export Rules + Catalog (Reuses Last Department Export)",
            command=lambda: self.run_network_rules("export", announce=True),
        )
        self.actions_menu.add_cascade(label="Rules Only (No PK3)", menu=self.rules_only_menu)

        self.folders_menu = tk.Menu(self, **menu_options)
        self.folders_menu.add_command(
            label="Open Source Data Folder",
            command=lambda: self.open_folder(self.source_directory),
        )
        self.folders_menu.add_command(
            label="Open Generated Output Folder",
            command=lambda: self.open_folder(self.generated_directory),
        )
        self.folders_menu.add_command(
            label="Open Validation Reports Folder",
            command=lambda: self.open_folder(self.report_directory),
        )
        self.folders_menu.add_command(
            label="Open Build Folder",
            command=lambda: self.open_folder(self.build_directory),
        )

        self.preview_menu = tk.Menu(self, **menu_options)
        self.preview_menu.add_command(
            label="Open FOIMS-X Monitor",
            command=self.open_foims_preview,
        )
        self.preview_menu.add_command(
            label="Refresh FOIMS-X Monitor",
            command=self.refresh_foims_preview,
        )
        self.preview_menu.add_separator()
        self.preview_menu.add_command(
            label="Task Resource Flow Preview (Saved Source)",
            command=lambda: open_task_flow_preview(self),
        )

        self.view_menu = tk.Menu(self, **menu_options)
        self.view_menu.add_command(
            label="Fullscreen",
            command=self.toggle_fullscreen,
            accelerator="F11",
        )
        self.view_menu.add_separator()
        self.view_menu.add_command(
            label="FOIMS-X Preview",
            command=self.open_foims_preview,
            accelerator="Ctrl+O",
        )

        self.help_menu = tk.Menu(self, **menu_options)
        self.help_menu.add_command(label="About", command=self.show_about)

    def open_foims_preview(self) -> None:
        """Open the singleton FOIMS-X preview monitor or raise it if already open."""

        if (
            self.foims_preview is not None and
            self.foims_preview.is_open()
        ):
            self.foims_preview.show()
            self.foims_preview.refresh_preview()
            return

        self.foims_preview = FoimsXPreview(self)
        self.log("Opened FOIMS-X Preview Monitor.")

    def refresh_foims_preview(self) -> None:
        """Refresh an open FOIMS-X monitor without creating a new window."""

        if (
            self.foims_preview is None or
            not self.foims_preview.is_open()
        ):
            self.open_foims_preview()
            return

        self.foims_preview.refresh_preview()
        self.foims_preview.show()
        self.log("Refreshed FOIMS-X Preview Monitor.")

    def toggle_fullscreen(
        self,
        _event: Any | None = None,
    ) -> str:
        """Toggle the main Content Workbench window between normal and full screen."""
        is_fullscreen = bool(self.attributes("-fullscreen"))
        self.attributes("-fullscreen", not is_fullscreen)
        return "break"

    def open_foims_preview_from_shortcut(
        self,
        _event: Any | None = None,
    ) -> str:
        """Open FOIMS-X from Ctrl+O while consuming the Tk key event."""
        self.open_foims_preview()
        return "break"
    def _show_client_menu(
        self,
        event: tk.Event[Any],
        menu: tk.Menu,
    ) -> str:
        """Post a client-area menu directly below the clicked menu button."""

        try:
            menu.tk_popup(
                event.x_root,
                event.y_root + event.widget.winfo_height(),
            )
        finally:
            menu.grab_release()

        return "break"

    def _build_client_menu_bar(self, parent: tk.Widget) -> None:
        """Render a dark, fully functional menu row inside the client area."""

        menu_row = tk.Frame(
            parent,
            background="#161b22",
            highlightthickness=0,
            borderwidth=0,
        )
        menu_row.pack(fill=tk.X, pady=(0, 10))

        menu_items = (
            ("File", self.file_menu),
            ("Actions", self.actions_menu),
            ("Preview", self.preview_menu),
            ("View", self.view_menu),
            ("Folders", self.folders_menu),
            ("Help", self.help_menu),
        )

        for label, menu in menu_items:
            button = tk.Menubutton(
                menu_row,
                text=label,
                menu=menu,
                background="#161b22",
                foreground="#e6edf3",
                activebackground="#264f78",
                activeforeground="#ffffff",
                disabledforeground="#6e7681",
                borderwidth=0,
                relief=tk.FLAT,
                highlightthickness=0,
                padx=10,
                pady=5,
                anchor=tk.W,
                cursor="hand2",
                font=("Segoe UI", 9),
                takefocus=True,
            )

            button.pack(side=tk.LEFT)

            button.bind(
                "<Button-1>",
                lambda event, target_menu=menu: self._show_client_menu(
                    event,
                    target_menu,
                ),
            )

            button.bind(
                "<Return>",
                lambda event, target_menu=menu: self._show_client_menu(
                    event,
                    target_menu,
                ),
            )

            button.bind(
                "<space>",
                lambda event, target_menu=menu: self._show_client_menu(
                    event,
                    target_menu,
                ),
            )

            button.bind(
                "<Enter>",
                lambda event, target=button: target.configure(
                    background="#264f78",
                    foreground="#ffffff",
                ),
            )

            button.bind(
                "<Leave>",
                lambda event, target=button: target.configure(
                    background="#161b22",
                    foreground="#e6edf3",
                ),
            )
    def select_relative_notebook_tab(self, offset: int) -> str:
        tab_ids = self.notebook.tabs()

        if not tab_ids:
            return "break"

        try:
            current_index = self.notebook.index(self.notebook.select())
        except tk.TclError:
            current_index = 0

        target_index = (current_index + offset) % len(tab_ids)

        self.notebook.select(tab_ids[target_index])
        self.notebook.focus_set()

        return "break"

    def select_previous_notebook_tab(
        self,
        _event: Any = None,
    ) -> str:
        return self.select_relative_notebook_tab(-1)

    def select_next_notebook_tab(
        self,
        _event: Any = None,
    ) -> str:
        return self.select_relative_notebook_tab(1)
    def _build_layout(self) -> None:
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        self._build_client_menu_bar(outer)

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
            foreground="#9da7b3",
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
            text="Validate All",
            command=self.run_validation,
        ).grid(row=0, column=1, padx=(0, 6))

        ttk.Button(
            action_frame,
            text="Export All",
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

        tab_navigation = ttk.Frame(outer)
        # Editor tab row removed: the grouped sidebar replaces it.

        ttk.Label(
            tab_navigation,
            text="Editor Tabs:",
            style="Section.TLabel",
        ).pack(side=tk.LEFT)

        ttk.Button(
            tab_navigation,
            text="◀ Previous Tab",
            command=self.select_previous_notebook_tab,
        ).pack(side=tk.RIGHT)

        ttk.Button(
            tab_navigation,
            text="Next Tab ▶",
            command=self.select_next_notebook_tab,
        ).pack(side=tk.RIGHT, padx=(0, 6))

        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.bind_all(
            "<Control-Prior>",
            self.select_previous_notebook_tab,
            add="+",
        )

        self.bind_all(
            "<Control-Next>",
            self.select_next_notebook_tab,
            add="+",
        )

        self.dashboard_tab = ttk.Frame(self.notebook, padding=10)
        self.tracks_tab = ttk.Frame(self.notebook, padding=10)
        self.metrics_tab = ttk.Frame(self.notebook, padding=10)
        self.metric_tiers_tab = ttk.Frame(self.notebook, padding=10)
        self.facilities_tab = ttk.Frame(self.notebook, padding=10)
        self.flavor_tab = ttk.Frame(self.notebook, padding=10)
        self.qualifications_tab = ttk.Frame(self.notebook, padding=10)
        self.capabilities_tab = ttk.Frame(self.notebook, padding=10)
        self.facility_capabilities_tab = ttk.Frame(self.notebook, padding=10)
        self.capability_staffing_rules_tab = ttk.Frame(self.notebook, padding=10)
        self.staffing_overrides_tab = ttk.Frame(self.notebook, padding=10)
        self.task_templates_tab = ttk.Frame(self.notebook, padding=10)
        self.activity_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.tracks_tab, text="Department Tracks — Editor")
        self.notebook.add(self.metrics_tab, text="Metrics — Editor")
        self.notebook.add(self.metric_tiers_tab, text="Metric Tiers — Editor")
        self.notebook.add(self.facilities_tab, text="Facilities — Editor")
        self.notebook.add(self.flavor_tab, text="Flavor Text — Editor")
        self.notebook.add(self.qualifications_tab, text="Qualifications — Editor")
        self.notebook.add(self.capabilities_tab, text="Capabilities — Editor")
        self.notebook.add(self.facility_capabilities_tab, text="Facility Capabilities — Editor")
        self.notebook.add(self.capability_staffing_rules_tab, text="Capability Staffing Rules — Editor")
        self.notebook.add(self.staffing_overrides_tab, text="Facility Staffing Overrides — Editor")
        self.notebook.add(self.task_templates_tab, text="Task Templates — Editor")
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
            text="v0.13 - Export All rebuilds content, rules, and the read-only ZScript catalog, including facilities and capabilities.",
            foreground="#9da7b3",
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
            background="#0d1117",
            foreground="#e6edf3",
            insertbackground="#e6edf3",
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
            background="#0d1117",
            foreground="#e6edf3",

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
            if hasattr(self, "metrics_editor"):
                self.metrics_editor.update()

            if hasattr(self, "metric_tiers_editor"):
                self.metric_tiers_editor.update()

            if hasattr(self, "facilities_editor"):
                self.facilities_editor.update()

            if hasattr(self, "enum_catalog_editor"):
                self.enum_catalog_editor.update()

            if hasattr(self, "qualification_catalog_editor"):
                self.qualification_catalog_editor.update()

            if hasattr(self, "capabilities_editor"):
                self.capabilities_editor.update()

            if hasattr(self, "facility_capabilities_editor"):
                self.facility_capabilities_editor.update()

            if hasattr(self, "capability_staffing_rules_editor"):
                self.capability_staffing_rules_editor.update()

            if hasattr(self, "facility_capability_staffing_overrides_editor"):
                self.facility_capability_staffing_overrides_editor.update()

            if hasattr(self, "task_templates_editor"):
                self.task_templates_editor.update()

            for network_editor in getattr(self, "network_editors", []):
                network_editor.update()

            if hasattr(self, "transfer_rules_view"):
                self.transfer_rules_view.update()

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
                f"Current mode: V1.1 authoring data is loaded; editor coverage is expanding."
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
        task_editor = getattr(self, "task_templates_editor", None)
        if task_editor is not None and getattr(task_editor, "dirty", False):
            self.log("Task Templates note: applied drafts are not included; this action uses saved source. Save to Source first to include them.")
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

        if not self.run_command(
            label="Validation",
            command=command,
            success_message="Validation completed successfully.",
            announce_success=False,
        ):
            return
        if self.run_network_rules("validate", announce=False):
            self.status_text.set("Validate All passed.")
            messagebox.showinfo(APP_TITLE, "Validate All passed. See the Activity Log for warnings.")

    def run_export(self) -> None:
        task_editor = getattr(self, "task_templates_editor", None)
        if task_editor is not None and getattr(task_editor, "dirty", False):
            self.log("Task Templates note: applied drafts are not included; this action uses saved source. Save to Source first to include them.")
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

        if not self.run_command(
            label="Export",
            command=command,
            success_message="Export and PK3 build completed successfully.",
            announce_success=False,
        ):
            self.log("Export All stopped: content export failed; catalog was not regenerated.")
            return
        if not self.run_network_rules("export", announce=False):
            self.status_text.set("Export All incomplete: rules/catalog export failed.")
            self.log("Export All incomplete: content/PK3 may have updated; no full success.")
            return
        self.status_text.set("Export All completed successfully.")
        messagebox.showinfo(APP_TITLE, "Export All completed: content, PK3, rules, and ZScript catalog.")

    def run_network_rules(self, mode: str, announce: bool) -> bool:
        """Validate or export network/transfer rules in-process and log the result.

        announce=False only raises a dialog on failure (used after the main
        validation/export so the user does not get two success dialogs).
        """
        dirty = network_editors_dirty(self)
        if dirty:
            self.log("Network rules note: unsaved drafts are not included: " + ", ".join(dirty))
        try:
            if mode == "export":
                if announce:
                    self.log("Rules-only export reuses generated/data/department_content.json; "
                             "use Export All to include saved facility/capability changes.")
                result, out_path = doda_network_rules.export(self.project_root)
                resource_result, resource_path = doda_resource_rules.export(self.project_root)
                result.errors += resource_result.errors
                result.warnings += resource_result.warnings
                flow_result, flow_path = doda_task_flow_rules.export(self.project_root)
                result.errors += flow_result.errors
                result.warnings += flow_result.warnings
                staffing_result, staffing_path = doda_task_staffing_rules.export(self.project_root)
                result.errors += staffing_result.errors
                result.warnings += staffing_result.warnings
                collection_result, collection_path = doda_collection_rules.export(self.project_root)
                result.errors += collection_result.errors
                result.warnings += collection_result.warnings
                collection_models_result, collection_models_path = doda_collection_model_rules.export(self.project_root)
                result.errors += collection_models_result.errors
                result.warnings += collection_models_result.warnings
                evidence_result, evidence_path = doda_evidence_instance_rules.export(self.project_root)
                result.errors += evidence_result.errors
                result.warnings += evidence_result.warnings
                prerequisite_result, prerequisite_path = doda_task_prerequisite_rules.export(self.project_root)
                result.errors += prerequisite_result.errors
                result.warnings += prerequisite_result.warnings
                vehicle_result, vehicle_path = doda_vehicle_rules.export(self.project_root)
                result.errors += vehicle_result.errors
                result.warnings += vehicle_result.warnings
                if vehicle_path is not None:
                    self.log(f"Vehicle catalog exported: {vehicle_path}")
                if prerequisite_path is not None:
                    self.log(f"Task prerequisites exported: {prerequisite_path}")
                if evidence_path is not None:
                    self.log(f"Evidence type instances exported: {evidence_path}")
                if collection_models_path is not None:
                    self.log(f"Collection models exported: {collection_models_path}")
                if collection_path is not None:
                    self.log(f"Collection receptacles exported: {collection_path}")
                if staffing_path is not None:
                    self.log(f"Task staffing rules exported: {staffing_path}")
                if flow_path is not None:
                    self.log(f"Task resource flows exported: {flow_path}")
                if resource_path is not None:
                    self.log(f"Resource catalog exported: {resource_path}")
                if result.valid:
                    equipment_result, equipment_path = doda_equipment_rules.export(self.project_root)
                    result.errors += equipment_result.errors
                    result.warnings += equipment_result.warnings
                    if equipment_path is not None:
                        self.log(f"Equipment catalog exported: {equipment_path}")
                    care_result, care_path = doda_care_rules.export(self.project_root)
                    result.errors += care_result.errors
                    result.warnings += care_result.warnings
                    if care_path is not None:
                        self.log(f"Care services catalog exported: {care_path}")
                    condition_result, condition_path = doda_condition_rules.export(self.project_root)
                    result.errors += condition_result.errors
                    result.warnings += condition_result.warnings
                    if condition_path is not None:
                        self.log(f"Personnel conditions catalog exported: {condition_path}")
                    attribute_result, attribute_path = doda_agent_attribute_rules.export(self.project_root)
                    result.errors += attribute_result.errors
                    result.warnings += attribute_result.warnings
                    if attribute_path is not None:
                        self.log(f"Personnel traits/training catalog exported: {attribute_path}")
                    pcare_result, pcare_path = doda_personal_care_rules.export(self.project_root)
                    result.errors += pcare_result.errors
                    result.warnings += pcare_result.warnings
                    if pcare_path is not None:
                        self.log(f"Personal-care catalog exported: {pcare_path}")
                    time_result, time_path = doda_time_rules.export(self.project_root)
                    result.errors += time_result.errors
                    result.warnings += time_result.warnings
                    if time_path is not None:
                        self.log(f"Time settings catalog exported: {time_path}")
                    rc_result, rc_path = doda_recreation_content_rules.export(self.project_root)
                    result.errors += rc_result.errors
                    result.warnings += rc_result.warnings
                    if rc_path is not None:
                        self.log(f"Recreation content catalog exported: {rc_path}")
                    sobriety_result, sobriety_path = doda_sobriety_rules.export(self.project_root)
                    result.errors += sobriety_result.errors
                    result.warnings += sobriety_result.warnings
                    if sobriety_path is not None:
                        self.log(f"Sobriety catalog exported: {sobriety_path}")
                    territory_result, territory_path = doda_territory_rules.export(self.project_root)
                    result.errors += territory_result.errors
                    result.warnings += territory_result.warnings
                    if territory_path is not None:
                        self.log(f"Territory catalog exported: {territory_path}")
                    weapon_result, weapon_path = doda_weapon_rules.export(self.project_root)
                    result.errors += weapon_result.errors
                    result.warnings += weapon_result.warnings
                    if weapon_path is not None:
                        self.log(f"Weapon catalog exported: {weapon_path}")
                    hostile_result, hostile_path = doda_hostile_rules.export(self.project_root)
                    result.errors += hostile_result.errors
                    result.warnings += hostile_result.warnings
                    if hostile_path is not None:
                        self.log(f"Hostile catalog exported: {hostile_path}")
                    identity_result, identity_path = doda_progression_identity_rules.export(self.project_root)
                    result.errors += identity_result.errors
                    result.warnings += identity_result.warnings
                    if identity_path is not None:
                        self.log(f"Progression identity catalog exported: {identity_path}")
                    mission_result, mission_path = doda_authored_mission_rules.export(self.project_root)
                    result.errors += mission_result.errors
                    result.warnings += mission_result.warnings
                    if mission_path is not None:
                        self.log(f"Authored mission catalog exported: {mission_path}")
                    if (equipment_result.valid and care_result.valid and condition_result.valid
                            and attribute_result.valid and pcare_result.valid and time_result.valid and rc_result.valid):
                        catalog_path, catalog_sha, included = doda_zscript_catalog.generate(self.project_root)
                        self.log(f"ZScript catalog regenerated: {catalog_path} sha256 {catalog_sha[:16]}")
                        if not included:
                            result.warnings.append("zscript.txt does not include DoDA/Generated/WorkbenchCatalog.zs")
            else:
                result = doda_network_rules.Result()
                doda_network_rules.validate_contract(result)
                doda_network_rules.validate_network(self.project_root, result)
                doda_equipment_rules.validate_equipment(self.project_root, result)
                doda_care_rules.validate_care(self.project_root, result)
                doda_condition_rules.validate_conditions(self.project_root, result)
                doda_agent_attribute_rules.validate_attributes(self.project_root, result)
                doda_personal_care_rules.validate_personal_care(self.project_root, result)
                doda_time_rules.validate_time_settings(self.project_root, result)
                doda_recreation_content_rules.validate_recreation_content(self.project_root, result)
                doda_sobriety_rules.validate_sobriety(self.project_root, result)
                doda_territory_rules.validate_territory(self.project_root, result)
                doda_weapon_rules.validate_weapons(self.project_root, result)
                doda_hostile_rules.validate_hostiles(self.project_root, result)
                doda_progression_identity_rules.validate_identities(self.project_root, result)
                doda_authored_mission_rules.validate_authored_missions(self.project_root, result)
                doda_resource_rules.validate_resources(self.project_root, result)
                doda_task_flow_rules.validate_flows(self.project_root, result)
                doda_task_staffing_rules.validate_staffing(self.project_root, result)
                doda_collection_rules.validate_collection(self.project_root, result)
                doda_collection_model_rules.validate_models(self.project_root, result)
                doda_evidence_instance_rules.validate_instances(self.project_root, result)
                doda_task_prerequisite_rules.validate_prerequisites(self.project_root, result)
                doda_vehicle_rules.validate_vehicles(self.project_root, result)
                if result.valid and not doda_zscript_catalog.is_current(self.project_root):
                    result.warnings.append("ZScript catalog is stale; export network rules to regenerate it")
                out_path = None
        except Exception as error:
            self.log(f"Network rules {mode} error: {error}")
            messagebox.showerror(APP_TITLE, f"Network rules {mode} could not run.\n\n{error}")
            return False
        for line in result.warnings:
            self.log(f"  NETWORK WARNING: {line}")
        for line in result.errors:
            self.log(f"  NETWORK ERROR: {line}")
        if out_path is not None:
            self.log(f"Network rules exported: {out_path}")
        verdict = "PASS" if result.valid else "FAIL"
        self.log(f"Network rules {mode}: {verdict} ({len(result.errors)} errors, {len(result.warnings)} warnings)")
        if not result.valid:
            messagebox.showerror(APP_TITLE, f"Network rules {mode} failed. See the Activity Log.")
        elif announce:
            messagebox.showinfo(APP_TITLE, f"Network rules {mode} passed ({len(result.warnings)} warnings).")
        return result.valid

    def request_close(self) -> None:
        handler = getattr(self, "_network_close_handler", None)
        if handler is not None:
            handler()
        else:
            self.destroy()

    def run_command(
        self,
        label: str,
        command: list[str],
        success_message: str,
        announce_success: bool = True,
    ) -> bool:
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
                if announce_success:
                    messagebox.showinfo(APP_TITLE, success_message)
                return True
            else:
                self.status_text.set(f"{label} failed.")
                messagebox.showerror(
                    APP_TITLE,
                    f"{label} failed with exit code {completed.returncode}.\n\n"
                    "Review the Activity Log tab for complete output.",
                )
                return False

        except OSError as error:
            self.status_text.set(f"{label} could not start.")
            self.log(f"{label} launch error: {error}")
            messagebox.showerror(
                APP_TITLE,
                f"Could not start {label.lower()}.\n\n{error}",
            )
            return False
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
        if not allow_facilities_project_change(self, messagebox):
            return
        if not allow_facility_capabilities_project_change(self, messagebox):
            return
        if not allow_capabilities_project_change(self, messagebox):
            return
        if not allow_qualification_project_change(self, messagebox):
            return
        if not allow_facility_staffing_overrides_project_change(self, messagebox):
            return
        if not allow_capability_staffing_project_change(self, messagebox):
            return
        if not allow_task_project_change(self, messagebox):
            return
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

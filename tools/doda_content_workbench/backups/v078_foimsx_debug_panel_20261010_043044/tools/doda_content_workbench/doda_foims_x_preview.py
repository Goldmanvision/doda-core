#!/usr/bin/env python3
"""
FOIMS-X High-Resolution Presentation Preview.

The FOIMS-X interface is defined on a 640 x 480 design grid but is drawn
directly at the final active 4:3 display dimensions. Text, borders, panels,
and wrap widths therefore scale with the selected presentation target rather
than being raster-scaled from a small intermediate image.
"""

from __future__ import annotations

import math
import tkinter as tk
import time
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import ttk, messagebox
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageTk

from doda_foims_x_sandbox import FoimsXSandbox
from doda_foims_x_facility_catalog import FacilityCatalog, status
from doda_foims_x_reference_catalog import TaskCatalog, QualificationCatalog
from doda_foims_x_roster import SandboxRoster, AVAILABLE, UNAVAILABLE
from doda_foims_x_personnel_catalog import PersonnelCatalog


DESIGN_SIZE = (640, 480)

# Dual CRT hardware scene dimensions.
DUAL_CRT_OVERLAY_SIZE = (1920, 1080)

# Physical display openings inside the dual CRT overlay.
# Format: x, y, width, height.
LEFT_CRT_APERTURE = (35, 110, 860, 640)
RIGHT_CRT_APERTURE = (1025, 110, 860, 640)

# Exact 4:3 FOIMS-X viewport inside each 860 x 640 physical opening.
FOIMS_VIEWPORT_SIZE = (853, 640)

# Compatibility alias for any existing CRT overlay reference.
CRT_OVERLAY_SIZE = DUAL_CRT_OVERLAY_SIZE

# Native overlay screen opening: x, y, width, height.
# The bezel is scaled and positioned from this rectangle—not from
# the outer monitor dimensions—so its opening exactly matches FOIMS-X.
CRT_SCREEN_APERTURE = (79, 50, 241, 181)

# Insets are applied inside the CRT opening after scaling. They preserve
# the visible bezel lip and make FOIMS-X appear behind the monitor glass.
CRT_SCREEN_INSET = (3, 3, 3, 4)

PRESENTATION_SIZES = {
    "720p (1280 x 720)": (1280, 720),
    "1080p (1920 x 1080)": (1920, 1080),
    "1440p (2560 x 1440)": (2560, 1440),
    "4K (3840 x 2160)": (3840, 2160),
}

PALETTE = {
    "desktop": "#07090B",
    "screen": "#06100B",
    "screen_alt": "#09190F",
    "panel": "#0C2417",
    "panel_alt": "#10301E",
    "border": "#4C9A6D",
    "grid": "#123D28",
    "text": "#B9FFD3",
    "muted": "#75B994",
    "accent": "#84FFB4",
    "shadow": "#000000",
    "fallback": "#8C939F",
}


def normalize_hex(value: str, fallback: str = PALETTE["fallback"]) -> str:
    color = value.strip().upper()

    if len(color) != 7 or not color.startswith("#"):
        return fallback

    allowed = "0123456789ABCDEF"

    if all(character in allowed for character in color[1:]):
        return color

    return fallback


def active_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("active", "TRUE").strip().upper() != "FALSE"
    ]


def numeric_value(value: str, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


# FOIMS_X_CANONICAL_CLOCK_1992_02_01
# Canonical DoDA campaign epoch: February 1, 1992 at 00:00:00.
# One real second advances one in-game minute.
FOIMS_X_EPOCH = datetime(1992, 2, 1, 0, 0, 0)
FOIMS_X_GAME_MINUTES_PER_REAL_SECOND = 1
FOIMS_X_GAME_DAY_MINUTES = 24 * 60


def foims_x_game_clock(elapsed_real_seconds: float) -> dict[str, object]:
    """Convert monotonic preview elapsed time into FOIMS-X campaign time."""
    elapsed_game_minutes = max(
        0,
        int(elapsed_real_seconds * FOIMS_X_GAME_MINUTES_PER_REAL_SECOND),
    )

    game_datetime = FOIMS_X_EPOCH + timedelta(minutes=elapsed_game_minutes)
    day_number = elapsed_game_minutes // FOIMS_X_GAME_DAY_MINUTES + 1
    minute_of_day = elapsed_game_minutes % FOIMS_X_GAME_DAY_MINUTES

    return {
        "date": game_datetime.strftime("%Y-%m-%d"),
        "time": game_datetime.strftime("%H:%M:%S"),
        "day": day_number,
        "cycle_percent": minute_of_day / FOIMS_X_GAME_DAY_MINUTES * 100.0,
    }


class FoimsXPreview:
    """Read-only FOIMS-X authoring preview at high-resolution output."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self.window = tk.Toplevel(app)
        self.window.title("FOIMS-X Local Simulation Preview")
        self.window.geometry("1400x960")
        self.window.minsize(900, 680)
        self.window.configure(background=PALETTE["desktop"])

        self.presentation_size_name = tk.StringVar(
            value="1080p (1920 x 1080)"
        )
        self.status_text = tk.StringVar(
            value="FOIMS-X native high-resolution preview ready."
        )
        self._photo: ImageTk.PhotoImage | None = None
        self._canvas_image_id: int | None = None
        self._presented_size: tuple[int, int] | None = None
        self._pending_resize: str | None = None
        self.sandbox = FoimsXSandbox(app.tables)
        self.roster = SandboxRoster(app.tables)
        self._clock_after_id = None
        self._frame_snapshot = self.sandbox.snapshot()
        self._activity_window = None
        self._activity_tree = None
        self._activity_signature = None

        self._build_controls()
        self._build_catalog_controls()
        self._build_canvas()

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind("<Control-r>", self.refresh_preview)
        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)
        self.window.bind("<Configure>", self._on_resize)
        self.window.after_idle(self.refresh_preview)
        self._clock_after_id = self.window.after(1000, self._clock_tick)

    def is_open(self) -> bool:
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False

    def _current_game_clock(self) -> dict[str, object]:
        return self._frame_snapshot

    def _clock_tick(self) -> None:
        self._clock_after_id = None
        if not self.is_open():
            return
        self.sandbox.tick()
        self.render()
        self._clock_after_id = self.window.after(1000, self._clock_tick)

    def _toggle_simulation(self) -> None:
        if self.sandbox.running:
            self.sandbox.pause()
        else:
            self.sandbox.play()
        self.render()

    def _step_simulation(self) -> None:
        if self.sandbox.running:
            return
        self.sandbox.step(int(self.step_minutes.get()))
        self.render()

    def _reset_simulation(self) -> None:
        self.sandbox.reset(self.app.tables)
        self.roster.reset()
        self._populate_metric_controls()
        if hasattr(self, "_facility_catalog"):
            self._refresh_facility_catalog()
        self.render()

    def _gather_evidence(self):
        try:
            self.sandbox.gather_evidence(self.evidence_amount.get())
        except ValueError as error:
            messagebox.showerror("Sandbox Evidence", str(error), parent=self.window)
            return
        self.render()

    def _spend_evidence(self):
        try:
            self.sandbox.spend_evidence(self.evidence_amount.get())
        except ValueError as error:
            messagebox.showerror("Sandbox Evidence", str(error), parent=self.window)
            return
        self.render()

    def _populate_metric_controls(self):
        ids = tuple(r["metric_id"] for r in self.sandbox.metric_rows())
        self.metric_combo.configure(values=ids)
        if self.selected_metric.get() not in ids:
            self.selected_metric.set(ids[0] if ids else "")
        self._select_metric()

    def _select_metric(self, _event=None):
        metric_id = self.selected_metric.get()
        row = next((r for r in self.sandbox.metric_rows()
                    if r["metric_id"] == metric_id), None)
        if row is None:
            self.metric_bounds.set("No active metrics")
            self.metric_value.set("")
            return
        self.metric_bounds.set(
            f'{row.get("display_name", metric_id)} | '
            f'{row["internal_min"]} to {row["internal_max"]}'
        )
        self.metric_value.set(str(int(self.sandbox.metrics[metric_id])))
        if hasattr(self, "canvas"):
            self.render()

    def _apply_metric(self):
        try:
            self.sandbox.set_metric(
                self.selected_metric.get(), self.metric_value.get()
            )
        except ValueError as error:
            messagebox.showerror(
                "Sandbox metric value", str(error), parent=self.window
            )
            return
        self.metric_value.set(
            str(int(self.sandbox.metrics[self.selected_metric.get()]))
        )
        self.render()

    def _visible_metric_rows(self):
        selected = self.selected_metric.get()
        return sorted(
            self.sandbox.metric_rows(),
            key=lambda row: row["metric_id"] != selected
        )[:3]

    def _show_activity(self):
        if self._activity_window is not None:
            try:
                if self._activity_window.winfo_exists():
                    self._activity_window.lift()
                    return
            except tk.TclError:
                pass

        self._activity_window = tk.Toplevel(self.window)
        self._activity_window.title("FOIMS-X Sandbox Activity - latest 200 changes")
        self._activity_window.geometry("900x380")
        frame = ttk.Frame(self._activity_window, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ("time", "metric", "before", "after")
        self._activity_tree = ttk.Treeview(
            frame, columns=columns, show="headings"
        )
        for key, label, width in (
            ("time", "Strategic time", 180),
            ("metric", "Metric / Transaction", 220),
            ("before", "Before", 240),
            ("after", "After", 240),
        ):
            self._activity_tree.heading(key, text=label)
            self._activity_tree.column(key, width=width)

        scroll = ttk.Scrollbar(
            frame, orient=tk.VERTICAL, command=self._activity_tree.yview
        )
        self._activity_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._activity_tree.pack(fill=tk.BOTH, expand=True)
        self._activity_signature = None
        self._refresh_activity()

    def _refresh_activity(self):
        if self._activity_tree is None:
            return
        try:
            if not self._activity_tree.winfo_exists():
                return
            entries = self._frame_snapshot.get("activity", [])
            signature = repr(entries)
            if signature == self._activity_signature:
                return
            children = self._activity_tree.get_children()
            if children:
                self._activity_tree.delete(*children)
            for entry in entries:
                self._activity_tree.insert(
                    "", "end", values=self.sandbox.activity_columns(entry)
                )
            self._activity_signature = signature
        except tk.TclError:
            pass

    def _build_catalog_controls(self):
        row = ttk.Frame(self.controls)
        row.pack(fill=tk.X, pady=(8, 0))
        self.catalog_mode = tk.StringVar(value="Overview")
        self.catalog_facility_id = tk.StringVar()
        self.catalog_info = tk.StringVar()
        self._catalog_detail_page = 0
        ttk.Label(row, text="FOIMS-X screen:").pack(side=tk.LEFT)
        mode = ttk.Combobox(
            row, state="readonly", width=16,
            values=("Overview", "Facilities", "Task Templates", "Qualifications", "Personnel"), textvariable=self.catalog_mode
        )
        mode.pack(side=tk.LEFT, padx=6)
        mode.bind("<<ComboboxSelected>>", self._catalog_mode_changed)
        self.catalog_facility_combo = ttk.Combobox(
            row, state="readonly", width=28,
            textvariable=self.catalog_facility_id
        )
        self.catalog_facility_combo.pack(side=tk.LEFT, padx=6)
        self.catalog_facility_combo.bind("<<ComboboxSelected>>", self._catalog_selected)
        ttk.Button(row, text="Previous Entry",
                   command=lambda: self._catalog_move(-1)).pack(side=tk.LEFT)
        ttk.Button(row, text="Next Entry",
                   command=lambda: self._catalog_move(1)).pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="Details <",
                   command=lambda: self._catalog_page(-1)).pack(side=tk.LEFT)
        ttk.Button(row, text="Details >",
                   command=lambda: self._catalog_page(1)).pack(side=tk.LEFT, padx=4)
        ttk.Label(self.controls, textvariable=self.catalog_info).pack(fill=tk.X)
        roster_row = ttk.Frame(self.controls)
        roster_row.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(roster_row, text="Sandbox roster (Personnel screen):").pack(side=tk.LEFT)
        ttk.Button(roster_row, text="Toggle Availability",
                   command=self._roster_toggle).pack(side=tk.LEFT, padx=6)
        ttk.Button(roster_row, text="Reset Roster",
                   command=self._roster_reset).pack(side=tk.LEFT)
        self._refresh_facility_catalog()

    def _refresh_facility_catalog(self):
        if not hasattr(self, "_catalog_selection_by_mode"):
            self._catalog_selection_by_mode = {}
            self._catalog_page_by_mode = {}
        old_mode = getattr(self, "_catalog_loaded_mode", None)
        if old_mode is not None:
            self._catalog_selection_by_mode[old_mode] = self.catalog_facility_id.get()
            self._catalog_page_by_mode[old_mode] = self._catalog_detail_page

        mode = self.catalog_mode.get()
        if mode == "Overview":
            mode = old_mode or "Facilities"
        classes = {
            "Facilities": FacilityCatalog,
            "Task Templates": TaskCatalog,
            "Qualifications": QualificationCatalog,
        }
        self._catalog_loaded_mode = mode
        if mode == "Personnel":
            self._facility_catalog = PersonnelCatalog(self.app.tables, self.roster)
        else:
            self._facility_catalog = classes[mode](self.app.tables)
        self._catalog_rows = self._facility_catalog.facilities()
        ids = tuple(row.get("facility_id", "") for row in self._catalog_rows)
        self.catalog_facility_combo.configure(values=ids)
        selected = self._catalog_selection_by_mode.get(mode, "")
        self.catalog_facility_id.set(
            selected if selected in ids else (ids[0] if ids else "")
        )
        self._catalog_detail_page = self._catalog_page_by_mode.get(mode, 0)
        self._update_catalog_info()
        if hasattr(self, "canvas"):
            self.render()

    def _catalog_mode_changed(self, _event=None):
        self._refresh_facility_catalog()

    def _roster_toggle(self):
        if self.catalog_mode.get() != "Personnel":
            return
        agent = self.roster.get(self.catalog_facility_id.get())
        if agent is None:
            return
        self.roster.set_availability(
            agent.agent_id,
            UNAVAILABLE if agent.availability == AVAILABLE else AVAILABLE,
        )
        self._refresh_facility_catalog()

    def _roster_reset(self):
        self.roster.reset()
        if self.catalog_mode.get() == "Personnel":
            self._refresh_facility_catalog()

    def _catalog_selected(self, _event=None):
        self._catalog_detail_page = 0
        self._update_catalog_info()
        if hasattr(self, "canvas"):
            self.render()

    def _catalog_move(self, delta):
        ids = [row.get("facility_id", "") for row in self._catalog_rows]
        if not ids:
            return
        current = self.catalog_facility_id.get()
        index = ids.index(current) if current in ids else 0
        self.catalog_facility_id.set(ids[(index + delta) % len(ids)])
        self._catalog_selected()

    def _catalog_page(self, delta):
        pages = self._facility_catalog.pages(self.catalog_facility_id.get())
        self._catalog_detail_page = max(
            0, min(len(pages) - 1, self._catalog_detail_page + delta)
        )
        self._update_catalog_info()
        if hasattr(self, "canvas"):
            self.render()

    def _update_catalog_info(self):
        selected = self.catalog_facility_id.get()
        row = next(
            (r for r in self._catalog_rows if r.get("facility_id") == selected), {}
        )
        pages = self._facility_catalog.pages(selected)
        self._catalog_detail_page = min(self._catalog_detail_page, len(pages) - 1)
        self.catalog_info.set(
            f'Catalog: {row.get("display_name", selected) or "No entries"} | '
            f'{len(self._catalog_rows)} entries | '
            f'Details {self._catalog_detail_page + 1}/{len(pages)} | Read only'
        )

    def _render_facility_catalog(self, active_width, active_height):
        image = Image.new("RGBA", (active_width, active_height), PALETTE["screen"])
        draw = ImageDraw.Draw(image)
        scale_x = active_width / DESIGN_SIZE[0]
        scale_y = active_height / DESIGN_SIZE[1]
        ui_scale = min(scale_x, scale_y)

        def panel(x0, y0, x1, y1, fill):
            draw.rectangle(
                (round(x0 * scale_x), round(y0 * scale_y),
                 round(x1 * scale_x), round(y1 * scale_y)),
                fill=fill, outline=PALETTE["border"],
                width=max(1, round(ui_scale))
            )

        def label(x, y, value, size=9, color=None):
            self._draw_text(
                image, round(x * scale_x), round(y * scale_y), value,
                max(8, round(size * ui_scale)), color or PALETTE["text"]
            )

        panel(12, 12, 628, 468, PALETTE["screen"])
        panel(18, 18, 622, 48, PALETTE["panel"])
        label(28, 26, "FOIMS-X / " + self.catalog_mode.get().upper() + (" / SANDBOX ROSTER" if self.catalog_mode.get() == "Personnel" else " / READ-ONLY CATALOG"), 11, PALETTE["accent"])
        panel(18, 58, 198, 446, PALETTE["screen_alt"])
        panel(206, 58, 622, 446, PALETTE["screen_alt"])
        label(26, 69, self.catalog_mode.get().upper(), 10, PALETTE["accent"])
        label(216, 69, "SELECTED ENTRY DETAILS", 10, PALETTE["accent"])

        selected = self.catalog_facility_id.get()
        ids = [row.get("facility_id", "") for row in self._catalog_rows]
        index = ids.index(selected) if selected in ids else 0
        start = index // 8 * 8
        for offset, row in enumerate(self._catalog_rows[start:start + 8]):
            y = 92 + offset * 40
            focused = row.get("facility_id") == selected
            if focused:
                panel(22, y - 4, 194, y + 32, PALETTE["panel_alt"])
            name = row.get("display_name") or row.get("facility_id", "")
            label(28, y, ("> " if focused else "  ") + name[:20], 8,
                  PALETTE["accent"] if focused else PALETTE["text"])
            label(40, y + 16, status(row), 8, PALETTE["muted"])

        if not self._catalog_rows:
            label(28, 100, "NO CATALOG ENTRIES", 8, PALETTE["muted"])

        pages = self._facility_catalog.pages(selected)
        page = min(self._catalog_detail_page, len(pages) - 1)
        for offset, line in enumerate(pages[page]):
            label(216, 92 + offset * 15, line, 8)

        panel(18, 452, 622, 466, PALETTE["panel"])
        label(26, 455,
              f'CATALOG ONLY / DETAILS {page + 1}/{len(pages)} / NO PURCHASES OR STAFFING CHANGES',
              7, PALETTE["muted"])
        return image

    def show(self) -> None:
        if not self.is_open():
            return

        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def close(self) -> None:
        self.sandbox.pause()
        for owner, name in ((self.window, "_clock_after_id"), (self.canvas, "_pending_resize")):
            callback = getattr(self, name, None)
            if callback is not None:
                try:
                    owner.after_cancel(callback)
                except tk.TclError:
                    pass
                setattr(self, name, None)
        if self.is_open():
            self.window.destroy()


    def toggle_fullscreen(
        self,
        _event: tk.Event[Any] | None = None,
    ) -> str:
        """
        Toggle FOIMS-X presentation fullscreen.

        Fullscreen intentionally hides all authoring controls and status
        readouts, leaving only the FOIMS-X image and CRT overlay visible.
        """
        if bool(self.window.attributes("-fullscreen")):
            self.exit_fullscreen()
            return "break"

        self.controls.pack_forget()
        self.status_label.pack_forget()

        self.window.attributes("-fullscreen", True)
        self.window.after_idle(self._render_fullscreen_presentation)

        return "break"

    def exit_fullscreen(
        self,
        _event: tk.Event[Any] | None = None,
    ) -> str:
        """
        Exit FOIMS-X presentation fullscreen and restore authoring controls.
        """
        if not bool(self.window.attributes("-fullscreen")):
            return "break"

        self.window.attributes("-fullscreen", False)

        self.controls.pack(fill=tk.X, before=self.canvas)
        self.status_label.pack(fill=tk.X, pady=(0, 6), before=self.canvas)

        self.window.after_idle(self.render)

        return "break"

    def _render_fullscreen_presentation(self) -> None:
        """Render after Tkinter applies its final fullscreen geometry."""
        if not self.is_open():
            return

        if self._pending_resize is not None:
            self.canvas.after_cancel(self._pending_resize)

        # Tk updates fullscreen canvas metrics asynchronously. Render after
        # the geometry event has settled, not during the transition frame.
        self._pending_resize = self.canvas.after(120, self.render)

    def _font_path(self) -> Path:
        return (
            self.app.project_root
            / "tools"
            / "doda_content_workbench"
            / "assets"
            / "fonts"
            / "perfect_dos_vga_437"
            / "Perfect DOS VGA 437 Win.ttf"
        )

    def _overlay_path(self) -> Path:
        return (
            self.app.project_root
            / "tools"
            / "doda_content_workbench"
            / "assets"
            / "crt_overlay.png"
        )

    def _build_controls(self) -> None:
        self.controls = ttk.Frame(self.window, padding=(10, 8))
        self.controls.pack(fill=tk.X)
        toolbar = ttk.Frame(self.controls)
        toolbar.pack(fill=tk.X)
        controls = toolbar
        simulation_controls = ttk.Frame(self.controls)
        simulation_controls.pack(fill=tk.X, pady=(8, 0))
        self.play_button = ttk.Button(simulation_controls, text="Play", command=self._toggle_simulation)
        self.play_button.pack(side=tk.LEFT)
        self.step_minutes = tk.StringVar(value="1")
        self.step_combo = ttk.Combobox(simulation_controls, state="readonly", width=8,
                                      values=("1", "10", "60", "1440"), textvariable=self.step_minutes)
        self.step_combo.pack(side=tk.LEFT, padx=6)
        ttk.Label(simulation_controls, text="strategic minutes").pack(side=tk.LEFT)
        self.step_button = ttk.Button(simulation_controls, text="Step", command=self._step_simulation)
        self.step_button.pack(side=tk.LEFT, padx=6)
        ttk.Button(simulation_controls, text="Reset Session", command=self._reset_simulation).pack(side=tk.LEFT)
        self.simulation_status = tk.StringVar()
        ttk.Label(simulation_controls, textvariable=self.simulation_status).pack(side=tk.LEFT, padx=10)
        metric_controls = ttk.Frame(self.controls)
        metric_controls.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(metric_controls, text="Sandbox metric:").pack(side=tk.LEFT)
        self.selected_metric = tk.StringVar()
        self.metric_value = tk.StringVar()
        self.metric_bounds = tk.StringVar()
        self.metric_combo = ttk.Combobox(
            metric_controls, state="readonly", width=23,
            textvariable=self.selected_metric
        )
        self.metric_combo.pack(side=tk.LEFT, padx=6)
        self.metric_combo.bind("<<ComboboxSelected>>", self._select_metric)
        ttk.Entry(
            metric_controls, textvariable=self.metric_value, width=8
        ).pack(side=tk.LEFT)
        ttk.Button(
            metric_controls, text="Apply", command=self._apply_metric
        ).pack(side=tk.LEFT, padx=6)
        ttk.Button(
            metric_controls, text="Activity Log", command=self._show_activity
        ).pack(side=tk.LEFT)
        ttk.Label(
            metric_controls, textvariable=self.metric_bounds
        ).pack(side=tk.LEFT, padx=10)
        self._populate_metric_controls()
        evidence_controls = ttk.Frame(self.controls)
        evidence_controls.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(evidence_controls, text="Sandbox Evidence:").pack(side=tk.LEFT)
        self.evidence_amount = tk.StringVar(value="100")
        ttk.Entry(
            evidence_controls, textvariable=self.evidence_amount, width=12
        ).pack(side=tk.LEFT, padx=6)
        ttk.Button(
            evidence_controls, text="Gather", command=self._gather_evidence
        ).pack(side=tk.LEFT)
        ttk.Button(
            evidence_controls, text="Spend", command=self._spend_evidence
        ).pack(side=tk.LEFT, padx=6)
        ttk.Label(
            evidence_controls, text="Manual test transactions; not mission rewards"
        ).pack(side=tk.LEFT, padx=8)
        self.evidence_progress_label = tk.StringVar()
        ttk.Label(
            self.controls, textvariable=self.evidence_progress_label
        ).pack(fill=tk.X, pady=(4, 0))


        ttk.Label(
            controls,
            text="FOIMS-X Local Simulation Preview",
            font=("Segoe UI", 11, "bold"),
        ).pack(side=tk.LEFT)

        ttk.Button(
            controls,
            text="Refresh Preview",
            command=self.refresh_preview,
        ).pack(side=tk.RIGHT)

        ttk.Button(
            controls,
            text="Fullscreen (F11)",
            command=self.toggle_fullscreen,
        ).pack(side=tk.RIGHT, padx=(0, 8))

        presentation_combo = ttk.Combobox(
            controls,
            state="readonly",
            values=tuple(PRESENTATION_SIZES),
            textvariable=self.presentation_size_name,
            width=22,
        )
        presentation_combo.pack(side=tk.RIGHT, padx=(0, 8))
        presentation_combo.bind(
            "<<ComboboxSelected>>",
            self._on_presentation_size_change,
        )

        ttk.Label(
            controls,
            text="Presentation:",
        ).pack(side=tk.RIGHT, padx=(0, 4))

        self.status_label = tk.Label(
            self.window,
            textvariable=self.status_text,
            foreground=PALETTE["muted"],
            background=PALETTE["desktop"],
            anchor=tk.W,
            padx=12,
        )
        self.status_label.pack(fill=tk.X, pady=(0, 6))

    def _build_canvas(self) -> None:
        self.canvas = tk.Canvas(
            self.window,
            background=PALETTE["desktop"],
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _on_presentation_size_change(self, _event: tk.Event[Any]) -> None:
        """Schedule a rerender after a fullscreen/windowed geometry change."""
        if not self.is_open():
            return

        if self._pending_resize is not None:
            self.canvas.after_cancel(self._pending_resize)

        self._pending_resize = self.canvas.after(90, self.render)

    def _on_resize(self, event: tk.Event[Any]) -> None:
        """Rerender after a real canvas-size change, with resize debouncing."""
        if event.widget is not self.window:
            return

        if not self.is_open():
            return

        if self._pending_resize is not None:
            self.canvas.after_cancel(self._pending_resize)

        self._pending_resize = self.canvas.after(90, self.render)

    def refresh_preview(self, _event: tk.Event[Any] | None = None) -> str:
        try:
            self.app.refresh_all(show_message=False)
            self._refresh_facility_catalog()
            self.status_text.set(
                "FOIMS-X refreshed from current authoring data."
            )
        except Exception as error:
            self.status_text.set(f"Preview refresh warning: {error}")

        self.render()
        return "break"

    def render(self) -> None:
        if not self.is_open():
            return

        self._pending_resize = None
        self._frame_snapshot = self.sandbox.snapshot()
        self._refresh_activity()
        self.evidence_progress_label.set(self.sandbox.evidence_progress_text())
        state = self._frame_snapshot
        self.play_button.configure(text="Pause" if state["running"] else "Play")
        self.step_button.configure(state="disabled" if state["running"] else "normal")
        self.simulation_status.set(
            f'{"RUNNING" if state["running"] else "PAUSED"} | '
            f'Evidence {state["available_evidence"]} / lifetime {state["lifetime_evidence"]} | Funding: unconfigured'
        )

        try:
            left_screen = self._render_foims_screen(
                FOIMS_VIEWPORT_SIZE[0],
                FOIMS_VIEWPORT_SIZE[1],
            )
            right_screen = self._render_secondary_console(
                FOIMS_VIEWPORT_SIZE[0],
                FOIMS_VIEWPORT_SIZE[1],
            )

            dual_crt_scene = self._compose_dual_crt(
                left_screen,
                right_screen,
            )

            self._present(dual_crt_scene)

        except Exception as error:
            self.status_text.set(f"FOIMS-X render error: {error}")
            self._draw_error(str(error))
    def _render_foims_screen(
        self,
        active_width: int,
        active_height: int,
    ) -> Image.Image:
        if self.catalog_mode.get() in ("Facilities", "Task Templates", "Qualifications", "Personnel"):
            return self._render_facility_catalog(active_width, active_height)
        image = Image.new(
            "RGBA",
            (active_width, active_height),
            PALETTE["screen"],
        )
        draw = ImageDraw.Draw(image)

        scale_x = active_width / DESIGN_SIZE[0]
        scale_y = active_height / DESIGN_SIZE[1]
        ui_scale = min(scale_x, scale_y)

        def sx(value: float) -> int:
            return round(value * scale_x)

        def sy(value: float) -> int:
            return round(value * scale_y)

        def border_width(value: int = 1) -> int:
            return max(1, round(value * ui_scale))

        def rectangle(
            left: float,
            top: float,
            right: float,
            bottom: float,
            fill: str,
            outline: str | None = None,
            width: int = 1,
        ) -> None:
            draw.rectangle(
                (
                    sx(left),
                    sy(top),
                    sx(right),
                    sy(bottom),
                ),
                fill=fill,
                outline=outline,
                width=border_width(width),
            )

        def line(
            left: float,
            top: float,
            right: float,
            bottom: float,
            fill: str,
            width: int = 1,
        ) -> None:
            draw.line(
                (
                    sx(left),
                    sy(top),
                    sx(right),
                    sy(bottom),
                ),
                fill=fill,
                width=border_width(width),
            )

        def text(
            left: float,
            top: float,
            value: str,
            size: int,
            color: str = PALETTE["text"],
            align: str = "left",
            max_width: float | None = None,
        ) -> None:
            self._draw_text(
                image=image,
                left=sx(left),
                top=sy(top),
                value=value,
                pixel_size=max(8, round(size * ui_scale)),
                color=color,
                align=align,
                max_width=(
                    sx(max_width)
                    if max_width is not None
                    else None
                ),
            )

        grid_step = max(8, sx(16))

        for grid_x in range(sx(16), active_width, grid_step):
            draw.line(
                (grid_x, sy(16), grid_x, sy(464)),
                fill=PALETTE["grid"],
                width=border_width(),
            )

        for grid_y in range(sy(16), sy(464), max(8, sy(16))):
            draw.line(
                (sx(16), grid_y, sx(624), grid_y),
                fill=PALETTE["grid"],
                width=border_width(),
            )

        rectangle(12, 12, 628, 468, PALETTE["screen"], PALETTE["border"])
        rectangle(18, 18, 622, 48, PALETTE["panel"], PALETTE["border"])

        text(
            28,
            25,
            "F.O.I.M.S.-X // FEDERAL OPERATIONAL INFORMATION",
            12,
            PALETTE["accent"],
        )
        clock = self._current_game_clock()

        text(
            612,
            26,
            f'{clock["date"]} // {clock["time"]} // D{clock["day"]:03d}',
            8,
            PALETTE["muted"],
            "right",
        )

        metrics = self.sandbox.metric_rows()
        tiers = active_rows(self.app.tables.get("metric_tiers", []))
        facilities = active_rows(self.app.tables.get("facilities", []))
        flavors = active_rows(self.app.tables.get("flavor_text", []))

        metric_left = 18
        metric_top = 58
        metric_right = 376
        metric_bottom = 450

        facility_left = 384
        facility_top = 58
        facility_right = 622
        facility_bottom = 450

        rectangle(
            metric_left,
            metric_top,
            metric_right,
            metric_bottom,
            PALETTE["screen_alt"],
            PALETTE["border"],
        )
        rectangle(
            facility_left,
            facility_top,
            facility_right,
            facility_bottom,
            PALETTE["screen_alt"],
            PALETTE["border"],
        )

        text(
            metric_left + 10,
            metric_top + 10,
            "DEPARTMENT STATUS",
            12,
            PALETTE["accent"],
        )
        text(
            facility_left + 10,
            facility_top + 10,
            "FACILITY MONITOR",
            12,
            PALETTE["accent"],
        )

        selected_metrics = self._visible_metric_rows()
        selected_facilities = facilities[:4]

        if selected_metrics:
            card_height = 112

            for index, metric in enumerate(selected_metrics):
                self._draw_metric_card(
                    image=image,
                    metric=metric,
                    tiers=tiers,
                    flavors=flavors,
                    left=metric_left + 8,
                    top=metric_top + 32 + index * card_height,
                    width=metric_right - metric_left - 16,
                    height=card_height - 6,
                    scale_x=scale_x,
                    scale_y=scale_y,
                    ui_scale=ui_scale,
                )
        else:
            text(
                metric_left + 10,
                metric_top + 40,
                "NO ACTIVE METRICS",
                11,
                PALETTE["fallback"],
            )

        if selected_facilities:
            for index, facility in enumerate(selected_facilities):
                self._draw_facility_row(
                    image=image,
                    facility=facility,
                    left=facility_left + 8,
                    top=facility_top + 34 + index * 47,
                    width=facility_right - facility_left - 16,
                    height=42,
                    index=index,
                    scale_x=scale_x,
                    scale_y=scale_y,
                    ui_scale=ui_scale,
                )
        else:
            text(
                facility_left + 10,
                facility_top + 40,
                "NO ACTIVE FACILITIES",
                10,
                PALETTE["fallback"],
            )

        directive_top = facility_top + 236

        rectangle(
            facility_left + 8,
            directive_top,
            facility_right - 8,
            facility_bottom - 8,
            PALETTE["panel"],
            PALETTE["border"],
        )

        directive = flavors[0] if flavors else {}

        text(
            facility_left + 16,
            directive_top + 10,
            "CURRENT DIRECTIVE",
            10,
            PALETTE["accent"],
        )
        text(
            facility_left + 16,
            directive_top + 31,
            directive.get("title", "NO ACTIVE DIRECTIVE"),
            11,
            PALETTE["text"],
            max_width=facility_right - facility_left - 32,
        )
        text(
            facility_left + 16,
            directive_top + 55,
            directive.get(
                "body",
                "ADD ACTIVE FLAVOR TEXT TO POPULATE THIS PANEL.",
            ),
            9,
            PALETTE["muted"],
            max_width=facility_right - facility_left - 32,
        )

        rectangle(18, 454, 622, 466, PALETTE["panel"], PALETTE["border"])

        text(
            26,
            456,
            "FOIMS-X // LOCAL SIMULATION // PREVIEW ONLY",
            8,
            PALETTE["muted"],
        )
        text(
            614,
            456,
            (
                f"M:{len(metrics):02d} "
                f"T:{len(tiers):02d} "
                f"F:{len(facilities):02d}"
            ),
            8,
            PALETTE["muted"],
            "right",
        )

        return image

    def _render_secondary_console(
        self,
        active_width: int,
        active_height: int,
    ) -> Image.Image:
        """Render a stable, independent FOIMS-X secondary operations panel."""
        image = Image.new(
            "RGBA",
            (active_width, active_height),
            PALETTE["screen"],
        )
        draw = ImageDraw.Draw(image)

        scale_x = active_width / DESIGN_SIZE[0]
        scale_y = active_height / DESIGN_SIZE[1]
        ui_scale = min(scale_x, scale_y)

        def sx(value: float) -> int:
            return round(value * scale_x)

        def sy(value: float) -> int:
            return round(value * scale_y)

        def line_width() -> int:
            return max(1, round(ui_scale))

        def panel(
            left: float,
            top: float,
            right: float,
            bottom: float,
            fill: str = PALETTE["panel_alt"],
        ) -> None:
            draw.rectangle(
                (sx(left), sy(top), sx(right), sy(bottom)),
                fill=fill,
                outline=PALETTE["border"],
                width=line_width(),
            )

        def text(
            left: float,
            top: float,
            value: str,
            size: int,
            color: str = PALETTE["text"],
            align: str = "left",
            max_width: float | None = None,
        ) -> None:
            self._draw_text(
                image=image,
                left=sx(left),
                top=sy(top),
                value=value,
                pixel_size=max(8, round(size * ui_scale)),
                color=color,
                align=align,
                max_width=sx(max_width) if max_width is not None else None,
            )

        for grid_x in range(sx(16), active_width, max(8, sx(16))):
            draw.line(
                (grid_x, sy(16), grid_x, sy(464)),
                fill=PALETTE["grid"],
                width=line_width(),
            )

        for grid_y in range(sy(16), sy(464), max(8, sy(16))):
            draw.line(
                (sx(16), grid_y, sx(624), grid_y),
                fill=PALETTE["grid"],
                width=line_width(),
            )

        panel(12, 12, 628, 468, PALETTE["screen"])
        panel(18, 18, 622, 48, PALETTE["panel"])

        text(
            28,
            25,
            "F.O.I.M.S.-X // OPERATIONS CONSOLE",
            12,
            PALETTE["accent"],
        )
        clock = self._current_game_clock()

        text(
            612,
            26,
            f'TEMPORAL LINK // {clock["time"]} // D{clock["day"]:03d}',
            8,
            PALETTE["muted"],
            "right",
        )

        panel(18, 58, 622, 198)
        panel(18, 208, 622, 342)
        panel(18, 352, 622, 450)

        text(30, 70, "SECONDARY SYSTEM STATUS", 12, PALETTE["accent"])

        status_rows = (
            ("CAMPAIGN DATE", str(clock["date"])),
            ("24-HOUR TIME", str(clock["time"])),
            ("CAMPAIGN DAY", f'DAY {clock["day"]:03d}'),
            (
                "DAY CYCLE",
                f'{clock["cycle_percent"]:05.2f}% // 01 GAME MIN / REAL SEC',
            ),
        )

        for index, (label, value) in enumerate(status_rows):
            top = 101 + index * 21
            panel(34, top, 606, top + 16, PALETTE["panel"])
            text(44, top + 3, label, 8, PALETTE["muted"])
            text(594, top + 2, value, 9, PALETTE["accent"], "right")

        text(30, 220, "FOIMS-X TELEMETRY", 12, PALETTE["accent"])

        telemetry_rows = (
            ("DISPLAY MODE", "LOCAL SIMULATION / DUAL CRT"),
            ("LEFT CHANNEL", "DEPARTMENT OPERATIONS"),
            ("RIGHT CHANNEL", "OPERATIONS CONSOLE"),
            ("SESSION STATE", "RUNNING" if clock["running"] else "PAUSED"),
        )

        for index, (label, value) in enumerate(telemetry_rows):
            top = 250 + index * 20
            text(40, top, label, 8, PALETTE["muted"])
            text(594, top, value, 8, PALETTE["text"], "right")

        text(30, 364, "SANDBOX ACTIVITY", 12, PALETTE["accent"])
        recent = clock.get("activity", [])[-2:]
        if not recent:
            text(40, 397, "NO METRIC CHANGES IN THIS SESSION", 9, PALETTE["text"])
        for index, entry in enumerate(recent):
            text(
                40, 393 + index * 23,
                self.sandbox.activity_line(entry),
                8, PALETTE["text"], max_width=550
            )

        panel(18, 454, 622, 466, PALETTE["panel"])
        text(
            26,
            456,
            "FOIMS-X // SECONDARY OPERATIONS DISPLAY",
            8,
            PALETTE["muted"],
        )
        text(
            614,
            456,
            "DUAL DISPLAY MODE",
            8,
            PALETTE["muted"],
            "right",
        )

        return image

    def _draw_metric_card(
        self,
        image: Image.Image,
        metric: dict[str, str],
        tiers: list[dict[str, str]],
        flavors: list[dict[str, str]],
        left: int,
        top: int,
        width: int,
        height: int,
        scale_x: float,
        scale_y: float,
        ui_scale: float,
    ) -> None:
        draw = ImageDraw.Draw(image)

        def sx(value: float) -> int:
            return round(value * scale_x)

        def sy(value: float) -> int:
            return round(value * scale_y)

        def line_width(value: int = 1) -> int:
            return max(1, round(value * ui_scale))

        metric_id = metric.get("metric_id", "")
        metric_name = metric.get("display_name", metric_id)
        value = self._frame_snapshot["metrics"].get(metric_id, numeric_value(metric.get("default_value", "0")))
        minimum = numeric_value(metric.get("internal_min", "0"))
        maximum = numeric_value(metric.get("internal_max", "100"))

        if maximum <= minimum:
            maximum = minimum + 1

        progress = min(max((value - minimum) / (maximum - minimum), 0.0), 1.0)
        tier = self._tier_for_value(metric_id, value, tiers)
        color = normalize_hex(tier.get("ui_color", PALETTE["fallback"]))
        tier_label = tier.get("display_label", "UNCLASSIFIED")
        short_status = tier.get("short_status", "")
        flavor = self._flavor_for_tier(tier, flavors)

        draw.rectangle(
            (sx(left), sy(top), sx(left + width), sy(top + height)),
            fill=PALETTE["panel_alt"],
            outline=PALETTE["border"],
            width=line_width(),
        )
        draw.rectangle(
            (sx(left), sy(top), sx(left + 5), sy(top + height)),
            fill=color,
        )

        self._draw_text(
            image,
            sx(left + 12),
            sy(top + 10),
            metric_name,
            max(8, round(10 * ui_scale)),
            PALETTE["text"],
        )
        self._draw_text(
            image,
            sx(left + width - 10),
            sy(top + 10),
            f"{int(value):04d}/{int(maximum):04d}",
            max(8, round(9 * ui_scale)),
            PALETTE["muted"],
            "right",
        )
        self._draw_text(
            image,
            sx(left + 12),
            sy(top + 28),
            tier_label,
            max(9, round(13 * ui_scale)),
            color,
        )

        bar_left = left + 12
        bar_top = top + 53
        bar_width = width - 24
        bar_height = 11

        draw.rectangle(
            (
                sx(bar_left),
                sy(bar_top),
                sx(bar_left + bar_width),
                sy(bar_top + bar_height),
            ),
            fill=PALETTE["screen"],
            outline=PALETTE["border"],
            width=line_width(),
        )
        draw.rectangle(
            (
                sx(bar_left),
                sy(bar_top),
                sx(bar_left + max(1, bar_width * progress)),
                sy(bar_top + bar_height),
            ),
            fill=color,
        )

        message = short_status or flavor.get("title", "")

        if message:
            self._draw_text(
                image,
                sx(left + 12),
                sy(top + 73),
                message,
                max(7, round(8 * ui_scale)),
                PALETTE["muted"],
                max_width=sx(width - 24),
            )

    def _draw_facility_row(
        self,
        image: Image.Image,
        facility: dict[str, str],
        left: int,
        top: int,
        width: int,
        height: int,
        index: int,
        scale_x: float,
        scale_y: float,
        ui_scale: float,
    ) -> None:
        draw = ImageDraw.Draw(image)

        def sx(value: float) -> int:
            return round(value * scale_x)

        def sy(value: float) -> int:
            return round(value * scale_y)

        def line_width(value: int = 1) -> int:
            return max(1, round(value * ui_scale))

        facility_name = facility.get(
            "display_name",
            facility.get("facility_id", "UNKNOWN"),
        )
        panel_id = facility.get("foims_panel_id", "UNASSIGNED")
        tier = facility.get("initial_tier_id", "UNCLASSIFIED")

        colors = (
            PALETTE["accent"],
            "#77D8FF",
            "#F4B942",
            "#EF5B5B",
        )
        color = colors[index % len(colors)]

        draw.rectangle(
            (sx(left), sy(top), sx(left + width), sy(top + height)),
            fill=PALETTE["panel_alt"],
            outline=PALETTE["border"],
            width=line_width(),
        )
        draw.rectangle(
            (sx(left), sy(top), sx(left + 4), sy(top + height)),
            fill=color,
        )

        self._draw_text(
            image,
            sx(left + 9),
            sy(top + 8),
            facility_name,
            max(7, round(9 * ui_scale)),
            PALETTE["text"],
            max_width=sx(width - 78),
        )
        self._draw_text(
            image,
            sx(left + width - 8),
            sy(top + 8),
            tier,
            max(7, round(8 * ui_scale)),
            color,
            "right",
        )
        self._draw_text(
            image,
            sx(left + 9),
            sy(top + 25),
            panel_id,
            max(6, round(7 * ui_scale)),
            PALETTE["muted"],
            max_width=sx(width - 18),
        )

    def _draw_text(
        self,
        image: Image.Image,
        left: int,
        top: int,
        value: str,
        pixel_size: int,
        color: str,
        align: str = "left",
        max_width: int | None = None,
    ) -> None:
        font = ImageFont.truetype(
            self._font_path(),
            max(8, pixel_size),
        )
        draw = ImageDraw.Draw(image)
        text_value = value.upper()

        if max_width is not None:
            text_value = self._wrap_text(
                text_value,
                font,
                max_width,
            )

        bounds = draw.multiline_textbbox(
            (0, 0),
            text_value,
            font=font,
            spacing=max(2, pixel_size // 3),
        )
        text_width = bounds[2] - bounds[0]

        if align == "right":
            left -= text_width

        shadow_offset = max(1, pixel_size // 10)

        draw.multiline_text(
            (left + shadow_offset, top + shadow_offset),
            text_value,
            font=font,
            fill=PALETTE["shadow"],
            spacing=max(2, pixel_size // 3),
        )
        draw.multiline_text(
            (left, top),
            text_value,
            font=font,
            fill=color,
            spacing=max(2, pixel_size // 3),
        )

    @staticmethod
    def _wrap_text(
        value: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
    ) -> str:
        lines: list[str] = []
        current = ""

        for word in value.split():
            candidate = f"{current} {word}".strip()

            if current and font.getlength(candidate) > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate

        if current:
            lines.append(current)

        return "\n".join(lines)

    def _compose_dual_crt(
        self,
        left_screen: Image.Image,
        right_screen: Image.Image,
    ) -> Image.Image:
        """Compose two native FOIMS-X screens beneath a front CRT bezel."""
        composition = Image.new(
            "RGBA",
            DUAL_CRT_OVERLAY_SIZE,
            PALETTE["desktop"],
        )

        left_x, left_y, left_width, left_height = LEFT_CRT_APERTURE
        right_x, right_y, right_width, right_height = RIGHT_CRT_APERTURE
        viewport_width, viewport_height = FOIMS_VIEWPORT_SIZE

        left_viewport_x = left_x + (left_width - viewport_width) // 2
        left_viewport_y = left_y + (left_height - viewport_height) // 2
        right_viewport_x = right_x + (right_width - viewport_width) // 2
        right_viewport_y = right_y + (right_height - viewport_height) // 2

        # Layer 1: FOIMS-X UI screens, rendered at final native dimensions.
        composition.alpha_composite(
            left_screen,
            (left_viewport_x, left_viewport_y),
        )
        composition.alpha_composite(
            right_screen,
            (right_viewport_x, right_viewport_y),
        )

        # Layer 2: CRT hardware overlay, closest to the viewer.
        overlay = Image.open(self._overlay_path()).convert("RGBA")

        if overlay.size != DUAL_CRT_OVERLAY_SIZE:
            overlay = overlay.resize(
                DUAL_CRT_OVERLAY_SIZE,
                Image.Resampling.NEAREST,
            )

        overlay_alpha = overlay.getchannel("A")
        aperture_draw = ImageDraw.Draw(overlay_alpha)

        # The asset contains white display regions. Clear them to alpha
        # so FOIMS-X remains visible behind the front monitor hardware.
        aperture_draw.rectangle(
            (
                left_x,
                left_y,
                left_x + left_width - 1,
                left_y + left_height - 1,
            ),
            fill=0,
        )
        aperture_draw.rectangle(
            (
                right_x,
                right_y,
                right_x + right_width - 1,
                right_y + right_height - 1,
            ),
            fill=0,
        )

        overlay.putalpha(overlay_alpha)
        composition.alpha_composite(overlay, (0, 0))

        return composition
    def _present(self, presentation: Image.Image) -> None:
        """FOIMS_X_PERSISTENT_CANVAS_CLOCK_REPAIR: update one canvas image in place."""
        self.canvas.update_idletasks()

        canvas_width = max(self.canvas.winfo_width(), 1)
        canvas_height = max(self.canvas.winfo_height(), 1)

        source_width, source_height = presentation.size

        if source_width <= 0 or source_height <= 0:
            raise ValueError("FOIMS-X presentation image has invalid dimensions.")

        # A single uniform scale factor preserves the 1920x1080 dual-CRT bezel.
        scale = min(
            canvas_width / source_width,
            canvas_height / source_height,
        )

        output_width = max(1, round(source_width * scale))
        output_height = max(1, round(source_height * scale))

        if (output_width, output_height) == presentation.size:
            output = presentation
        else:
            output = presentation.resize(
                (output_width, output_height),
                Image.Resampling.LANCZOS,
            )

        offset_x = (canvas_width - output_width) // 2
        offset_y = (canvas_height - output_height) // 2

        size_changed = self._presented_size != output.size

        if self._photo is None or self._canvas_image_id is None or size_changed:
            # Rebuild only on first presentation or a real window-size change.
            self.canvas.delete("all")
            self._photo = ImageTk.PhotoImage(output)
            self._canvas_image_id = self.canvas.create_image(
                offset_x,
                offset_y,
                image=self._photo,
                anchor=tk.NW,
            )
            self._presented_size = output.size
        else:
            # Clock updates retain the existing canvas image and avoid blank frames.
            self._photo.paste(output)
            self.canvas.coords(
                self._canvas_image_id,
                offset_x,
                offset_y,
            )

        mode = "FULLSCREEN" if bool(self.window.attributes("-fullscreen")) else "WINDOWED"

        self.status_text.set(
            f"{mode}: {output_width}x{output_height} of "
            f"{canvas_width}x{canvas_height} // "
            "SCENE: UNIFORM 16:9 // UI: RASTER RENDER"
        )

    def _draw_error(self, message: str) -> None:
        canvas_width = max(self.canvas.winfo_width(), 1)
        canvas_height = max(self.canvas.winfo_height(), 1)

        self.canvas.create_text(
            canvas_width / 2,
            canvas_height / 2,
            text=(
                "FOIMS-X PREVIEW ERROR\n\n"
                f"{message}\n\n"
                "Check the authoring data and local font asset."
            ),
            fill="#EF5B5B",
            font=("Consolas", 11),
            justify=tk.CENTER,
            anchor=tk.CENTER,
        )

    @staticmethod
    def _tier_for_value(
        metric_id: str,
        value: float,
        tiers: list[dict[str, str]],
    ) -> dict[str, str]:
        matching = [
            tier
            for tier in tiers
            if tier.get("metric_id", "") == metric_id
        ]

        matching.sort(
            key=lambda tier: numeric_value(
                tier.get("min_inclusive", "0")
            )
        )

        for tier in matching:
            minimum = numeric_value(tier.get("min_inclusive", "0"))
            maximum_text = tier.get("max_inclusive", "").strip()
            maximum = numeric_value(maximum_text, math.inf)

            if minimum <= value <= maximum:
                return tier

        return matching[-1] if matching else {}

    @staticmethod
    def _flavor_for_tier(
        tier: dict[str, str],
        flavors: list[dict[str, str]],
    ) -> dict[str, str]:
        flavor_id = tier.get("flavor_text_id", "")

        for flavor in flavors:
            if flavor.get("flavor_text_id", "") == flavor_id:
                return flavor

        return {}











#!/usr/bin/env python3
"""
FOIMS-X Preview Monitor.

A read-only Tkinter Toplevel window for previewing current DoDA authoring
data in a command-monitor style layout. The host Workbench owns source-data
loading; this module renders its current app.tables snapshot.
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from typing import Any


LOGICAL_SIZES = {
    "1280 x 720": (1280, 720),
    "1920 x 1080": (1920, 1080),
    "2560 x 1440": (2560, 1440),
}

PALETTE = {
    "background": "#070b10",
    "surface": "#101923",
    "surface_alt": "#141f2b",
    "border": "#3b5368",
    "grid": "#182936",
    "text": "#d9e8f4",
    "muted": "#88a0b4",
    "accent": "#58A6FF",
    "warning": "#F4B942",
    "critical": "#EF5B5B",
    "ok": "#5CCB72",
}


def normalize_hex(value: str, fallback: str = "#8C939F") -> str:
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


class FoimsXPreview:
    """A singleton-friendly, read-only FOIMS-X command monitor."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self.window = tk.Toplevel(app)
        self.window.title("FOIMS-X Preview Monitor")
        self.window.geometry("1280x760")
        self.window.minsize(900, 560)
        self.window.configure(background=PALETTE["background"])

        self.logical_size_name = tk.StringVar(value="1920 x 1080")
        self.status_text = tk.StringVar(value="Preview ready.")

        self._build_controls()
        self._build_canvas()

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind("<Control-r>", self.refresh_preview)
        self.window.bind("<Configure>", self._on_resize)

        self.window.after_idle(self.refresh_preview)

    def is_open(self) -> bool:
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False

    def show(self) -> None:
        if not self.is_open():
            return

        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def close(self) -> None:
        if self.is_open():
            self.window.destroy()

    def _build_controls(self) -> None:
        controls = ttk.Frame(self.window, padding=(10, 8))
        controls.pack(fill=tk.X)

        ttk.Label(
            controls,
            text="FOIMS-X Preview Monitor",
            font=("Segoe UI", 11, "bold"),
        ).pack(side=tk.LEFT)

        ttk.Button(
            controls,
            text="Refresh Preview",
            command=self.refresh_preview,
        ).pack(side=tk.RIGHT)

        size_combo = ttk.Combobox(
            controls,
            state="readonly",
            values=tuple(LOGICAL_SIZES),
            textvariable=self.logical_size_name,
            width=14,
        )
        size_combo.pack(side=tk.RIGHT, padx=(0, 8))
        size_combo.bind("<<ComboboxSelected>>", self._on_logical_size_change)

        ttk.Label(
            controls,
            text="Target:",
        ).pack(side=tk.RIGHT, padx=(0, 4))

        ttk.Label(
            self.window,
            textvariable=self.status_text,
            foreground=PALETTE["muted"],
            background=PALETTE["background"],
            anchor=tk.W,
        ).pack(fill=tk.X, padx=12, pady=(0, 6))

    def _build_canvas(self) -> None:
        self.canvas = tk.Canvas(
            self.window,
            background=PALETTE["background"],
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _on_logical_size_change(self, _event: tk.Event[Any]) -> None:
        self.render()

    def _on_resize(self, event: tk.Event[Any]) -> None:
        if event.widget is self.window:
            self.window.after_idle(self.render)

    def refresh_preview(self, _event: tk.Event[Any] | None = None) -> str:
        try:
            self.app.refresh_all(show_message=False)
            self.status_text.set("Preview refreshed from current authoring data.")
        except Exception as error:
            self.status_text.set(f"Preview refresh warning: {error}")

        self.render()
        return "break"

    def render(self) -> None:
        if not self.is_open():
            return

        self.canvas.delete("all")

        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        logical_width, logical_height = LOGICAL_SIZES[
            self.logical_size_name.get()
        ]

        scale = min(width / logical_width, height / logical_height)
        draw_width = logical_width * scale
        draw_height = logical_height * scale
        offset_x = (width - draw_width) / 2
        offset_y = (height - draw_height) / 2

        def x(value: float) -> float:
            return offset_x + value * scale

        def y(value: float) -> float:
            return offset_y + value * scale

        def font(size: int, weight: str = "normal") -> tuple[str, int, str]:
            return ("Consolas", max(8, int(size * scale)), weight)

        def rectangle(
            left: float,
            top: float,
            right: float,
            bottom: float,
            fill: str,
            outline: str = "",
            line_width: float = 1,
        ) -> None:
            self.canvas.create_rectangle(
                x(left),
                y(top),
                x(right),
                y(bottom),
                fill=fill,
                outline=outline,
                width=max(1, int(line_width * scale)),
            )

        def text(
            left: float,
            top: float,
            value: str,
            size: int = 18,
            color: str = PALETTE["text"],
            weight: str = "normal",
            anchor: str = tk.NW,
            width_limit: float | None = None,
        ) -> None:
            self.canvas.create_text(
                x(left),
                y(top),
                text=value,
                fill=color,
                font=font(size, weight),
                anchor=anchor,
                width=(width_limit * scale) if width_limit else 0,
            )

        rectangle(
            0,
            0,
            logical_width,
            logical_height,
            PALETTE["background"],
        )

        self._draw_grid(rectangle, logical_width, logical_height, scale)

        rectangle(
            24,
            24,
            logical_width - 24,
            logical_height - 24,
            PALETTE["background"],
            PALETTE["border"],
            2,
        )

        rectangle(
            24,
            24,
            logical_width - 24,
            106,
            PALETTE["surface"],
            PALETTE["border"],
            1,
        )

        text(
            52,
            46,
            "FOIMS-X // FEDERAL OPERATIONAL INFORMATION MANAGEMENT SYSTEM",
            22,
            PALETTE["accent"],
            "bold",
        )
        text(
            logical_width - 52,
            48,
            "NETWORK: SECURE  //  CYCLE: 08  //  STATUS: NOMINAL",
            15,
            PALETTE["muted"],
            anchor=tk.NE,
        )

        metrics = active_rows(self.app.tables.get("metrics", []))
        tiers = active_rows(self.app.tables.get("metric_tiers", []))
        facilities = active_rows(self.app.tables.get("facilities", []))
        flavors = active_rows(self.app.tables.get("flavor_text", []))

        selected_metrics = metrics[:3]
        selected_facilities = facilities[:4]

        left = 44
        top = 132
        left_width = 690
        gutter = 22
        right = left + left_width + gutter
        right_width = logical_width - right - 44
        bottom = logical_height - 52

        rectangle(
            left,
            top,
            left + left_width,
            bottom,
            PALETTE["surface"],
            PALETTE["border"],
            1,
        )
        rectangle(
            right,
            top,
            right + right_width,
            bottom,
            PALETTE["surface"],
            PALETTE["border"],
            1,
        )

        text(left + 22, top + 18, "STRATEGIC METRICS", 18, PALETTE["accent"], "bold")
        text(right + 22, top + 18, "FACILITY NETWORK", 18, PALETTE["accent"], "bold")

        metric_top = top + 62
        metric_height = 166

        if selected_metrics:
            for index, metric in enumerate(selected_metrics):
                self._draw_metric_card(
                    rectangle,
                    text,
                    metric,
                    tiers,
                    flavors,
                    left + 18,
                    metric_top + index * metric_height,
                    left_width - 36,
                    metric_height - 14,
                )
        else:
            text(
                left + 22,
                metric_top,
                "No active metrics are available in source data.",
                16,
                PALETTE["warning"],
            )

        facility_top = top + 62
        facility_height = 74

        if selected_facilities:
            for index, facility in enumerate(selected_facilities):
                self._draw_facility_row(
                    rectangle,
                    text,
                    facility,
                    right + 18,
                    facility_top + index * facility_height,
                    right_width - 36,
                    facility_height - 8,
                    index,
                )
        else:
            text(
                right + 22,
                facility_top,
                "No active facilities are available in source data.",
                16,
                PALETTE["warning"],
            )

        directive_top = top + max(
            62 + len(selected_facilities) * facility_height + 22,
            400,
        )

        rectangle(
            right + 18,
            directive_top,
            right + right_width - 18,
            bottom - 18,
            PALETTE["surface_alt"],
            PALETTE["border"],
            1,
        )

        text(
            right + 36,
            directive_top + 18,
            "CURRENT DIRECTIVE",
            16,
            PALETTE["accent"],
            "bold",
        )

        directive = flavors[0] if flavors else {}

        text(
            right + 36,
            directive_top + 54,
            directive.get("title", "No active directive"),
            18,
            PALETTE["text"],
            "bold",
            width_limit=right_width - 72,
        )

        text(
            right + 36,
            directive_top + 92,
            directive.get(
                "body",
                "Add active flavor-text records to populate the briefing panel.",
            ),
            15,
            PALETTE["muted"],
            width_limit=right_width - 72,
        )

        rectangle(
            24,
            logical_height - 68,
            logical_width - 24,
            logical_height - 24,
            PALETTE["surface"],
            PALETTE["border"],
            1,
        )

        text(
            48,
            logical_height - 55,
            "FOIMS-X / AUTHORING PREVIEW // DIRECT HEX COLOR MODE",
            14,
            PALETTE["muted"],
        )

        text(
            logical_width - 48,
            logical_height - 55,
            f"{len(metrics)} METRICS // {len(tiers)} TIERS // {len(facilities)} FACILITIES",
            14,
            PALETTE["muted"],
            anchor=tk.NE,
        )

    def _draw_grid(
        self,
        rectangle: Any,
        logical_width: float,
        logical_height: float,
        scale: float,
    ) -> None:
        spacing = 48

        for line in range(0, int(logical_width), spacing):
            rectangle(
                line,
                0,
                line + max(1, 1 / max(scale, 0.1)),
                logical_height,
                PALETTE["grid"],
            )

        for line in range(0, int(logical_height), spacing):
            rectangle(
                0,
                line,
                logical_width,
                line + max(1, 1 / max(scale, 0.1)),
                PALETTE["grid"],
            )

    def _draw_metric_card(
        self,
        rectangle: Any,
        text: Any,
        metric: dict[str, str],
        tiers: list[dict[str, str]],
        flavors: list[dict[str, str]],
        left: float,
        top: float,
        width: float,
        height: float,
    ) -> None:
        metric_id = metric.get("metric_id", "")
        metric_name = metric.get("display_name", metric_id)
        value = numeric_value(metric.get("default_value", "0"))
        minimum = numeric_value(metric.get("internal_min", "0"))
        maximum = numeric_value(metric.get("internal_max", "100"))

        if maximum <= minimum:
            maximum = minimum + 1

        progress = min(max((value - minimum) / (maximum - minimum), 0.0), 1.0)
        tier = self._tier_for_value(metric_id, value, tiers)
        color = normalize_hex(tier.get("ui_color", PALETTE["muted"]))
        tier_label = tier.get("display_label", "Unclassified")
        short_status = tier.get("short_status", "")
        flavor = self._flavor_for_tier(tier, flavors)

        rectangle(left, top, left + width, top + height, PALETTE["surface_alt"])
        rectangle(left, top, left + 6, top + height, color)

        text(left + 22, top + 14, metric_name.upper(), 16, PALETTE["text"], "bold")
        text(
            left + width - 20,
            top + 16,
            f"{int(value):,} / {int(maximum):,}",
            15,
            PALETTE["muted"],
            anchor=tk.NE,
        )

        text(left + 22, top + 46, tier_label.upper(), 22, color, "bold")

        bar_left = left + 22
        bar_top = top + 84
        bar_width = width - 44
        bar_height = 20

        rectangle(
            bar_left,
            bar_top,
            bar_left + bar_width,
            bar_top + bar_height,
            PALETTE["background"],
            PALETTE["border"],
        )

        rectangle(
            bar_left,
            bar_top,
            bar_left + bar_width * progress,
            bar_top + bar_height,
            color,
        )

        message = short_status or flavor.get("title", "")

        text(
            left + 22,
            top + 116,
            message,
            13,
            PALETTE["muted"],
            width_limit=width - 44,
        )

    def _draw_facility_row(
        self,
        rectangle: Any,
        text: Any,
        facility: dict[str, str],
        left: float,
        top: float,
        width: float,
        height: float,
        index: int,
    ) -> None:
        facility_name = facility.get(
            "display_name",
            facility.get("facility_id", "Unknown Facility"),
        )
        panel_id = facility.get("foims_panel_id", "UNASSIGNED")
        tier = facility.get("initial_tier_id", "UNCLASSIFIED")

        colors = (
            PALETTE["ok"],
            PALETTE["accent"],
            PALETTE["warning"],
            PALETTE["critical"],
        )
        color = colors[index % len(colors)]

        rectangle(left, top, left + width, top + height, PALETTE["surface_alt"])
        rectangle(left, top, left + 5, top + height, color)

        text(left + 18, top + 12, facility_name.upper(), 15, PALETTE["text"], "bold")
        text(
            left + width - 16,
            top + 12,
            tier.upper(),
            14,
            color,
            "bold",
            anchor=tk.NE,
        )
        text(left + 18, top + 39, panel_id, 12, PALETTE["muted"])

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
            key=lambda tier: numeric_value(tier.get("min_inclusive", "0"))
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

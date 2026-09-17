#!/usr/bin/env python3
"""
FOIMS-X Preview Monitor.

A read-only 4:3 CRT monitor preview for current DoDA authoring data.
The monitor image is rendered with Pillow, placed in the exact screen aperture
of the project CRT overlay, and displayed as one composite Tk Canvas image.
"""

from __future__ import annotations

import math
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageTk


LOGICAL_SIZES = {
    "320 x 240 CRT": (320, 240),
    "640 x 480 CRT": (640, 480),
    "800 x 600 CRT": (800, 600),
    "1024 x 768 CRT": (1024, 768),
}

OVERLAY_SIZE = (412, 309)
SCREEN_APERTURE = (79, 50, 241, 181)

PALETTE = {
    "desktop": "#090B0D",
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


class FoimsXPreview:
    """A singleton-friendly, read-only FOIMS-X 4:3 CRT monitor."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self.window = tk.Toplevel(app)
        self.window.title("FOIMS-X Preview Monitor")
        self.window.geometry("1200x900")
        self.window.minsize(720, 600)
        self.window.configure(background=PALETTE["desktop"])

        self.logical_size_name = tk.StringVar(value="640 x 480 CRT")
        self.display_scale_name = tk.StringVar(value="Fit")
        self.status_text = tk.StringVar(value="FOIMS-X CRT preview ready.")
        self._photo: ImageTk.PhotoImage | None = None
        self._pending_resize: str | None = None

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
        controls = ttk.Frame(self.window, padding=(10, 8))
        controls.pack(fill=tk.X)

        ttk.Label(
            controls,
            text="FOIMS-X CRT Preview Monitor",
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
            width=16,
        )
        size_combo.pack(side=tk.RIGHT, padx=(0, 8))
        size_combo.bind("<<ComboboxSelected>>", self._on_logical_size_change)

        display_scale_combo = ttk.Combobox(
            controls,
            state="readonly",
            values=("Fit", "Integer Fit", "1x", "2x", "3x", "4x"),
            textvariable=self.display_scale_name,
            width=12,
        )
        display_scale_combo.pack(side=tk.RIGHT, padx=(0, 8))
        display_scale_combo.bind(
            "<<ComboboxSelected>>",
            self._on_display_scale_change,
        )

        ttk.Label(
            controls,
            text="Display Scale:",
        ).pack(side=tk.RIGHT, padx=(0, 4))

        ttk.Label(
            controls,
            text="4:3 Target:",
        ).pack(side=tk.RIGHT, padx=(0, 12))

        tk.Label(
            self.window,
            textvariable=self.status_text,
            foreground=PALETTE["muted"],
            background=PALETTE["desktop"],
            anchor=tk.W,
            padx=12,
        ).pack(fill=tk.X, pady=(0, 6))

    def _build_canvas(self) -> None:
        self.canvas = tk.Canvas(
            self.window,
            background=PALETTE["desktop"],
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _on_logical_size_change(self, _event: tk.Event[Any]) -> None:
        self.render()

    def _on_display_scale_change(self, _event: tk.Event[Any]) -> None:
        self.render()

    def _on_resize(self, event: tk.Event[Any]) -> None:
        if event.widget is not self.window:
            return

        if self._pending_resize is not None:
            self.window.after_cancel(self._pending_resize)

        self._pending_resize = self.window.after(80, self.render)

    def refresh_preview(self, _event: tk.Event[Any] | None = None) -> str:
        try:
            self.app.refresh_all(show_message=False)
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
        self.canvas.delete("all")

        try:
            logical_width, logical_height = LOGICAL_SIZES[
                self.logical_size_name.get()
            ]

            screen = self._render_foims_screen(
                logical_width,
                logical_height,
            )

            monitor = self._compose_monitor(screen)
            self._present_monitor(monitor)

        except Exception as error:
            self.status_text.set(f"FOIMS-X render error: {error}")
            self._draw_error(str(error))

    def _render_foims_screen(
        self,
        logical_width: int,
        logical_height: int,
    ) -> Image.Image:
        image = Image.new(
            "RGBA",
            (logical_width, logical_height),
            PALETTE["screen"],
        )
        draw = ImageDraw.Draw(image)

        def scale_x(value: float) -> int:
            return round(value * logical_width / 640)

        def scale_y(value: float) -> int:
            return round(value * logical_height / 480)

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
                    scale_x(left),
                    scale_y(top),
                    scale_x(right),
                    scale_y(bottom),
                ),
                fill=fill,
                outline=outline,
                width=max(1, scale_x(width)),
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
                    scale_x(left),
                    scale_y(top),
                    scale_x(right),
                    scale_y(bottom),
                ),
                fill=fill,
                width=max(1, scale_x(width)),
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
                image,
                scale_x(left),
                scale_y(top),
                value,
                max(6, scale_y(size)),
                color,
                align,
                (
                    scale_x(max_width)
                    if max_width is not None
                    else None
                ),
            )

        for grid_x in range(16, 640, 16):
            line(grid_x, 16, grid_x, 464, PALETTE["grid"])

        for grid_y in range(16, 464, 16):
            line(16, grid_y, 624, grid_y, PALETTE["grid"])

        rectangle(12, 12, 628, 468, PALETTE["screen"], PALETTE["border"])
        rectangle(18, 18, 622, 48, PALETTE["panel"], PALETTE["border"])

        text(
            28,
            27,
            "F.O.I.M.S.-X // FEDERAL OPERATIONAL INFORMATION",
            12,
            PALETTE["accent"],
        )
        text(
            612,
            27,
            "LINK: SECURE  SYS: NOMINAL",
            10,
            PALETTE["muted"],
            "right",
        )

        metrics = active_rows(self.app.tables.get("metrics", []))
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

        selected_metrics = metrics[:3]
        selected_facilities = facilities[:4]

        if selected_metrics:
            card_height = 112

            for index, metric in enumerate(selected_metrics):
                self._draw_metric_card(
                    image,
                    metric,
                    tiers,
                    flavors,
                    metric_left + 8,
                    metric_top + 32 + index * card_height,
                    metric_right - metric_left - 16,
                    card_height - 6,
                    logical_width,
                    logical_height,
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
                    image,
                    facility,
                    facility_left + 8,
                    facility_top + 34 + index * 47,
                    facility_right - facility_left - 16,
                    42,
                    index,
                    logical_width,
                    logical_height,
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
            directive_top + 52,
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
            457,
            "FOIMS-X // AUTHORING PREVIEW // 4:3 CRT",
            8,
            PALETTE["muted"],
        )
        text(
            614,
            457,
            (
                f"M:{len(metrics):02d} "
                f"T:{len(tiers):02d} "
                f"F:{len(facilities):02d}"
            ),
            8,
            PALETTE["muted"],
            "right",
        )

        for scanline_y in range(18, logical_height - 18, 2):
            draw.line(
                (
                    0,
                    scanline_y,
                    logical_width,
                    scanline_y,
                ),
                fill=(0, 0, 0, 38),
                width=1,
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
        logical_width: int,
        logical_height: int,
    ) -> None:
        draw = ImageDraw.Draw(image)

        def sx(value: float) -> int:
            return round(value * logical_width / 640)

        def sy(value: float) -> int:
            return round(value * logical_height / 480)

        metric_id = metric.get("metric_id", "")
        metric_name = metric.get("display_name", metric_id)
        value = numeric_value(metric.get("default_value", "0"))
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
            max(7, sy(10)),
            PALETTE["text"],
        )
        self._draw_text(
            image,
            sx(left + width - 10),
            sy(top + 10),
            f"{int(value):04d}/{int(maximum):04d}",
            max(6, sy(9)),
            PALETTE["muted"],
            "right",
        )
        self._draw_text(
            image,
            sx(left + 12),
            sy(top + 28),
            tier_label,
            max(8, sy(13)),
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
                max(6, sy(8)),
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
        logical_width: int,
        logical_height: int,
    ) -> None:
        draw = ImageDraw.Draw(image)

        def sx(value: float) -> int:
            return round(value * logical_width / 640)

        def sy(value: float) -> int:
            return round(value * logical_height / 480)

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
            max(6, sy(9)),
            PALETTE["text"],
            max_width=sx(width - 78),
        )
        self._draw_text(
            image,
            sx(left + width - 8),
            sy(top + 8),
            tier,
            max(6, sy(8)),
            color,
            "right",
        )
        self._draw_text(
            image,
            sx(left + 9),
            sy(top + 25),
            panel_id,
            max(5, sy(7)),
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
            max(6, pixel_size),
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
            spacing=max(1, pixel_size // 3),
        )
        text_width = bounds[2] - bounds[0]

        if align == "right":
            left -= text_width

        draw.multiline_text(
            (left + 1, top + 1),
            text_value,
            font=font,
            fill=PALETTE["shadow"],
            spacing=max(1, pixel_size // 3),
        )
        draw.multiline_text(
            (left, top),
            text_value,
            font=font,
            fill=color,
            spacing=max(1, pixel_size // 3),
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

    def _display_scale(self) -> float:
        canvas_width = max(self.canvas.winfo_width(), 1)
        canvas_height = max(self.canvas.winfo_height(), 1)

        fit_scale = min(
            canvas_width / OVERLAY_SIZE[0],
            canvas_height / OVERLAY_SIZE[1],
        )

        mode = self.display_scale_name.get()

        if mode == "Fit":
            return max(1.0, fit_scale)

        if mode == "Integer Fit":
            return float(max(1, int(fit_scale)))

        return float(mode.rstrip("x"))

    def _compose_monitor(self, screen: Image.Image) -> Image.Image:
        display_scale = self._display_scale()

        monitor_width = max(1, round(OVERLAY_SIZE[0] * display_scale))
        monitor_height = max(1, round(OVERLAY_SIZE[1] * display_scale))

        aperture_x = round(SCREEN_APERTURE[0] * display_scale)
        aperture_y = round(SCREEN_APERTURE[1] * display_scale)
        aperture_width = max(1, round(SCREEN_APERTURE[2] * display_scale))
        aperture_height = max(1, round(SCREEN_APERTURE[3] * display_scale))

        overlay = Image.open(self._overlay_path()).convert("RGBA")

        if overlay.size != OVERLAY_SIZE:
            overlay = overlay.resize(
                OVERLAY_SIZE,
                Image.Resampling.NEAREST,
            )

        overlay = overlay.resize(
            (monitor_width, monitor_height),
            Image.Resampling.NEAREST,
        )

        screen_fit = screen.resize(
            (aperture_width, aperture_height),
            Image.Resampling.NEAREST,
        )

        monitor = Image.new(
            "RGBA",
            (monitor_width, monitor_height),
            PALETTE["desktop"],
        )

        monitor.alpha_composite(screen_fit, (aperture_x, aperture_y))
        monitor.alpha_composite(overlay, (0, 0))

        return monitor

    def _present_monitor(self, monitor: Image.Image) -> None:
        canvas_width = max(self.canvas.winfo_width(), 1)
        canvas_height = max(self.canvas.winfo_height(), 1)

        output_width, output_height = monitor.size

        self._photo = ImageTk.PhotoImage(monitor)

        self.canvas.create_image(
            canvas_width / 2,
            canvas_height / 2,
            image=self._photo,
            anchor=tk.CENTER,
        )

        logical_width, logical_height = LOGICAL_SIZES[
            self.logical_size_name.get()
        ]
        mode = self.display_scale_name.get()
        clipped = (
            output_width > canvas_width or output_height > canvas_height
        )

        clip_note = " // CLIPPED" if clipped else ""

        self.status_text.set(
            (
                f"EMULATION: {logical_width}x{logical_height} // "
                f"DISPLAY: {mode} // "
                f"MONITOR: {output_width}x{output_height}"
                f"{clip_note}"
            )
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
                "Check the CRT overlay and font asset paths."
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



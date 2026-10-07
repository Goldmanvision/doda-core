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
from pathlib import Path
from tkinter import ttk
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageTk


DESIGN_SIZE = (640, 480)

CRT_OVERLAY_SIZE = (412, 309)

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


class FoimsXPreview:
    """Read-only FOIMS-X authoring preview at high-resolution output."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self.window = tk.Toplevel(app)
        self.window.title("FOIMS-X Preview Monitor")
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
        self._pending_resize: str | None = None

        self._build_controls()
        self._build_canvas()

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind("<Control-r>", self.refresh_preview)
        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)
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


    def toggle_fullscreen(
        self,
        _event: tk.Event[Any] | None = None,
    ) -> str:
        """Toggle full screen for the FOIMS-X Preview Monitor only."""
        is_fullscreen = bool(self.window.attributes("-fullscreen"))
        self.window.attributes("-fullscreen", not is_fullscreen)
        self.window.after_idle(self.render)
        return "break"

    def exit_fullscreen(
        self,
        _event: tk.Event[Any] | None = None,
    ) -> str:
        """Exit FOIMS-X preview full screen without affecting the Workbench."""
        if bool(self.window.attributes("-fullscreen")):
            self.window.attributes("-fullscreen", False)
            self.window.after_idle(self.render)
        return "break"
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
            text="FOIMS-X High-Resolution Presentation Preview",
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

    def _on_presentation_size_change(
        self,
        _event: tk.Event[Any],
    ) -> None:
        self.render()

    def _on_resize(self, event: tk.Event[Any]) -> None:
        if event.widget is not self.window:
            return

        if self._pending_resize is not None:
            self.window.after_cancel(self._pending_resize)

        self._pending_resize = self.window.after(90, self.render)

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
            presentation_width, presentation_height = PRESENTATION_SIZES[
                self.presentation_size_name.get()
            ]

            active_width = round(presentation_height * 4 / 3)

            foims_screen = self._render_foims_screen(
                active_width,
                presentation_height,
            )

            presentation = self._compose_presentation(
                foims_screen,
                presentation_width,
                presentation_height,
            )

            self._present(presentation)

        except Exception as error:
            self.status_text.set(f"FOIMS-X render error: {error}")
            self._draw_error(str(error))

    def _render_foims_screen(
        self,
        active_width: int,
        active_height: int,
    ) -> Image.Image:
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
        text(
            612,
            26,
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
            "FOIMS-X // AUTHORING PREVIEW // NATIVE UI SCALE",
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

    def _compose_presentation(
        self,
        foims_screen: Image.Image,
        presentation_width: int,
        presentation_height: int,
    ) -> Image.Image:
        """
        Strict compositing order:

        Layer 1 (back):  native-resolution FOIMS-X display.
        Layer 2 (front): raster-scaled CRT hardware/bezel overlay.

        The CRT screen opening is explicitly transparent in Layer 2, so the
        front bezel never destroys the text rendered on Layer 1.
        """
        presentation = Image.new(
            "RGBA",
            (presentation_width, presentation_height),
            PALETTE["desktop"],
        )

        active_width, active_height = foims_screen.size
        active_x = (presentation_width - active_width) // 2

        # -----------------------------------------------------------------
        # LAYER 1: FOIMS-X is installed first, at its native final display
        # resolution. It is never raster-scaled by the CRT compositor.
        # -----------------------------------------------------------------
        presentation.alpha_composite(foims_screen, (active_x, 0))

        # -----------------------------------------------------------------
        # LAYER 2: CRT overlay is installed after FOIMS-X. This is the
        # closest/front-most visual layer.
        # -----------------------------------------------------------------
        bezel = Image.open(self._overlay_path()).convert("RGBA")

        if bezel.size != CRT_OVERLAY_SIZE:
            bezel = bezel.resize(
                CRT_OVERLAY_SIZE,
                Image.Resampling.NEAREST,
            )

        aperture_x, aperture_y, aperture_width, aperture_height = (
            CRT_SCREEN_APERTURE
        )

        # Resize only the raster overlay. X/Y use the screen-opening size
        # as their source reference, allowing the physical bezel opening
        # to align with the complete 4:3 FOIMS-X active display.
        bezel_scale_x = active_width / aperture_width
        bezel_scale_y = active_height / aperture_height

        bezel_width = max(
            1,
            round(CRT_OVERLAY_SIZE[0] * bezel_scale_x),
        )
        bezel_height = max(
            1,
            round(CRT_OVERLAY_SIZE[1] * bezel_scale_y),
        )

        bezel = bezel.resize(
            (bezel_width, bezel_height),
            Image.Resampling.NEAREST,
        )

        # The scaled CRT screen opening is registered exactly to FOIMS-X.
        bezel_x = round(active_x - aperture_x * bezel_scale_x)
        bezel_y = round(-aperture_y * bezel_scale_y)

        # Cut an alpha hole in the front layer where the CRT tube/display
        # opening sits. The bezel, corners, edges, and monitor housing
        # remain visible above FOIMS-X; the UI remains visible through
        # the transparent opening.
        bezel_alpha = bezel.getchannel("A")
        aperture_mask = ImageDraw.Draw(bezel_alpha)

        opening_left = round(aperture_x * bezel_scale_x)
        opening_top = round(aperture_y * bezel_scale_y)
        opening_right = round(
            (aperture_x + aperture_width) * bezel_scale_x
        )
        opening_bottom = round(
            (aperture_y + aperture_height) * bezel_scale_y
        )

        aperture_mask.rectangle(
            (
                opening_left,
                opening_top,
                opening_right,
                opening_bottom,
            ),
            fill=0,
        )

        bezel.putalpha(bezel_alpha)

        # This is deliberately the final visual composition operation:
        # the CRT overlay is Layer 2, in front of FOIMS-X.
        presentation.alpha_composite(bezel, (bezel_x, bezel_y))

        return presentation
    def _present(self, presentation: Image.Image) -> None:
        canvas_width = max(self.canvas.winfo_width(), 1)
        canvas_height = max(self.canvas.winfo_height(), 1)

        fit_scale = min(
            canvas_width / presentation.width,
            canvas_height / presentation.height,
        )

        output_width = max(1, round(presentation.width * fit_scale))
        output_height = max(1, round(presentation.height * fit_scale))

        output = presentation.resize(
            (output_width, output_height),
            Image.Resampling.LANCZOS,
        )

        self._photo = ImageTk.PhotoImage(output)

        self.canvas.create_image(
            canvas_width / 2,
            canvas_height / 2,
            image=self._photo,
            anchor=tk.CENTER,
        )

        presentation_width, presentation_height = presentation.size
        active_width = round(presentation_height * 4 / 3)

        self.status_text.set(
            (
                f"OUTPUT: {presentation_width}x{presentation_height} // "
                f"FOIMS-X ACTIVE: {active_width}x{presentation_height} // "
                "UI: NATIVE SCALED // ASPECT: 4:3"
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






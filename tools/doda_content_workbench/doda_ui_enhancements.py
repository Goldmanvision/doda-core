"""DoDA Content Workbench - small UI enhancements shared by every table.

Double-clicking a column header border resizes that column to fit its heading
and its longest value.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont, ttk
from typing import Any

PADDING = 18
MIN_WIDTH = 40
MAX_WIDTH = 900


def _font_for(tree: ttk.Treeview, heading: bool) -> tkfont.Font:
    name = "Treeview.Heading" if heading else "Treeview"
    spec = ttk.Style(tree).lookup(name, "font") or "TkDefaultFont"
    try:
        return tkfont.Font(root=tree, font=spec)
    except tk.TclError:
        return tkfont.nametofont("TkDefaultFont")


def _all_items(tree: ttk.Treeview, parent: str = "") -> list[str]:
    out: list[str] = []
    for item in tree.get_children(parent):
        out.append(item)
        out.extend(_all_items(tree, item))
    return out


def _display_columns(tree: ttk.Treeview) -> list[str]:
    cols = [str(c) for c in tree["columns"]]
    shown = [str(c) for c in tree["displaycolumns"]]
    if shown == ["#all"]:
        return cols
    return [cols[int(c)] if c.isdigit() else c for c in shown]


def autosize_column(tree: ttk.Treeview, column_id: str) -> None:
    cols = [str(c) for c in tree["columns"]]
    if column_id not in cols:
        return
    index = cols.index(column_id)
    head_font = _font_for(tree, True)
    body_font = _font_for(tree, False)
    width = head_font.measure(str(tree.heading(column_id, "text"))) + PADDING
    for item in _all_items(tree):
        values = tree.item(item, "values")
        if index < len(values):
            width = max(width, body_font.measure(str(values[index])) + PADDING)
    tree.column(column_id, width=max(MIN_WIDTH, min(MAX_WIDTH, int(width))))


def _on_double_click(event: Any) -> str | None:
    tree = event.widget
    if not isinstance(tree, ttk.Treeview):
        return None
    if tree.identify_region(event.x, event.y) != "separator":
        return None
    display = _display_columns(tree)
    if not display:
        return None
    show_tree = "tree" in str(tree.cget("show"))
    position = int(tree.column("#0", "width")) if show_tree else 0
    total = position + sum(int(tree.column(c, "width")) for c in display)
    offset = int(round(tree.xview()[0] * total))
    best: tuple[int, str] | None = None
    for c in display:
        position += int(tree.column(c, "width"))
        distance = abs((position - offset) - event.x)
        if best is None or distance < best[0]:
            best = (distance, c)
    if best is not None:
        autosize_column(tree, best[1])
    return "break"


def install_tree_autosize(app: Any) -> None:
    app.bind_class("Treeview", "<Double-1>", _on_double_click, add="+")
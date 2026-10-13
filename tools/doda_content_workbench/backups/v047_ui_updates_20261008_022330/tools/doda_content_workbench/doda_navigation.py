"""
DoDA Content Workbench - grouped, resizable, collapsible navigation sidebar.

Builds a grouped tree from the notebook's actual tabs (so no editor is
reinstalled or rebuilt) using doda_page_registry for grouping and labels.
Tabs not in the registry appear under "Other". The notebook tab strip is
hidden while the sidebar is shown; View > Navigation can restore it.
Switching pages never destroys page widgets, so unsaved forms are preserved.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from doda_page_registry import GROUP_ORDER, page_for_tab_text

MIN_WIDTH, MAX_WIDTH, DEFAULT_WIDTH = 160, 480, 240


class GroupedNavigation:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.nb: ttk.Notebook = app.notebook
        self.width = DEFAULT_WIDTH
        self.visible = True
        self.tab_strip_hidden = False
        self.item_to_tab: dict[str, str] = {}
        self.tab_to_item: dict[str, str] = {}
        self.groups: dict[str, list[tuple[str, str]]] = {}

        style = ttk.Style(app)
        self._orig_layout = style.layout("TNotebook.Tab")
        style.layout("Grouped.TNotebook.Tab", [])
        style.configure("Grouped.TNotebook", tabmargins=0)

        self.container = ttk.Frame(self.nb.master, width=self.width)
        self.container.pack_propagate(False)
        self.container.pack(side=tk.LEFT, fill=tk.Y, before=self.nb, padx=(0, 0))
        self.handle = tk.Frame(self.nb.master, width=5, cursor="sb_h_double_arrow", background="#30363d")
        self.handle.pack(side=tk.LEFT, fill=tk.Y, before=self.nb, padx=(2, 8))
        self.handle.bind("<B1-Motion>", self._drag)

        bar = ttk.Frame(self.container)
        bar.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(bar, text="Navigation", style="Section.TLabel").pack(side=tk.LEFT)
        ttk.Button(bar, text="+", width=2, command=lambda: self.set_all_open(True)).pack(side=tk.RIGHT)
        ttk.Button(bar, text="−", width=2, command=lambda: self.set_all_open(False)).pack(side=tk.RIGHT, padx=(0, 2))

        self.tree = ttk.Treeview(self.container, show="tree", selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.nb.bind("<<NotebookTabChanged>>", self._sync_from_notebook, add="+")

        self.rebuild()
        self.set_tab_strip_hidden(True)

    # ------------------------------------------------------------------
    def rebuild(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.item_to_tab.clear()
        self.tab_to_item.clear()
        self.groups = {}
        for tab_id in self.nb.tabs():
            text = self.nb.tab(tab_id, "text")
            page = page_for_tab_text(text.replace(" - ", " — "))
            group = page.group if page else "Other"
            label = page.label if page else text
            self.groups.setdefault(group, []).append((label, tab_id))
        order = [g for g in GROUP_ORDER if g in self.groups] + (["Other"] if "Other" in self.groups else [])
        for g in order:
            gid = self.tree.insert("", tk.END, text=g, open=True)
            for label, tab_id in self.groups[g]:
                iid = self.tree.insert(gid, tk.END, text="  " + label)
                self.item_to_tab[iid] = tab_id
                self.tab_to_item[tab_id] = iid
        self._sync_from_notebook()

    def _on_select(self, _e: Any = None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        tab = self.item_to_tab.get(sel[0])
        if tab is None:      # group row: toggle open/closed
            self.tree.item(sel[0], open=not self.tree.item(sel[0], "open"))
            return
        if self.nb.select() != tab:
            self.nb.select(tab)

    def _sync_from_notebook(self, _e: Any = None) -> None:
        item = self.tab_to_item.get(self.nb.select())
        if item and self.tree.selection() != (item,):
            self.tree.item(self.tree.parent(item), open=True)
            self.tree.selection_set(item)
            self.tree.see(item)

    def _drag(self, event: Any) -> None:
        new = self.container.winfo_width() + event.x
        self.width = max(MIN_WIDTH, min(MAX_WIDTH, new))
        self.container.configure(width=self.width)

    # ---- View-menu actions ------------------------------------------
    def set_all_open(self, is_open: bool) -> None:
        for g in self.tree.get_children():
            self.tree.item(g, open=is_open)

    def toggle_sidebar(self) -> None:
        if self.visible:
            self.container.pack_forget()
            self.handle.pack_forget()
            self.set_tab_strip_hidden(False)
        else:
            self.container.pack(side=tk.LEFT, fill=tk.Y, before=self.nb)
            self.handle.pack(side=tk.LEFT, fill=tk.Y, before=self.nb, padx=(2, 8))
            self.set_tab_strip_hidden(True)
        self.visible = not self.visible

    def set_tab_strip_hidden(self, hidden: bool) -> None:
        self.nb.configure(style="Grouped.TNotebook" if hidden else "TNotebook")
        self.tab_strip_hidden = hidden

    def go(self, tab_id: str) -> None:
        self.nb.select(tab_id)


def install_grouped_navigation(app: Any) -> GroupedNavigation:
    nav = GroupedNavigation(app)
    app.navigation = nav

    menu = app.view_menu
    opts = {k: menu.cget(k) for k in ("background", "foreground", "activebackground", "activeforeground")}
    nav_menu = tk.Menu(menu, tearoff=False, borderwidth=0, relief=tk.FLAT, **opts)
    nav_menu.add_command(label="Show/Hide Navigation Sidebar", command=nav.toggle_sidebar, accelerator="Ctrl+B")
    nav_menu.add_command(label="Expand All Groups", command=lambda: nav.set_all_open(True))
    nav_menu.add_command(label="Collapse All Groups", command=lambda: nav.set_all_open(False))
    nav_menu.add_separator()
    ordered = [g for g in GROUP_ORDER if g in nav.groups] + [g for g in nav.groups if g not in GROUP_ORDER]
    for group in ordered:
        pages = nav.groups[group]
        sub = tk.Menu(nav_menu, tearoff=False, borderwidth=0, relief=tk.FLAT, **opts)
        for label, tab_id in pages:
            sub.add_command(label=label, command=lambda t=tab_id: nav.go(t))
        nav_menu.add_cascade(label=group, menu=sub)
    menu.add_separator()
    menu.add_cascade(label="Navigation", menu=nav_menu)
    app.bind_all("<Control-b>", lambda _e: (nav.toggle_sidebar(), "break")[1], add="+")
    return nav

"""Checkbox multi-select dropdown; values are semicolon-separated IDs."""
import csv
import tkinter as tk
from pathlib import Path
from tkinter import ttk


def parse_selection(raw):
    return list(dict.fromkeys(
        value.strip() for value in raw.split(";") if value.strip()
    ))


def merged_selection(raw, options, checked):
    keys = [key for key, label in options]
    unknown = [key for key in parse_selection(raw) if key not in keys]
    return ";".join(
        [key for key in keys if key in checked] + unknown
    )


def evidence_choices(source_directory):
    path = Path(source_directory) / "resources.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = []
    for row in rows:
        rid = (row.get("resource_id") or "").strip()
        if not rid.startswith("EVIDENCE_"):
            continue
        if (row.get("resource_kind") or "").strip().upper() != "STOCKPILE":
            continue
        label = (row.get("display_name") or rid).strip()
        if (row.get("active") or "").strip().upper() != "TRUE":
            label += " (inactive)"
        result.append((rid, label))
    return result


class MultiSelectDropdown(ttk.Menubutton):
    def __init__(self, parent, variable):
        self.variable = variable
        self.summary = tk.StringVar(master=parent)
        super().__init__(parent, textvariable=self.summary, width=32)
        self.options = []
        self.flags = {}
        self.menu = tk.Menu(
            self, tearoff=False, background="#1f2933",
            foreground="#e6edf3", activebackground="#264f78",
            activeforeground="#ffffff",
        )
        self.configure(menu=self.menu)
        self.trace_id = self.variable.trace_add("write", self._sync)
        self.set_options([])

    def set_options(self, options):
        self.options = list(options)
        self.flags = {}
        self.menu.delete(0, "end")
        for key, label in self.options:
            flag = tk.BooleanVar(master=self)
            self.flags[key] = flag
            self.menu.add_checkbutton(
                label=label, variable=flag, command=self._commit,
            )
        self.menu.add_separator()
        self.menu.add_command(
            label="Clear selection", command=lambda: self.variable.set("")
        )
        self._sync()

    def _sync(self, *args):
        selected = parse_selection(self.variable.get())
        labels = dict(self.options)
        for key, flag in self.flags.items():
            flag.set(key in selected)
        self.summary.set(
            "; ".join(labels.get(key, key) for key in selected)
            if selected else ("" if getattr(self, "_bulk_mode", False) else "Select evidence types...")
        )

    def _commit(self):
        checked = {key for key, flag in self.flags.items() if flag.get()}
        raw = self.variable.get()
        if getattr(self, "_bulk_mode", False) and raw == "Multiple values":
            raw = ""
        self.variable.set(merged_selection(raw, self.options, checked))

    def destroy(self):
        try:
            self.variable.trace_remove("write", self.trace_id)
        except tk.TclError:
            pass
        super().destroy()

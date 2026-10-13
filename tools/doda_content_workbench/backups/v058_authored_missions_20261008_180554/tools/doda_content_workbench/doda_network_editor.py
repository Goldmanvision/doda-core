"""
DoDA Content Workbench - Network and Transfers editors.

Adds three pages to the main notebook:
  * Network Tiers - Editor        (network_tiers.csv)
  * Modems and Routers - Editor   (network_hardware_models.csv)
  * Transfer and Interruption Rules - Reference (read-only contract view)

Field definitions come from doda_page_registry.TABLE_METADATA. Saves are
candidate-validated with doda_network_rules before any source file is replaced,
back up the previous file, and refuse to overwrite a file changed externally
since it was loaded. Authoring only; no runtime behaviour.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any

import doda_network_rules as network_rules
import doda_equipment_rules as equipment_rules
import doda_care_rules as care_rules
import doda_condition_rules as condition_rules
import doda_agent_attribute_rules as attribute_rules
import doda_personal_care_rules as personal_care_rules
import doda_time_rules as time_rules
import doda_recreation_content_rules as rc_rules
import doda_sobriety_rules as sobriety_rules
import doda_territory_rules as territory_rules
import doda_weapon_rules as weapon_rules
import doda_hostile_rules as hostile_rules
import doda_progression_identity_rules as progression_identity_rules
from doda_page_registry import TABLE_METADATA, TableSpec


SASH_IDLE = "#30363d"
SASH_ACTIVE = "#58a6ff"


def _sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def read_rows(path: Path, spec: TableSpec) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = []
        for raw in reader:
            row = {c: (raw.get(c) or "").strip() for c in spec.columns}
            if any(row.values()):
                rows.append(row)
    return rows


def write_rows(path: Path, spec: TableSpec, rows: list[dict[str, str]]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=spec.columns, lineterminator="\r\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in spec.columns})
    tmp.replace(path)


def validate_candidate(project_root: Path, table: str, rows: list[dict[str, str]]) -> network_rules.Result:
    """Validate the candidate table together with the other current network table."""
    src = project_root / "data_authoring" / "source"
    tmp_root = Path(tempfile.gettempdir()) / f"doda_net_candidate_{datetime.now():%Y%m%d%H%M%S%f}"
    tmp_src = tmp_root / "data_authoring" / "source"
    tmp_src.mkdir(parents=True)
    (tmp_root / "tools").mkdir()
    try:
        for other in TABLE_METADATA.values():
            if other.table == table:
                write_rows(tmp_src / other.filename, other, rows)
            elif (src / other.filename).is_file():
                shutil.copy2(src / other.filename, tmp_src / other.filename)
        track_path = src / "department_tracks.csv"
        if track_path.is_file():
            shutil.copy2(track_path, tmp_src / track_path.name)
        res = network_rules.Result()
        network_rules.validate_contract(res)
        network_rules.validate_network(tmp_root, res)
        equipment_rules.validate_equipment(tmp_root, res)
        care_rules.validate_care(tmp_root, res)
        condition_rules.validate_conditions(tmp_root, res)
        attribute_rules.validate_attributes(tmp_root, res)
        personal_care_rules.validate_personal_care(tmp_root, res)
        time_rules.validate_time_settings(tmp_root, res)
        rc_rules.validate_recreation_content(tmp_root, res)
        sobriety_rules.validate_sobriety(tmp_root, res)
        territory_rules.validate_territory(tmp_root, res)
        weapon_rules.validate_weapons(tmp_root, res)
        hostile_rules.validate_hostiles(tmp_root, res)
        progression_identity_rules.validate_identities(tmp_root, res)
        return res
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)



def reference_keys(source_directory, field):
    if field.kind == "track_ref":
        path = source_directory / "department_tracks.csv"
        if not path.is_file():
            return []
        with path.open(encoding="utf-8-sig", newline="") as fh:
            keys = [(row.get("track_id") or "").strip() for row in csv.DictReader(fh)]
        return list(dict.fromkeys(key for key in keys if key))
    ref = TABLE_METADATA[field.ref_table]
    return [row[ref.key] for row in read_rows(source_directory / ref.filename, ref)]

class NetworkTableEditor:
    def __init__(self, app: Any, tab: ttk.Frame, table: str, title: str) -> None:
        self.app = app
        self.tab = tab
        self.spec = TABLE_METADATA[table]
        self.title = title
        self.rows: list[dict[str, str]] = []
        self.loaded_sha: str | None = None
        self.dirty = False
        self.selected_index: int | None = None
        self.vars: dict[str, tk.StringVar] = {}
        self.widgets: dict[str, Any] = {}
        self._build()

    # ---- paths -------------------------------------------------------
    @property
    def path(self) -> Path:
        return self.app.source_directory / self.spec.filename

    @property
    def backup_dir(self) -> Path:
        return self.app.project_root / "data_authoring" / "backups" / self.spec.table

    # ---- UI ----------------------------------------------------------
    def _build(self) -> None:
        tab = self.tab
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2, minsize=430)
        tab.rowconfigure(1, weight=1)

        self.status = tk.StringVar(value="")
        ttk.Label(tab, text=self.title, style="Section.TLabel").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(tab, textvariable=self.status, foreground="#9da7b3").grid(row=0, column=1, sticky=tk.E)

        pane = tk.PanedWindow(tab, orient=tk.HORIZONTAL, sashwidth=6, sashrelief=tk.FLAT,
                              background=SASH_IDLE, borderwidth=0, opaqueresize=True)
        pane.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self.pane = pane
        pane.bind("<Motion>", self._sash_hover)
        pane.bind("<Leave>", lambda _e: pane.configure(background=SASH_IDLE))
        pane.bind("<Map>", lambda _e: pane.after(60, self._place_sash))

        left = ttk.Frame(pane)
        pane.add(left, minsize=320, stretch="always")
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        self._list_frame = left
        cols = [f.name for f in self.spec.fields if not f.multiline]
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for f in self.spec.fields:
            if f.multiline:
                continue
            self.tree.heading(f.name, text=f.label)
            self.tree.column(f.name, width=110, minwidth=60, stretch=False, anchor=tk.W)
        sb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        xsb = ttk.Scrollbar(left, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=xsb.set)
        xsb.grid(row=1, column=0, sticky=tk.EW)
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        sb.grid(row=0, column=1, sticky=tk.NS)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        form = ttk.LabelFrame(pane, text="Record", padding=8)
        pane.add(form, minsize=400, stretch="never")
        form.columnconfigure(0, weight=1)
        form.rowconfigure(0, weight=1)
        self._form_frame = form

        bg = ttk.Style().lookup("TFrame", "background") or "#0d1117"
        canvas = tk.Canvas(form, highlightthickness=0, borderwidth=0, background=bg,
                           yscrollincrement=24, xscrollincrement=24)
        vbar = ttk.Scrollbar(form, orient=tk.VERTICAL, command=canvas.yview)
        hbar = ttk.Scrollbar(form, orient=tk.HORIZONTAL, command=canvas.xview)
        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vbar.grid(row=0, column=1, sticky=tk.NS)
        hbar.grid(row=1, column=0, sticky=tk.EW)
        fields = ttk.Frame(canvas)
        fields.columnconfigure(1, weight=1)
        win = canvas.create_window((0, 0), window=fields, anchor="nw")

        def fit(_e: Any = None) -> None:
            canvas.itemconfigure(win, width=max(canvas.winfo_width(), fields.winfo_reqwidth()))
            canvas.configure(scrollregion=canvas.bbox("all"))

        fields.bind("<Configure>", fit)
        canvas.bind("<Configure>", fit)

        for i, f in enumerate(self.spec.fields):
            ttk.Label(fields, text=f.label + ("" if f.required else " (optional)")).grid(
                row=i, column=0, sticky=tk.W, pady=2, padx=(0, 6))
            var = tk.StringVar()
            self.vars[f.name] = var
            if f.kind == "bool":
                w = ttk.Combobox(fields, textvariable=var, values=("true", "false"), state="readonly")
            elif f.kind in ("choice", "ref", "track_ref"):
                # Optional dropdowns get a blank entry so a value can be cleared.
                values = tuple(f.choices) if f.required else ("",) + tuple(f.choices)
                w = ttk.Combobox(fields, textvariable=var, values=values, state="readonly")
            else:
                w = ttk.Entry(fields, textvariable=var)
            w.grid(row=i, column=1, sticky=tk.EW, pady=2)
            self.widgets[f.name] = w

        def on_wheel(event: Any) -> str:
            step = -2 if event.delta > 0 else 2
            if event.state & 0x0001:
                canvas.xview_scroll(step, "units")
            elif fields.winfo_reqheight() > canvas.winfo_height():
                canvas.yview_scroll(step, "units")
            return "break"

        def reveal(event: Any) -> None:
            w = event.widget
            total = fields.winfo_reqheight()
            view = canvas.winfo_height()
            if total <= view or total <= 0:
                return
            top, bottom = w.winfo_y(), w.winfo_y() + w.winfo_height()
            y0 = canvas.canvasy(0)
            if top < y0:
                canvas.yview_moveto(max(0.0, (top - 4) / total))
            elif bottom > y0 + view:
                canvas.yview_moveto(min(1.0, (bottom + 4 - view) / total))

        for w in [canvas, fields] + list(fields.winfo_children()):
            w.bind("<MouseWheel>", on_wheel)
        for w in self.widgets.values():
            w.bind("<FocusIn>", reveal, add="+")

        btns = ttk.Frame(form)
        btns.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=(10, 0))
        for text, cmd in (("New", self.new_record), ("Apply to List", self.apply_record),
                          ("Delete", self.delete_record)):
            ttk.Button(btns, text=text, command=cmd).pack(side=tk.LEFT, padx=(0, 4))
        btns2 = ttk.Frame(form)
        btns2.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(6, 0))
        ttk.Button(btns2, text="Save to Source", command=self.save).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btns2, text="Revert", command=self.revert).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btns2, text="Validate Draft", command=self.validate_draft).pack(side=tk.LEFT)
        btns3 = ttk.Frame(form)
        btns3.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(6, 0))
        ttk.Button(btns3, text="Copy to CSV", command=self.copy_csv).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btns3, text="Paste CSV", command=self.paste_csv).pack(side=tk.LEFT)

        state = getattr(self.app, "panel_state", None) or {}
        for which in ("list", "record"):
            if not state.get(which, True):
                self.set_panel_visible(which, False)

    # ---- panel show / hide (View > Show / Hide Panel) ----------------
    def _pane_paths(self) -> list:
        return [str(p) for p in self.pane.panes()]

    def set_panel_visible(self, which: str, show: bool) -> None:
        frame = self._list_frame if which == "list" else self._form_frame
        present = str(frame) in self._pane_paths()
        if show == present:
            return
        try:
            if not show:
                if len(self._pane_paths()) < 2:
                    return
                self.pane.forget(frame)
            elif which == "list":
                paths = self._pane_paths()
                if paths:
                    self.pane.add(frame, before=paths[0], minsize=320, stretch="always")
                else:
                    self.pane.add(frame, minsize=320, stretch="always")
            else:
                self.pane.add(frame, minsize=400, stretch="never")
            paths = self._pane_paths()
            if len(paths) == 1:
                self.pane.paneconfigure(paths[0], stretch="always")
            else:
                self.pane.paneconfigure(self._list_frame, stretch="always")
                self.pane.paneconfigure(self._form_frame, stretch="never")
                self._sash_set = False
                self.pane.after(60, self._place_sash)
        except tk.TclError:
            pass

    # ---- CSV copy / paste --------------------------------------------
    def copy_csv(self) -> None:
        import io
        names = [f.name for f in self.spec.fields]
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\r\n")
        w.writerow(names)
        w.writerow([self.vars[n].get().strip() for n in names])
        self.tab.clipboard_clear()
        self.tab.clipboard_append(buf.getvalue())
        self.tab.update()
        self.app.log(f"[{self.spec.table}] Copied current record to clipboard as CSV.")
        self._set_status("Copied current record to clipboard as CSV.")

    def paste_csv(self) -> None:
        import io
        try:
            text = self.tab.clipboard_get()
        except tk.TclError:
            messagebox.showwarning(self.title, "The clipboard is empty or does not contain text.")
            return
        try:
            rows = [r for r in csv.reader(io.StringIO(text.lstrip("\ufeff")))
                    if any(c.strip() for c in r)]
        except csv.Error as exc:
            messagebox.showwarning(self.title, f"Clipboard text is not valid CSV: {exc}")
            return
        if len(rows) < 2:
            messagebox.showwarning(self.title, "Expected a header row followed by one data row.")
            return
        header = [h.strip() for h in rows[0]]
        names = {f.name for f in self.spec.fields}
        pasted = {h: v.strip() for h, v in zip(header, rows[1]) if h in names}
        if not pasted:
            messagebox.showwarning(self.title, "No column in the clipboard CSV matches this table.")
            return
        for f in self.spec.fields:
            blank = "true" if f.kind == "bool" else ""
            self.vars[f.name].set(pasted.get(f.name, blank))
        notes = []
        unknown = [h for h in header if h and h not in names]
        if unknown:
            notes.append("ignored columns: " + ", ".join(unknown))
        if len(rows) > 2:
            notes.append(f"used the first of {len(rows) - 1} data rows")
        self._set_status(f"Pasted {len(pasted)} field(s) into the form; not applied yet."
                         + (" (" + "; ".join(notes) + ")" if notes else ""))

    # ---- data --------------------------------------------------------
    def _sash_hover(self, event: Any) -> None:
        over = bool(self.pane.identify(event.x, event.y))
        self.pane.configure(background=SASH_ACTIVE if over else SASH_IDLE)

    def _place_sash(self) -> None:
        if getattr(self, "_sash_set", False):
            return
        try:
            width = self.pane.winfo_width()
            if width > 700:
                self.pane.sash_place(0, max(320, width - 450), 0)
                self._sash_set = True
        except tk.TclError:
            pass

    def _ref_choices(self) -> None:
        for f in self.spec.fields:
            if f.kind in ("ref", "track_ref"):
                keys = reference_keys(self.app.source_directory, f)
                if not f.required:
                    keys = [""] + keys
                self.widgets[f.name].configure(values=keys)

    def load(self) -> None:
        self.rows = read_rows(self.path, self.spec)
        self.loaded_sha = _sha(self.path)
        self.dirty = False
        self.selected_index = None
        self._ref_choices()
        self._render()
        self._clear_form()

    def update(self) -> None:
        """Called by the main refresh. Never discards unsaved drafts silently."""
        if self.dirty:
            self._ref_choices()
            self._set_status("Unsaved draft kept; source refresh skipped for this table.")
            return
        self.load()

    def _render(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for i, r in enumerate(self.rows):
            self.tree.insert("", tk.END, iid=str(i),
                             values=[r.get(f.name, "") for f in self.spec.fields if not f.multiline])
        n = len(self.rows)
        self._set_status(f"{n} row{'s' if n != 1 else ''}" + (" - UNSAVED CHANGES" if self.dirty else ""))

    def _set_status(self, text: str) -> None:
        self.status.set(text)

    def _clear_form(self) -> None:
        for f in self.spec.fields:
            self.vars[f.name].set("true" if f.kind == "bool" else "")

    def _on_select(self, _e: Any = None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        self.selected_index = int(sel[0])
        row = self.rows[self.selected_index]
        for f in self.spec.fields:
            self.vars[f.name].set(row.get(f.name, ""))

    def new_record(self) -> None:
        self.tree.selection_remove(self.tree.selection())
        self.selected_index = None
        self._clear_form()
        next_sort = max([int(r["sort_order"]) for r in self.rows if r.get("sort_order", "").isdigit()] or [0]) + 10
        self.vars["sort_order"].set(str(next_sort))

    def _form_row(self) -> dict[str, str] | None:
        row = {f.name: self.vars[f.name].get().strip() for f in self.spec.fields}
        missing = [f.label for f in self.spec.fields if f.required and not row[f.name]]
        if missing:
            messagebox.showwarning(self.title, "Required fields are blank:\n" + "\n".join(missing))
            return None
        for f in self.spec.fields:
            if f.kind == "int" and (f.required or row[f.name]):
                try:
                    int(row[f.name])
                except ValueError:
                    messagebox.showwarning(self.title, f"{f.label} must be a whole number.")
                    return None
        key = tuple(row[k] for k in self.spec.key_columns)
        for i, r in enumerate(self.rows):
            if tuple(r[k] for k in self.spec.key_columns) == key and i != self.selected_index:
                messagebox.showwarning(self.title, f"{' / '.join(key)} already exists.")
                return None
        return row

    def apply_record(self) -> None:
        row = self._form_row()
        if row is None:
            return
        if self.selected_index is None:
            self.rows.append(row)
            self.selected_index = len(self.rows) - 1
        else:
            self.rows[self.selected_index] = row
        self.dirty = True
        self._render()
        self.tree.selection_set(str(self.selected_index))

    def delete_record(self) -> None:
        if self.selected_index is None:
            return
        key = " / ".join(self.rows[self.selected_index][k] for k in self.spec.key_columns)
        if not messagebox.askyesno(self.title, f"Remove {key} from the draft? (Not saved until Save to Source.)"):
            return
        del self.rows[self.selected_index]
        self.selected_index = None
        self.dirty = True
        self._render()
        self._clear_form()

    def revert(self) -> None:
        if self.dirty and not messagebox.askyesno(self.title, "Discard unsaved changes to this table?"):
            return
        self.load()

    def validate_draft(self) -> bool:
        res = validate_candidate(self.app.project_root, self.spec.table, self.rows)
        self._report(res, "Draft validation")
        return res.valid

    def _report(self, res: network_rules.Result, label: str) -> None:
        for line in res.errors:
            self.app.log(f"[{self.spec.table}] ERROR: {line}")
        for line in res.warnings:
            self.app.log(f"[{self.spec.table}] WARNING: {line}")
        if res.errors:
            messagebox.showerror(self.title, f"{label} failed:\n\n" + "\n".join(res.errors[:12]))
        elif res.warnings:
            messagebox.showwarning(self.title, f"{label} passed with warnings:\n\n" + "\n".join(res.warnings[:12]))
        else:
            self._set_status(f"{label} passed.")

    def save(self) -> None:
        if _sha(self.path) != self.loaded_sha:
            messagebox.showerror(self.title, f"{self.spec.filename} changed on disk since it was loaded.\n"
                                             "Revert to reload it, then reapply your edits.")
            return
        res = validate_candidate(self.app.project_root, self.spec.table, self.rows)
        if not res.valid:
            self._report(res, "Save blocked; validation")
            return
        if self.path.is_file():
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup = self.backup_dir / f"{self.path.stem}_{datetime.now():%Y%m%d_%H%M%S_%f}.csv"
            shutil.copy2(self.path, backup)
            self.app.log(f"Backup written: {backup}")
        write_rows(self.path, self.spec, self.rows)
        self.app.log(f"Saved {self.spec.filename} ({len(self.rows)} rows).")
        if res.warnings:
            self._report(res, "Saved")
        self.load()
        for other in getattr(self.app, "network_editors", []):
            if other is not self and not other.dirty:
                other.load()


class TransferRulesView:
    def __init__(self, app: Any, tab: ttk.Frame) -> None:
        self.app = app
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        ttk.Label(tab, text="Transfer and Interruption Rules (read-only; settled design decisions)",
                  style="Section.TLabel").grid(row=0, column=0, sticky=tk.W, pady=(0, 6))
        self.text = tk.Text(tab, wrap=tk.WORD, background="#0d1117", foreground="#e6edf3",
                            insertbackground="#e6edf3", relief=tk.FLAT, font=("Consolas", 10))
        sb = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=sb.set)
        self.text.grid(row=1, column=0, sticky=tk.NSEW)
        sb.grid(row=1, column=1, sticky=tk.NS)
        self.update()

    def update(self) -> None:
        c = network_rules.build_contract()
        lines = [f"Contract version {c['contractVersion']}   Runtime implemented: {c['runtimeImplemented']}", ""]
        lines.append("TRANSFER STATES")
        for s in c["transferStates"]:
            lines.append(f"  {s['state']:<20} {'(terminal) ' if s['terminal'] else ''}{s['description']}")
        lines += ["", "TRANSITIONS"]
        for t in c["transferTransitions"]:
            lines.append(f"  {t['from']:<20} -> {t['to']:<20} on {t['trigger']:<18} {t['notes']}")
        lines += ["", "RULE FLAGS"]
        lines += [f"  {k:<42} {v}" for k, v in c["ruleFlags"].items()]
        lines += ["", "ROLE PERMISSIONS", json.dumps(c["rolePermissions"], indent=2)]
        lines += ["", "TASK AND UPDATE INTERRUPTION", json.dumps(c["taskInterruption"], indent=2)]
        lines += ["", "PERMANENT UNAVAILABILITY CAUSES", "  " + ", ".join(c["permanentUnavailabilityCauses"])]
        lines += ["", "OPEN ITEMS"] + [f"  {k}: {v}" for k, v in c["openItems"].items()]
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", "\n".join(lines))
        self.text.configure(state=tk.DISABLED)


def network_editors_dirty(app: Any) -> list[str]:
    return [e.title for e in getattr(app, "network_editors", []) if e.dirty]


def install_network_editor(app: Any) -> None:
    tiers_tab = ttk.Frame(app.notebook, padding=10)
    hw_tab = ttk.Frame(app.notebook, padding=10)
    rules_tab = ttk.Frame(app.notebook, padding=10)
    app.notebook.add(tiers_tab, text="Network Tiers — Editor")
    app.notebook.add(hw_tab, text="Modems and Routers — Editor")
    app.notebook.add(rules_tab, text="Transfer and Interruption Rules — Reference")
    app.network_tiers_tab, app.network_hardware_tab, app.transfer_rules_tab = tiers_tab, hw_tab, rules_tab

    tiers = NetworkTableEditor(app, tiers_tab, "network_tiers", "Network Tiers")
    hw = NetworkTableEditor(app, hw_tab, "network_hardware_models", "Modems and Routers")
    app.network_editors = [tiers, hw]
    app.transfer_rules_view = TransferRulesView(app, rules_tab)
    fam_tab = ttk.Frame(app.notebook, padding=10)
    mod_tab = ttk.Frame(app.notebook, padding=10)
    app.notebook.add(fam_tab, text="Equipment Families — Editor")
    app.notebook.add(mod_tab, text="Equipment Models — Editor")
    app.equipment_families_tab, app.equipment_models_tab = fam_tab, mod_tab
    app.network_editors += [
        NetworkTableEditor(app, fam_tab, "equipment_families", "Equipment Families"),
        NetworkTableEditor(app, mod_tab, "equipment_models", "Equipment Models"),
    ]
    care_tab = ttk.Frame(app.notebook, padding=10)
    app.notebook.add(care_tab, text="Care Services — Editor")
    app.care_services_tab = care_tab
    app.network_editors.append(NetworkTableEditor(app, care_tab, "care_services", "Care Services"))
    for table, title in (("care_location_features", "Care Locations"),
                         ("care_service_locations", "Care Service Locations"),
                         ("condition_stats", "Condition Stats"),
                         ("condition_bands", "Condition Bands"),
                         ("personnel_traits", "Traits"),
                         ("training_catalog", "Training"),
                         ("personal_care_actions", "Personal Care"),
                         ("personal_care_features", "Personal Care Places"),
                         ("personal_care_locations", "Personal Care Place Links"),
                         ("personal_care_trainings", "Personal Care Trainings"),
                         ("personal_care_place_types", "Place Types"),
                         ("personal_care_place_type_features", "Place Type Features"),
                         ("recreation_activities", "Recreation Activities"),
                         ("personal_care_during_care", "Personal Care During Care"),
                         ("time_settings", "Time Settings"),
                         ("effect_levels", "Effect Levels"),
                         ("book_titles", "Book Titles"),
                         ("sobriety_stages", "Sobriety Stages"),
                         ("sobriety_settings", "Sobriety Settings"),
                         ("sobriety_shift_rules", "Sobriety Shift Rules"),
                         ("territories", "Territories"),
                         ("territory_settings", "Territory Settings"),
                         ("mission_tiers", "Mission Tiers"),
                         ("map_formats", "Map Formats"),
                         ("maps", "Maps"),
                         ("weapons", "Weapons"),
                         ("hostiles", "Hostiles"),
                         ("upgrades", "Upgrades"),
                         ("plot_milestones", "Plot Milestones"),
                         ("plot_items", "Plot Items"),
                         ("mission_tier_requirements", "Mission Tier Requirements")):
        extra_tab = ttk.Frame(app.notebook, padding=10)
        app.notebook.add(extra_tab, text=f"{title} — Editor")
        app.network_editors.append(NetworkTableEditor(app, extra_tab, table, title))
    for e in app.network_editors:
        e.load()

    def on_close() -> None:
        dirty = network_editors_dirty(app)
        if dirty and not messagebox.askyesno(
                "DoDA Content Workbench",
                "Unsaved network changes in: " + ", ".join(dirty) + "\n\nClose anyway and discard them?"):
            return
        app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)

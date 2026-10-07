from __future__ import annotations

import json
import re
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import doda_metric_bundle_service as service
from doda_content_workbench import TABLE_SPECS
from doda_metric_tiers_editor import MetricTiersEditor


ID_PATTERN = re.compile(r"[A-Z][A-Z0-9_]*")
METRIC_FIELDS = tuple(TABLE_SPECS["metrics"]["required_columns"])
TIER_FIELDS = tuple(
    field for field in TABLE_SPECS["metric_tiers"]["required_columns"]
    if field != "metric_id"
)
LABELS = {
    "metric_id": "Metric ID",
    "display_name": "Display Name",
    "description": "Description",
    "owner_system": "Owner System",
    "internal_min": "Internal Minimum",
    "internal_max": "Internal Maximum",
    "default_value": "Default Value",
    "polarity": "Polarity",
    "ui_display_mode": "UI Display Mode",
    "update_notes": "Update Notes",
    "active": "Active",
    "tier_id": "Tier ID",
    "min_inclusive": "Minimum (inclusive)",
    "max_inclusive": "Maximum (inclusive)",
    "display_label": "Display Label",
    "short_status": "Short Status",
    "ui_color": "UI Color",
    "flavor_text_id": "Flavor Text",
    "sort_order": "Sort Order",
}


class MetricBundleEditor(tk.Toplevel):
    def __init__(self, app):
        self.app = app
        self.root_path = Path(app.project_root).resolve()
        self.snapshot = service.read_snapshot(self.root_path)
        super().__init__(app)

        self.title("Metric and Tiers - Coordinated Editor")
        self.geometry("1100x760")
        self.minsize(1000, 700)
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.editing_id = None
        self.tiers = []
        self.tier_index = None
        self.metric_vars = {}
        self.metric_widgets = {}
        self.tier_vars = {}
        self.tier_widgets = {}
        self.load_id = tk.StringVar(master=self)
        self.status = tk.StringVar(master=self)
        self.build()
        self.set_new_metric()
        self.grab_set()

    def enum_choices(self, group):
        rows = [
            row for row in self.snapshot["rows"]["enum_catalog.csv"]
            if row["enum_group"] == group
            and row["active"].upper() == "TRUE"
        ]
        return [
            row["enum_value"]
            for row in sorted(
                rows, key=lambda row: (int(row["sort_order"]), row["enum_value"])
            )
        ]

    def build(self):
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(
            outer, text=str(self.root_path), wraplength=1000
        ).pack(anchor="w")

        toolbar = ttk.Frame(outer)
        toolbar.pack(fill="x", pady=8)
        values = sorted(
            row["metric_id"]
            for row in self.snapshot["rows"]["metrics.csv"]
        )
        ttk.Combobox(
            toolbar, textvariable=self.load_id,
            values=values, state="readonly", width=28
        ).pack(side="left")
        ttk.Button(
            toolbar, text="Load Metric", command=self.load_metric
        ).pack(side="left", padx=6)
        ttk.Button(
            toolbar, text="New Metric", command=self.new_metric
        ).pack(side="left")

        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True)
        metric_tab = ttk.Frame(notebook, padding=10)
        tier_tab = ttk.Frame(notebook, padding=10)
        notebook.add(metric_tab, text="Metric")
        notebook.add(tier_tab, text="Staged Tiers")

        self.build_form(
            metric_tab, METRIC_FIELDS,
            self.metric_vars, self.metric_widgets, metric=True
        )

        left = ttk.Frame(tier_tab)
        right = ttk.Frame(tier_tab)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(
            left, columns=("id", "min", "max", "label"),
            show="headings", selectmode="browse"
        )
        for field, title in (
            ("id", "Tier ID"), ("min", "Min"),
            ("max", "Max"), ("label", "Label")
        ):
            self.tree.heading(field, text=title)
            self.tree.column(field, width=100, minwidth=50)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.select_tier)

        self.build_form(
            right, TIER_FIELDS, self.tier_vars, self.tier_widgets
        )
        tier_buttons = ttk.Frame(right)
        tier_buttons.grid(
            row=len(TIER_FIELDS), column=0, columnspan=2,
            sticky="ew", pady=8
        )
        for label, command in (
            ("New Tier", self.new_tier),
            ("Apply Tier to Draft", self.apply_tier),
            ("Remove Staged Tier", self.remove_tier),
        ):
            ttk.Button(
                tier_buttons, text=label, command=command
            ).pack(fill="x", pady=2)

        ttk.Label(
            outer,
            text=(
                "Apply each tier edit to the draft before validation or saving. "
                "Draft changes do not alter CSVs. Saving replaces metrics.csv "
                "and metric_tiers.csv together through the coordinated service. "
                "No export is performed."
            ),
            wraplength=1000,
        ).pack(anchor="w", pady=8)

        bottom = ttk.Frame(outer)
        bottom.pack(fill="x")
        for label, command in (
            ("Validate Draft", self.validate_draft),
            ("Save Metric and Tiers", self.save_bundle),
            ("Cancel / Close", self.close),
        ):
            ttk.Button(
                bottom, text=label, command=command
            ).pack(side="left", padx=(0, 8))
        ttk.Label(
            outer, textvariable=self.status, wraplength=1000
        ).pack(anchor="w", pady=(8, 0))

    def build_form(self, parent, fields, variables, widgets, metric=False):
        parent.columnconfigure(1, weight=1)
        for index, field in enumerate(fields):
            ttk.Label(parent, text=LABELS[field] + ":").grid(
                row=index, column=0, sticky="nw", padx=(0, 8), pady=3
            )
            var = tk.StringVar(master=self)
            variables[field] = var
            if field == "active":
                widget = ttk.Checkbutton(
                    parent, variable=var, onvalue="TRUE", offvalue="FALSE"
                )
            elif field in {"polarity", "ui_display_mode", "flavor_text_id"}:
                if field == "flavor_text_id":
                    values = sorted(
                        row["flavor_text_id"]
                        for row in self.snapshot["rows"]["flavor_text.csv"]
                    )
                else:
                    group = (
                        "METRIC_POLARITY" if field == "polarity"
                        else "METRIC_DISPLAY_MODE"
                    )
                    values = self.enum_choices(group)
                widget = ttk.Combobox(
                    parent, textvariable=var,
                    values=values, state="readonly"
                )
            elif field in {"description", "update_notes", "short_status"}:
                widget = tk.Text(parent, height=2, wrap="word")
            else:
                widget = ttk.Entry(parent, textvariable=var)
            widget.grid(row=index, column=1, sticky="ew", pady=3)
            widgets[field] = widget

    @staticmethod
    def get_form(variables, widgets):
        values = {}
        for field, var in variables.items():
            widget = widgets[field]
            values[field] = (
                widget.get("1.0", "end-1c")
                if isinstance(widget, tk.Text) else var.get()
            )
        return values

    @staticmethod
    def set_form(values, variables, widgets):
        for field, var in variables.items():
            value = values.get(field, "")
            widget = widgets[field]
            if isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
                widget.insert("1.0", value)
            else:
                var.set(value)

    def state(self):
        return json.dumps({
            "metric": self.get_form(self.metric_vars, self.metric_widgets),
            "tiers": self.tiers,
            "tierForm": self.get_form(self.tier_vars, self.tier_widgets),
        }, sort_keys=True)

    def allow_discard(self):
        return self.state() == self.baseline or messagebox.askyesno(
            "Discard draft?",
            "Discard unsaved metric and tier draft changes?",
            parent=self, default=messagebox.NO,
        )

    def check_root(self):
        if Path(self.app.project_root).resolve() != self.root_path:
            raise service.BundleError(
                "The application project changed. Close and reopen this editor."
            )

    def set_new_metric(self):
        self.editing_id = None
        self.tiers = []
        self.metric_widgets["metric_id"].configure(state="normal")
        polarities = self.enum_choices("METRIC_POLARITY")
        modes = self.enum_choices("METRIC_DISPLAY_MODE")
        self.set_form({
            "owner_system": "NativeStrategicCore",
            "internal_min": "0", "internal_max": "1000",
            "default_value": "0", "active": "TRUE",
            "polarity": (
                "HIGHER_IS_BETTER" if "HIGHER_IS_BETTER" in polarities
                else polarities[0] if polarities else ""
            ),
            "ui_display_mode": (
                "TIERED_BAR" if "TIERED_BAR" in modes
                else modes[0] if modes else ""
            ),
        }, self.metric_vars, self.metric_widgets)
        self.draw_tiers()
        self.reset_tier()
        self.baseline = self.state()
        self.status.set("New metric draft. Stage complete tier coverage.")

    def new_metric(self):
        if self.allow_discard():
            self.set_new_metric()

    def load_metric(self):
        try:
            self.check_root()
            key = self.load_id.get()
            row = next(
                (row for row in self.snapshot["rows"]["metrics.csv"]
                 if row["metric_id"] == key), None
            )
            if row is None:
                raise ValueError("Choose an existing metric.")
            if not self.allow_discard():
                return
            self.editing_id = key
            self.metric_widgets["metric_id"].configure(state="normal")
            self.set_form(row, self.metric_vars, self.metric_widgets)
            self.metric_widgets["metric_id"].configure(state="disabled")
            self.tiers = [
                dict(row)
                for row in self.snapshot["rows"]["metric_tiers.csv"]
                if row["metric_id"] == key
            ]
            self.draw_tiers()
            self.reset_tier()
            self.baseline = self.state()
            self.status.set("Loaded " + key + " from the opening snapshot.")
        except (ValueError, service.BundleError) as error:
            messagebox.showerror("Metric and Tiers", str(error), parent=self)

    def reset_tier(self):
        self.tier_index = None
        self.tree.selection_remove(*self.tree.selection())
        self.tier_widgets["tier_id"].configure(state="normal")
        self.set_form(
            {"ui_color": "#8C939F", "sort_order": str(len(self.tiers) + 1)},
            self.tier_vars, self.tier_widgets
        )
        self.tier_baseline = self.get_form(self.tier_vars, self.tier_widgets)

    def tier_dirty(self):
        return (
            self.get_form(self.tier_vars, self.tier_widgets)
            != self.tier_baseline
        )

    def new_tier(self):
        if self.tier_dirty() and not messagebox.askyesno(
            "Discard tier form?",
            "Discard the unapplied tier form?",
            parent=self, default=messagebox.NO,
        ):
            return
        self.reset_tier()

    def draw_tiers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, row in enumerate(self.tiers):
            self.tree.insert(
                "", "end", iid=str(index),
                values=(
                    row["tier_id"], row["min_inclusive"],
                    row["max_inclusive"], row["display_label"]
                )
            )

    def select_tier(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        if index == self.tier_index:
            return
        if self.tier_dirty() and not messagebox.askyesno(
            "Discard tier form?",
            "Discard the unapplied tier form and select another tier?",
            parent=self, default=messagebox.NO,
        ):
            if self.tier_index is not None:
                self.tree.selection_set(str(self.tier_index))
            else:
                self.tree.selection_remove(*self.tree.selection())
            return
        self.tier_index = index
        self.set_form(
            self.tiers[index], self.tier_vars, self.tier_widgets
        )
        self.tier_widgets["tier_id"].configure(state="disabled")
        self.tier_baseline = self.get_form(self.tier_vars, self.tier_widgets)

    def apply_tier(self):
        try:
            row = {
                key: value.strip()
                for key, value in self.get_form(
                    self.tier_vars, self.tier_widgets
                ).items()
            }
            if not ID_PATTERN.fullmatch(row["tier_id"]):
                raise ValueError("Tier ID must use uppercase ID syntax.")
            for field in ("display_label", "short_status"):
                if not row[field]:
                    raise ValueError(LABELS[field] + " is required.")
            if int(row["min_inclusive"]) > int(row["max_inclusive"]):
                raise ValueError("Tier minimum cannot exceed its maximum.")
            if int(row["sort_order"]) < 1:
                raise ValueError("Tier Sort Order must be at least 1.")
            flavor_ids = {
                row["flavor_text_id"]
                for row in self.snapshot["rows"]["flavor_text.csv"]
            }
            if row["flavor_text_id"] not in flavor_ids:
                raise ValueError("Choose an existing Flavor Text.")
            row["ui_color"] = MetricTiersEditor.normalized_ui_color(
                row["ui_color"]
            )
            if any(
                item["tier_id"] == row["tier_id"] and index != self.tier_index
                for index, item in enumerate(self.tiers)
            ):
                raise ValueError("Tier ID already exists in this draft.")
            row["metric_id"] = self.metric_vars["metric_id"].get().strip()
            if self.tier_index is None:
                self.tiers.append(row)
            else:
                if row["tier_id"] != self.tiers[self.tier_index]["tier_id"]:
                    raise ValueError("Existing Tier ID cannot change.")
                self.tiers[self.tier_index] = row
            self.draw_tiers()
            self.reset_tier()
            self.status.set(
                "Tier applied to draft only. Complete coverage is checked "
                "by Validate Draft or Save."
            )
        except ValueError as error:
            messagebox.showerror("Tier draft", str(error), parent=self)

    def remove_tier(self):
        if self.tier_index is None:
            messagebox.showwarning(
                "Tier draft", "Select a staged tier first.", parent=self
            )
            return
        if messagebox.askyesno(
            "Remove staged tier?",
            "Remove this tier from the draft only?",
            parent=self, default=messagebox.NO,
        ):
            del self.tiers[self.tier_index]
            self.draw_tiers()
            self.reset_tier()
            self.status.set("Tier removed from draft only.")

    def candidate_rows(self):
        self.check_root()
        if self.tier_dirty():
            raise ValueError(
                "Apply the tier form to the draft, or discard it with New Tier, "
                "before validating or saving."
            )
        metric = {
            field: value.strip()
            for field, value in self.get_form(
                self.metric_vars, self.metric_widgets
            ).items()
        }
        key = metric["metric_id"]
        if not ID_PATTERN.fullmatch(key):
            raise ValueError("Metric ID must use uppercase ID syntax.")
        for field in ("display_name", "description", "owner_system"):
            if not metric[field]:
                raise ValueError(LABELS[field] + " is required.")
        minimum = int(metric["internal_min"])
        maximum = int(metric["internal_max"])
        default = int(metric["default_value"])
        if not minimum <= default <= maximum:
            raise ValueError("Default must be inside the inclusive metric range.")
        if metric["active"] not in {"TRUE", "FALSE"}:
            raise ValueError("Active must be TRUE or FALSE.")
        original_metrics = self.snapshot["rows"]["metrics.csv"]
        if self.editing_id is not None and key != self.editing_id:
            raise ValueError("Existing Metric ID cannot change.")
        if self.editing_id is None and any(
            row["metric_id"] == key for row in original_metrics
        ):
            raise ValueError("Metric ID already exists. Load it for editing.")
        if not self.tiers:
            raise ValueError("Stage at least one tier covering the full range.")
        metrics = [
            dict(row) for row in original_metrics if row["metric_id"] != key
        ] + [metric]
        tiers = [
            dict(row)
            for row in self.snapshot["rows"]["metric_tiers.csv"]
            if row["metric_id"] != key
        ] + [dict(row, metric_id=key) for row in self.tiers]
        return metrics, tiers

    def validate_draft(self):
        try:
            metrics, tiers = self.candidate_rows()
            files = service.source_files(self.root_path)
            raw = {name: path.read_bytes() for name, path in files.items()}
            if {
                name: service.sha256(data) for name, data in raw.items()
            } != self.snapshot["hashes"]:
                raise service.BundleError(
                    "Source changed since opening. Preserve your draft "
                    "elsewhere, then close and reopen this editor."
                )
            raw["metrics.csv"] = service.encode_table("metrics", metrics)
            raw["metric_tiers.csv"] = service.encode_table("metric_tiers", tiers)
            output = service.validate_candidate(self.root_path, raw)
            self.app.log(output)
            self.status.set("Draft validation passed. No source CSVs changed.")
            messagebox.showinfo(
                "Metric and Tiers",
                "Draft validation passed. No source CSVs changed.",
                parent=self,
            )
        except (ValueError, OSError, service.BundleError) as error:
            self.app.log(str(error))
            messagebox.showerror("Metric and Tiers", str(error), parent=self)

    def save_bundle(self):
        try:
            metrics, tiers = self.candidate_rows()
            if not messagebox.askyesno(
                "Save Metric and Tiers?",
                "Save metric " + self.metric_vars["metric_id"].get().strip()
                + " with " + str(len(self.tiers))
                + " staged tier(s)?\n\n"
                "Both CSVs will be backed up and replaced after full validation. "
                "No export will run.",
                parent=self, default=messagebox.NO,
            ):
                return
            result = service.commit_bundle(
                self.root_path, metrics, tiers, self.snapshot["hashes"]
            )
        except (ValueError, OSError, service.BundleError) as error:
            self.app.log(str(error))
            messagebox.showerror("Metric and Tiers", str(error), parent=self)
            return

        self.app.log(result["validationOutput"])
        self.app.log(
            "Metric bundle committed. Backups: "
            + result["transactionDirectory"]
        )
        try:
            self.app.refresh_all(False)
        except Exception as error:
            self.app.log("Bundle saved; GUI refresh raised: " + str(error))
        messagebox.showinfo(
            "Metric and Tiers",
            "Coordinated save completed.\n\nBackups and transaction record:\n"
            + result["transactionDirectory"]
            + "\n\nThe editor will close. Export separately when needed.",
            parent=self,
        )
        self.destroy()

    def close(self):
        if self.allow_discard():
            self.destroy()


def open_metric_bundle_editor(app):
    try:
        return MetricBundleEditor(app)
    except (ValueError, OSError, service.BundleError) as error:
        messagebox.showerror("Metric and Tiers", str(error), parent=app)
        return None
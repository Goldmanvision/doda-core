from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any
from uuid import uuid4

FIELDS = ("track_id", "display_name", "description", "sort_order", "active")
ID = re.compile(r"^[A-Z][A-Z0-9_]*$")
FILES = (
    "enum_catalog.csv",
    "department_tracks.csv",
    "metrics.csv",
    "metric_tiers.csv",
    "facilities.csv",
    "flavor_text.csv",
    "qualification_catalog.csv",
    "capabilities.csv",
    "facility_capabilities.csv",
    "capability_staffing_rules.csv",
    "facility_capability_staffing_overrides.csv",
    "task_templates.csv",
)
FILES = tuple(FILES) + ("equipment_families.csv",)

class TrackEditor:
    def __init__(self, app: Any) -> None:
        self.app, self.editing = app, None
        self.id = tk.StringVar(); self.name = tk.StringVar(); self.sort = tk.StringVar(); self.active = tk.BooleanVar(value=True)
        self.build()

    def path(self) -> Path: return self.app.source_directory / "department_tracks.csv"
    def backups(self) -> Path: return self.app.project_root / "data_authoring" / "backups" / "department_tracks"
    def rows(self) -> list[dict[str, str]]: return [dict(x) for x in self.app.tables.get("department_tracks", [])]

    def build(self) -> None:
        for child in self.app.tracks_tab.winfo_children(): child.destroy()
        tab = self.app.tracks_tab; tab.columnconfigure(0, weight=3); tab.columnconfigure(1, weight=2); tab.rowconfigure(0, weight=1)
        left = ttk.LabelFrame(tab, text="Department Tracks", padding=8); right = ttk.LabelFrame(tab, text="Track Editor", padding=10)
        left.grid(row=0, column=0, sticky=tk.NSEW, padx=(0,6)); right.grid(row=0, column=1, sticky=tk.NSEW)
        left.columnconfigure(0, weight=1); left.rowconfigure(0, weight=1); right.columnconfigure(1, weight=1)
        self.tree = ttk.Treeview(left, columns=("id","name","sort","active"), show="headings", selectmode="browse")
        for key, label, width in (("id","Track ID",200),("name","Display Name",240),("sort","Sort",60),("active","Active",70)):
            self.tree.heading(key,text=label); self.tree.column(key,width=width,anchor=tk.W)
        bar=ttk.Scrollbar(left,orient=tk.VERTICAL,command=self.tree.yview); self.tree.configure(yscrollcommand=bar.set)
        self.tree.grid(row=0,column=0,sticky=tk.NSEW); bar.grid(row=0,column=1,sticky=tk.NS); self.tree.bind("<<TreeviewSelect>>",self.select)
        def label(text,row): ttk.Label(right,text=text,style="Section.TLabel").grid(row=row,column=0,sticky=tk.NW,padx=(0,8),pady=(0,8))
        label("Track ID:",0); self.id_entry=ttk.Entry(right,textvariable=self.id); self.id_entry.grid(row=0,column=1,sticky=tk.EW,pady=(0,8))
        ttk.Label(right,text="Uppercase ID; immutable after creation.",foreground="#9da7b3").grid(row=1,column=1,sticky=tk.W,pady=(0,10))
        label("Display Name:",2); ttk.Entry(right,textvariable=self.name).grid(row=2,column=1,sticky=tk.EW,pady=(0,8))
        label("Description:",3); self.desc=tk.Text(right,height=8,wrap=tk.WORD,background="#0d1117",foreground="#e6edf3",insertbackground="#e6edf3",highlightbackground="#3b4754",highlightcolor="#58a6ff")
        self.desc.grid(row=3,column=1,sticky=tk.NSEW,pady=(0,8))
        label("Sort Order:",4); ttk.Entry(right,textvariable=self.sort,width=12).grid(row=4,column=1,sticky=tk.W,pady=(0,8))
        label("Active:",5); ttk.Checkbutton(right,text="This track is active",variable=self.active).grid(row=5,column=1,sticky=tk.W,pady=(0,8))
        buttons=ttk.Frame(right); buttons.grid(row=6,column=0,columnspan=2,sticky=tk.EW,pady=(8,0))
        ttk.Button(buttons,text="Add Track",command=self.new).pack(side=tk.LEFT)
        ttk.Button(buttons,text="Save Track",command=self.save).pack(side=tk.LEFT,padx=6)
        ttk.Button(buttons,text="Remove Track",command=self.remove).pack(side=tk.LEFT,padx=6)
        ttk.Button(buttons,text="Revert Form",command=self.revert).pack(side=tk.LEFT,padx=6)
        ttk.Button(buttons,text="Open Backups",command=self.open_backups).pack(side=tk.RIGHT)
        ttk.Label(right,text="Save validates an isolated candidate, backs up the real CSV, then atomically replaces it.",foreground="#9da7b3",wraplength=380).grid(row=7,column=0,columnspan=2,sticky=tk.EW,pady=(12,0))
        self.new()

    def update(self) -> None:
        selected=self.editing
        for item in self.tree.get_children(): self.tree.delete(item)
        for row in self.rows():
            key=row.get("track_id",""); self.tree.insert("",tk.END,iid=key,values=(key,row.get("display_name",""),row.get("sort_order",""),row.get("active","")))
        if selected and self.tree.exists(selected): self.tree.selection_set(selected)

    def new(self) -> None:
        self.editing=None; self.id_entry.configure(state=tk.NORMAL); self.id.set(""); self.name.set(""); self.active.set(True); self.desc.delete("1.0",tk.END)
        orders=[]
        for row in self.rows():
            try: orders.append(int(row.get("sort_order","")))
            except ValueError: pass
        self.sort.set(str(max(orders,default=0)+1)); self.id_entry.focus_set()

    def select(self,_:Any=None) -> None:
        chosen=self.tree.selection()
        if not chosen:return
        row=next((x for x in self.rows() if x.get("track_id")==chosen[0]),None)
        if not row:return
        self.editing=row["track_id"]; self.id_entry.configure(state=tk.NORMAL); self.id.set(row["track_id"]); self.id_entry.configure(state=tk.DISABLED)
        self.name.set(row.get("display_name","")); self.sort.set(row.get("sort_order","")); self.active.set(row.get("active","").upper()=="TRUE")
        self.desc.delete("1.0",tk.END); self.desc.insert("1.0",row.get("description",""))

    def revert(self) -> None:
        if self.editing and self.tree.exists(self.editing): self.tree.selection_set(self.editing); self.select()
        else:self.new()

    def record(self) -> dict[str,str] | None:
        r={"track_id":self.id.get().strip(),"display_name":self.name.get().strip(),"description":self.desc.get("1.0",tk.END).strip(),"sort_order":self.sort.get().strip(),"active":"TRUE" if self.active.get() else "FALSE"}
        errors=[]
        if not ID.fullmatch(r["track_id"]):errors.append("Track ID must begin with an uppercase letter and use only uppercase letters, digits, or underscores.")
        if not r["display_name"]:errors.append("Display Name is required.")
        if not r["description"]:errors.append("Description is required.")
        try:
            if int(r["sort_order"])<1:errors.append("Sort Order must be at least 1.")
        except ValueError:errors.append("Sort Order must be a whole number.")
        if errors:messagebox.showerror("DoDA Content Workbench","Correct before saving:\n\n- "+"\n- ".join(errors));return None
        return r

    def write(self,path:Path,rows:list[dict[str,str]])->None:
        with path.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator="\n");w.writeheader()
            for row in rows:w.writerow({x:row.get(x,"") for x in FIELDS})

    def candidate_valid(self,candidate:Path)->tuple[bool,str]:
        with tempfile.TemporaryDirectory(prefix="doda-track-") as temp:
            root=Path(temp);dst=root/"data_authoring"/"source";dst.mkdir(parents=True)
            for file in FILES:shutil.copy2(candidate if file=="department_tracks.csv" else self.app.source_directory/file,dst/file)
            done=subprocess.run([sys.executable,str(self.app.validator_path),"--root",str(root),"validate"],cwd=root,text=True,encoding="utf-8",errors="replace",capture_output=True)
            return done.returncode==0,(done.stdout+"\n"+done.stderr).strip()

    def save(self)->None:
        r=self.record()
        if not r:return
        rows=self.rows()
        if self.editing:
            if r["track_id"]!=self.editing:messagebox.showerror("DoDA Content Workbench","Track ID cannot change after creation.");return
            rows=[r if x.get("track_id")==self.editing else x for x in rows];action="updated"
        else:
            if any(x.get("track_id")==r["track_id"] for x in rows):messagebox.showerror("DoDA Content Workbench","Track ID already exists.");return
            rows.append(r);action="added"
        rows.sort(key=lambda x:(int(x["sort_order"]),x["track_id"]));tmp=self.app.source_directory/f".tracks-{uuid4().hex}.tmp.csv"
        try:
            self.write(tmp,rows);ok,output=self.candidate_valid(tmp)
            self.app.log("Candidate validation output:");[self.app.log(" "+line) for line in output.splitlines()]
            if not ok:messagebox.showerror("DoDA Content Workbench","Candidate validation failed; source CSV was unchanged. See Activity Log.");return
            folder=self.backups();folder.mkdir(parents=True,exist_ok=True);backup=folder/f"department_tracks_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.csv"
            shutil.copy2(self.path(),backup);os.replace(tmp,self.path());self.editing=r["track_id"];self.app.refresh_all(False)
            done=subprocess.run([sys.executable,str(self.app.validator_path),"--root",str(self.app.project_root),"validate"],cwd=self.app.project_root,text=True,encoding="utf-8",errors="replace",capture_output=True)
            [self.app.log(" "+line) for line in (done.stdout+"\n"+done.stderr).strip().splitlines()]
            self.app.refresh_all(False)
            if done.returncode==0:messagebox.showinfo("DoDA Content Workbench",f"Track '{r['track_id']}' {action}.\n\nBackup created:\n{backup}\n\nValidation passed.")
            else:messagebox.showwarning("DoDA Content Workbench",f"Track {action}, but post-save validation failed.\nBackup: {backup}")
        finally:
            if tmp.exists():tmp.unlink()

    def remove(self)->None:
        """Remove the selected track only after explicit confirmation and validation."""

        if not self.editing:
            messagebox.showwarning(
                "DoDA Content Workbench",
                "Select an existing Department Track before using Remove Track.",
            )
            return

        track_id = self.editing

        confirmed = messagebox.askyesno(
            "Remove Department Track?",
            (
                f"ARE YOU SURE you want to remove '{track_id}'?\n\n"
                "This will remove the track from department_tracks.csv.\n\n"
                "A timestamped backup will be created first. The removal will "
                "not occur if full candidate validation detects references or "
                "other source-data errors."
            ),
            icon="warning",
            default=messagebox.NO,
        )

        if not confirmed:
            self.app.log(f"Remove Track cancelled for '{track_id}'.")
            return

        remaining_rows = [
            row for row in self.rows()
            if row.get("track_id") != track_id
        ]

        temporary = self.app.source_directory / (
            f".tracks-remove-{uuid4().hex}.tmp.csv"
        )

        self.app.config(cursor="watch")
        self.app.update_idletasks()

        try:
            self.write(temporary, remaining_rows)

            valid, output = self.candidate_valid(temporary)

            self.app.log(
                f"Candidate validation output for removal of '{track_id}':"
            )

            for line in output.splitlines():
                self.app.log(" " + line)

            if not valid:
                messagebox.showerror(
                    "DoDA Content Workbench",
                    (
                        f"Removal of '{track_id}' was blocked because candidate "
                        "validation failed.\n\n"
                        "The real source CSV was not changed.\n\n"
                        "Review Activity Log for complete details."
                    ),
                )
                return

            backup_folder = self.backups()
            backup_folder.mkdir(parents=True, exist_ok=True)

            backup = backup_folder / (
                "department_tracks_before_remove_"
                + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                + ".csv"
            )

            shutil.copy2(self.path(), backup)

            os.replace(temporary, self.path())

            self.app.log(f"Created pre-removal backup: {backup}")
            self.app.log(f"Removed Department Track: {track_id}")

            self.editing = None
            self.app.refresh_all(False)
            self.new()

            command = [
                sys.executable,
                str(self.app.validator_path),
                "--root",
                str(self.app.project_root),
                "validate",
            ]

            completed = subprocess.run(
                command,
                cwd=self.app.project_root,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.app.log(
                f"Post-removal validation exit code: {completed.returncode}"
            )

            for line in (
                completed.stdout + "\n" + completed.stderr
            ).strip().splitlines():
                self.app.log(" " + line)

            self.app.refresh_all(False)

            if completed.returncode == 0:
                messagebox.showinfo(
                    "DoDA Content Workbench",
                    (
                        f"Track '{track_id}' was removed successfully.\n\n"
                        f"Backup created:\n{backup}\n\n"
                        "Project validation passed."
                    ),
                )
            else:
                messagebox.showwarning(
                    "DoDA Content Workbench",
                    (
                        f"Track '{track_id}' was removed, but post-removal "
                        "validation failed unexpectedly.\n\n"
                        f"Backup:\n{backup}\n\n"
                        "Review Activity Log before making additional changes."
                    ),
                )

        except (OSError, ValueError) as error:
            self.app.log(f"TRACK REMOVE ERROR: {error}")

            messagebox.showerror(
                "DoDA Content Workbench",
                f"Unable to remove Department Track.\n\n{error}",
            )

        finally:
            if temporary.exists():
                temporary.unlink()

            self.app.config(cursor="")
            self.app.update_idletasks()
    def open_backups(self)->None:
        self.backups().mkdir(parents=True,exist_ok=True);self.app.open_folder(self.backups())

def install_track_editor(app:Any)->None:
    editor=TrackEditor(app);app.track_editor=editor;app.update_tracks=editor.update

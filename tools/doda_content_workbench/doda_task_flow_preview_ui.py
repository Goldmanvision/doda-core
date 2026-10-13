"""Workbench-owned preview of saved task-flow source; read only."""
import tkinter as tk
from tkinter import messagebox, ttk
import doda_task_flow_preview as preview


def initial_index(previews, template_id):
    if not template_id:
        return 0 if previews else -1
    for index, item in enumerate(previews):
        if item["template"]["task_template_id"] == template_id:
            return index
    raise ValueError("Template is not in saved source: " + template_id)


def open_task_flow_preview(owner, template_id=None):
    try:
        previews, warnings = preview.load_previews(owner.project_root)
        index = initial_index(previews, template_id)
    except Exception as error:
        owner.log("Task flow preview blocked: " + str(error))
        messagebox.showerror("Task Resource Flow Preview", str(error), parent=owner)
        return None

    previous = getattr(owner, "task_flow_preview_window", None)
    if previous is not None and previous.winfo_exists():
        previous.destroy()

    window = tk.Toplevel(owner)
    owner.task_flow_preview_window = window
    window.title("DoDA - Task Resource Flow Preview (Saved Source, Read Only)")
    window.geometry("1100x740")
    window.columnconfigure(0, weight=1)
    window.rowconfigure(2, weight=1)

    ttk.Label(
        window,
        text="SAVED SOURCE ONLY - unsaved drafts are not included. Reopen to refresh.",
    ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 0))

    selector = ttk.Combobox(
        window, state="readonly",
        values=[p["template"]["task_template_id"] for p in previews],
    )
    selector.grid(row=1, column=0, sticky="ew", padx=12, pady=12)

    frame = ttk.Frame(window)
    frame.grid(row=2, column=0, sticky="nsew", padx=12)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    text = tk.Text(
        frame, wrap="word", font=("Consolas", 11),
        background="#0d1117", foreground="#e6edf3",
    )
    text.grid(row=0, column=0, sticky="nsew")
    scroll = ttk.Scrollbar(frame, command=text.yview)
    scroll.grid(row=0, column=1, sticky="ns")
    text.configure(yscrollcommand=scroll.set)

    def refresh(event=None):
        selected = selector.current()
        if selected < 0:
            return
        text.configure(state="normal")
        text.delete("1.0", "end")
        text.insert("1.0", preview.render_preview(previews[selected]))
        text.configure(state="disabled")

    selector.bind("<<ComboboxSelected>>", refresh)
    ttk.Label(
        window,
        text=f"Validated saved snapshot: {len(previews)} templates; "
             f"{len(warnings)} warnings. No execution or balance writes.",
    ).grid(row=3, column=0, sticky="w", padx=12, pady=12)

    if index >= 0:
        selector.current(index)
        refresh()
    owner.log("Opened saved-source Task Resource Flow Preview" +
              (": " + template_id if template_id else "."))
    return window

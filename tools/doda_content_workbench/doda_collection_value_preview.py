"""Read-only model-value preview; no saving, inventory or evidence credits."""
import re
import tkinter as tk
from tkinter import ttk, messagebox
import doda_collection_model_rules as models


def calculate_preview(base_value, multiplier, piece_count):
    if isinstance(piece_count, (bool, float)) or not re.fullmatch(
        r"[0-9]+", str(piece_count).strip()
    ):
        raise ValueError("Piece count must be a positive whole number")
    count = int(str(piece_count).strip())
    if count < 1:
        raise ValueError("Piece count must be a positive whole number")
    base = models.decimal_value(base_value, False)
    factor = models.decimal_value(multiplier)
    each = models.piece_value(base_value, multiplier)
    return {
        "baseValuePerPiece": format(base, "f"),
        "multiplier": format(factor, "f"),
        "pieceCount": count,
        "valuePerPiece": each,
        "totalValue": each * count,
    }


def open_collection_value_preview(parent, variables):
    name = variables["display_name"].get().strip()
    name = name or variables["model_id"].get().strip() or "Current model"
    multiplier = variables["evidence_value_multiplier"].get().strip()
    try:
        models.decimal_value(multiplier)
    except ValueError as error:
        messagebox.showwarning(
            "Collection Value Preview",
            "Enter a positive model multiplier first.\n\n" + str(error),
            parent=parent,
        )
        return None

    window = tk.Toplevel(parent)
    window.title("Collection Value Preview")
    window.geometry("620x390")
    window.minsize(560, 360)
    window.transient(parent.winfo_toplevel())
    frame = ttk.Frame(window, padding=14)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text=name, style="Section.TLabel").grid(
        row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8)
    )
    ttk.Label(
        frame,
        text="Current form snapshot; does not Apply or Save.\n"
             "Value arithmetic only; eligibility and inventory are not simulated.",
        wraplength=540,
    ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 12))

    base = tk.StringVar(master=window, value="1.25")
    count = tk.StringVar(master=window, value="1")
    result = tk.StringVar(master=window)
    ttk.Label(frame, text="Model multiplier:").grid(row=2, column=0, sticky=tk.W)
    ttk.Label(frame, text=multiplier + "x").grid(row=2, column=1, sticky=tk.W)

    ttk.Label(frame, text="Base value per piece:").grid(
        row=3, column=0, sticky=tk.W, pady=5
    )
    base_entry = ttk.Entry(frame, textvariable=base)
    base_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
    ttk.Label(frame, text="Piece count:").grid(
        row=4, column=0, sticky=tk.W, pady=5
    )
    count_entry = ttk.Entry(frame, textvariable=count)
    count_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)

    def refresh():
        try:
            data = calculate_preview(base.get(), multiplier, count.get())
        except ValueError as error:
            result.set("Invalid input; no preview value calculated.")
            messagebox.showwarning(
                "Collection Value Preview", str(error), parent=window
            )
            return
        result.set(
            f"Rounded value per piece: {data['valuePerPiece']}\n"
            f"Piece count: {data['pieceCount']} (unchanged)\n"
            f"Total value: {data['totalValue']}\n\n"
            "Rounding: HALF UP, separately for every piece."
        )

    ttk.Button(frame, text="Calculate Preview", command=refresh).grid(
        row=5, column=0, columnspan=2, sticky=tk.EW, pady=(8, 10)
    )
    ttk.Label(frame, textvariable=result, wraplength=540).grid(
        row=6, column=0, columnspan=2, sticky=tk.W
    )
    ttk.Button(frame, text="Close", command=window.destroy).grid(
        row=7, column=0, columnspan=2, sticky=tk.E, pady=(12, 0)
    )
    for entry in (base_entry, count_entry):
        entry.bind("<Return>", lambda event: refresh())
    window.bind("<Escape>", lambda event: window.destroy())
    refresh()
    base_entry.focus_set()
    return window

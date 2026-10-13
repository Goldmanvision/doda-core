"""Read-only evidence range bounds; saved models, no sampling or credits."""
import tkinter as tk
from tkinter import ttk, messagebox
import doda_network_rules as net
import doda_evidence_instance_rules as evidence
import doda_collection_model_rules as models
from doda_collection_value_preview import calculate_preview


def compatible_models(resource_id, items):
    if resource_id not in evidence.EVIDENCE_RESOURCES:
        raise ValueError("Select an authored evidence category first")
    result = []
    for item in items:
        if resource_id not in item["evidenceTypes"]:
            continue
        factor = item["evidenceValueMultiplier"]
        if factor is None:
            continue
        models.decimal_value(factor)
        result.append(item)
    return result


def calculate_range(base_min, base_max, resource_id, model, piece_count):
    low = evidence.whole_value(base_min)
    high = evidence.whole_value(base_max)
    if low > high:
        raise ValueError("Minimum base value must not exceed maximum")
    if resource_id not in evidence.EVIDENCE_RESOURCES:
        raise ValueError("Unknown evidence category")
    if resource_id not in model["evidenceTypes"]:
        raise ValueError("Collection model does not collect this evidence category")
    factor = model["evidenceValueMultiplier"]
    if factor is None:
        raise ValueError("Collection model multiplier is unconfigured")
    minimum = calculate_preview(low, factor, piece_count)
    maximum = calculate_preview(high, factor, piece_count)
    return {
        "baseValueMin": low, "baseValueMax": high,
        "evidenceResourceId": resource_id, "modelId": model["modelId"],
        "modelActive": model["active"], "multiplier": minimum["multiplier"],
        "pieceCount": minimum["pieceCount"],
        "valuePerPieceMin": minimum["valuePerPiece"],
        "valuePerPieceMax": maximum["valuePerPiece"],
        "totalValueMin": minimum["totalValue"],
        "totalValueMax": maximum["totalValue"],
    }


def load_saved_models(root):
    result = net.Result()
    data = models.validate_models(root, result)
    if not result.valid:
        raise ValueError("Saved collection catalog is invalid:\n" +
                         "\n".join(result.errors[:8]))
    return data["models"]


def model_label(item):
    status = "ACTIVE" if item["active"] else "DRAFT / INACTIVE"
    return f"{item['displayName']} [{item['modelId']}] - {status}"


def open_evidence_range_preview(parent, project_root, variables):
    snapshot = {key: value.get().strip() for key, value in variables.items()}
    rid = snapshot["evidence_resource_id"]
    try:
        low = evidence.whole_value(snapshot["base_value_min"])
        high = evidence.whole_value(snapshot["base_value_max"])
        if low > high:
            raise ValueError("Minimum base value must not exceed maximum")
        choices = compatible_models(rid, load_saved_models(project_root))
        if not choices:
            raise ValueError(
                "No saved collection model has this evidence category and a "
                "configured multiplier.\n\nSave intentional collection-model "
                "changes separately before reopening this preview."
            )
    except (ValueError, OSError) as error:
        messagebox.showwarning("Evidence Collection Range", str(error), parent=parent)
        return None

    window = tk.Toplevel(parent)
    window.title("Evidence Collection Range")
    window.geometry("760x540")
    window.minsize(700, 500)
    window.transient(parent.winfo_toplevel())
    frame = ttk.Frame(window, padding=14)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.columnconfigure(0, weight=1)
    name = snapshot["display_name"] or snapshot["evidence_instance_id"] or "Current definition"
    ttk.Label(frame, text=name, style="Section.TLabel").grid(
        row=0, column=0, sticky=tk.W, pady=(0, 8)
    )
    ttk.Label(
        frame,
        text=f"Category: {rid}\nBase value per piece: {low} to {high}\n\n"
             "Evidence: current form snapshot (including unapplied values).\n"
             "Models: saved catalog snapshot; unsaved model edits are excluded.\n"
             "Draft models are inspectable, not runtime-eligible equipment.",
        wraplength=690,
    ).grid(row=1, column=0, sticky=tk.W, pady=(0, 12))
    ttk.Label(frame, text="Compatible collection model:").grid(
        row=2, column=0, sticky=tk.W
    )
    labels = [model_label(item) for item in choices]
    selector = ttk.Combobox(frame, values=labels, state="readonly")
    selector.grid(row=3, column=0, sticky=tk.EW, pady=(4, 10))
    selector.current(0)
    count = tk.StringVar(master=window, value="1")
    ttk.Label(frame, text="Sample piece count:").grid(row=4, column=0, sticky=tk.W)
    entry = ttk.Entry(frame, textvariable=count)
    entry.grid(row=5, column=0, sticky=tk.EW, pady=(4, 8))
    output = tk.StringVar(master=window)

    def refresh():
        index = selector.current()
        try:
            if index < 0:
                raise ValueError("Select a collection model")
            item = choices[index]
            data = calculate_range(low, high, rid, item, count.get())
        except ValueError as error:
            output.set("Invalid input; no range calculated.")
            messagebox.showwarning("Evidence Collection Range", str(error), parent=window)
            return
        status = "ACTIVE" if data["modelActive"] else "DRAFT / INACTIVE"
        output.set(
            f"Model status: {status}     Multiplier: {data['multiplier']}x\n"
            f"Rounded value per piece: {data['valuePerPieceMin']} to "
            f"{data['valuePerPieceMax']}\n"
            f"Piece count: {data['pieceCount']} (unchanged)\n"
            f"Total value bounds: {data['totalValueMin']} to {data['totalValueMax']}\n\n"
            "HALF UP per piece, before totaling. Bounds only; no random rolls.\n"
            "No Apply, Save, inventory changes, evidence credits or processing."
        )

    ttk.Button(frame, text="Calculate Range", command=refresh).grid(
        row=6, column=0, sticky=tk.EW, pady=(0, 10)
    )
    ttk.Label(frame, textvariable=output, wraplength=690).grid(
        row=7, column=0, sticky=tk.W
    )
    ttk.Button(frame, text="Close", command=window.destroy).grid(
        row=8, column=0, sticky=tk.E, pady=(14, 0)
    )
    selector.bind("<<ComboboxSelected>>", lambda event: refresh())
    entry.bind("<Return>", lambda event: refresh())
    window.bind("<Escape>", lambda event: window.destroy())
    refresh()
    entry.focus_set()
    return window

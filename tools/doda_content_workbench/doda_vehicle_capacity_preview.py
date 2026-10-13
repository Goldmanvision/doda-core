"""Read-only single-vehicle capacity arithmetic; no allocation or task eligibility."""
import re


def positive_whole(raw, label):
    if type(raw) is int:
        value = raw
    elif isinstance(raw, str) and re.fullmatch(r"[0-9]+", raw.strip()):
        value = int(raw.strip())
    else:
        raise ValueError(label + " must be a positive whole number")
    if value < 1:
        raise ValueError(label + " must be a positive whole number")
    return value


def calculate_preview(max_team_members, team_members):
    capacity = positive_whole(max_team_members, "Vehicle capacity")
    team = positive_whole(team_members, "Team members")
    return {
        "maxTeamMembers": capacity,
        "teamMembers": team,
        "fitsSingleVehicle": team <= capacity,
        "unusedCapacity": max(0, capacity - team),
        "membersOverCapacity": max(0, team - capacity),
        "scope": "SINGLE_VEHICLE_CAPACITY_ARITHMETIC_ONLY",
        "taskEligibilityChecked": False,
        "inventoryChecked": False,
        "allocationImplemented": False,
        "runtimeImplemented": False,
    }


def open_vehicle_capacity_preview(parent, variables):
    import tkinter as tk
    from tkinter import ttk, messagebox

    capacity_raw = variables["max_team_members"].get().strip()
    try:
        capacity = positive_whole(capacity_raw, "Vehicle capacity")
    except ValueError as error:
        messagebox.showwarning("Vehicle Capacity Preview", str(error), parent=parent)
        return None

    name = variables["display_name"].get().strip()
    vid = variables["vehicle_type_id"].get().strip()
    state = variables["active"].get().strip()
    title = name or vid or "Current vehicle form"

    window = tk.Toplevel(parent)
    window.title("Single-Vehicle Capacity Preview")
    window.geometry("640x420")
    window.minsize(570, 380)
    window.transient(parent.winfo_toplevel())

    frame = ttk.Frame(window, padding=14)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text=title, style="Section.TLabel").grid(
        row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))
    ttk.Label(frame, text=(
        "Current form snapshot; does not Apply, Save or Export.\n"
        "Capacity arithmetic for one hypothetical vehicle, not task eligibility."
    ), wraplength=580).grid(
        row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 12))

    ttk.Label(frame, text="Vehicle definition").grid(
        row=2, column=0, sticky=tk.W)
    ttk.Label(frame, text=(vid or "Unsaved form") + " | active field: " + state).grid(
        row=2, column=1, sticky=tk.W)
    ttk.Label(frame, text="Maximum team members").grid(
        row=3, column=0, sticky=tk.W, pady=5)
    ttk.Label(frame, text=str(capacity)).grid(
        row=3, column=1, sticky=tk.W, pady=5)

    team = tk.StringVar(master=window, value="1")
    result = tk.StringVar(master=window)
    ttk.Label(frame, text="Hypothetical team members").grid(
        row=4, column=0, sticky=tk.W, pady=5)
    entry = ttk.Entry(frame, textvariable=team)
    entry.grid(row=4, column=1, sticky=tk.EW, pady=5)

    def refresh():
        try:
            data = calculate_preview(capacity, team.get())
        except ValueError as error:
            result.set("Invalid input; no capacity result calculated.")
            messagebox.showwarning("Vehicle Capacity Preview", str(error), parent=window)
            return

        if data["fitsSingleVehicle"]:
            result.set(
                "FITS the authored capacity of one vehicle.\n"
                + str(data["unusedCapacity"]) + " unused team-member capacity."
            )
        else:
            result.set(
                "EXCEEDS the authored capacity of one vehicle.\n"
                + str(data["membersOverCapacity"]) + " team member(s) over capacity."
            )

    ttk.Button(frame, text="Calculate Preview", command=refresh).grid(
        row=5, column=0, columnspan=2, sticky=tk.EW, pady=(8, 10))
    ttk.Label(frame, textvariable=result, wraplength=580).grid(
        row=6, column=0, columnspan=2, sticky=tk.W)
    ttk.Label(frame, text=(
        "Does not check task staffing, prerequisites, active status, drivers or owned vehicles. "
        "No multi-vehicle policy or allocation is inferred."
    ), wraplength=580).grid(
        row=7, column=0, columnspan=2, sticky=tk.W, pady=(12, 0))
    ttk.Button(frame, text="Close", command=window.destroy).grid(
        row=8, column=0, columnspan=2, sticky=tk.E, pady=(12, 0))

    entry.bind("<Return>", lambda event: refresh())
    window.bind("<Escape>", lambda event: window.destroy())
    refresh()
    entry.focus_set()
    return window

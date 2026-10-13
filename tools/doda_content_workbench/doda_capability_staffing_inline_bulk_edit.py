"""Capability Staffing batch candidate foundation; no GUI or source writes."""
from doda_row_selection import MULTIPLE_VALUES

IDENTITY_FIELDS = ("capability_id", "qualification_id")
EDITABLE_FIELDS = (
    "min_contributors", "preferred_contributors", "max_contributors",
    "sort_order", "active",
)


def row_key(row):
    return (row["capability_id"], row["qualification_id"])


def validate_row(row):
    for name in IDENTITY_FIELDS:
        value = row.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Capability and Qualification identity are required.")
        if value.strip() == MULTIPLE_VALUES:
            raise ValueError("Placeholder text is not an identity.")
    try:
        counts = [int(row[name]) for name in EDITABLE_FIELDS[:3]]
        order = int(row["sort_order"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("Contributor counts and Sort Order must be integers.") from None
    if not 0 <= counts[0] <= counts[1] <= counts[2]:
        raise ValueError("Required contributor range: 0 <= Min <= Preferred <= Max.")
    if order < 1:
        raise ValueError("Sort Order must be at least 1.")
    if row.get("active") not in ("TRUE", "FALSE"):
        raise ValueError("Active must be TRUE or FALSE.")


def build_batch_candidate(rows, selected_keys, changes, validate_candidate):
    """Return a validated copy; caller owns draft/session checks and installation.

    Keys are Capability/Qualification tuples, never tree-row positions.
    The callback performs the existing project-level candidate validation.
    Empty changes return an unchanged copy without invoking validation.
    """
    selected = tuple(selected_keys)
    if len(selected) < 2:
        raise ValueError("Select at least two staffing rules.")
    if any(
        not isinstance(key, tuple) or len(key) != 2
        or any(not isinstance(part, str) for part in key)
        for key in selected
    ):
        raise ValueError("Invalid staffing selection identity.")
    if len(set(selected)) != len(selected):
        raise ValueError("Duplicate staffing selection identity.")
    original = [dict(row) for row in rows]
    keys = [row_key(row) for row in original]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate Capability/Qualification identity in draft.")
    if any(key not in keys for key in selected):
        raise ValueError("Selection no longer matches the staffing draft.")
    normalized = {}
    for name, value in changes.items():
        if name not in EDITABLE_FIELDS:
            raise ValueError("Identity or unknown fields cannot be batch-edited.")
        if not isinstance(value, str) or value.strip() == MULTIPLE_VALUES:
            raise ValueError("Placeholder or non-text values cannot be applied.")
        normalized[name] = value.strip()
    if not normalized:
        return original
    chosen = set(selected)
    candidate = [dict(row) for row in original]
    for row in candidate:
        if row_key(row) in chosen:
            row.update(normalized)
            validate_row(row)
    # Keep a private copy so a callback cannot change the returned candidate.
    validate_candidate([dict(row) for row in candidate])
    return candidate

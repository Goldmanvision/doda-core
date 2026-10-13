"""Shared task-template contract. No deadlines, spawning or scheduler state."""
COLUMNS = ('task_template_id', 'display_name', 'description', 'capability_id', 'priority', 'target_type', 'target_family_id', 'loop_task', 'time_to_complete_minutes', 'reward_mode', 'payout_count', 'sort_order', 'active')
TARGET_TYPES = ("STATION", "TERRITORY", "MISSION_AREA")
REWARD_MODES = ("CONTINUOUS", "PERIODIC_LUMP_SUM")

def boolean(value):
    if type(value) is bool:
        return value
    if isinstance(value, str) and value.strip().upper() in ("TRUE", "FALSE"):
        return value.strip().upper() == "TRUE"
    raise ValueError("must be TRUE or FALSE")

def integer(value, optional=False):
    if optional and value in (None, ""):
        return None
    if type(value) is int:
        return value
    if isinstance(value, str):
        return int(value.strip())
    raise ValueError("must be a whole number")

def errors(row, priorities):
    problems = []
    for field in ("display_name", "description"):
        if not row.get(field):
            problems.append(field + " is required")
    if row.get("priority") not in priorities:
        problems.append("unknown priority")
    if row.get("target_type") not in TARGET_TYPES:
        problems.append("invalid target_type")
    if row.get("reward_mode") not in REWARD_MODES:
        problems.append("invalid reward_mode")
    values = {}
    for field in ("active", "loop_task"):
        try:
            values[field] = boolean(row.get(field))
        except ValueError:
            problems.append(field + " must be TRUE or FALSE")
    for field, optional, minimum in (
        ("time_to_complete_minutes", True, 1), ("payout_count", False, 0),
        ("sort_order", False, 1),
    ):
        try:
            value = integer(row.get(field), optional)
            if value is not None and value < minimum:
                raise ValueError()
            values[field] = value
        except (ValueError, TypeError):
            problems.append(field + " has an invalid whole-number value")
    active = values.get("active", False)
    duration = values.get("time_to_complete_minutes")
    payouts = values.get("payout_count", 0)
    if active and not row.get("capability_id"):
        problems.append("active template requires capability_id")
    if row.get("target_type") != "STATION" and row.get("target_family_id"):
        problems.append("target_family_id applies only to STATION")
    if active and row.get("target_type") == "STATION" and not row.get("target_family_id"):
        problems.append("active STATION template requires target_family_id")
    if active and values.get("loop_task") and duration is None:
        problems.append("active loop task requires a completion-cycle duration")
    if row.get("reward_mode") == "CONTINUOUS" and payouts:
        problems.append("CONTINUOUS templates use payout_count 0")
    if row.get("reward_mode") == "PERIODIC_LUMP_SUM":
        if active and (duration is None or not payouts):
            problems.append("active periodic task requires duration and payout_count")
        if duration is not None and payouts and duration % payouts:
            problems.append("duration must divide evenly into payout intervals")
    return problems

"""Sandbox task instances. In-memory only; never written to CSV."""
from dataclasses import dataclass, replace

OPEN = "OPEN"
OVERDUE = "OVERDUE"
CANCELLED = "CANCELLED"

def is_true(row):
    return str(row.get("active", "")).strip().upper() == "TRUE"

def positive_minutes(row, key):
    raw = str(row.get(key, "")).strip()
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(key + " must be an integer; found '" + raw + "'.")
    if value < 1:
        raise ValueError(key + " must be at least 1.")
    return value

@dataclass(frozen=True)
class TaskInstance:
    instance_id: str
    template_id: str
    display_name: str
    capability_id: str
    priority: str
    target_effort_minutes: int
    created_minute: int
    deadline_minute: int
    cancelled: bool = False

class TaskBoard:
    def __init__(self, tables):
        self.tables = tables
        self._tasks = {}
        self._next = 1

    def _unique(self, table, key, value):
        rows = [r for r in self.tables.get(table, []) if r.get(key) == value]
        return rows[0] if len(rows) == 1 else None

    def spawn(self, template_id, now_minute):
        if int(now_minute) < 0:
            raise ValueError("now_minute cannot be negative.")
        template = self._unique("task_templates", "task_template_id", template_id)
        if template is None:
            raise ValueError("Unknown or duplicate task template: " + str(template_id))
        if not is_true(template):
            raise ValueError("Task template is inactive: " + template_id)
        capability_id = template.get("capability_id", "")
        capability = self._unique("capabilities", "capability_id", capability_id)
        if capability is None or not is_true(capability):
            raise ValueError("Capability missing or inactive: " + str(capability_id))
        effort = positive_minutes(template, "default_target_effort_minutes")
        deadline = positive_minutes(template, "default_deadline_minutes")
        instance_id = "TASK_%04d" % self._next
        self._next += 1
        task = TaskInstance(
            instance_id=instance_id,
            template_id=template_id,
            display_name=template.get("display_name") or template_id,
            capability_id=capability_id,
            priority=template.get("priority", ""),
            target_effort_minutes=effort,
            created_minute=int(now_minute),
            deadline_minute=int(now_minute) + deadline,
        )
        self._tasks[instance_id] = task
        return task

    def cancel(self, instance_id):
        if instance_id not in self._tasks:
            raise KeyError("Unknown task: " + instance_id)
        self._tasks[instance_id] = replace(self._tasks[instance_id], cancelled=True)

    @staticmethod
    def state(task, now_minute):
        if task.cancelled:
            return CANCELLED
        return OVERDUE if int(now_minute) > task.deadline_minute else OPEN

    def view(self, now_minute):
        rows = []
        for iid in sorted(self._tasks):
            task = self._tasks[iid]
            rows.append({
                "instance_id": task.instance_id,
                "template_id": task.template_id,
                "display_name": task.display_name,
                "capability_id": task.capability_id,
                "priority": task.priority,
                "target_effort_minutes": task.target_effort_minutes,
                "created_minute": task.created_minute,
                "deadline_minute": task.deadline_minute,
                "state": self.state(task, now_minute),
                "remaining_minutes": (
                    None if task.cancelled
                    else task.deadline_minute - int(now_minute)
                ),
            })
        return rows

    def reset(self):
        self._tasks = {}
        self._next = 1

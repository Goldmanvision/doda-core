#!/usr/bin/env python3
"""
DoDA Strategic Data CSV Operations Report Generator

Standalone offline developer utility to generate Markdown operations briefs
from validated authoring CSV datasets for future DoDA strategic systems.
"""

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Dict, List, Optional, Set, Tuple


REQUIRED_SCHEMAS: Dict[str, List[str]] = {
    "people.csv": ["person_id", "display_name", "status", "workload"],
    "locations.csv": ["location_id", "display_name"],
    "tasks.csv": [
        "task_id",
        "display_name",
        "location_id",
        "state",
        "required_work",
        "current_progress",
        "assigned_person_count",
    ],
    "assignments.csv": [
        "assignment_id",
        "person_id",
        "task_id",
        "assignment_state",
    ],
}

VALID_TASK_STATES: Set[str] = {"PENDING", "ACTIVE", "COMPLETE"}
VALID_ASSIGNMENT_STATES: Set[str] = {"PENDING", "ACTIVE", "COMPLETE", "CANCELLED"}


@dataclass
class Person:
    person_id: str
    display_name: str
    status: str
    workload: int


@dataclass
class Location:
    location_id: str
    display_name: str


@dataclass
class Task:
    task_id: str
    display_name: str
    location_id: str
    state: str
    required_work: int
    current_progress: int
    assigned_person_count: int


@dataclass
class Assignment:
    assignment_id: str
    person_id: str
    task_id: str
    assignment_state: str


def read_csv_rows(file_path: Path, required_columns: List[str]) -> Tuple[Optional[List[Dict[str, str]]], Optional[str]]:
    file_name = file_path.name
    if not file_path.exists():
        return None, f"Required file not found: {file_path}"
    if not file_path.is_file():
        return None, f"Path is not a regular file: {file_path}"

    try:
        with file_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            try:
                header_row = next(reader)
            except StopIteration:
                return None, f"CSV file '{file_name}' is empty (missing header row)"

            cleaned_headers = [h.strip() for h in header_row]
            missing_headers = [col for col in required_columns if col not in cleaned_headers]
            if missing_headers:
                return None, f"CSV file '{file_name}' is missing required header(s): {', '.join(missing_headers)}"

            header_indices = {col: cleaned_headers.index(col) for col in required_columns}
            rows: List[Dict[str, str]] = []
            for line_idx, row in enumerate(reader, start=2):
                if not row or all(c.strip() == "" for c in row):
                    continue
                row_dict: Dict[str, str] = {}
                for col, idx in header_indices.items():
                    if idx < len(row):
                        row_dict[col] = row[idx].strip()
                    else:
                        return None, f"CSV file '{file_name}' row {line_idx} missing value for column '{col}'"
                rows.append(row_dict)
            return rows, None
    except UnicodeDecodeError as exc:
        return None, f"UTF-8 decoding error reading '{file_name}': {exc}"
    except Exception as exc:
        return None, f"Failed to read CSV '{file_name}': {exc}"


def load_dataset(data_dir: Path) -> Tuple[
    Optional[Dict[str, Person]],
    Optional[Dict[str, Location]],
    Optional[Dict[str, Task]],
    Optional[List[Assignment]],
    Optional[str],
]:
    # 1. Read all four files
    raw_tables: Dict[str, List[Dict[str, str]]] = {}
    for filename, cols in REQUIRED_SCHEMAS.items():
        rows, err = read_csv_rows(data_dir / filename, cols)
        if err:
            return None, None, None, None, err
        assert rows is not None
        raw_tables[filename] = rows

    # 2. Parse locations
    locations: Dict[str, Location] = {}
    for r in raw_tables["locations.csv"]:
        loc_id = r["location_id"]
        d_name = r["display_name"]
        if not loc_id:
            return None, None, None, None, "locations.csv contains blank location_id"
        if loc_id in locations:
            return None, None, None, None, f"Duplicate location_id '{loc_id}' in locations.csv"
        if not d_name:
            return None, None, None, None, f"locations.csv location '{loc_id}' has blank display_name"
        locations[loc_id] = Location(location_id=loc_id, display_name=d_name)

    # 3. Parse people
    people: Dict[str, Person] = {}
    for r in raw_tables["people.csv"]:
        p_id = r["person_id"]
        d_name = r["display_name"]
        status = r["status"]
        workload_raw = r["workload"]

        if not p_id:
            return None, None, None, None, "people.csv contains blank person_id"
        if p_id in people:
            return None, None, None, None, f"Duplicate person_id '{p_id}' in people.csv"
        if not d_name:
            return None, None, None, None, f"people.csv person '{p_id}' has blank display_name"
        try:
            workload_val = int(workload_raw)
            if workload_val < 0 or workload_val > 100:
                return None, None, None, None, f"people.csv person '{p_id}' workload out of range [0, 100]: {workload_val}"
        except ValueError:
            return None, None, None, None, f"people.csv person '{p_id}' has non-integer workload: '{workload_raw}'"

        people[p_id] = Person(person_id=p_id, display_name=d_name, status=status, workload=workload_val)

    # 4. Parse tasks
    tasks: Dict[str, Task] = {}
    for r in raw_tables["tasks.csv"]:
        t_id = r["task_id"]
        d_name = r["display_name"]
        loc_id = r["location_id"]
        state = r["state"]
        req_work_raw = r["required_work"]
        progress_raw = r["current_progress"]
        asg_count_raw = r["assigned_person_count"]

        if not t_id:
            return None, None, None, None, "tasks.csv contains blank task_id"
        if t_id in tasks:
            return None, None, None, None, f"Duplicate task_id '{t_id}' in tasks.csv"
        if not d_name:
            return None, None, None, None, f"tasks.csv task '{t_id}' has blank display_name"
        if loc_id not in locations:
            return None, None, None, None, f"tasks.csv task '{t_id}' references unknown location_id '{loc_id}'"
        if state not in VALID_TASK_STATES:
            return None, None, None, None, f"tasks.csv task '{t_id}' has invalid state '{state}'"

        try:
            req_work_val = int(req_work_raw)
            if req_work_val <= 0:
                return None, None, None, None, f"tasks.csv task '{t_id}' required_work must be > 0, got {req_work_val}"
        except ValueError:
            return None, None, None, None, f"tasks.csv task '{t_id}' has non-integer required_work: '{req_work_raw}'"

        try:
            progress_val = int(progress_raw)
            if progress_val < 0 or progress_val > req_work_val:
                return None, None, None, None, f"tasks.csv task '{t_id}' current_progress ({progress_val}) must be between 0 and {req_work_val}"
        except ValueError:
            return None, None, None, None, f"tasks.csv task '{t_id}' has non-integer current_progress: '{progress_raw}'"

        try:
            asg_count_val = int(asg_count_raw)
            if asg_count_val < 0:
                return None, None, None, None, f"tasks.csv task '{t_id}' assigned_person_count must be >= 0, got {asg_count_val}"
        except ValueError:
            return None, None, None, None, f"tasks.csv task '{t_id}' has non-integer assigned_person_count: '{asg_count_raw}'"

        tasks[t_id] = Task(
            task_id=t_id,
            display_name=d_name,
            location_id=loc_id,
            state=state,
            required_work=req_work_val,
            current_progress=progress_val,
            assigned_person_count=asg_count_val,
        )

    # 5. Parse assignments
    assignments: List[Assignment] = []
    seen_assignment_ids: Set[str] = set()
    for r in raw_tables["assignments.csv"]:
        a_id = r["assignment_id"]
        p_id = r["person_id"]
        t_id = r["task_id"]
        asg_state = r["assignment_state"]

        if not a_id:
            return None, None, None, None, "assignments.csv contains blank assignment_id"
        if a_id in seen_assignment_ids:
            return None, None, None, None, f"Duplicate assignment_id '{a_id}' in assignments.csv"
        seen_assignment_ids.add(a_id)

        if p_id not in people:
            return None, None, None, None, f"assignments.csv assignment '{a_id}' references unknown person_id '{p_id}'"
        if t_id not in tasks:
            return None, None, None, None, f"assignments.csv assignment '{a_id}' references unknown task_id '{t_id}'"
        if asg_state not in VALID_ASSIGNMENT_STATES:
            return None, None, None, None, f"assignments.csv assignment '{a_id}' has invalid assignment_state '{asg_state}'"

        assignments.append(
            Assignment(
                assignment_id=a_id,
                person_id=p_id,
                task_id=t_id,
                assignment_state=asg_state,
            )
        )

    return people, locations, tasks, assignments, None


def generate_operations_report(
    data_dir: Path,
    people: Dict[str, Person],
    locations: Dict[str, Location],
    tasks: Dict[str, Task],
    assignments: List[Assignment],
    timestamp_utc: Optional[str] = None,
) -> str:
    if timestamp_utc is None:
        timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Input directory name only, not absolute path
    dir_name = data_dir.resolve().name if data_dir.resolve().name else "data"

    # Process assignments
    # Current staffing = PENDING or ACTIVE
    # Historical = CANCELLED or COMPLETE
    current_assignments_by_task: Dict[str, List[Assignment]] = {t_id: [] for t_id in tasks}
    historical_assignments_by_task: Dict[str, List[Assignment]] = {t_id: [] for t_id in tasks}
    current_assignments_by_person: Dict[str, List[Assignment]] = {p_id: [] for p_id in people}

    for asg in assignments:
        if asg.assignment_state in {"PENDING", "ACTIVE"}:
            current_assignments_by_task[asg.task_id].append(asg)
            current_assignments_by_person[asg.person_id].append(asg)
        else:
            historical_assignments_by_task[asg.task_id].append(asg)

    # Sort assignments within each task by person_id
    for t_id in tasks:
        current_assignments_by_task[t_id].sort(key=lambda a: a.person_id)
        historical_assignments_by_task[t_id].sort(key=lambda a: a.person_id)

    # Task counts by state
    tasks_active = [t for t in tasks.values() if t.state == "ACTIVE"]
    tasks_pending = [t for t in tasks.values() if t.state == "PENDING"]
    tasks_complete = [t for t in tasks.values() if t.state == "COMPLETE"]

    total_current_staffing_count = sum(len(asgs) for asgs in current_assignments_by_task.values())
    unassigned_people_count = sum(1 for p_id in people if len(current_assignments_by_person[p_id]) == 0)

    # Sort tasks:
    # Current operations: ACTIVE first, then PENDING, then task_id
    current_tasks = sorted(
        tasks_active + tasks_pending,
        key=lambda t: (0 if t.state == "ACTIVE" else 1, t.task_id),
    )
    # Completed operations: COMPLETE tasks sorted by task_id
    completed_tasks = sorted(tasks_complete, key=lambda t: t.task_id)

    # Personnel sorted by person_id
    sorted_people = sorted(people.values(), key=lambda p: p.person_id)

    lines: List[str] = []

    # Title & Metadata
    lines.append("# DoDA Authoring Operations Brief")
    lines.append("")
    lines.append(f"- **Generated (UTC):** {timestamp_utc}")
    lines.append(f"- **Source Directory:** {dir_name}")
    lines.append("")

    # Summary Section
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Personnel:** {len(people)}")
    lines.append(f"- **Total Locations:** {len(locations)}")
    lines.append(f"- **Total Tasks:** {len(tasks)}")
    lines.append(f"- **Current Staffing Assignments:** {total_current_staffing_count}")
    lines.append("- **Task Counts by State:**")
    lines.append(f"  - **ACTIVE:** {len(tasks_active)}")
    lines.append(f"  - **PENDING:** {len(tasks_pending)}")
    lines.append(f"  - **COMPLETE:** {len(tasks_complete)}")
    lines.append(f"- **Unassigned Personnel:** {unassigned_people_count}")
    lines.append("")

    # Current Operations Section
    lines.append("## Current Operations")
    lines.append("")
    if not current_tasks:
        lines.append("*No active or pending operations.*")
        lines.append("")
    else:
        for t in current_tasks:
            loc = locations[t.location_id]
            pct = (t.current_progress * 100) // t.required_work
            task_asgs = current_assignments_by_task[t.task_id]

            lines.append(f"### {t.task_id}: {t.display_name}")
            lines.append(f"- **Task ID:** {t.task_id}")
            lines.append(f"- **Display Name:** {t.display_name}")
            lines.append(f"- **State:** {t.state}")
            lines.append(f"- **Location:** {t.location_id} ({loc.display_name})")
            lines.append(f"- **Progress:** {t.current_progress} / {t.required_work} ({pct}%)")
            lines.append(f"- **Declared Assigned Personnel Count:** {t.assigned_person_count}")
            lines.append(f"- **Resolved Current Staffing Count:** {len(task_asgs)}")

            if not task_asgs:
                lines.append("- **Assigned Personnel:** — UNASSIGNED —")
            else:
                lines.append("- **Assigned Personnel:**")
                for a in task_asgs:
                    p = people[a.person_id]
                    lines.append(f"  - {p.display_name} ({p.person_id})")
            lines.append("")

    # Completed Operations Section
    lines.append("## Completed Operations")
    lines.append("")
    if not completed_tasks:
        lines.append("*No completed operations.*")
        lines.append("")
    else:
        for t in completed_tasks:
            loc = locations[t.location_id]
            pct = (t.current_progress * 100) // t.required_work
            curr_asgs = current_assignments_by_task[t.task_id]
            hist_asgs = historical_assignments_by_task[t.task_id]
            comp_count = sum(1 for a in hist_asgs if a.assignment_state == "COMPLETE")
            canc_count = sum(1 for a in hist_asgs if a.assignment_state == "CANCELLED")

            lines.append(f"### {t.task_id}: {t.display_name}")
            lines.append(f"- **Task ID:** {t.task_id}")
            lines.append(f"- **Display Name:** {t.display_name}")
            lines.append(f"- **Location:** {loc.display_name} ({t.location_id})")
            lines.append(f"- **Final Progress:** {t.current_progress} / {t.required_work} ({pct}%)")
            lines.append(
                f"- **Assignment Summary:** {len(curr_asgs)} current assignments, "
                f"{len(hist_asgs)} historical assignments ({comp_count} COMPLETE, {canc_count} CANCELLED)"
            )
            lines.append("")

    # Personnel Availability Section
    lines.append("## Personnel Availability")
    lines.append("")
    for p in sorted_people:
        asgs = current_assignments_by_person[p.person_id]
        lines.append(f"- **{p.person_id}** ({p.display_name})")
        lines.append(f"  - **Status:** {p.status}")
        lines.append(f"  - **Workload:** {p.workload}")
        if not asgs:
            lines.append("  - **Current Assignment:** UNASSIGNED")
        else:
            asg_descriptions = [
                f"{a.task_id} ({tasks[a.task_id].display_name})"
                for a in asgs
            ]
            lines.append(f"  - **Current Assignment:** {', '.join(asg_descriptions)}")
    lines.append("")

    # Validation Notes Section
    lines.append("## Validation Notes")
    lines.append("")
    lines.append(
        "- This report is an offline authoring review artifact. "
        "It does not load data into UZDoom, native DoDA, LibColony, save files, FOIMS-X, or ZScript."
    )
    lines.append("- Run validate_doda_authoring.py before relying on this report.")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Markdown operations briefs from validated DoDA CSV datasets."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Path to directory containing people.csv, locations.csv, tasks.csv, and assignments.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output Markdown report file",
    )

    args = parser.parse_args()

    people, locations, tasks, assignments, err = load_dataset(args.data_dir)
    if err:
        sys.stderr.write(f"DODA AUTHORING REPORT ERROR: {err}\n")
        return 1

    assert people is not None and locations is not None and tasks is not None and assignments is not None

    report_md = generate_operations_report(args.data_dir, people, locations, tasks, assignments)

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="\n") as f:
            f.write(report_md)
    except Exception as exc:
        sys.stderr.write(f"DODA AUTHORING REPORT ERROR: Failed to write output file '{args.output}': {exc}\n")
        return 1

    print(f"DODA AUTHORING REPORT GENERATED: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

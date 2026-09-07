#!/usr/bin/env python3
"""
DoDA Strategic Data CSV Authoring Validator

Standalone offline developer utility to validate authoring CSV datasets
for future DoDA strategic systems.
"""

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ValidationIssue:
    file_name: str
    row_number: int
    column_or_rule: str
    explanation: str

    def format(self) -> str:
        return f"{self.file_name}:{self.row_number} [{self.column_or_rule}] {self.explanation}"


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
class ParsedRecord:
    row_number: int
    data: Dict[str, str]


def parse_csv_file(
    file_path: Path, required_columns: List[str]
) -> Tuple[Optional[List[ParsedRecord]], List[ValidationIssue]]:
    issues: List[ValidationIssue] = []
    file_name = file_path.name

    if not file_path.exists():
        issues.append(
            ValidationIssue(
                file_name=file_name,
                row_number=0,
                column_or_rule="file_exists",
                explanation=f"Required file does not exist: {file_path}",
            )
        )
        return None, issues

    if not file_path.is_file():
        issues.append(
            ValidationIssue(
                file_name=file_name,
                row_number=0,
                column_or_rule="is_file",
                explanation=f"Path is not a regular file: {file_path}",
            )
        )
        return None, issues

    try:
        with file_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            try:
                header_row = next(reader)
            except StopIteration:
                issues.append(
                    ValidationIssue(
                        file_name=file_name,
                        row_number=0,
                        column_or_rule="headers",
                        explanation="CSV file is empty; header row missing",
                    )
                )
                return None, issues

            cleaned_headers = [h.strip() for h in header_row]
            missing_headers = [col for col in required_columns if col not in cleaned_headers]
            if missing_headers:
                issues.append(
                    ValidationIssue(
                        file_name=file_name,
                        row_number=1,
                        column_or_rule="headers",
                        explanation=f"Missing required header(s): {', '.join(missing_headers)}",
                    )
                )
                return None, issues

            header_indices = {col: cleaned_headers.index(col) for col in required_columns}

            records: List[ParsedRecord] = []
            for row in reader:
                line_num = reader.line_num
                # Skip empty lines if any
                if not row or all(c.strip() == "" for c in row):
                    continue

                row_dict: Dict[str, str] = {}
                row_has_error = False
                for col, idx in header_indices.items():
                    if idx < len(row):
                        row_dict[col] = row[idx].strip()
                    else:
                        issues.append(
                            ValidationIssue(
                                file_name=file_name,
                                row_number=line_num,
                                column_or_rule=col,
                                explanation=f"Missing column value for '{col}'",
                            )
                        )
                        row_has_error = True

                if not row_has_error:
                    records.append(ParsedRecord(row_number=line_num, data=row_dict))

            return records, issues

    except UnicodeDecodeError as exc:
        issues.append(
            ValidationIssue(
                file_name=file_name,
                row_number=0,
                column_or_rule="encoding",
                explanation=f"UTF-8 decoding error: {exc}",
            )
        )
        return None, issues
    except Exception as exc:
        issues.append(
            ValidationIssue(
                file_name=file_name,
                row_number=0,
                column_or_rule="csv_read",
                explanation=f"Failed to read CSV: {exc}",
            )
        )
        return None, issues


def validate_dataset(data_dir: Path) -> Tuple[bool, List[ValidationIssue], Dict[str, int]]:
    issues: List[ValidationIssue] = []
    record_counts: Dict[str, int] = {}

    # 1. Parse each file
    parsed_tables: Dict[str, Optional[List[ParsedRecord]]] = {}
    for filename, required_headers in REQUIRED_SCHEMAS.items():
        file_path = data_dir / filename
        records, file_issues = parse_csv_file(file_path, required_headers)
        issues.extend(file_issues)
        parsed_tables[filename] = records
        if records is not None:
            record_counts[filename] = len(records)
        else:
            record_counts[filename] = 0

    people_records = parsed_tables.get("people.csv")
    locations_records = parsed_tables.get("locations.csv")
    tasks_records = parsed_tables.get("tasks.csv")
    assignments_records = parsed_tables.get("assignments.csv")

    people_ids: Set[str] = set()
    location_ids: Set[str] = set()
    task_ids: Set[str] = set()
    assignment_ids: Set[str] = set()

    # 2. Validate people.csv
    if people_records is not None:
        seen_person_ids: Dict[str, int] = {}
        for rec in people_records:
            p_id = rec.data.get("person_id", "")
            d_name = rec.data.get("display_name", "")
            workload_raw = rec.data.get("workload", "")

            # ID nonblank & unique
            if not p_id:
                issues.append(
                    ValidationIssue(
                        file_name="people.csv",
                        row_number=rec.row_number,
                        column_or_rule="person_id",
                        explanation="person_id cannot be blank",
                    )
                )
            elif p_id in seen_person_ids:
                issues.append(
                    ValidationIssue(
                        file_name="people.csv",
                        row_number=rec.row_number,
                        column_or_rule="person_id",
                        explanation=f"Duplicate person_id '{p_id}' (first defined at row {seen_person_ids[p_id]})",
                    )
                )
            else:
                seen_person_ids[p_id] = rec.row_number
                people_ids.add(p_id)

            # display_name nonblank
            if not d_name:
                issues.append(
                    ValidationIssue(
                        file_name="people.csv",
                        row_number=rec.row_number,
                        column_or_rule="display_name",
                        explanation="display_name cannot be blank",
                    )
                )

            # workload integer [0, 100]
            try:
                workload_val = int(workload_raw)
                if workload_val < 0 or workload_val > 100:
                    issues.append(
                        ValidationIssue(
                            file_name="people.csv",
                            row_number=rec.row_number,
                            column_or_rule="workload",
                            explanation=f"workload must be an integer from 0 through 100 inclusive, got {workload_val}",
                        )
                    )
            except ValueError:
                issues.append(
                    ValidationIssue(
                        file_name="people.csv",
                        row_number=rec.row_number,
                        column_or_rule="workload",
                        explanation=f"workload must be a valid integer, got '{workload_raw}'",
                    )
                )

    # 3. Validate locations.csv
    if locations_records is not None:
        seen_location_ids: Dict[str, int] = {}
        for rec in locations_records:
            loc_id = rec.data.get("location_id", "")
            d_name = rec.data.get("display_name", "")

            # ID nonblank & unique
            if not loc_id:
                issues.append(
                    ValidationIssue(
                        file_name="locations.csv",
                        row_number=rec.row_number,
                        column_or_rule="location_id",
                        explanation="location_id cannot be blank",
                    )
                )
            elif loc_id in seen_location_ids:
                issues.append(
                    ValidationIssue(
                        file_name="locations.csv",
                        row_number=rec.row_number,
                        column_or_rule="location_id",
                        explanation=f"Duplicate location_id '{loc_id}' (first defined at row {seen_location_ids[loc_id]})",
                    )
                )
            else:
                seen_location_ids[loc_id] = rec.row_number
                location_ids.add(loc_id)

            # display_name nonblank
            if not d_name:
                issues.append(
                    ValidationIssue(
                        file_name="locations.csv",
                        row_number=rec.row_number,
                        column_or_rule="display_name",
                        explanation="display_name cannot be blank",
                    )
                )

    # 4. Validate tasks.csv
    if tasks_records is not None:
        seen_task_ids: Dict[str, int] = {}
        for rec in tasks_records:
            t_id = rec.data.get("task_id", "")
            d_name = rec.data.get("display_name", "")
            loc_id = rec.data.get("location_id", "")
            state = rec.data.get("state", "")
            req_work_raw = rec.data.get("required_work", "")
            progress_raw = rec.data.get("current_progress", "")
            assigned_count_raw = rec.data.get("assigned_person_count", "")

            # ID nonblank & unique
            if not t_id:
                issues.append(
                    ValidationIssue(
                        file_name="tasks.csv",
                        row_number=rec.row_number,
                        column_or_rule="task_id",
                        explanation="task_id cannot be blank",
                    )
                )
            elif t_id in seen_task_ids:
                issues.append(
                    ValidationIssue(
                        file_name="tasks.csv",
                        row_number=rec.row_number,
                        column_or_rule="task_id",
                        explanation=f"Duplicate task_id '{t_id}' (first defined at row {seen_task_ids[t_id]})",
                    )
                )
            else:
                seen_task_ids[t_id] = rec.row_number
                task_ids.add(t_id)

            # display_name nonblank
            if not d_name:
                issues.append(
                    ValidationIssue(
                        file_name="tasks.csv",
                        row_number=rec.row_number,
                        column_or_rule="display_name",
                        explanation="display_name cannot be blank",
                    )
                )

            # foreign key: location_id
            if locations_records is not None:
                if not loc_id or loc_id not in location_ids:
                    issues.append(
                        ValidationIssue(
                            file_name="tasks.csv",
                            row_number=rec.row_number,
                            column_or_rule="location_id",
                            explanation=f"Referenced location_id '{loc_id}' does not exist in locations.csv",
                        )
                    )

            # state in PENDING, ACTIVE, COMPLETE
            if state not in VALID_TASK_STATES:
                issues.append(
                    ValidationIssue(
                        file_name="tasks.csv",
                        row_number=rec.row_number,
                        column_or_rule="state",
                        explanation=f"Invalid task state '{state}'. Must be one of: {', '.join(sorted(VALID_TASK_STATES))}",
                    )
                )

            # required_work integer > 0
            req_work_val: Optional[int] = None
            try:
                req_work_val = int(req_work_raw)
                if req_work_val <= 0:
                    issues.append(
                        ValidationIssue(
                            file_name="tasks.csv",
                            row_number=rec.row_number,
                            column_or_rule="required_work",
                            explanation=f"required_work must be an integer greater than zero, got {req_work_val}",
                        )
                    )
                    req_work_val = None
            except ValueError:
                issues.append(
                    ValidationIssue(
                        file_name="tasks.csv",
                        row_number=rec.row_number,
                        column_or_rule="required_work",
                        explanation=f"required_work must be a valid integer, got '{req_work_raw}'",
                    )
                )

            # current_progress integer [0, required_work]
            try:
                progress_val = int(progress_raw)
                if progress_val < 0:
                    issues.append(
                        ValidationIssue(
                            file_name="tasks.csv",
                            row_number=rec.row_number,
                            column_or_rule="current_progress",
                            explanation=f"current_progress must be an integer >= 0, got {progress_val}",
                        )
                    )
                elif req_work_val is not None and progress_val > req_work_val:
                    issues.append(
                        ValidationIssue(
                            file_name="tasks.csv",
                            row_number=rec.row_number,
                            column_or_rule="current_progress",
                            explanation=f"current_progress ({progress_val}) exceeds required_work ({req_work_val})",
                        )
                    )
            except ValueError:
                issues.append(
                    ValidationIssue(
                        file_name="tasks.csv",
                        row_number=rec.row_number,
                        column_or_rule="current_progress",
                        explanation=f"current_progress must be a valid integer, got '{progress_raw}'",
                    )
                )

            # assigned_person_count valid integer syntax
            try:
                _ = int(assigned_count_raw)
            except ValueError:
                issues.append(
                    ValidationIssue(
                        file_name="tasks.csv",
                        row_number=rec.row_number,
                        column_or_rule="assigned_person_count",
                        explanation=f"assigned_person_count must be a valid integer, got '{assigned_count_raw}'",
                    )
                )

    # 5. Validate assignments.csv
    active_assignments_by_person: Dict[str, List[Tuple[str, int]]] = {}
    task_active_or_pending_assignment_counts: Dict[str, int] = {}

    if assignments_records is not None:
        seen_assignment_ids: Dict[str, int] = {}
        for rec in assignments_records:
            asg_id = rec.data.get("assignment_id", "")
            p_id = rec.data.get("person_id", "")
            t_id = rec.data.get("task_id", "")
            asg_state = rec.data.get("assignment_state", "")

            # ID nonblank & unique
            if not asg_id:
                issues.append(
                    ValidationIssue(
                        file_name="assignments.csv",
                        row_number=rec.row_number,
                        column_or_rule="assignment_id",
                        explanation="assignment_id cannot be blank",
                    )
                )
            elif asg_id in seen_assignment_ids:
                issues.append(
                    ValidationIssue(
                        file_name="assignments.csv",
                        row_number=rec.row_number,
                        column_or_rule="assignment_id",
                        explanation=f"Duplicate assignment_id '{asg_id}' (first defined at row {seen_assignment_ids[asg_id]})",
                    )
                )
            else:
                seen_assignment_ids[asg_id] = rec.row_number
                assignment_ids.add(asg_id)

            # foreign key: person_id
            if people_records is not None:
                if not p_id or p_id not in people_ids:
                    issues.append(
                        ValidationIssue(
                            file_name="assignments.csv",
                            row_number=rec.row_number,
                            column_or_rule="person_id",
                            explanation=f"Referenced person_id '{p_id}' does not exist in people.csv",
                        )
                    )

            # foreign key: task_id
            if tasks_records is not None:
                if not t_id or t_id not in task_ids:
                    issues.append(
                        ValidationIssue(
                            file_name="assignments.csv",
                            row_number=rec.row_number,
                            column_or_rule="task_id",
                            explanation=f"Referenced task_id '{t_id}' does not exist in tasks.csv",
                        )
                    )

            # assignment_state in PENDING, ACTIVE, COMPLETE, CANCELLED
            if asg_state not in VALID_ASSIGNMENT_STATES:
                issues.append(
                    ValidationIssue(
                        file_name="assignments.csv",
                        row_number=rec.row_number,
                        column_or_rule="assignment_state",
                        explanation=f"Invalid assignment_state '{asg_state}'. Must be one of: {', '.join(sorted(VALID_ASSIGNMENT_STATES))}",
                    )
                )
            else:
                if asg_state == "ACTIVE":
                    if p_id:
                        active_assignments_by_person.setdefault(p_id, []).append((asg_id, rec.row_number))

                if asg_state in {"PENDING", "ACTIVE"}:
                    if t_id:
                        task_active_or_pending_assignment_counts[t_id] = (
                            task_active_or_pending_assignment_counts.get(t_id, 0) + 1
                        )

        # Rule 12: A person may not have more than one ACTIVE assignment
        for p_id, active_list in active_assignments_by_person.items():
            if len(active_list) > 1:
                for asg_id, row_num in active_list[1:]:
                    prev_id, prev_row = active_list[0]
                    issues.append(
                        ValidationIssue(
                            file_name="assignments.csv",
                            row_number=row_num,
                            column_or_rule="assignment_state",
                            explanation=f"Person '{p_id}' has multiple ACTIVE assignments (also active in '{prev_id}' at row {prev_row})",
                        )
                    )

    # Rule 13: task.assigned_person_count must equal count of PENDING or ACTIVE assignments for that task
    if tasks_records is not None and assignments_records is not None:
        for rec in tasks_records:
            t_id = rec.data.get("task_id", "")
            assigned_count_raw = rec.data.get("assigned_person_count", "")
            try:
                expected_count = int(assigned_count_raw)
                actual_count = task_active_or_pending_assignment_counts.get(t_id, 0)
                if expected_count != actual_count:
                    issues.append(
                        ValidationIssue(
                            file_name="tasks.csv",
                            row_number=rec.row_number,
                            column_or_rule="assigned_person_count",
                            explanation=(
                                f"assigned_person_count is {expected_count}, but found {actual_count} "
                                f"PENDING or ACTIVE assignment(s) for task '{t_id}' in assignments.csv"
                            ),
                        )
                    )
            except ValueError:
                # already reported format error
                pass

    is_valid = len(issues) == 0
    return is_valid, issues, record_counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate DoDA Strategic Data authoring CSV files."
    )
    parser.add_argument(
        "--data-dir",
        "-d",
        required=True,
        type=Path,
        help="Path to directory containing authoring CSV files (people.csv, locations.csv, tasks.csv, assignments.csv)",
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    if not data_dir.exists():
        print(f"Error: Specified data directory does not exist: {data_dir}", file=sys.stderr)
        sys.exit(1)
    if not data_dir.is_dir():
        print(f"Error: Specified path is not a directory: {data_dir}", file=sys.stderr)
        sys.exit(1)

    is_valid, issues, record_counts = validate_dataset(data_dir)

    if not is_valid:
        print(f"Validation failed with {len(issues)} issue(s):\n", file=sys.stderr)
        for issue in issues:
            print(f"  {issue.format()}", file=sys.stderr)
        sys.exit(1)

    print("Authoring CSV records validated successfully:")
    for filename in REQUIRED_SCHEMAS.keys():
        count = record_counts.get(filename, 0)
        print(f"  {filename}: {count} record(s)")
    print()
    print("DODA AUTHORING VALIDATION PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()

import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doda_foims_x_tasks import TaskBoard, OPEN, OVERDUE, CANCELLED

def tables():
    return {
        "task_templates": [
            {"task_template_id": "REVIEW", "display_name": "Signal Review",
             "capability_id": "ANALYSIS", "priority": "HIGH",
             "default_target_effort_minutes": "240",
             "default_deadline_minutes": "120", "active": "TRUE"},
            {"task_template_id": "DRAFT", "display_name": "Draft",
             "capability_id": "ANALYSIS", "priority": "NORMAL",
             "default_target_effort_minutes": "10",
             "default_deadline_minutes": "10", "active": "FALSE"},
            {"task_template_id": "ORPHAN", "display_name": "Orphan",
             "capability_id": "GONE", "priority": "NORMAL",
             "default_target_effort_minutes": "10",
             "default_deadline_minutes": "10", "active": "TRUE"},
            {"task_template_id": "BAD", "display_name": "Bad",
             "capability_id": "ANALYSIS", "priority": "NORMAL",
             "default_target_effort_minutes": "abc",
             "default_deadline_minutes": "10", "active": "TRUE"},
            {"task_template_id": "ZERO", "display_name": "Zero",
             "capability_id": "ANALYSIS", "priority": "NORMAL",
             "default_target_effort_minutes": "10",
             "default_deadline_minutes": "0", "active": "TRUE"},
        ],
        "capabilities": [
            {"capability_id": "ANALYSIS", "active": "TRUE"},
        ],
    }

class TaskBoardTests(unittest.TestCase):
    def test_spawn_copies_template(self):
        task = TaskBoard(tables()).spawn("REVIEW", 100)
        self.assertEqual(task.instance_id, "TASK_0001")
        self.assertEqual(task.capability_id, "ANALYSIS")
        self.assertEqual(task.priority, "HIGH")
        self.assertEqual(task.target_effort_minutes, 240)
        self.assertEqual(task.created_minute, 100)
        self.assertEqual(task.deadline_minute, 220)

    def test_ids_sequential_and_not_reused(self):
        board = TaskBoard(tables())
        board.spawn("REVIEW", 0)
        board.cancel("TASK_0001")
        self.assertEqual(board.spawn("REVIEW", 0).instance_id, "TASK_0002")

    def test_unknown_or_inactive_template_rejected(self):
        board = TaskBoard(tables())
        with self.assertRaises(ValueError):
            board.spawn("NOPE", 0)
        with self.assertRaises(ValueError):
            board.spawn("DRAFT", 0)
        self.assertEqual(board.view(0), [])

    def test_inactive_or_missing_capability_rejected(self):
        board = TaskBoard(tables())
        with self.assertRaises(ValueError):
            board.spawn("ORPHAN", 0)
        board.tables["capabilities"][0]["active"] = "FALSE"
        with self.assertRaises(ValueError):
            board.spawn("REVIEW", 0)

    def test_invalid_minutes_rejected(self):
        board = TaskBoard(tables())
        with self.assertRaises(ValueError):
            board.spawn("BAD", 0)
        with self.assertRaises(ValueError):
            board.spawn("ZERO", 0)
        with self.assertRaises(ValueError):
            board.spawn("REVIEW", -1)

    def test_overdue_is_derived(self):
        board = TaskBoard(tables())
        board.spawn("REVIEW", 0)
        self.assertEqual(board.view(120)[0]["state"], OPEN)
        self.assertEqual(board.view(120)[0]["remaining_minutes"], 0)
        self.assertEqual(board.view(121)[0]["state"], OVERDUE)
        self.assertEqual(board.view(121)[0]["remaining_minutes"], -1)
        self.assertEqual(board.view(50)[0]["state"], OPEN)

    def test_cancel(self):
        board = TaskBoard(tables())
        board.spawn("REVIEW", 0)
        board.cancel("TASK_0001")
        row = board.view(9999)[0]
        self.assertEqual(row["state"], CANCELLED)
        self.assertIsNone(row["remaining_minutes"])
        with self.assertRaises(KeyError):
            board.cancel("TASK_0099")

    def test_reset_restarts_ids(self):
        board = TaskBoard(tables())
        board.spawn("REVIEW", 0)
        board.reset()
        self.assertEqual(board.view(0), [])
        self.assertEqual(board.spawn("REVIEW", 0).instance_id, "TASK_0001")

    def test_tables_not_mutated_and_effort_may_exceed_deadline(self):
        t = tables()
        before = deepcopy(t)
        board = TaskBoard(t)
        task = board.spawn("REVIEW", 5)
        board.view(5)
        self.assertGreater(task.target_effort_minutes, task.deadline_minute - task.created_minute)
        self.assertEqual(t, before)

if __name__ == "__main__":
    unittest.main()

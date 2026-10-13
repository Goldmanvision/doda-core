import ast
import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doda_foims_x_task_catalog import TasksCatalog
from doda_foims_x_tasks import TaskBoard

def tables():
    return {
        "task_templates": [
            {"task_template_id": "REVIEW", "display_name": "Signal Review",
             "capability_id": "ANALYSIS", "priority": "HIGH",
             "default_target_effort_minutes": "240",
             "default_deadline_minutes": "120", "active": "TRUE"},
        ],
        "capabilities": [
            {"capability_id": "ANALYSIS", "display_name": "Analysis", "active": "TRUE"}
        ],
        "capability_staffing_rules": [
            {"capability_id": "ANALYSIS", "qualification_id": "SIGNALS_ANALYSIS",
             "min_contributors": "1", "preferred_contributors": "2",
             "max_contributors": "3", "active": "TRUE"}
        ],
        "qualification_catalog": [
            {"qualification_id": "SIGNALS_ANALYSIS",
             "display_name": "Signals Analysis", "active": "TRUE"}
        ],
    }

def build(now=0):
    t = tables()
    clock = [now]
    board = TaskBoard(t)
    return t, clock, board, TasksCatalog(t, board, lambda: clock[0])

def text(catalog, identity="TASK_0001"):
    return "\n".join(catalog.describe(identity))

class TasksCatalogTests(unittest.TestCase):
    def test_rows_follow_clock(self):
        _, clock, board, catalog = build()
        board.spawn("REVIEW", 0)
        self.assertEqual(catalog.facilities()[0]["display_name"], "TASK_0001 OPEN")
        clock[0] = 500
        self.assertEqual(catalog.facilities()[0]["display_name"], "TASK_0001 OVERDUE")

    def test_timing_lines(self):
        _, clock, board, catalog = build()
        board.spawn("REVIEW", 100)
        clock[0] = 150
        out = text(catalog)
        self.assertIn("Created: minute 100 (1992-02-01 01:40)", out)
        self.assertIn("Deadline: minute 220 (1992-02-01 03:40)", out)
        self.assertIn("Remaining: 70 strategic minutes", out)
        self.assertIn("Target effort: 240 minutes", out)
        clock[0] = 225
        self.assertIn("OVERDUE by 5 strategic minutes", text(catalog))
        board.cancel("TASK_0001")
        self.assertIn("Cancelled; deadline no longer applies.", text(catalog))

    def test_template_capability_qualification(self):
        _, _, board, catalog = build()
        board.spawn("REVIEW", 0)
        out = text(catalog)
        self.assertIn("Signal Review / REVIEW [ACTIVE]", out)
        self.assertIn("Analysis / ANALYSIS [ACTIVE]", out)
        self.assertIn("Signals Analysis / SIGNALS_ANALYSIS [ACTIVE]", out)
        self.assertIn("1/2/3", out)
        self.assertIn("Priority: HIGH", out)

    def test_empty_and_unknown(self):
        _, _, _, catalog = build()
        self.assertEqual(catalog.facilities(), [])
        self.assertIn("missing", text(catalog, "").lower())
        self.assertIn("missing", text(catalog, "TASK_0099").lower())

    def test_board_follows_refreshed_tables(self):
        t, clock, board, _ = build()
        fresh = deepcopy(t)
        TasksCatalog(fresh, board, lambda: clock[0])
        self.assertIs(board.tables, fresh)

    def test_read_only_and_pages(self):
        t, clock, board, catalog = build()
        board.spawn("REVIEW", 0)
        before = deepcopy(t)
        pages = catalog.pages("TASK_0001", width=52, page_size=3)
        self.assertGreater(len(pages), 1)
        self.assertTrue(all(len(p) <= 3 for p in pages))
        self.assertTrue(all(len(line) <= 52 for p in pages for line in p))
        self.assertEqual(t, before)
        self.assertEqual(len(board.view(0)), 1)

    def test_preview_integration_structure(self):
        source = (Path(__file__).resolve().parents[1]
                  / "doda_foims_x_preview.py").read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        cls = next(n for n in tree.body
                   if isinstance(n, ast.ClassDef) and n.name == "FoimsXPreview")
        names = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
        for name in ("_task_now", "_populate_task_templates", "_task_spawn",
                     "_task_cancel", "_task_clear"):
            self.assertIn(name, names)
        self.assertIn("self.task_board.reset()", source)
        self.assertIn('"Tasks"', source)

if __name__ == "__main__":
    unittest.main()

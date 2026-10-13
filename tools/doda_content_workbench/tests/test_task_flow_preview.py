import copy
import unittest
from fractions import Fraction
import doda_task_flow_preview as p

class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.template = {"task_template_id": "T", "display_name": "Test", "active": "FALSE"}
        self.resources = [{"resource_id": "R", "display_name": "Resource"}]
        self.row = {"taskTemplateId": "T", "direction": "OUT", "resourceId": "R", "flowMode": "FIXED", "amount": None, "weight": None, "sortOrder": 1, "active": False}
    def preview(self, rows=None):
        return p.build_preview(self.template, rows if rows is not None else [self.row], self.resources)
    def test_blank_draft(self):
        self.assertIn("UNCONFIGURED", p.render_preview(self.preview()))
    def test_no_mutation(self):
        before = copy.deepcopy((self.template, self.row, self.resources))
        self.preview()
        self.assertEqual(before, (self.template, self.row, self.resources))
    def test_filter_template(self):
        self.assertEqual(self.preview([dict(self.row, taskTemplateId="OTHER")])["flows"], [])
    def test_resource_name(self):
        self.assertEqual(self.preview()["flows"][0]["resourceName"], "Resource")
    def test_weighted_share(self):
        rows = [dict(self.row, active=True, flowMode="WEIGHTED", amount=10, weight=2), dict(self.row, active=True, flowMode="WEIGHTED", resourceId="S", amount=10, weight=3)]
        self.assertEqual([r["probability"] for r in self.preview(rows)["flows"]], [Fraction(2,5), Fraction(3,5)])
    def test_inactive_excluded(self):
        rows = [dict(self.row, active=True, flowMode="WEIGHTED", weight=2), dict(self.row, flowMode="WEIGHTED", resourceId="S", weight=100)]
        self.assertEqual([r["probability"] for r in self.preview(rows)["flows"]], [Fraction(1), None])
    def test_missing_weight_no_share(self):
        rows = [dict(self.row, active=True, flowMode="WEIGHTED", weight=2), dict(self.row, active=True, flowMode="WEIGHTED", resourceId="S")]
        self.assertTrue(all(r["probability"] is None for r in self.preview(rows)["flows"]))
    def test_no_authored_rows(self):
        self.assertIn("No authored rows.", p.render_preview(self.preview([])))
    def test_fixed_amount(self):
        self.assertIn("amount=7", p.render_preview(self.preview([dict(self.row, amount=7)])))
    def test_runtime_not_implemented(self):
        self.assertFalse(self.preview()["runtimeImplemented"])
        self.assertIn("no task execution", p.render_preview(self.preview()))

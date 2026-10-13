import copy
import unittest
import doda_task_flow_preview as preview


class StaffingPreviewTests(unittest.TestCase):
    def setUp(self):
        self.model = preview.build_preview(
            {"task_template_id": "T", "display_name": "Test", "active": "FALSE"},
            [], [],
        )
        self.rule = {
            "taskTemplateId": "T", "personnelRole": "ANALYST",
            "minContributors": 3, "preferredContributors": None,
            "maxContributors": None, "sortOrder": 10, "active": False,
        }

    def combined(self, rules=None):
        return preview.attach_staffing(
            [self.model], rules if rules is not None else [self.rule]
        )[0]

    def test_matching_template_only(self):
        other = dict(self.rule, taskTemplateId="OTHER")
        self.assertEqual(self.combined([self.rule, other])["staffingRules"],
                         [self.rule])

    def test_no_mutation_or_rule_alias(self):
        original = copy.deepcopy((self.model, self.rule))
        result = self.combined()
        result["staffingRules"][0]["minContributors"] = 99
        self.assertEqual(original, (self.model, self.rule))
        self.assertNotIn("staffingRules", self.model)

    def test_inactive_minimum_display(self):
        text = preview.render_preview(self.combined())
        self.assertIn("TASK-SPECIFIC STAFFING", text)
        self.assertIn("ANALYST: minimum=3", text)
        self.assertIn("maximum=UNSPECIFIED; INACTIVE DRAFT", text)

    def test_blank_minimum_not_zero(self):
        rule = dict(self.rule, minContributors=None)
        text = preview.render_preview(self.combined([rule]))
        self.assertIn("minimum=UNCONFIGURED", text)
        self.assertNotIn("minimum=0", text)

    def test_configured_preferred_and_maximum(self):
        rule = dict(self.rule, preferredContributors=4, maxContributors=5)
        text = preview.render_preview(self.combined([rule]))
        self.assertIn("preferred=4; maximum=5", text)

    def test_absent_rules_not_no_staff_needed(self):
        text = preview.render_preview(self.combined([]))
        self.assertIn("No authored task-specific staffing rules.", text)
        self.assertIn("does not establish that no personnel are required", text)

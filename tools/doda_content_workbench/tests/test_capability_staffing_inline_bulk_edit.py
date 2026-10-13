import copy
import unittest
from unittest.mock import Mock

from doda_capability_staffing_inline_bulk_edit import (
    build_batch_candidate, row_key, validate_row,
)
from doda_row_selection import MULTIPLE_VALUES


def rule(capability, qualification, minimum="0", preferred="1", maximum="3"):
    return {
        "capability_id": capability, "qualification_id": qualification,
        "min_contributors": minimum, "preferred_contributors": preferred,
        "max_contributors": maximum, "sort_order": "1", "active": "TRUE",
    }


class StaffingBatchCandidateTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            rule("CAP_A", "QUAL_A"),
            rule("CAP_A", "QUAL_B", preferred="2"),
            rule("CAP_B", "QUAL_A"),
        ]
        self.before = copy.deepcopy(self.rows)
        self.selected = tuple(row_key(row) for row in self.rows[:2])
        self.validator = Mock()

    def candidate(self, changes):
        return build_batch_candidate(
            self.rows, self.selected, changes, self.validator
        )

    def test_only_deliberately_edited_fields_change(self):
        result = self.candidate({"max_contributors": "4"})
        self.assertEqual([r["max_contributors"] for r in result], ["4", "4", "3"])
        self.assertEqual([r["preferred_contributors"] for r in result], ["1", "2", "1"])
        self.assertEqual(self.rows, self.before)
        self.validator.assert_called_once()

    def test_identity_preserved(self):
        result = self.candidate({"active": "FALSE"})
        self.assertEqual([row_key(r) for r in result], [row_key(r) for r in self.rows])

    def test_identity_edits_blocked(self):
        for field in ("capability_id", "qualification_id"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.candidate({field: "OTHER"})
        self.validator.assert_not_called()

    def test_unknown_field_blocked(self):
        with self.assertRaises(ValueError):
            self.candidate({"invented": "1"})

    def test_placeholder_blocked(self):
        with self.assertRaises(ValueError):
            self.candidate({"sort_order": MULTIPLE_VALUES})

    def test_nontext_change_blocked(self):
        with self.assertRaises(ValueError):
            self.candidate({"active": True})

    def test_invalid_second_row_is_atomic(self):
        with self.assertRaises(ValueError):
            self.candidate({"max_contributors": "1"})
        self.assertEqual(self.rows, self.before)
        self.validator.assert_not_called()

    def test_project_validation_failure_is_atomic(self):
        self.validator.side_effect = ValueError("Project constraint failed")
        with self.assertRaisesRegex(ValueError, "Project constraint"):
            self.candidate({"sort_order": "2"})
        self.assertEqual(self.rows, self.before)

    def test_empty_changes_skip_validation(self):
        result = self.candidate({})
        self.assertEqual(result, self.rows)
        self.assertIsNot(result[0], self.rows[0])
        self.validator.assert_not_called()

    def test_missing_selection_blocked(self):
        with self.assertRaises(ValueError):
            build_batch_candidate(
                self.rows, (self.selected[0], ("MISSING", "QUAL")),
                {"active": "FALSE"}, self.validator,
            )

    def test_duplicate_selection_blocked(self):
        with self.assertRaises(ValueError):
            build_batch_candidate(
                self.rows, (self.selected[0], self.selected[0]),
                {"active": "FALSE"}, self.validator,
            )

    def test_duplicate_draft_identity_blocked(self):
        with self.assertRaises(ValueError):
            build_batch_candidate(
                self.rows + [dict(self.rows[0])], self.selected,
                {"active": "FALSE"}, self.validator,
            )

    def test_single_selection_blocked(self):
        with self.assertRaises(ValueError):
            build_batch_candidate(
                self.rows, self.selected[:1], {}, self.validator,
            )

    def test_selected_values_are_trimmed(self):
        result = self.candidate({"sort_order": " 2 "})
        self.assertEqual(result[0]["sort_order"], "2")

    def test_callback_cannot_mutate_returned_candidate(self):
        def mutate(rows):
            rows[0]["active"] = "INVALID"
        self.validator.side_effect = mutate
        result = self.candidate({"sort_order": "2"})
        self.assertEqual(result[0]["active"], "TRUE")
        self.assertEqual(self.rows, self.before)

    def test_range_and_sort_validation(self):
        for field, value in (
            ("min_contributors", "-1"), ("preferred_contributors", "4"),
            ("max_contributors", ""), ("sort_order", "0"),
            ("active", "UNKNOWN"),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_row(dict(self.rows[0], **{field: value}))


if __name__ == "__main__":
    unittest.main()

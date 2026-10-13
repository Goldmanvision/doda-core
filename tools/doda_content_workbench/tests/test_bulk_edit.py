import copy
import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock
from doda_bulk_edit import BulkEditError, build_candidate, apply_to_draft


def field(name, kind="text", required=False, choices=()):
    return NS(name=name, label=name, kind=kind, required=required, choices=choices)


class BulkEditTests(unittest.TestCase):
    def setUp(self):
        self.spec = NS(table="example", key_columns=("id",), fields=(
            field("id", required=True), field("name", required=True),
            field("count", "int"), field("blank"), field("active", "bool"),
            field("choice", "choice", choices=("A", "B")),
            field("decimal", "decimal"), field("evidence", "evidence_multi"),
        ))
        self.rows = [
            dict(id="ONE", name="Same", count="3", blank="", active="false", choice="A", decimal="", evidence=""),
            dict(id="TWO", name="Same", count="7", blank="", active="false", choice="B", decimal="", evidence=""),
            dict(id="THREE", name="Other", count="9", blank="", active="false", choice="A", decimal="", evidence=""),
        ]

    def candidate(self, changes, indices=(0, 1)):
        return build_candidate(self.rows, indices, changes, self.spec)

    def test_empty_change_map_preserves_every_value(self):
        self.assertEqual(self.candidate({}), self.rows)

    def test_only_changed_fields_apply(self):
        result = self.candidate({"name": "New"})
        self.assertEqual([r["name"] for r in result], ["New", "New", "Other"])
        self.assertEqual([r["count"] for r in result], ["3", "7", "9"])
        self.assertEqual([r["blank"] for r in result], ["", "", ""])

    def test_source_rows_are_not_mutated(self):
        before = copy.deepcopy(self.rows)
        self.candidate({"count": "4"})
        self.assertEqual(self.rows, before)

    def test_explicit_clear(self):
        result = self.candidate({"count": ""})
        self.assertEqual([r["count"] for r in result], ["", "", "9"])

    def test_set_previously_blank(self):
        self.assertEqual(self.candidate({"blank": "value"})[1]["blank"], "value")

    def test_required_clear_rejected(self):
        with self.assertRaises(BulkEditError): self.candidate({"name": ""})

    def test_placeholder_rejected(self):
        with self.assertRaises(BulkEditError): self.candidate({"name": "Multiple values"})

    def test_evidence_placeholder_token_rejected(self):
        with self.assertRaises(BulkEditError): self.candidate({"evidence": "EVIDENCE_A;Multiple values"})

    def test_identity_change_rejected(self):
        with self.assertRaises(BulkEditError): self.candidate({"id": "NEW"})

    def test_composite_identity_protected(self):
        self.spec.key_columns = ("id", "choice")
        with self.assertRaises(BulkEditError): self.candidate({"choice": "B"})

    def test_unknown_field_rejected(self):
        with self.assertRaises(BulkEditError): self.candidate({"missing": "x"})

    def test_invalid_integer_rejected(self):
        with self.assertRaises(BulkEditError): self.candidate({"count": "4.5"})

    def test_invalid_boolean_rejected(self):
        with self.assertRaises(BulkEditError): self.candidate({"active": "yes"})

    def test_invalid_choice_rejected(self):
        with self.assertRaises(BulkEditError): self.candidate({"choice": "X"})

    def test_invalid_decimal_rejected(self):
        checker = Mock(side_effect=ValueError("invalid decimal"))
        with self.assertRaises(BulkEditError):
            build_candidate(self.rows, (0, 1), {"decimal": "bad"}, self.spec, checker)

    def test_invalid_selection_rejected(self):
        for indices in ((0,), (0, 0), (0, 9), (-1, 1)):
            with self.subTest(indices=indices), self.assertRaises(BulkEditError):
                self.candidate({}, indices)

    def editor(self):
        return NS(rows=copy.deepcopy(self.rows), dirty=False, spec=self.spec,
                  tree=NS(selection=lambda: ("0", "1")),
                  app=NS(project_root="root"), save=Mock())

    def test_full_validation_failure_is_atomic(self):
        editor = self.editor()
        before = copy.deepcopy(editor.rows)
        validate = Mock(return_value=NS(valid=False, errors=["row two fails"]))
        with self.assertRaises(BulkEditError):
            apply_to_draft(editor, ("0", "1"), before, {"count": "4"}, validate)
        self.assertEqual(editor.rows, before)
        self.assertFalse(editor.dirty)
        editor.save.assert_not_called()

    def test_validation_exception_preserves_draft(self):
        editor = self.editor()
        before = copy.deepcopy(editor.rows)
        with self.assertRaises(OSError):
            apply_to_draft(editor, ("0", "1"), before, {"count": "4"}, Mock(side_effect=OSError("read failed")))
        self.assertEqual(editor.rows, before)
        self.assertFalse(editor.dirty)

    def test_success_changes_draft_without_save(self):
        editor = self.editor()
        validate = Mock(return_value=NS(valid=True, errors=[]))
        self.assertTrue(apply_to_draft(editor, ("0", "1"), copy.deepcopy(editor.rows), {"count": "4"}, validate))
        self.assertEqual([r["count"] for r in editor.rows], ["4", "4", "9"])
        self.assertTrue(editor.dirty)
        editor.save.assert_not_called()
        validate.assert_called_once()

    def test_untouched_apply_does_not_validate_or_mark_dirty(self):
        editor = self.editor()
        validate = Mock()
        self.assertFalse(apply_to_draft(editor, ("0", "1"), copy.deepcopy(editor.rows), {}, validate))
        self.assertFalse(editor.dirty)
        validate.assert_not_called()

    def test_stale_draft_rejected(self):
        editor = self.editor()
        before = copy.deepcopy(editor.rows)
        editor.rows[0]["count"] = "10"
        with self.assertRaises(BulkEditError):
            apply_to_draft(editor, ("0", "1"), before, {"count": "4"}, Mock())
        self.assertEqual(editor.rows[0]["count"], "10")

    def test_stale_selection_rejected(self):
        editor = self.editor()
        editor.tree.selection = lambda: ("1", "2")
        with self.assertRaises(BulkEditError):
            apply_to_draft(editor, ("0", "1"), editor.rows, {"count": "4"}, Mock())

    def test_change_during_validation_rejected(self):
        editor = self.editor()
        before = copy.deepcopy(editor.rows)
        def validate(*_args):
            editor.rows[0]["count"] = "10"
            return NS(valid=True, errors=[])
        with self.assertRaises(BulkEditError):
            apply_to_draft(editor, ("0", "1"), before, {"count": "4"}, validate)
        self.assertEqual(editor.rows[0]["count"], "10")
        self.assertFalse(editor.dirty)

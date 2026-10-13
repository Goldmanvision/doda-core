import ast
import copy
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import doda_task_schema as schema
import doda_task_staffing_rules as staffing
import doda_task_prerequisite_rules as prerequisites
import doda_task_requirements_preview as preview


class TaskRequirementsPreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.template = dict.fromkeys(schema.COLUMNS, "")
        self.template.update(
            task_template_id="INVESTIGATE", display_name="Investigate",
            description="Draft task", priority="NORMAL", target_type="TERRITORY",
            loop_task="TRUE", reward_mode="CONTINUOUS", payout_count="0",
            sort_order="10", active="FALSE",
        )
        self.staff = dict(
            taskTemplateId="INVESTIGATE", personnelRole="AGENT",
            minContributors=1, preferredContributors=1, maxContributors=2,
            sortOrder=10, active=False,
        )
        self.pistol = dict(
            prerequisiteId="PRE_PISTOL", taskTemplateId="INVESTIGATE",
            requirementKind="WEAPON_TYPE", scope="PER_ASSIGNED_AGENT",
            personnelRole="AGENT", requirementValue="PISTOL", minQuantity=1,
            description="Pistol per agent.", sortOrder=10, active=False,
        )
        self.vehicle = dict(
            self.pistol, prerequisiteId="PRE_VEHICLE",
            requirementKind="MOTOR_VEHICLE", scope="TASK",
            personnelRole=None, requirementValue=None,
            description="One shared vehicle.", sortOrder=20,
        )
        self.write("task_templates.csv", schema.COLUMNS, [self.template])
        self.write(staffing.STAFFING_FILE, staffing.COLUMNS, [
            dict(zip(staffing.COLUMNS, (
                "INVESTIGATE", "AGENT", "1", "1", "2", "10", "false",
            )))
        ])
        self.pre_rows = [dict(zip(prerequisites.COLUMNS, (
            "PRE_PISTOL", "INVESTIGATE", "WEAPON_TYPE", "PER_ASSIGNED_AGENT",
            "AGENT", "PISTOL", "1", "Pistol per agent.", "10", "false",
        )))]
        self.write(
            prerequisites.PREREQUISITES_FILE, prerequisites.COLUMNS, self.pre_rows
        )

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, columns, rows):
        with (self.src / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def model(self):
        return preview.build_preview(
            self.template, [self.staff], [self.pistol, self.vehicle]
        )

    def test_join_filters_template(self):
        other = dict(self.pistol, taskTemplateId="OTHER")
        model = preview.build_preview(
            self.template, [self.staff], [self.pistol, other]
        )
        self.assertEqual(model["prerequisites"], [self.pistol])

    def test_no_input_aliasing(self):
        original = copy.deepcopy((self.template, self.staff, self.pistol))
        model = self.model()
        model["template"]["active"] = "TRUE"
        model["staffingRules"][0]["minContributors"] = 99
        model["prerequisites"][0]["minQuantity"] = 99
        self.assertEqual(original, (self.template, self.staff, self.pistol))

    def test_staffing_counts(self):
        self.assertIn(
            "AGENT: minimum=1; preferred=1; maximum=2",
            preview.render_preview(self.model()),
        )

    def test_unspecified_maximum(self):
        model = self.model()
        model["staffingRules"][0]["maxContributors"] = None
        text = preview.render_preview(model)
        self.assertIn("maximum=UNSPECIFIED", text)
        self.assertIn("not confirmation of unlimited staffing", text)

    def test_per_agent_scope(self):
        text = preview.render_preview(self.model())
        self.assertIn("PER-ASSIGNED-AGENT PREREQUISITES", text)
        self.assertIn("value=PISTOL", text)
        self.assertIn("separately to EACH assigned agent", text)

    def test_task_vehicle_quantity(self):
        text = preview.render_preview(self.model())
        self.assertIn("PRE_VEHICLE: MOTOR_VEHICLE; minimum=1", text)
        self.assertIn("Task-wide minimum applies once", text)
        self.assertIn("Vehicle quantity is not team capacity", text)

    def test_absent_rules_not_no_requirements(self):
        text = preview.render_preview(
            preview.build_preview(self.template, [], [])
        )
        self.assertIn("does not establish that no personnel are required", text)
        self.assertIn("absence is not confirmation of no requirements", text)

    def test_blank_quantity_unconfigured(self):
        model = self.model()
        model["prerequisites"][0]["minQuantity"] = None
        self.assertIn(
            "WEAPON_TYPE; minimum=UNCONFIGURED",
            preview.render_preview(model),
        )

    def test_inactive_definition_display(self):
        self.assertIn("INACTIVE DRAFT", preview.render_preview(self.model()))

    def test_boundaries(self):
        model = self.model()
        self.assertTrue(model["savedSourceOnly"])
        for key in (
            "runtimeImplemented", "inventoryChecked",
            "eligibilityChecked", "allocationImplemented",
        ):
            self.assertFalse(model[key])
        self.assertNotIn("eligible", model)

    def test_load_saved_without_writes(self):
        before = preview.source_hashes(self.src)
        models, warnings = preview.load_previews(self.root)
        self.assertEqual(models[0]["staffingRules"][0]["maxContributors"], 2)
        self.assertEqual(models[0]["prerequisites"][0]["minQuantity"], 1)
        self.assertEqual(preview.source_hashes(self.src), before)
        self.assertFalse((self.root / "generated").exists())

    def test_invalid_quantity_blocks_load(self):
        self.pre_rows[0]["min_quantity"] = "0"
        self.write(
            prerequisites.PREREQUISITES_FILE, prerequisites.COLUMNS, self.pre_rows
        )
        with self.assertRaises(ValueError):
            preview.load_previews(self.root)

    def test_missing_source_blocks_load(self):
        (self.src / prerequisites.PREREQUISITES_FILE).unlink()
        with self.assertRaises((OSError, ValueError)):
            preview.load_previews(self.root)

    def test_wrong_template_header_blocks_load(self):
        (self.src / "task_templates.csv").write_text(
            "task_template_id,active\nINVESTIGATE,false\n", encoding="utf-8"
        )
        with self.assertRaises(ValueError):
            preview.load_previews(self.root)

    def test_changed_snapshot_blocks_load(self):
        with patch.object(
            preview, "source_hashes",
            side_effect=[{"x": "before"}, {"x": "after"}],
        ):
            with self.assertRaisesRegex(ValueError, "Source changed"):
                preview.load_previews(self.root)

    def test_saved_selection(self):
        models = [self.model()]
        self.assertEqual(preview.initial_index(models, None), 0)
        self.assertEqual(preview.initial_index([], None), -1)
        self.assertEqual(preview.initial_index(models, "INVESTIGATE"), 0)
        with self.assertRaises(ValueError):
            preview.initial_index(models, "UNSAVED")

    def test_button_wiring(self):
        w = Path(__file__).resolve().parents[1]
        shared = (w / "doda_network_editor.py").read_text(encoding="utf-8-sig")
        tasks = (w / "doda_task_templates_editor.py").read_text(encoding="utf-8-sig")
        for source in (shared, tasks):
            ast.parse(source)
            self.assertIn("Preview Saved Requirements", source)
            self.assertIn("open_task_requirements_preview(", source)
        self.assertIn(
            'self.spec.table in ("task_staffing_rules", "task_prerequisites")',
            shared,
        )

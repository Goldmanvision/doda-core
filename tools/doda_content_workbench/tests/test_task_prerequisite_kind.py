import inspect
import unittest
from types import SimpleNamespace
import doda_network_editor as editor


class Scalar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class Widget:
    def __init__(self):
        self.values = ()

    def configure(self, **kwargs):
        self.values = tuple(kwargs["values"])


class TaskPrerequisiteKindTests(unittest.TestCase):
    def fake(self, kind, scope="TASK", role="", value="PISTOL"):
        fields = {
            "requirement_kind": kind, "scope": scope, "personnel_role": role,
            "requirement_value": value, "min_quantity": "",
            "description": "Keep this.", "active": "false",
        }
        fake = SimpleNamespace(
            vars={key: Scalar(value) for key, value in fields.items()},
            widgets={key: Widget() for key in (
                "scope", "personnel_role", "requirement_value"
            )},
        )
        fake._prerequisite_choices = lambda: editor.NetworkTableEditor._prerequisite_choices(fake)
        return fake

    def change(self, fake):
        editor.NetworkTableEditor._prerequisite_kind_changed(fake)

    def test_weapon_sets_scope_role_keeps_type(self):
        fake = self.fake("WEAPON_TYPE")
        self.change(fake)
        self.assertEqual(fake.vars["scope"].get(), "PER_ASSIGNED_AGENT")
        self.assertEqual(fake.vars["personnel_role"].get(), "AGENT")
        self.assertEqual(fake.vars["requirement_value"].get(), "PISTOL")
        self.assertEqual(fake.widgets["requirement_value"].values,
                         ("",) + tuple(editor.weapon_rules.WEAPON_TYPES))

    def test_weapon_clears_invalid_type(self):
        fake = self.fake("WEAPON_TYPE", value="WPN_BERETTA_M92")
        self.change(fake)
        self.assertEqual(fake.vars["requirement_value"].get(), "")

    def test_receptacle_sets_agent_and_clears_value(self):
        fake = self.fake("APPLICABLE_COLLECTION_RECEPTACLE")
        self.change(fake)
        self.assertEqual(fake.vars["scope"].get(), "PER_ASSIGNED_AGENT")
        self.assertEqual(fake.vars["personnel_role"].get(), "AGENT")
        self.assertEqual(fake.vars["requirement_value"].get(), "")
        self.assertEqual(fake.widgets["requirement_value"].values, ("",))

    def test_vehicle_sets_task_and_clears_role_value(self):
        fake = self.fake("MOTOR_VEHICLE", scope="PER_ASSIGNED_AGENT", role="AGENT")
        self.change(fake)
        self.assertEqual(fake.vars["scope"].get(), "TASK")
        self.assertEqual(fake.vars["personnel_role"].get(), "")
        self.assertEqual(fake.vars["requirement_value"].get(), "")
        self.assertEqual(fake.widgets["scope"].values, ("TASK",))

    def test_refresh_preserves_stored_values(self):
        fake = self.fake("MOTOR_VEHICLE", scope="PER_ASSIGNED_AGENT", role="AGENT")
        before = {key: value.get() for key, value in fake.vars.items()}
        fake._prerequisite_choices()
        self.assertEqual({key: value.get() for key, value in fake.vars.items()}, before)

    def test_quantity_description_active_unchanged(self):
        for kind in ("WEAPON_TYPE", "APPLICABLE_COLLECTION_RECEPTACLE", "MOTOR_VEHICLE"):
            with self.subTest(kind=kind):
                fake = self.fake(kind)
                self.change(fake)
                self.assertEqual(fake.vars["min_quantity"].get(), "")
                self.assertEqual(fake.vars["description"].get(), "Keep this.")
                self.assertEqual(fake.vars["active"].get(), "false")

    def test_blank_unknown_kind_preserve_values(self):
        for kind in ("", "UNKNOWN"):
            fake = self.fake(kind)
            before = {key: value.get() for key, value in fake.vars.items()}
            self.change(fake)
            self.assertEqual({key: value.get() for key, value in fake.vars.items()}, before)
            self.assertEqual(fake.widgets["scope"].values, ())

    def test_binding_and_refresh_hooks(self):
        build = inspect.getsource(editor.NetworkTableEditor._build)
        self.assertIn('"<<ComboboxSelected>>", self._prerequisite_kind_changed', build)
        refresh = inspect.getsource(editor.NetworkTableEditor._ref_choices)
        self.assertIn('self.spec.table == "task_prerequisites"', refresh)
        self.assertIn("self._prerequisite_choices()", refresh)
        for name in ("_on_select", "_clear_form", "paste_csv"):
            self.assertIn("self._ref_choices()",
                          inspect.getsource(getattr(editor.NetworkTableEditor, name)))

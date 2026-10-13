import unittest
import doda_task_schema as schema

class TaskSchemaTests(unittest.TestCase):
    def row(self):
        return dict(task_template_id="T", display_name="Task", description="Work.",
                    capability_id="C", priority="NORMAL", target_type="TERRITORY",
                    target_family_id="", loop_task=False, time_to_complete_minutes=None,
                    reward_mode="CONTINUOUS", payout_count=0, sort_order=1, active=True)
    def test_open_ended(self):
        self.assertEqual(schema.errors(self.row(), {"NORMAL"}), [])
    def test_active_loop_requires_duration(self):
        row = self.row(); row["loop_task"] = True
        self.assertTrue(schema.errors(row, {"NORMAL"}))
        row["time_to_complete_minutes"] = 10
        self.assertEqual(schema.errors(row, {"NORMAL"}), [])
    def test_drafts_can_be_unconfigured(self):
        row = self.row(); row.update(active=False, capability_id="", loop_task=True)
        self.assertEqual(schema.errors(row, {"NORMAL"}), [])
    def test_station_contract(self):
        row = self.row(); row["target_type"] = "STATION"
        self.assertTrue(schema.errors(row, {"NORMAL"}))
        row["target_family_id"] = "PAPER_FORENSICS"
        self.assertEqual(schema.errors(row, {"NORMAL"}), [])
        row["target_type"] = "TERRITORY"
        self.assertTrue(schema.errors(row, {"NORMAL"}))
    def test_undercover_intervals(self):
        for days in (7, 14, 31):
            row=self.row(); row.update(reward_mode="PERIODIC_LUMP_SUM", payout_count=3,
                                      time_to_complete_minutes=days*1440)
            self.assertEqual(schema.errors(row, {"NORMAL"}), [])
            self.assertEqual(row["time_to_complete_minutes"] // 3, days*480)
    def test_periodic_missing_and_indivisible(self):
        row=self.row(); row.update(reward_mode="PERIODIC_LUMP_SUM", payout_count=3)
        self.assertTrue(schema.errors(row, {"NORMAL"}))
        row["time_to_complete_minutes"]=10
        self.assertTrue(schema.errors(row, {"NORMAL"}))
    def test_bad_fields(self):
        for field,value in (("priority","BAD"),("loop_task","maybe"),
                            ("time_to_complete_minutes",0),("payout_count",-1),
                            ("time_to_complete_minutes",1.5),("sort_order",0)):
            row=self.row(); row[field]=value
            self.assertTrue(schema.errors(row,{"NORMAL"}),field)
    def test_removed_columns_and_csv_types(self):
        self.assertNotIn("default_" + "deadline_minutes",schema.COLUMNS)
        self.assertNotIn("default_target_" + "effort_minutes",schema.COLUMNS)
        self.assertNotIn("auto_" + "allocate",schema.COLUMNS)
        row=self.row(); row.update(active="TRUE", loop_task="FALSE", payout_count="0",
                                  sort_order="1", time_to_complete_minutes="")
        self.assertEqual(schema.errors(row,{"NORMAL"}),[])

import ast
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "doda_foims_x_preview.py").read_text(
    encoding="utf-8-sig"
)

def preview_class():
    tree = ast.parse(SOURCE)
    return next(
        n for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "FoimsXPreview"
    )

class DebugPanelStructureTests(unittest.TestCase):
    def test_panel_methods_exist(self):
        names = {n.name for n in preview_class().body if isinstance(n, ast.FunctionDef)}
        for name in ("toggle_debug", "show_debug", "hide_debug", "is_open"):
            self.assertIn(name, names)

    def test_controls_live_in_debug_window(self):
        self.assertIn("self.controls = ttk.Frame(self.debug_window", SOURCE)
        self.assertIn("self.toolbar_frame = ttk.Frame(self.window", SOURCE)

    def test_fullscreen_uses_toolbar_not_controls(self):
        self.assertIn("self.toolbar_frame.pack_forget()", SOURCE)
        self.assertNotIn("self.controls.pack_forget", SOURCE)
        self.assertNotIn("self.controls.pack(fill=tk.X", SOURCE)

if __name__ == "__main__":
    unittest.main()

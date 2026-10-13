import unittest
from doda_foims_x_catalog_layout import header_layout, detail_pages, sidebar_pages

class CatalogHeaderTests(unittest.TestCase):
    def geometry(self, title="Catalog", left="Tasks",
                 title_width=584, left_width=160):
        return header_layout(
            title, left, "Selected Entry Details", len, len,
            title_width, left_width, 394
        )

    def test_short_headers_preserve_original_positions(self):
        g = self.geometry()
        self.assertEqual(g["banner_bottom"], 48)
        self.assertEqual(g["panel_top"], 58)
        self.assertEqual(g["body_top"], 92)

    def test_long_left_heading_wraps_and_reserves_space(self):
        g = self.geometry(left="Task Templates", left_width=10)
        self.assertEqual(g["left_lines"], ["Task", "Templates"])
        self.assertEqual(g["body_top"], 108)
        self.assertLess(g["detail_page_size"], self.geometry()["detail_page_size"])

    def test_title_wraps_without_losing_words(self):
        title = "FOIMS-X / LONG CATALOG TITLE / READ-ONLY CATALOG"
        g = self.geometry(title=title, title_width=25)
        self.assertGreater(len(g["title_lines"]), 1)
        self.assertEqual(" ".join(g["title_lines"]), title)
        self.assertTrue(all(len(line) <= 25 for line in g["title_lines"]))
        self.assertGreater(g["panel_top"], 58)

    def test_body_pagination_respects_wrapped_headers(self):
        g = self.geometry(left="Long Panel Heading", left_width=10)
        pages = detail_pages(
            ["description " * 100], len, 30,
            page_size=g["detail_page_size"]
        )
        for page in pages:
            self.assertLessEqual(
                g["body_top"] + (len(page) - 1) * 15, 435
            )
        rows = [{"facility_id": str(i), "display_name": "Undercover Investigation - 31 Days"}
                for i in range(13)]
        lists = sidebar_pages(rows, len, 18, height=g["sidebar_height"])
        self.assertEqual(sum(len(page) for page in lists), 13)
        self.assertTrue(all(sum(h for _, _, h in page) <= g["sidebar_height"]
                            for page in lists))

import unittest
from doda_foims_x_catalog_layout import wrap_lines, detail_pages, sidebar_pages

class CatalogLayoutTests(unittest.TestCase):
    def test_full_undercover_names_preserved(self):
        rows = [
            {"facility_id": str(days),
             "display_name": "Undercover Investigation - %d Days" % days}
            for days in (7, 14, 31)
        ]
        pages = sidebar_pages(rows, len, 18)
        names = [" ".join(lines) for page in pages for _, lines, _ in page]
        self.assertEqual(names, [r["display_name"] for r in rows])

    def test_measured_width_not_character_count(self):
        measure = lambda text: sum(3 if c == "W" else 1 for c in text)
        lines = wrap_lines(["WWW iii WWW"], measure, 10)
        self.assertTrue(all(measure(line) <= 10 for line in lines))
        self.assertEqual(" ".join(lines), "WWW iii WWW")

    def test_long_identifier_not_lost(self):
        value = "LONG_IDENTIFIER_WITHOUT_SPACES"
        lines = wrap_lines([value], len, 8)
        self.assertEqual("".join(lines), value)
        self.assertTrue(all(len(line) <= 8 for line in lines))

    def test_sidebar_pages_fit(self):
        rows = [{"facility_id": str(i), "display_name": "Undercover Investigation - 31 Days"}
                for i in range(13)]
        pages = sidebar_pages(rows, len, 18, height=150)
        self.assertGreater(len(pages), 1)
        self.assertEqual(sum(len(page) for page in pages), 13)
        self.assertTrue(all(sum(h for _, _, h in page) <= 150 for page in pages))

    def test_detail_pages_and_empty(self):
        pages = detail_pages(["A long description " * 20], len, 20, page_size=3)
        self.assertGreater(len(pages), 1)
        self.assertTrue(all(len(page) <= 3 for page in pages))
        self.assertTrue(all(len(line) <= 20 for page in pages for line in page))
        self.assertEqual(detail_pages([], len, 20), [[""]])

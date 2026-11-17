"""Every book of the Bible has a coloring storybook: pages with a real chapter, one of the drawings, a
short paragraph and a lesson, all fitting on US Letter paper."""
import contextlib
import io
import tempfile
import unittest
import xml.dom.minidom
from pathlib import Path

from coe.art import H, TEXT_WRAP, W, cover_layout, draw_cover, draw_story_page, page_layout, wrap
from coe.books import BIBLE, BOOKS, BadReference
from coe.cli import main
from coe.picture import FOLDER, catalog, path_data
from coe.storybook import book_id, chapters, storybook, written


def all_pages():
    for b in written():
        book = storybook(b)
        for n, page in enumerate(book["pages"], 1):
            yield book, n, page


class Books(unittest.TestCase):
    def test_every_book_of_the_bible_has_a_storybook(self):
        self.assertEqual(written(), [b[0] for b in BIBLE])

    def test_every_page_has_its_parts_and_a_real_chapter(self):
        for book, n, page in all_pages():
            where = f"{book['label']} page {n}"
            self.assertTrue({"title", "chapter", "picture", "scene", "text", "lesson"} <= set(page), where)
            self.assertTrue(set(page) <= {"title", "chapter", "to", "picture", "scene", "text", "lesson"}, where)
            last = page.get("to", page["chapter"])
            self.assertTrue(1 <= page["chapter"] < last + 1 <= BOOKS[book["label"]] + 1, where)
            self.assertLessEqual(len(page["text"].split()), 60, where)    # short enough for a child to read
            self.assertTrue(page["lesson"].endswith((".", "!")), where)
            self.assertLessEqual(len(page["title"]), 34, where)

    def test_every_picture_is_one_of_the_drawings(self):
        ids = {p["id"] for p in catalog()}
        for b in written():
            self.assertIn(storybook(b)["cover"], ids, b)
        for book, n, page in all_pages():
            self.assertIn(page["picture"], ids, f"{book['label']} page {n}")

    def test_books_are_found_by_any_name(self):
        self.assertEqual(book_id("1 kingdoms"), "1 Samuel")
        self.assertEqual(book_id("Susanna"), "sus")
        self.assertEqual(storybook("susanna")["label"], "Susanna")
        self.assertEqual(chapters(storybook("Genesis"), storybook("Genesis")["pages"][2]), "Genesis 6–9")
        with self.assertRaises(BadReference):
            storybook("Hezekiah")


class Pages(unittest.TestCase):
    def test_sixty_traced_drawings_each_with_its_file(self):
        self.assertEqual(len(catalog()), 60)
        for p in catalog():
            svg = (FOLDER / f"{p['id']}.svg").read_text(encoding="utf-8")
            self.assertIn(f'viewBox="0 0 {p["width"]} {p["height"]}"', svg, p["id"])
            self.assertTrue(path_data(p["id"]).startswith("M"), p["id"])

    def test_every_page_and_cover_fits_on_letter_paper(self):
        for book, n, page in all_pages():
            plan = page_layout(page)
            x, y, w, h, _ = plan["box"]
            self.assertTrue(x >= 40 and x + w <= W - 40, f"{book['label']} page {n}")
            self.assertLessEqual(plan["bottom"], H - 50, f"{book['label']} page {n}")
            self.assertTrue(all(len(line) <= TEXT_WRAP for line in plan["lines"]))
        for b in written():
            self.assertLessEqual(cover_layout(storybook(b))["bottom"], H - 40, b)

    def test_pages_are_valid_svg_with_all_their_words(self):
        book = storybook("Genesis")
        for n, page in enumerate(book["pages"], 1):
            root = xml.dom.minidom.parseString(draw_story_page(book, n)).documentElement
            self.assertEqual((root.getAttribute("width"), root.getAttribute("height")), ("8.5in", "11in"))
            words = " ".join(t.firstChild.data for t in root.getElementsByTagName("text"))
            self.assertIn(" ".join(wrap(page["text"], TEXT_WRAP)), words)
            self.assertIn(page["lesson"], words)
            self.assertIn(chapters(book, page), words)
        cover = draw_cover(book)
        xml.dom.minidom.parseString(cover)
        self.assertIn("A Coloring Storybook", cover)


class Command(unittest.TestCase):
    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = main(list(args))
        return code, out.getvalue()

    def test_list_books_and_save_one(self):
        code, text = self.run_cli("books")
        self.assertEqual(code, 0)
        self.assertIn("Genesis", text)
        with tempfile.TemporaryDirectory() as tmp:
            code, text = self.run_cli("book", "Ruth", "--out", tmp)
            self.assertEqual(code, 0)
            self.assertEqual(len(list((Path(tmp) / "ruth").glob("*.svg"))), 1 + len(storybook("Ruth")["pages"]))

    def test_a_wrong_book_name_explains_itself(self):
        code, text = self.run_cli("book", "Hezekiah")
        self.assertEqual(code, 1)
        self.assertIn("no book called", text)


if __name__ == "__main__":
    unittest.main()

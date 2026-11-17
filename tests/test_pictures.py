import unittest
import xml.dom.minidom

from coe.art import H, draw_page, picture_layout
from coe.picture import FOLDER, catalog, choose, path_data
from coe.scenes import plan_page
from coe.text import BUNDLED, Chapter

DANIEL_6 = Chapter("Daniel", 6, [
    (1, "It pleased Darius to set over the kingdom one hundred twenty local governors."),
    (16, "Then the king commanded, and they brought Daniel, and cast him into the den of lions."),
    (22, "My God has sent his angel, and has shut the lions' mouths, and they have not hurt me."),
    (27, "He has delivered Daniel from the power of the lions."),
])


class Pictures(unittest.TestCase):
    def test_sixty_traced_drawings_each_with_its_file(self):
        pics = catalog()
        self.assertEqual(len(pics), 60)
        self.assertEqual(len({p["id"] for p in pics}), 60)
        for kind in ("animals", "places", "people"):
            self.assertEqual(sum(p["id"].startswith(kind + "/") for p in pics), 20, kind)
        for p in pics:
            svg = (FOLDER / f"{p['id']}.svg").read_text()
            self.assertIn(f'viewBox="0 0 {p["width"]} {p["height"]}"', svg, p["id"])
            self.assertTrue(path_data(p["id"]).startswith("M"), p["id"])
            self.assertEqual(p["words"], [w.lower() for w in p["words"]], p["id"])

    def test_a_picture_needs_three_mentions(self):
        self.assertEqual(choose("the lion, the lions, and a lioness"), "animals/lion")
        self.assertIsNone(choose("a lion and another lion"))
        self.assertEqual(choose("Pharaoh said to Pharaoh's servants that Pharaoh would go"), "people/egyptian-man")

    def test_the_chapters_that_ship_keep_their_drawn_pages(self):
        for ref, verses in BUNDLED.items():
            book, n = ref.rsplit(" ", 1)
            self.assertIsNone(plan_page(Chapter(book, int(n), list(enumerate(verses, 1)))).picture, ref)

    def test_a_picture_page_shows_a_verse_that_names_it(self):
        plan = plan_page(DANIEL_6)
        self.assertEqual(plan.picture, "animals/lion")
        self.assertEqual(plan.verse[0], 16)

    def test_a_picture_page_is_valid_and_fits_on_the_page(self):
        plan = plan_page(DANIEL_6)
        svg = draw_page(plan)
        root = xml.dom.minidom.parseString(svg).documentElement
        self.assertEqual((root.getAttribute("width"), root.getAttribute("height")), ("8.5in", "11in"))
        self.assertIn("Daniel 6:16 (WEB)", svg)
        self.assertIn('fill-rule="evenodd"', svg)
        self.assertNotIn("nan", svg.lower().replace("daniel", ""))
        for p in catalog():
            x, y, w, h = picture_layout(p["width"], p["height"], 4)
            self.assertGreaterEqual(y, 30, p["id"])
            self.assertLessEqual(y + h + 60 + 28 + 4 * 36 + 64, H - 20, p["id"])


class Command(unittest.TestCase):
    def test_choose_a_picture_or_none_from_the_command_line(self):
        import io
        from contextlib import redirect_stdout
        from coe.cli import main
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["plan", "Psalms", "23", "--picture", "people/shepherd"]), 0)
            self.assertEqual(main(["plan", "Psalms", "23", "--picture", "none"]), 0)
            self.assertEqual(main(["pictures"]), 0)
        text = out.getvalue()
        self.assertIn("Picture:    Shepherd (people/shepherd)", text)
        self.assertIn("Verse 1: Yahweh is my shepherd", text)
        self.assertIn("In front:", text)
        self.assertEqual(text.count("\n"), 3 + 4 + 60)

import re
import unittest
import xml.dom.minidom

from coe.art import BACKGROUND_ART, FOREGROUND_ART, draw_page, wrap
from coe.scenes import MOTIF_WORDS, Plan


def plan(bg=("sun", "waves"), fg=("sheep", "tree"), verse=(1, "The LORD is my shepherd; I shall not want.")):
    return Plan("Psalms 23", list(bg) + list(fg), list(bg), list(fg), verse)


class Art(unittest.TestCase):
    def test_every_motif_the_planner_can_pick_has_a_drawing(self):
        self.assertEqual(set(MOTIF_WORDS), set(BACKGROUND_ART) | set(FOREGROUND_ART))

    def test_a_page_is_valid_letter_size_svg(self):
        svg = draw_page(plan())
        doc = xml.dom.minidom.parseString(svg)
        root = doc.documentElement
        self.assertEqual((root.getAttribute("width"), root.getAttribute("height")), ("8.5in", "11in"))
        self.assertIn("Psalms 23:1 (WEB)", svg)

    def test_only_outlines_to_color_in(self):
        svg = draw_page(plan(bg=list(BACKGROUND_ART), fg=list(FOREGROUND_ART)))
        fills = set(re.findall(r'fill="([^"]+)"', svg))
        self.assertLessEqual(fills, {"#fff", "none", "#111"})       # #111 is only for eyes and the text
        self.assertEqual(set(re.findall(r'stroke="([^"]+)"', svg)), {"#111"})

    def test_every_drawing_renders_on_its_own(self):
        for m in FOREGROUND_ART:
            xml.dom.minidom.parseString(draw_page(plan(bg=["mountains"], fg=[m])))
        for m in BACKGROUND_ART:
            xml.dom.minidom.parseString(draw_page(plan(bg=[m], fg=["tree"])))

    def test_the_same_chapter_always_draws_the_same_page(self):
        self.assertEqual(draw_page(plan()), draw_page(plan()))
        self.assertNotEqual(draw_page(plan()), draw_page(plan(), seed="another"))

    def test_verses_are_wrapped_and_escaped(self):
        lines = wrap("word " * 40, 30)
        self.assertTrue(all(len(l) <= 30 for l in lines))
        svg = draw_page(plan(verse=(3, "Fish & <loaves>")))
        self.assertIn("Fish &amp; &lt;loaves&gt;", svg)


if __name__ == "__main__":
    unittest.main()

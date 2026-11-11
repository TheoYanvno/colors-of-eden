import json
import tempfile
import unittest
from pathlib import Path

from coe.books import BOOKS, BadReference, check, find_book
from coe.scenes import motif_counts, plan_page
from coe.text import BUNDLED, Chapter, load_chapter


def offline(url):
    raise OSError("no network in tests")


class Books(unittest.TestCase):
    def test_all_66_books_and_their_chapters(self):
        self.assertEqual(len(BOOKS), 66)
        self.assertEqual(sum(BOOKS.values()), 1189)
        self.assertEqual(find_book("  1   john "), "1 John")
        self.assertEqual(find_book("Psalm"), "Psalms")
        self.assertEqual(check("genesis", "50"), ("Genesis", 50))
        for bad in [("Genesis", 51), ("Genesis", 0), ("Hezekiah", 1), ("Jude", "two")]:
            with self.assertRaises(BadReference, msg=bad):
                check(*bad)


class Text(unittest.TestCase):
    def test_fetches_once_then_reads_the_cache(self):
        calls = []
        def fake(url):
            calls.append(url)
            return json.dumps({"verses": [{"chapter": 1, "verse": 1, "text": "Jonah  text\n"},
                                          {"chapter": 1, "verse": 2, "text": "More text."}]}).encode()
        with tempfile.TemporaryDirectory() as d:
            ch = load_chapter("jonah", 1, cache=Path(d), get=fake)
            again = load_chapter("Jonah", 1, cache=Path(d), get=offline)
        self.assertEqual(len(calls), 1)
        self.assertIn("translation=kjv", calls[0])
        self.assertEqual(ch.verses[0], (1, "Jonah text"))      # spaces and line breaks tidied
        self.assertEqual(again, ch)
        self.assertEqual(ch.reference, "Jonah 1")

    def test_bundled_chapters_work_offline_and_others_explain_the_problem(self):
        ch = load_chapter("Psalms", 23, cache=None, get=offline)
        self.assertEqual(len(ch.verses), 6)
        self.assertTrue(ch.verses[0][1].startswith("The LORD is my shepherd"))
        with self.assertRaisesRegex(ConnectionError, "internet"):
            load_chapter("Ruth", 1, cache=None, get=offline)


class Scenes(unittest.TestCase):
    def test_words_point_to_motifs(self):
        c = motif_counts("The LORD is my shepherd; he leadeth me beside the still waters.")
        self.assertEqual(c["sheep"], 3)                 # specific things count three times
        self.assertEqual(c["waves"], 1)
        self.assertNotIn("fish", c)

    def test_psalm_23_gets_sheep_and_a_short_verse(self):
        plan = plan_page(Chapter("Psalms", 23, list(enumerate(BUNDLED["Psalms 23"], 1))))
        self.assertIn("sheep", plan.motifs)
        self.assertTrue(plan.background and plan.foreground)
        self.assertLessEqual(len(plan.verse[1]), 160)

    def test_creation_gets_sky_and_water(self):
        plan = plan_page(Chapter("Genesis", 1, list(enumerate(BUNDLED["Genesis 1"], 1))))
        for m in ("sun", "waves"):
            self.assertIn(m, plan.motifs)

    def test_a_chapter_with_no_cues_still_gets_a_page(self):
        plan = plan_page(Chapter("Philemon", 1, [(1, "Paul, a prisoner, unto Philemon.")]))
        self.assertTrue(plan.background and plan.foreground)


if __name__ == "__main__":
    unittest.main()

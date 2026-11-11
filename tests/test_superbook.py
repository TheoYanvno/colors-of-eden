"""SuperBook is the reference for the Bible here. When SuperBook is checked out next to this repo, check
that our list of books still matches its BIBLE list exactly."""
import ast
import pathlib
import re
import unittest

from coe.books import BIBLE

SRC = pathlib.Path(__file__).resolve().parents[2] / "superbook" / "src" / "books.js"


@unittest.skipUnless(SRC.exists(), "SuperBook is not checked out next to Colors of Eden")
class MatchesSuperBook(unittest.TestCase):
    def test_same_books_same_order_same_labels(self):
        body = re.search(r"export const BIBLE = \[(.*?)\n\];", SRC.read_text(), re.S).group(1)
        theirs = [(b[0], b[1], b[2] if len(b) > 2 else b[0]) for b in ast.literal_eval("[" + body + "]")]
        self.assertEqual(BIBLE, theirs)

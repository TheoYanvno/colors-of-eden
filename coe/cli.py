"""`python -m coe books` lists the storybooks; `book Genesis` saves a book's cover and pages; `pictures`
lists the drawings."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .art import draw_cover, draw_story_page
from .books import BIBLE, BadReference
from .picture import catalog
from .storybook import storybook, written


def save_book(book: dict, out: Path) -> Path:
    """Save the cover as 00-cover.svg and the pages as 01-<title>.svg and on, in out/<book>/."""
    folder = out / re.sub(r"[^a-z0-9]+", "-", book["label"].lower()).strip("-")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "00-cover.svg").write_text(draw_cover(book), encoding="utf-8")
    for n, page in enumerate(book["pages"], 1):
        name = re.sub(r"[^a-z0-9]+", "-", page["title"].lower()).strip("-")
        (folder / f"{n:02d}-{name}.svg").write_text(draw_story_page(book, n), encoding="utf-8")
    return folder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="coe", description="Coloring storybooks of the Bible.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("books", help="list the books and how many pages each storybook has")
    b = sub.add_parser("book", help="save a book's cover and pages as SVG files, ready to print")
    b.add_argument("name", nargs="+", help='the book, e.g. Genesis, "1 Samuel" or Tobit')
    b.add_argument("--out", default="out", help="folder for the pages (default: out)")
    sub.add_parser("pictures", help="list the drawings")
    args = parser.parse_args(argv)
    if args.cmd == "books":
        have = set(written())
        for book_id, _, label in BIBLE:
            print(f"{label:<28} {len(storybook(book_id)['pages']):>2} pages" if book_id in have else f"{label:<28} not written yet")
        return 0
    if args.cmd == "pictures":
        for pic in catalog():
            print(f"{pic['id']:<28} {pic['label']}")
        return 0
    try:
        book = storybook(" ".join(args.name))
    except (KeyError, BadReference) as e:
        print(e.args[0], file=sys.stderr)
        return 1
    folder = save_book(book, Path(args.out))
    print(f"Saved the cover and {len(book['pages'])} pages of {book['label']} in {folder}/ (print them at 100% on US Letter paper)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

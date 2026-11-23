"""The coloring storybooks: any book of the Bible told for children ages 5 to 8, one page per story, each
page a drawing of its scene to color with a short paragraph to read. Each book is coe/storybook/<id>.json,
named by the book's id in SuperBook's list (Genesis.json, 1 Samuel.json, sus.json for Susanna)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .books import BIBLE, find_book

FOLDER = Path(__file__).parent / "storybook"
LABELS = {book_id: label for book_id, _, label in BIBLE}


def written() -> list[str]:
    """The ids of the books that have a storybook so far, in Bible order."""
    have = {p.stem for p in FOLDER.glob("*.json")}
    return [book_id for book_id, _, _ in BIBLE if book_id in have]


def book_id(name: str) -> str:
    """The id of a book given any of its names ("1 Kingdoms", "susanna")."""
    label = find_book(name)
    return next(i for i, lbl in LABELS.items() if lbl == label)


@lru_cache(maxsize=None)
def storybook(name: str) -> dict:
    """One book's storybook: book (its id), label, cover (a picture), about and pages. Each page has a
    title, chapter (and "to" when it runs over several), picture and text."""
    bid = book_id(name)
    path = FOLDER / f"{bid}.json"
    if not path.exists():
        raise KeyError(f"{LABELS[bid]} isn't written yet; see `python -m coe books`")
    book = json.loads(path.read_text(encoding="utf-8"))
    return {**book, "label": LABELS[bid]}


def chapters(book: dict, page: dict) -> str:
    """Where a page's story is told: "Genesis 3", or "Genesis 6–9" when it runs over several chapters."""
    to = f"–{page['to']}" if page.get("to") else ""
    return f"{book['label']} {page['chapter']}{to}"

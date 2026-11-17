"""Picture pages: 60 drawings of animals, places and people of the Middle East (coe/pictures/), each traced
into clean outlines from the author's picture sheets by tools/trace_pictures.py. When a chapter names one
of them often enough (a lion, the Nile, Pharaoh), its coloring page is that drawing, full width, with the
verse underneath. Chapters that don't name one keep the page drawn in code."""
from __future__ import annotations

import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

FOLDER = Path(__file__).parent / "pictures"
MIN_MENTIONS = 3        # a picture needs at least this many mentions in the chapter
WORD = re.compile(r"[a-z]+")


@lru_cache(maxsize=1)
def catalog() -> tuple[dict, ...]:
    """Every picture: id ("animals/lion"), label, width, height and the words that choose it."""
    return tuple(json.loads((FOLDER / "catalog.json").read_text(encoding="utf-8")))


def find(picture_id: str) -> dict:
    for p in catalog():
        if p["id"] == picture_id:
            return p
    raise KeyError(f"no picture called {picture_id!r}; see `python -m coe pictures`")


def choose(text: str) -> str | None:
    """The picture the chapter names most (at least MIN_MENTIONS times), or None. Ties go to the one
    listed first in the catalog."""
    words = Counter(WORD.findall(text.lower()))
    best, best_n = None, MIN_MENTIONS - 1
    for p in catalog():
        n = sum(words[w] for w in p["words"])
        if n > best_n:
            best, best_n = p["id"], n
    return best


def path_data(picture_id: str) -> str:
    """The traced outlines of a picture, as SVG path data in its own width x height space."""
    find(picture_id)
    svg = (FOLDER / f"{picture_id}.svg").read_text(encoding="utf-8")
    return re.search(r' d="([^"]+)"', svg).group(1)

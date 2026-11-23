"""The drawings (coe/pictures/), each traced into clean outlines from the author's picture sheets by
tools/trace_pictures.py: a scene for most story pages (scenes/<page number>) and 60 drawings of
animals, places and people of the Middle East, used on the covers and the pages still waiting for theirs."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

FOLDER = Path(__file__).parent / "pictures"


@lru_cache(maxsize=1)
def catalog() -> tuple[dict, ...]:
    """Every picture: id ("animals/lion"), label, width and height."""
    return tuple(json.loads((FOLDER / "catalog.json").read_text(encoding="utf-8")))


def find(picture_id: str) -> dict:
    for p in catalog():
        if p["id"] == picture_id:
            return p
    raise KeyError(f"no picture called {picture_id!r}; see `python -m coe pictures`")


def path_data(picture_id: str) -> str:
    """The traced outlines of a picture, as SVG path data in its own width x height space."""
    find(picture_id)
    svg = (FOLDER / f"{picture_id}.svg").read_text(encoding="utf-8")
    return re.search(r' d="([^"]+)"', svg).group(1)

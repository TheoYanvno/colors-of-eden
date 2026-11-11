"""Chapter text from the King James Version, which is in the public domain in the United States.

Text comes from bible-api.com (it serves public-domain translations) and is cached on disk, so each
chapter is fetched only once. A few chapters ship with Colors of Eden so it works offline and in tests.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .books import check

API = "https://bible-api.com/{ref}?translation=kjv"


@dataclass(frozen=True)
class Chapter:
    book: str
    number: int
    verses: list[tuple[int, str]]
    translation: str = "King James Version (public domain)"

    @property
    def reference(self) -> str:
        return f"{self.book} {self.number}"


BUNDLED: dict[str, list[str]] = {
    "Genesis 1": [
        "In the beginning God created the heaven and the earth.",
        "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.",
        "And God said, Let there be light: and there was light.",
        "And God saw the light, that it was good: and God divided the light from the darkness.",
        "And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day.",
    ],
    "Psalms 23": [
        "The LORD is my shepherd; I shall not want.",
        "He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
        "He restoreth my soul: he leadeth me in the paths of righteousness for his name's sake.",
        "Yea, though I walk through the valley of the shadow of death, I will fear no evil: for thou art with me; thy rod and thy staff they comfort me.",
        "Thou preparest a table before me in the presence of mine enemies: thou anointest my head with oil; my cup runneth over.",
        "Surely goodness and mercy shall follow me all the days of my life: and I will dwell in the house of the LORD for ever.",
    ],
}
PARTIAL = {"Genesis 1"}       # bundled copies that hold only the opening verses


def urllib_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "colors-of-eden"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def load_chapter(book: str, chapter, cache: Path | None = Path(".coe-cache"), get=urllib_get,
                 allow_partial: bool = True) -> Chapter:
    name, n = check(book, chapter)
    ref = f"{name} {n}"
    if cache is not None:
        cached = cache / f"{ref.replace(' ', '_')}.json"
        if cached.is_file():
            data = json.loads(cached.read_text(encoding="utf-8"))
            return Chapter(name, n, [(v, t) for v, t in data["verses"]])
    try:
        body = json.loads(get(API.format(ref=urllib.parse.quote(ref.lower()))))
        verses = [(int(v["verse"]), " ".join(v["text"].split())) for v in body["verses"] if int(v["chapter"]) == n]
        if not verses:
            raise ValueError("no verses in the answer")
    except Exception as e:                       # offline, blocked, or an odd answer
        if ref in BUNDLED and (allow_partial or ref not in PARTIAL):
            return Chapter(name, n, list(enumerate(BUNDLED[ref], start=1)))
        raise ConnectionError(f"Couldn't get {ref} ({e}). Check your internet connection and try again.") from None
    if cache is not None:
        cache.mkdir(parents=True, exist_ok=True)
        cached.write_text(json.dumps({"verses": verses}), encoding="utf-8")
    return Chapter(name, n, verses)

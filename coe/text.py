"""Chapter text from the World English Bible, a public-domain translation, from the same place SuperBook
reads it: bible-api.com, which also has the Orthodox books Protestant Bibles leave out.

Each chapter is fetched once and cached on disk. A few chapters ship with Colors of Eden so it works
offline and in tests.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .books import API_ID, check

API = "https://bible-api.com/{ref}?translation=web"


@dataclass(frozen=True)
class Chapter:
    book: str
    number: int
    verses: list[tuple[int, str]]
    translation: str = "World English Bible (public domain)"

    @property
    def reference(self) -> str:
        return f"{self.book} {self.number}"


BUNDLED: dict[str, list[str]] = {
    "Genesis 1": [
        "In the beginning, God created the heavens and the earth.",
        "The earth was formless and empty. Darkness was on the surface of the deep and God\u2019s Spirit was hovering over the surface of the waters.",
        "God said, \u201cLet there be light,\u201d and there was light.",
        "God saw the light, and saw that it was good. God divided the light from the darkness.",
        "God called the light \u201cday\u201d, and the darkness he called \u201cnight\u201d. There was evening and there was morning, the first day.",
    ],
    "Psalms 23": [
        "Yahweh is my shepherd: I shall lack nothing.",
        "He makes me lie down in green pastures. He leads me beside still waters.",
        "He restores my soul. He guides me in the paths of righteousness for his name\u2019s sake.",
        "Even though I walk through the valley of the shadow of death, I will fear no evil, for you are with me. Your rod and your staff, they comfort me.",
        "You prepare a table before me in the presence of my enemies. You anoint my head with oil. My cup runs over.",
        "Surely goodness and loving kindness shall follow me all the days of my life, and I will dwell in Yahweh\u2019s house forever.",
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
    api_ref = f"{API_ID[name]} {n}"
    if cache is not None:
        cached = cache / f"{api_ref.replace(' ', '_')}.json"
        if cached.is_file():
            data = json.loads(cached.read_text(encoding="utf-8"))
            return Chapter(name, n, [(v, t) for v, t in data["verses"]])
    try:
        body = json.loads(get(API.format(ref=urllib.parse.quote(api_ref.lower()))))
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

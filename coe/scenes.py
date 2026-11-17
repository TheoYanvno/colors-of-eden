"""Choosing what to draw for a chapter: words in the text point to motifs (a shepherd's psalm gets
sheep, a hill and still water; the creation story gets a sun, moon, stars and waves). The motifs
that come up most often, plus one verse to print under the picture, make the page's plan."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .picture import choose as choose_picture, find as find_picture
from .text import Chapter

# motif -> words that suggest it (whole words, lower case)
MOTIF_WORDS: dict[str, tuple[str, ...]] = {
    "sun": ("sun", "light", "day", "morning", "shine", "shined", "bright"),
    "moon": ("moon", "night", "evening"),
    "stars": ("star", "stars", "heaven", "heavens", "firmament"),
    "clouds": ("cloud", "clouds", "rain", "sky"),
    "waves": ("sea", "seas", "waters", "water", "deep", "flood", "river", "waves"),
    "mountains": ("mountain", "mountains", "hill", "hills", "valley", "earth", "land"),
    "tree": ("tree", "trees", "garden", "fruit", "vine", "branch", "seed", "grass", "herb"),
    "flowers": ("flower", "flowers", "lily", "lilies", "pastures", "field", "fields", "green"),
    "sheep": ("sheep", "lamb", "lambs", "flock", "shepherd", "shepherds"),
    "dove": ("dove", "spirit", "bird", "birds", "fowl", "wings"),
    "fish": ("fish", "fishes", "whale", "net", "nets"),
    "boat": ("ship", "ships", "boat", "ark", "sailed"),
    "crown": ("king", "kings", "crown", "throne", "kingdom", "reign"),
    "lamp": ("lamp", "lamps", "candle", "candlestick", "lantern"),
    "cup": ("cup", "table", "bread", "wine", "feast"),
    "path": ("path", "paths", "way", "walk", "road", "journey"),
    "heart": ("love", "loved", "heart", "mercy", "goodness", "joy"),
}
BACKGROUND = {"sun", "moon", "stars", "clouds", "waves", "mountains", "path"}
# Specific things (a shepherd, a dove, a boat) say more about a chapter than general words like
# "day" or "way", so each mention of them counts three times.
WEIGHT = {"sheep": 3, "dove": 3, "fish": 3, "boat": 3, "crown": 3, "lamp": 2, "cup": 2}
WORD = re.compile(r"[a-z]+")


@dataclass(frozen=True)
class Plan:
    reference: str
    motifs: list[str]          # most suggested first
    background: list[str]
    foreground: list[str]
    verse: tuple[int, str]     # the verse printed on the page
    picture: str | None = None # one of the drawings in coe/pictures, if the chapter names one


def motif_counts(text: str) -> Counter:
    words = Counter(WORD.findall(text.lower()))
    counts = Counter()
    for motif, cues in MOTIF_WORDS.items():
        n = sum(words[w] for w in cues)
        if n:
            counts[motif] = n * WEIGHT.get(motif, 1)
    return counts


def pick_verse(chapter: Chapter, motifs: list[str], max_chars: int = 160) -> tuple[int, str]:
    """The short verse that mentions the most chosen motifs (ties go to the earlier verse)."""
    best, best_score = None, -1
    for number, text in chapter.verses:
        if len(text) > max_chars:
            continue
        score = sum(motif_counts(text)[m] > 0 for m in motifs)
        if score > best_score:
            best, best_score = (number, text), score
    return best or min(chapter.verses, key=lambda v: len(v[1]))


def picture_verse(chapter: Chapter, picture: str, max_chars: int = 160) -> tuple[int, str] | None:
    """The short verse that names the picture most (ties go to the earlier verse), if any does."""
    cues = set(find_picture(picture)["words"])
    best, best_n = None, 0
    for number, text in chapter.verses:
        n = sum(w in cues for w in WORD.findall(text.lower()))
        if len(text) <= max_chars and n > best_n:
            best, best_n = (number, text), n
    return best


def plan_page(chapter: Chapter, max_motifs: int = 5) -> Plan:
    text = " ".join(t for _, t in chapter.verses)
    counts = motif_counts(text)
    picture = choose_picture(text)
    motifs = [m for m, _ in counts.most_common()][:max_motifs] or ["sun", "mountains", "tree", "flowers"]
    if not any(m not in BACKGROUND for m in motifs):
        motifs.append("tree")                # always something in front to color
    if not any(m in BACKGROUND for m in motifs):
        motifs.insert(0, "mountains")
    if picture:                              # a picture page shows a verse that names the picture
        verse = picture_verse(chapter, picture)
        return Plan(chapter.reference, motifs, [m for m in motifs if m in BACKGROUND],
                    [m for m in motifs if m not in BACKGROUND], verse or pick_verse(chapter, motifs), picture)
    return Plan(chapter.reference, motifs,
                [m for m in motifs if m in BACKGROUND], [m for m in motifs if m not in BACKGROUND],
                pick_verse(chapter, motifs), picture)

"""The books of the Bible as SuperBook has them: the Eastern Orthodox canon in Orthodox order (the Old
Testament following the Septuagint, with Tobit, Judith, the Maccabees, Wisdom, Sirach, Baruch and the
other books Protestant Bibles leave out), then the 27 books of the New Testament.

SuperBook (https://github.com/TheoYanvno/SuperBook) is the reference for every Bible project here, so this
list is a copy of `BIBLE` in SuperBook's src/books.js: [id the text API understands, chapters, label readers
see]. tests/test_superbook.py checks the two still match when SuperBook is checked out next to this repo.
"""
from __future__ import annotations

SUPERBOOK = "https://theoyanvno.github.io/SuperBook/"

BIBLE: list[tuple[str, int, str]] = [(b[0], b[1], b[2] if len(b) > 2 else b[0]) for b in [
    ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36), ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21),
    ("Ruth", 4), ("1 Samuel", 31, "1 Kingdoms (1 Samuel)"), ("2 Samuel", 24, "2 Kingdoms (2 Samuel)"),
    ("1 Kings", 22, "3 Kingdoms (1 Kings)"), ("2 Kings", 25, "4 Kingdoms (2 Kings)"),
    ("1 Chronicles", 29), ("2 Chronicles", 36), ("Prayer of Manasses", 1, "Prayer of Manasseh"),
    ("1 Esdras", 9), ("Ezra", 10, "2 Esdras (Ezra)"), ("Nehemiah", 13), ("Tobit", 14), ("Judith", 16), ("Esther", 10),
    ("1 Maccabees", 16), ("2 Maccabees", 15), ("3 Maccabees", 7),
    ("Psalms", 150), ("Job", 42), ("Proverbs", 31), ("Ecclesiastes", 12), ("Song of Solomon", 8, "Song of Songs"),
    ("Wisdom", 19, "Wisdom of Solomon"), ("Sirach", 51),
    ("Hosea", 14), ("Amos", 9), ("Micah", 7), ("Joel", 3), ("Obadiah", 1), ("Jonah", 4), ("Nahum", 3), ("Habakkuk", 3),
    ("Zephaniah", 3), ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4),
    ("Isaiah", 66), ("Jeremiah", 52), ("Baruch", 5), ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12),
    ("sus", 1, "Susanna"), ("Bel and the Dragon", 1), ("4 Maccabees", 18, "4 Maccabees (appendix)"),
    ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21), ("Acts", 28), ("Romans", 16), ("1 Corinthians", 16),
    ("2 Corinthians", 13), ("Galatians", 6), ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4), ("1 Thessalonians", 5),
    ("2 Thessalonians", 3), ("1 Timothy", 6), ("2 Timothy", 4), ("Titus", 3), ("Philemon", 1), ("Hebrews", 13), ("James", 5),
    ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5), ("2 John", 1), ("3 John", 1), ("Jude", 1), ("Revelation", 22),
]]

BOOKS: dict[str, int] = {label: chapters for _, chapters, label in BIBLE}     # label -> chapters, in order
API_ID: dict[str, str] = {label: api for api, _, label in BIBLE}

ALIASES = {"psalm": "Psalms", "revelations": "Revelation", "song of solomon": "Song of Songs", "wisdom": "Wisdom of Solomon",
           "ecclesiasticus": "Sirach", "prayer of manasses": "Prayer of Manasseh", "bel": "Bel and the Dragon",
           "4 maccabees": "4 Maccabees (appendix)"}


class BadReference(ValueError):
    pass


def _keys() -> dict[str, str]:
    """Every name a reader might type for a book: its label, its API name and the names in brackets
    ("1 Samuel", "1 Kingdoms", "Ezra", "2 Esdras")."""
    keys = {}
    for api, _, label in BIBLE:
        keys[label.lower()] = label
        keys[api.lower()] = label
        if "(" in label:
            outer, inner = label.split(" (", 1)
            keys[outer.lower()] = label
            if inner.rstrip(")") != "appendix":
                keys[inner.rstrip(")").lower()] = label
    keys.update({k: v for k, v in ALIASES.items()})
    return keys


KEYS = _keys()


def find_book(name: str) -> str:
    """The book's label as SuperBook shows it, matched without caring about case or extra spaces."""
    key = " ".join(str(name).split()).lower()
    if key in KEYS:
        return KEYS[key]
    raise BadReference(f"There's no book called {name!r}. Try a name like Genesis, Tobit, Psalms or 1 John.")


def check(book: str, chapter) -> tuple[str, int]:
    name = find_book(book)
    try:
        n = int(chapter)
    except (TypeError, ValueError):
        raise BadReference(f"The chapter must be a number, not {chapter!r}.") from None
    if not 1 <= n <= BOOKS[name]:
        raise BadReference(f"{name} has chapters 1 to {BOOKS[name]}.")
    return name, n

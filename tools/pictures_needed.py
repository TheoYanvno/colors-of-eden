"""Write PICTURES_NEEDED.md: every storybook page's scene, the drawing it borrows for now and where it
goes, so new drawings can be made for each one. Run it again after changing a storybook."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from coe.picture import find  # noqa: E402
from coe.storybook import chapters, storybook, written  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "PICTURES_NEEDED.md"


def main() -> None:
    books = [storybook(b) for b in written()]
    total = sum(len(b["pages"]) for b in books)
    lines = ["# Pictures needed", "",
             f"Every page of the {len(books)} storybooks, {total} in all, with the scene its picture should show. "
             "Until a new drawing is made, each page borrows one of the 60 drawings (shown in brackets).", "",
             "**To add drawings:** draw them in the same style as the first three sheets (bold black outlines, white "
             "inside, no shading, a little ground or sky around the subject), 20 to a sheet in 4 rows of 5 boxes with "
             "the picture's name printed at the top of each box, like the animals sheet. Each new sheet goes in "
             "`coe/pictures/source/`, its names go in `tools/trace_pictures.py`, and the tracer cuts out, cleans "
             "and traces every drawing; then each page is pointed at its new picture.", ""]
    n = 0
    for book in books:
        lines += [f"## {book['label']}", ""]
        for i, page in enumerate(book["pages"], 1):
            n += 1
            lines.append(f"{n}. **{page['title']}** ({chapters(book, page)}, page {i}): {page['scene']} "
                         f"[{find(page['picture'])['label']}]")
        lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"Wrote {OUT.name}: {total} pictures for {len(books)} books")


if __name__ == "__main__":
    main()

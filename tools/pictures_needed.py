"""Write PICTURES_NEEDED.md: the storybook pages that don't have their own drawing yet, with the scene each
one should show and the drawing it borrows for now. Run it again after adding drawings or changing a
storybook."""
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
    needed, n = [], 0
    for book in books:
        for i, page in enumerate(book["pages"], 1):
            n += 1
            if page["picture"] != f"scenes/{n:03d}":
                needed.append(f"{n}. **{page['title']}** ({chapters(book, page)}, page {i}): {page['scene']} "
                              f"[borrows {find(page['picture'])['label']}]")
    lines = ["# Pictures needed", "",
             f"{total - len(needed)} of the {total} storybook pages have their own drawing of their story. These "
             f"{len(needed)} still borrow one of the 60 cover drawings (shown in brackets) until theirs is drawn. "
             "The number is the page's place in the whole set, counting from Genesis page 1.", "",
             "**To add drawings:** draw them in the same style (bold black outlines, white inside, no shading), one "
             "to a box with the page's number in the corner, and save the sheet anywhere. Add the sheet to "
             "`GRIDS` in `tools/cut_scenes.py`, run it on the folder of sheets, then run "
             "`tools/trace_pictures.py`, point each page at `scenes/<number>` and run this script again.", ""]
    OUT.write_text("\n".join(lines + needed) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {OUT.name}: {len(needed)} of {total} pages still need a drawing")


if __name__ == "__main__":
    main()

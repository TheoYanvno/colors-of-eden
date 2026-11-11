"""`python -m coe plan Psalms 23` prints what the coloring page for a chapter will show."""
from __future__ import annotations

import argparse
import sys

from .books import BadReference
from .art import draw_page
from .scenes import plan_page
from pathlib import Path
from .text import load_chapter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="coe", description="Coloring pages from any Bible chapter.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="show the motifs and verse chosen for a chapter")
    p.add_argument("book", nargs="+", help='book name, e.g. Genesis or "1 John"')
    p.add_argument("chapter", type=int)
    g = sub.add_parser("page", help="draw the coloring page for a chapter as an SVG file")
    g.add_argument("book", nargs="+", help='book name, e.g. Genesis or "1 John"')
    g.add_argument("chapter", type=int)
    g.add_argument("--out", default="out", help="folder for the page (default: out)")
    args = parser.parse_args(argv)
    try:
        chapter = load_chapter(" ".join(args.book), args.chapter)
    except (BadReference, ConnectionError) as e:
        print(e, file=sys.stderr)
        return 1
    plan = plan_page(chapter)
    if args.cmd == "page":
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{plan.reference.replace(' ', '-').lower()}.svg"
        path.write_text(draw_page(plan), encoding="utf-8")
        print(f"Saved {path} (print it at 100% on US Letter paper)")
        return 0
    print(f"{plan.reference} ({chapter.translation})")
    print(f"Background: {', '.join(plan.background) or '-'}")
    print(f"In front:   {', '.join(plan.foreground) or '-'}")
    print(f"Verse {plan.verse[0]}: {plan.verse[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

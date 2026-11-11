"""`python -m coe plan Psalms 23` prints what the coloring page for a chapter will show."""
from __future__ import annotations

import argparse
import sys

from .books import BadReference
from .scenes import plan_page
from .text import load_chapter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="coe", description="Coloring pages from any Bible chapter.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="show the motifs and verse chosen for a chapter")
    p.add_argument("book", nargs="+", help='book name, e.g. Genesis or "1 John"')
    p.add_argument("chapter", type=int)
    args = parser.parse_args(argv)
    try:
        chapter = load_chapter(" ".join(args.book), args.chapter)
    except (BadReference, ConnectionError) as e:
        print(e, file=sys.stderr)
        return 1
    plan = plan_page(chapter)
    print(f"{plan.reference} ({chapter.translation})")
    print(f"Background: {', '.join(plan.background) or '-'}")
    print(f"In front:   {', '.join(plan.foreground) or '-'}")
    print(f"Verse {plan.verse[0]}: {plan.verse[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

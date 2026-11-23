"""Storybook pages: a drawing of the story to color, with a short paragraph to read and its lesson.

A page is US Letter (8.5 x 11 in) as an SVG with an 850 x 1100 view box. A book starts with a cover (its
name, a drawing and a sentence about the book), then one page per story: the title and chapter at the top,
the drawing in a frame, a short paragraph, the lesson it teaches in a box and the page number. The drawings are the only things to color; the
words are plain black type. web/src/art.js draws exactly the same pages, and a test checks they match.
"""
from __future__ import annotations

from xml.sax.saxutils import escape

from .picture import find as find_picture, path_data
from .storybook import chapters

W, H = 850, 1100
INK = "#111"
INSIDE = 18                         # space between the drawing and its frame
PIC_W, PIC_H = 700, 560             # the most room a drawing and its frame can take on a story page
COVER_H = 520
BOTTOM = H - 50                     # the lowest a story page's words may reach (the page number is below)
TEXT_X = 80                         # left edge of the paragraph
ROW = 42                            # paragraph line height
TEXT_WRAP = 50                      # characters a paragraph line holds at 28px Georgia across 690px
FONT = "Georgia, serif"


def f(n: float) -> str:
    return f"{n:.1f}"


def wrap(text: str, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + ([cur] if cur else [])


def frame(x: float, y: float, w: float, h: float) -> str:
    """A double-line frame with rounded corners."""
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="22" fill="none" stroke="{INK}" stroke-width="7"/>'
            f'<rect x="{f(x + 10)}" y="{f(y + 10)}" width="{f(w - 20)}" height="{f(h - 20)}" rx="16" fill="none" stroke="{INK}" stroke-width="2.5"/>')


def text(x: float, y: float, words: str, size: float, anchor: str = "middle", style: str = "") -> str:
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}" font-family="{FONT}" font-size="{f(size)}"{style} '
            f'fill="{INK}">{escape(words)}</text>')


def picture_box(picture_id: str, top: float, max_h: float) -> tuple[float, float, float, float, float]:
    """Where a drawing's frame goes (x, y, w, h) and the drawing's scale: as big as fits PIC_W x max_h,
    centred across the page."""
    pic = find_picture(picture_id)
    k = min((PIC_W - 2 * INSIDE) / pic["width"], (max_h - 2 * INSIDE) / pic["height"])
    w, h = pic["width"] * k + 2 * INSIDE, pic["height"] * k + 2 * INSIDE
    return (W - w) / 2, top, w, h, k


def drawing(picture_id: str, box: tuple, outlines: str | None) -> str:
    x, y, w, h, k = box
    d = outlines if outlines is not None else path_data(picture_id)
    return (f'<g transform="translate({f(x + INSIDE)} {f(y + INSIDE)}) scale({k:.4f})">'
            f'<path d="{d}" fill="{INK}" fill-rule="evenodd"/></g>' + frame(x, y, w, h))


def svg_page(label: str, parts: list[str]) -> str:
    label = escape(label)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="Coloring page: {label}">'
            f'<title>Colors of Eden: {label}</title><rect width="{W}" height="{H}" fill="#fff"/>'
            + "".join(parts) + "</svg>")


def page_layout(page: dict) -> dict:
    """Where everything on a story page sits, so the drawing code and the tests share one plan. The drawing
    gets the room the words leave, up to PIC_H, so a long story still fits above the page number."""
    lines = wrap(page["text"], TEXT_WRAP)
    lesson = wrap(page["lesson"], 46)
    lesson_h = 24 + len(lesson) * 34
    words_h = 52 + (len(lines) - 1) * ROW + 34 + lesson_h
    box = picture_box(page["picture"], 136, min(PIC_H, BOTTOM - 136 - words_h))
    top = box[1] + box[3] + 52
    lesson_top = top + (len(lines) - 1) * ROW + 34
    return {"box": box, "lines": lines, "top": top, "lesson": (lesson_top, lesson_h, lesson),
            "bottom": lesson_top + lesson_h}


def draw_story_page(book: dict, n: int, outlines: str | None = None) -> str:
    """Story page n (counting from 1) of a book as an SVG string. outlines is the drawing's path data
    (read from coe/pictures when not given)."""
    page = book["pages"][n - 1]
    plan = page_layout(page)
    parts = [text(W / 2, 78, page["title"], 40, style=' font-weight="bold"'),
             text(W / 2, 112, chapters(book, page), 22, style=' font-style="italic"'),
             drawing(page["picture"], plan["box"], outlines)]
    parts += [text(TEXT_X, plan["top"] + i * ROW, line, 28, anchor="start") for i, line in enumerate(plan["lines"])]
    lesson_top, lesson_h, lesson = plan["lesson"]
    parts.append(f'<rect x="{f(TEXT_X - 10)}" y="{f(lesson_top)}" width="{f(W - 2 * (TEXT_X - 10))}" height="{f(lesson_h)}" rx="14" '
                 f'fill="none" stroke="{INK}" stroke-width="2.5"/>')
    parts += [text(W / 2, lesson_top + 36 + i * 34, line, 26, style=' font-weight="bold"') for i, line in enumerate(lesson)]
    parts.append(text(W / 2, H - 34, str(n), 18))
    return svg_page(f"{page['title']} ({chapters(book, page)})", parts)


def cover_layout(book: dict) -> dict:
    size = min(72.0, 1300 / len(book["label"]))
    box = picture_box(book["cover"], 290, COVER_H)
    about = wrap(book["about"], 62)
    top = box[1] + box[3] + 56
    return {"size": size, "box": box, "about": about, "top": top, "bottom": top + (len(about) - 1) * 32 + 10}


def draw_cover(book: dict, outlines: str | None = None) -> str:
    """The book's cover: its name, "A Coloring Storybook", a drawing and a sentence about the book."""
    plan = cover_layout(book)
    parts = [text(W / 2, 100, "Colors of Eden", 24, style=' letter-spacing="3"'),
             text(W / 2, 190, book["label"], plan["size"], style=' font-weight="bold"'),
             text(W / 2, 244, "A Coloring Storybook", 30, style=' font-style="italic"'),
             drawing(book["cover"], plan["box"], outlines)]
    parts += [text(W / 2, plan["top"] + i * 32, line, 22) for i, line in enumerate(plan["about"])]
    return svg_page(f"{book['label']}, a coloring storybook", parts)

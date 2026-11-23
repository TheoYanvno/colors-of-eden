"""Cut the scene drawings out of the author's picture sheets: one drawing per storybook page, saved as
coe/pictures/source/scenes/<page>.png, numbered in Bible order like PICTURES_NEEDED.md (001 is Genesis
page 1).

Most sheets hold several numbered panels in a grid; a few hold one big picture. Each panel is found by its
rounded border (panels the search misses, such as night skies, are filled in from the grid), cut out, and
cleaned: the number badge, the title (bare text or a title box) and bits of the border are erased, and a
badge on a night sky is painted dark instead of white. Then run tools/trace_pictures.py to trace them.

    pip install -r tools/requirements.txt
    python tools/cut_scenes.py "C:/Users/me/Pictures/Color of Eden"
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

OUT = Path(__file__).resolve().parents[1] / "coe" / "pictures" / "source" / "scenes"

# Sheet file -> (first page number, panels to cut, grids side by side, title style, skip panels at the start)
GRIDS = {
    "Bible Stories in Five Panels-1.png": (5, 5, 1, None, 0),
    "Biblical Stories in Five Panels-3.png": (11, 4, 1, None, 1),        # its first panel is another Jacob's dream
    "Exodus Coloring Book Panels 15–20.png": (15, 6, 1, "box", 0),
    "Biblical Coloring Scenes_ Panels 21–30.png": (21, 10, 1, None, 0),
    "Biblical Stories Coloring Page Collection.png": (31, 15, 1, "box", 0),
    "Bible Story Coloring Sheet_ Coronation to Elijah.png": (46, 20, 1, None, 0),
    "Biblical Coloring Pages 66–95-2.png": (66, 30, 2, None, 0),
    "Biblical Storybook Panels 96–135.png": (96, 40, 1, None, 0),
    "Bible Stories Coloring Grid_ Daniel to Acts.png": (136, 50, 1, 0.45, 0),
    "Bible Story Coloring Book Finale.png": (186, 17, 1, 0.36, 0),
}
# Pages drawn as one picture per file.
WHOLE = {
    1: "Garden of Eden Creation Scene.png",
    2: "Garden of Eden Coloring Scene.png",
    3: "Noah’s Ark Rainbow Adventure.png",
    4: "Tower of Babel_ A World of Confusion.png",
    10: "Jacob’s Dream_ Angels on the Stairway-4.png",
}
# Panel numbers that don't match the storybook's page numbers. Panels 43-65 and 135-185 were drawn from
# another list of stories, so each is matched to its page by what it shows; the ones no page asks for are
# left out (PICTURES_NEEDED.md lists the pages still waiting for a drawing).
PAGE_OF = {44: 43, 46: 44, 48: 45, 49: 46, 50: 47, 51: 48, 53: 49, 55: 51, 54: 52, 59: 53, 62: 54, 64: 55,
           65: 56, 63: 58, 56: 60, 58: 63,
           136: 137, 137: 138, 138: 139, 139: 140, 157: 144, 159: 145, 165: 148, 182: 149, 161: 150, 155: 154,
           166: 155, 167: 156, 169: 157, 180: 159, 162: 160, 164: 162, 183: 165, 184: 166}
REMATCHED = (range(43, 66), range(135, 186))
INSET = 6          # pixels trimmed inside each panel's border
INK = 150          # darker than this is a line


def panels(gray: np.ndarray, count: int, grids: int) -> list[tuple[int, int, int, int]]:
    """The panels of a sheet as (x, y, w, h), grid by grid, top to bottom and left to right."""
    height, width = gray.shape
    contours, _ = cv2.findContours((gray < INK).astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    found = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if width * 0.08 <= w <= width * 0.9 and h >= height * 0.05 and cv2.contourArea(c) >= 0.85 * w * h:
            found.append((x, y, w, h))
    found.sort(key=lambda b: -b[2] * b[3])
    boxes: list[tuple[int, int, int, int]] = []
    for b in found:                                  # the outer and inner edge of one border are one panel
        if not any(abs(b[0] - k[0]) < 25 and abs(b[1] - k[1]) < 25 and abs(b[0] + b[2] - k[0] - k[2]) < 25 for k in boxes):
            boxes.append(b)
    inside = lambda b, k: k[0] >= b[0] - 2 and k[1] >= b[1] - 2 and k[0] + k[2] <= b[0] + b[2] + 2 and k[1] + k[3] <= b[1] + b[3] + 2
    boxes = [b for b in boxes if sum(1 for k in boxes if k != b and inside(b, k)) < 2]     # not an outer frame
    boxes = [b for b in boxes if not any(k != b and inside(k, b) for k in boxes)]          # not a badge
    groups = [boxes] if grids == 1 else [[b for b in boxes if b[0] + b[2] / 2 < width / 2],
                                          [b for b in boxes if b[0] + b[2] / 2 >= width / 2]]
    out = []
    for group in groups:
        if len(boxes) < count:
            group = fill_gaps(group)
        group.sort(key=lambda b: b[1])
        rows: list[list] = []
        for b in group:
            if rows and abs(rows[-1][0][1] + rows[-1][0][3] / 2 - (b[1] + b[3] / 2)) < min(b[3], rows[-1][0][3]) / 2:
                rows[-1].append(b)
            else:
                rows.append([b])
        out += [b for row in rows for b in sorted(row)]
    if len(out) != count:
        raise RuntimeError(f"expected {count} panels, found {len(out)}")
    return out


def fill_gaps(group: list) -> list:
    """Add the grid cells the border search missed, from the rows and columns of the panels it found."""
    def centres(values: list[float], tolerance: float) -> list[float]:
        groups: list[list[float]] = []
        for v in sorted(values):
            if groups and v - groups[-1][-1] < tolerance:
                groups[-1].append(v)
            else:
                groups.append([v])
        return [sum(g) / len(g) for g in groups]
    mw, mh = np.median([b[2] for b in group]), np.median([b[3] for b in group])
    near = lambda b, cx, cy: abs(b[0] + b[2] / 2 - cx) < mw / 2 and abs(b[1] + b[3] / 2 - cy) < mh / 2
    out = list(group)
    for cy in centres([b[1] + b[3] / 2 for b in group], mh / 2):
        row = [b for b in group if abs(b[1] + b[3] / 2 - cy) < mh / 2]
        for cx in centres([b[0] + b[2] / 2 for b in group], mw / 2):
            if not any(near(b, cx, cy) for b in out):
                column = [b for b in group if abs(b[0] + b[2] / 2 - cx) < mw / 2]
                w, h = int(np.median([b[2] for b in column])), int(np.median([b[3] for b in row]))
                out.append((int(cx - w / 2), int(np.median([b[1] for b in row])), w, h))
    return out


def paint(panel: np.ndarray, dark: np.ndarray, y1: int, x0: int, x1: int, y0: int = 0) -> None:
    """Blank a rectangle: white, or black when it sits in a night sky."""
    ring = np.concatenate([dark[y1:y1 + 6, x0:x1].ravel(), dark[y0:y1, max(0, x0 - 6):x0].ravel(),
                           dark[y0:y1, x1:x1 + 6].ravel()])
    panel[y0:y1, x0:x1] = 0 if ring.size and ring.mean() > 0.6 else 255


def erase(panel: np.ndarray, labels: np.ndarray, k: int, grow: int = 2) -> None:
    panel[ndimage.binary_dilation(labels == k, iterations=grow)] = 255


def clean(panel: np.ndarray, title) -> np.ndarray:
    """Erase a panel's number badge, title and border, and trim it to the drawing."""
    p = panel.copy()
    H, W = p.shape
    dark = (p < INK).astype(np.uint8)
    contours, _ = cv2.findContours(dark, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    badge_right, boxed_title = 0, False
    for c in contours:                     # closed label boxes along the top: the badge, sometimes the title
        bx, by, bw, bh = cv2.boundingRect(c)
        if by > 0.1 * H or bh > 0.42 * H or bw > 0.95 * W or bw < 0.06 * W or bh < 0.06 * H:
            continue
        if cv2.contourArea(c) < 0.8 * bw * bh or dark[by:by + bh, bx:bx + bw].mean() > 0.5:
            continue
        paint(p, dark, by + bh + 3, max(0, bx - 2), bx + bw + 3, max(0, by - 2))
        if bx < 0.15 * W:
            badge_right = max(badge_right, bx + bw)
        boxed_title |= bw > 0.3 * W
    if title == "box" and not boxed_title:
        # a title box joined to the border: find its letters (rows of five or more) and blank the box around them
        labels, _ = ndimage.label(p < INK)
        letters = sorted(((sl[0].start + sl[0].stop) / 2, sl) for sl in ndimage.find_objects(labels)
                         if sl[0].start < 0.32 * H and 0.015 * H < sl[0].stop - sl[0].start < 0.1 * H
                         and sl[1].stop - sl[1].start < 0.12 * W)
        rows: list[list] = []
        for centre, sl in letters:
            if rows and abs(centre - rows[-1][-1][0]) < 0.03 * H:
                rows[-1].append((centre, sl))
            else:
                rows.append([(centre, sl)])
        rows = [r for r in rows if len(r) >= 5 and r[0][0] < 0.3 * H]
        rows = [r for r in rows if r[0][0] - rows[0][0][0] < 0.16 * H] if rows else []
        text = [sl for r in rows for _, sl in r]
        if text:
            bottom = max(sl[0].stop for sl in text)
            left, right = min(sl[1].start for sl in text), max(sl[1].stop for sl in text)
            paint(p, dark, int(bottom + 0.06 * H), max(0, int(left - 0.1 * W)), int(right + 0.1 * W))
    p = p[INSET:H - INSET, INSET:W - INSET]
    h, w = p.shape
    if isinstance(title, float):           # bare title text in the top part of the panel
        labels, _ = ndimage.label(p < INK)
        for k, (ys, xs) in enumerate(ndimage.find_objects(labels), 1):
            th, tw = ys.stop - ys.start, xs.stop - xs.start
            if ys.stop <= title * H - INSET and ((th < 0.17 * H and tw < 0.3 * W) or (th < 0.12 * H and tw < 0.5 * W)) \
                    and xs.start >= badge_right - INSET - 2:
                erase(p, labels, k)
    labels, _ = ndimage.label(p < INK)
    for k, (ys, xs) in enumerate(ndimage.find_objects(labels), 1):      # what's left of a badge
        if ys.start < 0.05 * H and ys.stop < 0.3 * H and xs.stop < 0.3 * W and ys.stop - ys.start < 0.26 * H \
                and xs.stop - xs.start < 0.28 * W:
            erase(p, labels, k)
    labels, _ = ndimage.label(p < INK)
    for k, (ys, xs) in enumerate(ndimage.find_objects(labels), 1):      # bits of the rounded border
        edge = ys.start == 0 or xs.start == 0 or ys.stop == h or xs.stop == w
        if edge and ((labels[ys, xs] == k).sum() < 60 or ys.stop - ys.start <= 4 or xs.stop - xs.start <= 4):
            erase(p, labels, k, 1)
    p[p > 215] = 255
    return trim(p)


def trim(gray: np.ndarray) -> np.ndarray:
    ys, xs = np.where(gray < INK)
    return gray[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3] if len(ys) else gray


def read(path: Path) -> np.ndarray:
    # np.fromfile + imdecode, so folder names with accents or spaces work on Windows too
    return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)


def main(folder: str) -> None:
    sheets = Path(folder)
    OUT.mkdir(parents=True, exist_ok=True)
    pages: dict[int, np.ndarray] = {n: trim(read(sheets / name)) for n, name in WHOLE.items()}
    for name, (first, count, grids, title, skip) in GRIDS.items():
        gray = read(sheets / name)
        for k, (x, y, w, h) in enumerate(panels(gray, count + skip, grids)[skip:]):
            pages[first + k] = clean(gray[y:y + h, x:x + w], title)
    matched = {}
    for panel, gray in pages.items():
        if panel in PAGE_OF:
            matched[PAGE_OF[panel]] = gray
        elif not any(panel in r for r in REMATCHED):
            matched[panel] = gray
    for old in OUT.glob("*.png"):
        old.unlink()
    for n, gray in sorted(matched.items()):
        cv2.imencode(".png", gray)[1].tofile(str(OUT / f"{n:03d}.png"))
    missing = sorted(set(range(1, 203)) - set(matched))
    print(f"saved {len(matched)} drawings in {OUT}; no drawing yet for pages {missing}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

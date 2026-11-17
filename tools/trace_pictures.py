"""Cut the 60 drawings out of the three picture sheets and trace each one into clean SVG line art.

The sheets in coe/pictures/source/ (animals, places and people of the Middle East, 20 each) are small
screenshots, so each drawing is only about 225 pixels wide. Printed at full page size the pixels would
show, so every drawing is cut out, its printed name above it is removed, it is enlarged 4x and traced
with potrace into smooth outlines that stay sharp at any size. The result goes to
coe/pictures/<sheet>/<name>.svg, and each drawing's size is written into coe/pictures/catalog.json
(the words that choose a drawing are kept as they are).

Run from the repository root:  python tools/trace_pictures.py
Needs Pillow, NumPy, SciPy and the potrace library (libpotrace.so.0, e.g. `apt install libpotrace0`).
"""
from __future__ import annotations

import ctypes as C
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent / "coe" / "pictures"
SCALE = 4            # enlarge before tracing, so the curves come out smooth
INSET = 8            # pixels trimmed inside each panel's border

SHEETS = {
    "animals": ("Lion", "Arabian Oryx", "Camel", "Bull", "Goat", "Sheep", "Leopard", "Snake", "Crocodile",
                "Scorpion", "Fish", "Shark", "Sea Turtle", "Dolphin", "Ray", "Fennec Fox", "Desert Hare",
                "Hyrax", "Ibex", "Gazelle"),
    "places": ("The Pyramids", "The Sea of Galilee", "The Dead Sea", "The Nile River", "The Desert",
               "Ancient Egyptian Slave Homes", "Babylonian Palace", "Hebrew Tents", "Temple", "Farm", "Forest",
               "Mountains", "Garden", "Oasis", "Rocky Canyon", "Coastal Shore", "Ancient Ruins", "Desert Wadi",
               "Caravan Route", "Traditional Village"),
    "people": ("Hebrew Man", "Hebrew Woman", "Hebrew Child", "Egyptian Man", "Egyptian Woman", "Egyptian Child",
               "Babylonian Man", "Babylonian Woman", "Babylonian Child", "Roman Man", "Roman Woman", "Roman Child",
               "Merchant", "Farmer", "Shepherd", "Desert Nomad", "Bedouin Woman", "Bedouin Child",
               "Royal Persian", "Priest"),
}
TITLE_ROWS = {"animals": 86, "places": 84, "people": 68}   # each sheet's title band, above the panels


def slug(label: str) -> str:
    words = label.lower().replace("the ", "").replace("ancient egyptian", "egyptian").replace("traditional ", "")
    return "-".join(words.split())


# --- potrace, through its C library -------------------------------------------------------------
_lib = C.CDLL("libpotrace.so.0")
_WORD = C.c_ulong
_BITS = C.sizeof(_WORD) * 8


class _Progress(C.Structure):
    _fields_ = [("callback", C.c_void_p), ("data", C.c_void_p), ("min", C.c_double), ("max", C.c_double),
                ("epsilon", C.c_double)]


class _Param(C.Structure):
    _fields_ = [("turdsize", C.c_int), ("turnpolicy", C.c_int), ("alphamax", C.c_double),
                ("opticurve", C.c_int), ("opttolerance", C.c_double), ("progress", _Progress)]


class _Bitmap(C.Structure):
    _fields_ = [("w", C.c_int), ("h", C.c_int), ("dy", C.c_int), ("map", C.POINTER(_WORD))]


class _Point(C.Structure):
    _fields_ = [("x", C.c_double), ("y", C.c_double)]


class _Curve(C.Structure):
    _fields_ = [("n", C.c_int), ("tag", C.POINTER(C.c_int)), ("c", C.POINTER(_Point * 3))]


class _Path(C.Structure):
    pass


_Path._fields_ = [("area", C.c_int), ("sign", C.c_int), ("curve", _Curve), ("next", C.POINTER(_Path)),
                  ("childlist", C.POINTER(_Path)), ("sibling", C.POINTER(_Path)), ("priv", C.c_void_p)]


class _State(C.Structure):
    _fields_ = [("status", C.c_int), ("plist", C.POINTER(_Path)), ("priv", C.c_void_p)]


_lib.potrace_param_default.restype = C.POINTER(_Param)
_lib.potrace_trace.restype = C.POINTER(_State)
_lib.potrace_trace.argtypes = [C.POINTER(_Param), C.POINTER(_Bitmap)]


def trace(black: np.ndarray, scale: float) -> str:
    """SVG path data for the black pixels (True) of a bitmap, its coordinates multiplied by scale."""
    h, w = black.shape
    dy = (w + _BITS - 1) // _BITS
    bits = np.zeros((h, dy * _BITS), dtype=np.uint8)
    bits[:, :w] = black
    groups = np.packbits(bits, axis=1).reshape(h, dy, _BITS // 8).astype(np.uint64)
    shifts = np.arange(_BITS // 8 - 1, -1, -1, dtype=np.uint64) * np.uint64(8)
    words = (groups << shifts).sum(axis=2).astype(np.uint64).ravel()
    bitmap = _Bitmap(w, h, dy, (_WORD * len(words))(*words.tolist()))
    param = _lib.potrace_param_default()
    param.contents.turdsize = 40                    # drop specks smaller than this (in enlarged pixels)
    state = _lib.potrace_trace(param, C.byref(bitmap))
    if not state or state.contents.status != 0:
        raise RuntimeError("potrace failed")

    def n(v: float) -> str:
        return f"{v * scale:.1f}".rstrip("0").rstrip(".")

    out, node = [], state.contents.plist
    while node:
        curve = node.contents.curve
        end = curve.c[curve.n - 1][2]
        parts = [f"M{n(end.x)} {n(end.y)}"]
        for i in range(curve.n):
            a, b, c = curve.c[i]
            parts.append(f"C{n(a.x)} {n(a.y)} {n(b.x)} {n(b.y)} {n(c.x)} {n(c.y)}" if curve.tag[i] == 1
                         else f"L{n(b.x)} {n(b.y)} {n(c.x)} {n(c.y)}")
        out.append("".join(parts) + "Z")
        node = node.contents.next
    _lib.potrace_state_free(state)
    _lib.potrace_param_free(param)
    return "".join(out)


# --- finding and cleaning each drawing ----------------------------------------------------------
def runs(mask) -> list[tuple[int, int]]:
    out, start = [], None
    for i, on in enumerate(mask):
        if on and start is None:
            start = i
        elif not on and start is not None:
            out.append((start, i - 1))
            start = None
    return out + ([(start, len(mask) - 1)] if start is not None else [])


def panels(gray: np.ndarray, sheet: str) -> list[tuple[int, int, int, int]]:
    """The 20 panels of a sheet, left to right and top to bottom, found by the white gaps between them."""
    dark = gray < 140
    skip = TITLE_ROWS[sheet]
    rows = [(a + skip, b + skip) for a, b in runs(dark[skip:].mean(1) > 0.004) if b - a > 100]
    boxes = []
    for top, bottom in rows:
        cols = [(a, b) for a, b in runs(dark[top:bottom + 1].mean(0) > 0.01) if b - a > 150]
        boxes += [(left, top, right, bottom) for left, right in cols]
    if len(boxes) != 20:
        raise RuntimeError(f"expected 20 panels, found {len(boxes)}")
    return boxes


def remove_name(gray: np.ndarray, two_lines: bool) -> None:
    """Erase the printed name at the top of a panel: only the letters, so horns and tails that reach up
    beside it stay whole."""
    dark = gray < 140
    width = dark.shape[1]
    centre = dark[:, int(width * 0.3):int(width * 0.7)].any(1)
    y0 = next((y for y in range(22) if centre[y]), None)
    if y0 is None:
        return
    y1, gap = y0, 0
    for y in range(y0 + 1, y0 + (44 if two_lines else 24)):
        if centre[y]:
            y1, gap = y, 0
        else:
            gap += 1
            if gap > (6 if two_lines else 2):
                break
    clusters: list[list[int]] = []
    for x in np.where(dark[y0:y1 + 1].any(0))[0]:
        if clusters and x - clusters[-1][1] < 11:
            clusters[-1][1] = x
        else:
            clusters.append([x, x])
    name = [c for c in clusters if c[0] < width * 0.7 and c[1] > width * 0.3]
    if not name:
        return
    top, bottom = max(0, y0 - 3), y1 + 8           # room for descenders (p, y, g)
    left, right = max(0, min(c[0] for c in name) - 3), max(c[1] for c in name) + 4
    labels, _ = ndimage.label(dark)
    for k in np.unique(labels[top:bottom, left:right]):
        if not k:
            continue
        ys, xs = np.where(labels == k)
        if ys.min() >= top and ys.max() < bottom and xs.min() >= left and xs.max() < right:
            gray[ndimage.binary_dilation(labels == k, iterations=2)] = 255


def remove_border_bits(gray: np.ndarray) -> None:
    """Erase small leftovers of the panel's rounded border along the edges."""
    labels, _ = ndimage.label(gray < 140)
    h, w = gray.shape
    for k, sl in enumerate(ndimage.find_objects(labels), 1):
        ys, xs = sl
        touches = ys.start == 0 or xs.start == 0 or ys.stop == h or xs.stop == w
        if touches and (labels[sl] == k).sum() < 80:
            gray[labels == k] = 255


def main() -> None:
    catalog_file = ROOT / "catalog.json"
    old = {p["id"]: p for p in json.loads(catalog_file.read_text())} if catalog_file.exists() else {}
    catalog = []
    for sheet, labels in SHEETS.items():
        gray_sheet = np.array(Image.open(ROOT / "source" / f"{sheet}.png").convert("L"))
        (ROOT / sheet).mkdir(exist_ok=True)
        for label, (left, top, right, bottom) in zip(labels, panels(gray_sheet, sheet)):
            name = slug(label)
            gray = gray_sheet[top + INSET:bottom + 1 - INSET, left + INSET:right + 1 - INSET].copy()
            remove_name(gray, two_lines=name == "egyptian-slave-homes")
            remove_border_bits(gray)
            h, w = gray.shape
            big = np.array(Image.fromarray(gray).resize((w * SCALE, h * SCALE), Image.LANCZOS))
            d = trace(big < 150, 1 / SCALE)
            (ROOT / sheet / f"{name}.svg").write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
                f'<path d="{d}" fill="#111" fill-rule="evenodd"/></svg>\n')
            pid = f"{sheet}/{name}"
            catalog.append({"id": pid, "label": label, "width": w, "height": h,
                            "words": old.get(pid, {}).get("words", [])})
    catalog_file.write_text(json.dumps(catalog, indent=1) + "\n")
    print(f"traced {len(catalog)} drawings into {ROOT}")


if __name__ == "__main__":
    main()

"""Original storybook-style line art for coloring pages, drawn from shapes in code.

A page is US Letter (8.5 x 11 in) as an SVG with an 850 x 1100 view box: a framed picture with
layered hills, a textured sky, water and ground, the things the chapter talks about in front, and the
verse on a ribbon underneath. Outlines are black with white fills, so shapes in front cover the lines
behind them and every area is a closed space to color. Thinner texture lines (bark, wool, ripples,
grass) add detail without boxing areas in.
"""
from __future__ import annotations

import math
import random
from xml.sax.saxutils import escape

from .scenes import Plan

W, H = 850, 1100
PIC = (40, 40, 770, 760)            # x, y, width, height of the picture frame
GROUND = 600                        # the front edge of the hills
INK = "#111"
LINE = 4.5                          # outlines
FINE = 2.5                          # texture lines


def f(n: float) -> str:
    return f"{n:.1f}"


def shape(d: str, fill: str = "#fff", width: float = LINE) -> str:
    return (f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def line(d: str, width: float = FINE) -> str:
    return shape(d, "none", width)


def dot(x, y, r) -> str:
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{INK}"/>'


def ellipse(cx, cy, rx, ry, width=LINE, angle=0.0) -> str:
    turn = f' transform="rotate({f(angle)} {f(cx)} {f(cy)})"' if angle else ""
    return (f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="#fff" stroke="{INK}" '
            f'stroke-width="{width}"{turn}/>')


def scallop(cx, cy, rx, ry, n, bulge=0.6, start=0.0) -> str:
    """A closed puffy outline (a cloud, a tree's leaves, a sheep's wool): n arcs around an ellipse."""
    pts = [(cx + rx * math.cos(start + 2 * math.pi * k / n), cy + ry * math.sin(start + 2 * math.pi * k / n))
           for k in range(n)]
    d = f"M{f(pts[0][0])} {f(pts[0][1])} "
    for k in range(n):
        (x1, y1), (x2, y2) = pts[k], pts[(k + 1) % n]
        r = math.hypot(x2 - x1, y2 - y1) * bulge
        d += f"A{f(r)} {f(r)} 0 0 1 {f(x2)} {f(y2)} "
    return d + "Z"


# ---- sky ----

def sun(rng, x=175, y=165, r=50) -> str:
    rays = []
    for k in range(16):
        a = k * math.pi / 8
        reach = 34 if k % 2 == 0 else 20
        rays.append(shape(f"M{f(x + math.cos(a - .12) * (r + 10))} {f(y + math.sin(a - .12) * (r + 10))} "
                          f"L{f(x + math.cos(a) * (r + 10 + reach))} {f(y + math.sin(a) * (r + 10 + reach))} "
                          f"L{f(x + math.cos(a + .12) * (r + 10))} {f(y + math.sin(a + .12) * (r + 10))} Z", width=3))
    glow = line(f"M{f(x - r * .55)} {f(y + 8)} a{f(r * .55)} {f(r * .5)} 0 0 0 {f(r * 1.1)} 0")
    return "".join(rays) + ellipse(x, y, r, r) + glow


def sparkle(x, y, r) -> str:
    return line(f"M{f(x - r)} {f(y)} L{f(x + r)} {f(y)} M{f(x)} {f(y - r)} L{f(x)} {f(y + r)}")


def moon(rng, x=690, y=150, r=46) -> str:
    inner = r * 1.3
    crescent = shape(f"M{f(x)} {f(y - r)} A{r} {r} 0 1 0 {f(x)} {f(y + r)} A{f(inner)} {f(inner)} 0 0 1 {f(x)} {f(y - r)} Z")
    return crescent + sparkle(x - 70, y + 50, 10) + sparkle(x + 40, y + 70, 7)


def star(x, y, r) -> str:
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append(f"{f(x + math.cos(a) * rr)} {f(y + math.sin(a) * rr)}")
    return shape("M" + " L".join(pts) + " Z", width=3)


def stars(rng) -> str:
    out = [star(rng.uniform(290, 760), rng.uniform(75, 250), rng.uniform(11, 20)) for _ in range(6)]
    out += [sparkle(rng.uniform(260, 780), rng.uniform(70, 280), rng.uniform(5, 8)) for _ in range(6)]
    return "".join(out)


def cloud(x, y, s=1.0) -> str:
    puff = shape(scallop(x, y, 85 * s, 34 * s, 9, 0.62, start=0.3))
    swirls = line(f"M{f(x - 40 * s)} {f(y + 6 * s)} q {f(18 * s)} {f(-16 * s)} {f(36 * s)} 0 "
                  f"M{f(x + 10 * s)} {f(y - 4 * s)} q {f(16 * s)} {f(-14 * s)} {f(32 * s)} 0")
    return puff + swirls


def clouds(rng) -> str:
    return cloud(rng.uniform(330, 400), 120, 1.0) + cloud(rng.uniform(560, 620), 215, 0.8)


# ---- land, water and the way through ----

def hill(top, height, bulges) -> str:
    x0, x1, n = 40, 810, len(bulges) - 1
    d = f"M{x0} {f(top + height)} L{x0} {f(top + bulges[0])} "
    for k in range(n):
        xa, xb = x0 + (x1 - x0) * k / n, x0 + (x1 - x0) * (k + 1) / n
        ya, yb = top + bulges[k], top + bulges[k + 1]
        d += f"C {f(xa + (xb - xa) * .35)} {f(ya - 40)}, {f(xa + (xb - xa) * .65)} {f(yb - 40)}, {f(xb)} {f(yb)} "
    return d + f"L{x1} {f(top + height)} Z"


def hills(rng) -> str:
    """Three layers of rolling hills, back to front, each with a few strokes of texture."""
    out = []
    for top, rows in ((GROUND - 170, 3), (GROUND - 95, 4), (GROUND - 25, 3)):
        out.append(shape(hill(top, 320, [rng.uniform(-25, 25) for _ in range(rows + 1)])))
        for _ in range(5):
            x, y = rng.uniform(80, 770), top + rng.uniform(28, 62)
            out.append(line(f"M{f(x)} {f(y)} q 14 -8 28 0"))
    return "".join(out)


def mountains(rng) -> str:
    peaks = [(40, 430), (150, 300), (260, 380), (390, 250), (520, 360), (640, 280), (810, 400)]
    pts = [(x, y + rng.uniform(-15, 15)) for x, y in peaks]
    out = [shape(f"M40 {GROUND} " + " ".join(f"L{f(x)} {f(y)}" for x, y in pts) + f" L810 {GROUND} Z")]
    for x, y in pts[1:-1]:                          # snow caps and ridge lines
        if y < 330:
            out.append(line(f"M{f(x - 34)} {f(y + 40)} l 14 -8 l 10 10 l 10 -10 l 14 8"))
        out.append(line(f"M{f(x)} {f(y + 6)} q {f(rng.uniform(-14, 14))} 60 {f(rng.uniform(-30, 30))} 120"))
    return "".join(out)


def waves(rng, top=GROUND + 60) -> str:
    out = [shape(f"M40 {top} C 240 {top - 14}, 560 {top + 14}, 810 {top} L810 800 L40 800 Z")]
    for row in range(4):
        y, x = top + 30 + row * 34, 40 - (row % 2) * 40
        while x < 810:                              # a crest that curls over at its tip
            out.append(line(f"M{f(x)} {f(y)} q 30 -22 60 0 q -10 -2 -14 -9 q 4 -5 10 -3", 3))
            x += 80
    return "".join(out)


def path(rng) -> str:
    """A path that starts narrow far away in the hills and widens toward the front."""
    top = GROUND - 120
    road = shape(f"M405 {top} C 380 {top + 70}, 470 {top + 140}, 400 {top + 210} C 350 {top + 260}, 360 770, 320 800 "
                 f"L 545 800 C 520 770, 520 {top + 260}, 470 {top + 210} C 540 {top + 140}, 430 {top + 70}, 425 {top} Z")
    stones = "".join(ellipse(rng.uniform(390, 490), rng.uniform(top + 230, 790), rng.uniform(7, 12), rng.uniform(4, 7), FINE)
                     for _ in range(5))
    return road + stones


def meadow(rng) -> str:
    """Grass tufts across the front of the land."""
    out = []
    for _ in range(14):
        x, y = rng.uniform(60, 790), rng.uniform(GROUND + 30, 790)
        out.append(line(f"M{f(x)} {f(y)} q -4 -14 -12 -22 M{f(x)} {f(y)} q 0 -16 2 -28 M{f(x)} {f(y)} q 4 -12 12 -20"))
    return "".join(out)


# ---- things in front (each drawn around a base point x, y on the ground, at scale s) ----

def tree(x, y, s=1.0) -> str:
    trunk = shape(f"M{f(x - 34*s)} {f(y)} q {f(16*s)} {f(-8*s)} {f(20*s)} {f(-30*s)} L{f(x - 12*s)} {f(y - 120*s)} "
                  f"L{f(x + 12*s)} {f(y - 120*s)} L{f(x + 14*s)} {f(y - 30*s)} q {f(4*s)} {f(22*s)} {f(20*s)} {f(30*s)} Z")
    bark = line(f"M{f(x - 4*s)} {f(y - 20*s)} q {f(-4*s)} {f(-30*s)} 0 {f(-60*s)} "
                f"M{f(x + 6*s)} {f(y - 50*s)} q {f(4*s)} {f(-20*s)} 0 {f(-40*s)}")
    leaves = shape(scallop(x, y - 180 * s, 95 * s, 78 * s, 11, 0.6, start=0.2))
    clumps = "".join(line(f"M{f(x + dx*s)} {f(y + dy*s)} q {f(14*s)} {f(-14*s)} {f(28*s)} 0")
                     for dx, dy in ((-60, -195), (-10, -230), (20, -165), (-40, -145), (40, -205)))
    return trunk + bark + leaves + clumps


def flower(x, y, s=1.0) -> str:
    head = y - 80 * s
    stem = line(f"M{f(x)} {f(y)} q {f(-6*s)} {f(-40*s)} 0 {f(-80*s)}", 3)
    leaf = shape(f"M{f(x - 2*s)} {f(y - 30*s)} q {f(26*s)} {f(-22*s)} {f(40*s)} {f(-6*s)} "
                 f"q {f(-18*s)} {f(18*s)} {f(-40*s)} {f(6*s)} Z", width=3)
    petals = "".join(ellipse(x + math.cos(a) * 20 * s, head + math.sin(a) * 20 * s, 15 * s, 8 * s, 3, math.degrees(a))
                     for a in (k * math.pi / 4 for k in range(8)))
    return stem + leaf + petals + ellipse(x, head, 10 * s, 10 * s, 3) + dot(x, head, 2.5 * s)


def flowers(x, y, s=1.0) -> str:
    return flower(x - 48 * s, y + 6 * s, s * 0.85) + flower(x + 46 * s, y + 4 * s, s * 0.9) + flower(x, y, s * 1.05)


def sheep(x, y, s=1.0) -> str:
    legs = ""
    for dx in (-48, -22, 22, 46):
        lx = x + dx * s
        legs += shape(f"M{f(lx - 6*s)} {f(y - 40*s)} L{f(lx - 6*s)} {f(y - 4*s)} L{f(lx + 7*s)} {f(y - 4*s)} L{f(lx + 7*s)} {f(y - 40*s)} Z", width=3.5)
        legs += shape(f"M{f(lx - 7*s)} {f(y - 6*s)} h {f(15*s)} v {f(7*s)} h {f(-15*s)} Z", INK, 2)
    wool = shape(scallop(x, y - 75 * s, 78 * s, 44 * s, 13, 0.62))
    curls = "".join(line(f"M{f(x + dx*s)} {f(y + dy*s)} a {f(6*s)} {f(6*s)} 0 1 1 {f(8*s)} {f(4*s)}", 2.2)
                    for dx, dy in ((-40, -90), (-12, -70), (14, -95), (36, -68), (-30, -60), (2, -108)))
    head = shape(f"M{f(x + 58*s)} {f(y - 100*s)} q {f(34*s)} {f(-10*s)} {f(44*s)} {f(16*s)} "
                 f"q {f(4*s)} {f(30*s)} {f(-22*s)} {f(36*s)} q {f(-26*s)} {f(-4*s)} {f(-30*s)} {f(-24*s)} Z")
    ear = shape(f"M{f(x + 64*s)} {f(y - 96*s)} q {f(-24*s)} {f(-6*s)} {f(-30*s)} {f(10*s)} q {f(14*s)} {f(8*s)} {f(28*s)} {f(4*s)} Z", width=3)
    face = dot(x + 86 * s, y - 86 * s, 3.5 * s) + line(f"M{f(x + 92*s)} {f(y - 66*s)} q {f(4*s)} {f(4*s)} {f(8*s)} 0", 2.2)
    tail = shape(scallop(x - 82 * s, y - 84 * s, 12 * s, 10 * s, 6, 0.6), width=3)
    return legs + tail + wool + curls + head + ear + face


def dove(x, y, s=1.0) -> str:
    y = max(170 + 60 * s, y - 330 * s)               # doves fly, inside the frame
    body = shape(f"M{f(x - 80*s)} {f(y + 10*s)} q {f(60*s)} {f(-50*s)} {f(140*s)} {f(-20*s)} "
                 f"q {f(20*s)} {f(-16*s)} {f(36*s)} {f(2*s)} l {f(14*s)} {f(4*s)} l {f(-16*s)} {f(6*s)} "
                 f"q {f(-30*s)} {f(40*s)} {f(-104*s)} {f(30*s)} l {f(-50*s)} {f(18*s)} l {f(10*s)} {f(-22*s)} l {f(-30*s)} {f(-4*s)} Z")
    wing = shape(f"M{f(x - 20*s)} {f(y - 10*s)} q {f(-10*s)} {f(-80*s)} {f(60*s)} {f(-110*s)} "
                 f"q {f(-6*s)} {f(20*s)} {f(4*s)} {f(24*s)} q {f(-12*s)} {f(18*s)} {f(2*s)} {f(24*s)} "
                 f"q {f(-14*s)} {f(16*s)} 0 {f(26*s)} q {f(-20*s)} {f(20*s)} {f(-66*s)} {f(36*s)} Z")
    feathers = line(f"M{f(x + 4*s)} {f(y - 60*s)} q {f(10*s)} {f(-10*s)} {f(24*s)} {f(-12*s)} "
                    f"M{f(x - 4*s)} {f(y - 36*s)} q {f(14*s)} {f(-8*s)} {f(30*s)} {f(-8*s)}")
    branch = line(f"M{f(x + 92*s)} {f(y - 10*s)} q {f(20*s)} {f(10*s)} {f(36*s)} {f(4*s)}", 3)
    leaves = "".join(shape(f"M{f(x + bx*s)} {f(y + by*s)} q {f(8*s)} {f(-12*s)} {f(18*s)} {f(-4*s)} "
                           f"q {f(-8*s)} {f(10*s)} {f(-18*s)} {f(4*s)} Z", width=2.5)
                     for bx, by in ((100, -6), (112, -2), (122, 0)))
    return body + wing + feathers + branch + leaves + dot(x + 60 * s, y - 14 * s, 3.5 * s)


def fish(x, y, s=1.0) -> str:
    y = y + 20 * s
    tail = shape(f"M{f(x - 58*s)} {f(y)} q {f(-20*s)} {f(-30*s)} {f(-40*s)} {f(-32*s)} q {f(10*s)} {f(32*s)} 0 {f(64*s)} "
                 f"q {f(20*s)} {f(-2*s)} {f(40*s)} {f(-32*s)} Z")
    body = shape(f"M{f(x - 60*s)} {f(y)} q {f(60*s)} {f(-56*s)} {f(120*s)} 0 q {f(-60*s)} {f(56*s)} {f(-120*s)} 0 Z")
    fin = shape(f"M{f(x - 10*s)} {f(y - 26*s)} q {f(14*s)} {f(-28*s)} {f(40*s)} {f(-22*s)} q {f(-12*s)} {f(12*s)} {f(-10*s)} {f(24*s)} Z", width=3)
    scales = "".join(line(f"M{f(x + dx*s)} {f(y + dy*s)} a {f(9*s)} {f(9*s)} 0 0 0 0 {f(16*s)}", 2.2)
                     for dx in (-30, -12, 6) for dy in (-16, 0))
    gill = line(f"M{f(x + 26*s)} {f(y - 20*s)} q {f(-10*s)} {f(20*s)} 0 {f(40*s)}", 3)
    return tail + body + fin + scales + gill + dot(x + 40 * s, y - 8 * s, 4 * s)


def boat(x, y, s=1.0) -> str:
    y = y - 20 * s
    hull = shape(f"M{f(x - 130*s)} {f(y - 10*s)} L{f(x + 130*s)} {f(y - 10*s)} q {f(-10*s)} {f(50*s)} {f(-40*s)} {f(70*s)} "
                 f"L{f(x - 90*s)} {f(y + 60*s)} q {f(-30*s)} {f(-20*s)} {f(-40*s)} {f(-70*s)} Z")
    planks = line(f"M{f(x - 118*s)} {f(y + 14*s)} L{f(x + 118*s)} {f(y + 14*s)} M{f(x - 104*s)} {f(y + 38*s)} L{f(x + 104*s)} {f(y + 38*s)}")
    house = shape(f"M{f(x - 70*s)} {f(y - 10*s)} L{f(x - 70*s)} {f(y - 70*s)} L{f(x + 70*s)} {f(y - 70*s)} L{f(x + 70*s)} {f(y - 10*s)} Z")
    roof = shape(f"M{f(x - 84*s)} {f(y - 70*s)} L{f(x)} {f(y - 124*s)} L{f(x + 84*s)} {f(y - 70*s)} Z")
    shingles = line(f"M{f(x - 56*s)} {f(y - 86*s)} L{f(x + 56*s)} {f(y - 86*s)} M{f(x - 30*s)} {f(y - 103*s)} L{f(x + 30*s)} {f(y - 103*s)}")
    windows = "".join(shape(f"M{f(x + wx*s)} {f(y - 56*s)} h {f(26*s)} v {f(24*s)} h {f(-26*s)} Z", width=3) for wx in (-34, 8))
    return hull + planks + house + roof + shingles + windows


def crown(x, y, s=1.0) -> str:
    y = y - 50 * s
    band = shape(f"M{f(x - 70*s)} {f(y)} L{f(x - 70*s)} {f(y - 70*s)} L{f(x - 38*s)} {f(y - 36*s)} L{f(x)} {f(y - 86*s)} "
                 f"L{f(x + 38*s)} {f(y - 36*s)} L{f(x + 70*s)} {f(y - 70*s)} L{f(x + 70*s)} {f(y)} Z")
    trim = line(f"M{f(x - 70*s)} {f(y - 18*s)} L{f(x + 70*s)} {f(y - 18*s)}", 3)
    jewels = "".join(ellipse(x + dx * s, y - 9 * s, 8 * s, 6 * s, 3) for dx in (-40, 0, 40))
    tips = "".join(ellipse(x + dx * s, y + dy * s, 7 * s, 7 * s, 3) for dx, dy in ((-70, -76), (0, -93), (70, -76)))
    return band + trim + jewels + tips


def lamp(x, y, s=1.0) -> str:
    y = y - 10 * s
    handle = line(f"M{f(x - 70*s)} {f(y - 22*s)} q {f(-30*s)} {f(-10*s)} {f(-20*s)} {f(-36*s)} q {f(10*s)} {f(-10*s)} {f(24*s)} {f(4*s)}", 4)
    body = shape(f"M{f(x - 70*s)} {f(y - 20*s)} q {f(60*s)} {f(-60*s)} {f(120*s)} {f(-30*s)} l {f(24*s)} {f(-10*s)} "
                 f"l {f(-6*s)} {f(18*s)} q {f(-50*s)} {f(46*s)} {f(-138*s)} {f(22*s)} Z")
    foot = shape(f"M{f(x - 40*s)} {f(y - 4*s)} q {f(30*s)} {f(-14*s)} {f(60*s)} 0 l {f(6*s)} {f(12*s)} h {f(-72*s)} Z", width=3.5)
    flame = shape(f"M{f(x + 80*s)} {f(y - 58*s)} q {f(-22*s)} {f(-30*s)} {f(6*s)} {f(-70*s)} q {f(24*s)} {f(38*s)} {f(-6*s)} {f(70*s)} Z")
    inner = line(f"M{f(x + 82*s)} {f(y - 64*s)} q {f(-6*s)} {f(-14*s)} {f(4*s)} {f(-30*s)}")
    deco = line(f"M{f(x - 30*s)} {f(y - 40*s)} q {f(30*s)} {f(-14*s)} {f(60*s)} {f(-6*s)}")
    return handle + body + foot + flame + inner + deco


def cup(x, y, s=1.0) -> str:
    foot = shape(f"M{f(x - 40*s)} {f(y)} q {f(40*s)} {f(-28*s)} {f(80*s)} 0 Z")
    stem = shape(f"M{f(x - 7*s)} {f(y - 60*s)} L{f(x - 7*s)} {f(y - 16*s)} L{f(x + 7*s)} {f(y - 16*s)} L{f(x + 7*s)} {f(y - 60*s)} Z")
    knot = ellipse(x, y - 40 * s, 13 * s, 7 * s, 3)
    bowl = shape(f"M{f(x - 50*s)} {f(y - 140*s)} L{f(x + 50*s)} {f(y - 140*s)} q {f(4*s)} {f(70*s)} {f(-50*s)} {f(80*s)} "
                 f"q {f(-54*s)} {f(-10*s)} {f(-50*s)} {f(-80*s)} Z")
    band = line(f"M{f(x - 46*s)} {f(y - 112*s)} q {f(46*s)} {f(12*s)} {f(92*s)} 0", 3)
    rim = ellipse(x, y - 140 * s, 50 * s, 9 * s, 3.5)
    drop = shape(f"M{f(x + 44*s)} {f(y - 136*s)} q {f(10*s)} {f(16*s)} 0 {f(26*s)} q {f(-10*s)} {f(-10*s)} 0 {f(-26*s)} Z", width=2.5)
    return foot + stem + knot + bowl + band + rim + drop


def heart(x, y, s=1.0) -> str:
    y = max(130 + 60 * s, y - 260 * s)

    def outline(k):
        return (f"M{f(x)} {f(y + 44*s*k)} C {f(x - 76*s*k)} {f(y - 8*s*k)}, {f(x - 44*s*k)} {f(y - 76*s*k)}, {f(x)} {f(y - 38*s*k)} "
                f"C {f(x + 44*s*k)} {f(y - 76*s*k)}, {f(x + 76*s*k)} {f(y - 8*s*k)}, {f(x)} {f(y + 44*s*k)} Z")
    rays = "".join(line(f"M{f(x + math.cos(a) * 90 * s)} {f(y + math.sin(a) * 80 * s)} "
                        f"L{f(x + math.cos(a) * 112 * s)} {f(y + math.sin(a) * 100 * s)}", 3)
                   for a in (k * math.pi / 5 - math.pi / 2 for k in range(10)))
    return rays + shape(outline(1)) + line(outline(0.6))


BACKGROUND_ART = {"sun": sun, "moon": moon, "stars": stars, "clouds": clouds, "mountains": mountains,
                  "waves": waves, "path": path}
FOREGROUND_ART = {"tree": tree, "flowers": flowers, "sheep": sheep, "dove": dove, "fish": fish, "boat": boat,
                  "crown": crown, "lamp": lamp, "cup": cup, "heart": heart}
SKY = ["stars", "sun", "moon", "clouds"]
# About how wide each drawing is at scale 1, and how far its base point sits from its middle.
SIZES = {"tree": 190, "flowers": 150, "sheep": 220, "dove": 240, "fish": 200, "boat": 270, "crown": 150,
         "lamp": 210, "cup": 110, "heart": 230}
OFFSET = {"sheep": -10, "lamp": -15, "dove": -25}
MAX_SCALE = {"dove": 1.3, "heart": 1.3, "crown": 1.6, "cup": 1.7}   # so they never fill the whole sky


def wrap(text: str, width: int = 50) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + ([cur] if cur else [])


def frame() -> str:
    x, y, w, h = PIC
    curls = "".join(line(f"M{f(cx)} {f(cy)} q {f(dx*26)} {f(dy*4)} {f(dx*30)} {f(dy*30)} "
                         f"q {f(-dx*12)} {f(-dy*4)} {f(-dx*16)} {f(-dy*16)}", 3)
                    for cx, cy, dx, dy in ((x + 16, y + 16, 1, 1), (x + w - 16, y + 16, -1, 1),
                                           (x + 16, y + h - 16, 1, -1), (x + w - 16, y + h - 16, -1, -1)))
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="none" stroke="{INK}" stroke-width="7"/>'
            f'<rect x="{x + 10}" y="{y + 10}" width="{w - 20}" height="{h - 20}" rx="16" fill="none" stroke="{INK}" stroke-width="2.5"/>'
            + curls)


def ribbon(top: float, height: float) -> str:
    """A banner for the verse, with folded ends tucked behind it."""
    l, r = 70, 780
    left = shape(f"M{l + 50} {f(top + 18)} L{l} {f(top + 18)} L{l + 24} {f(top + 18 + height / 2)} L{l} {f(top + 18 + height)} L{l + 50} {f(top + 18 + height)} Z")
    right = shape(f"M{r - 50} {f(top + 18)} L{r} {f(top + 18)} L{r - 24} {f(top + 18 + height / 2)} L{r} {f(top + 18 + height)} L{r - 50} {f(top + 18 + height)} Z")
    body = shape(f"M{l + 36} {f(top)} L{r - 36} {f(top)} L{r - 36} {f(top + height)} L{l + 36} {f(top + height)} Z")
    return left + right + body


def draw_page(plan: Plan, seed: str | None = None) -> str:
    """The whole coloring page as an SVG string."""
    rng = random.Random(seed or plan.reference)
    x, y, w, h = PIC
    parts = [f'<clipPath id="pic"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22"/></clipPath><g clip-path="url(#pic)">']
    for m in SKY:
        if m in plan.background:
            parts.append(BACKGROUND_ART[m](rng))
    if len([m for m in plan.background if m in SKY]) < 2:
        parts.append(clouds(rng))                     # a sky with something in it to color
    if "mountains" in plan.background:
        parts.append(mountains(rng))
    parts.append(hills(rng))
    if "path" in plan.background:
        parts.append(path(rng))
    parts.append(waves(rng) if "waves" in plan.background else meadow(rng))
    front = plan.foreground[:3]                       # up to three things, so each has room
    widths = [SIZES.get(m, 150) for m in front]
    scale = min(1.9, (w - 80) / (sum(widths) + 50 * (len(front) - 1)))
    gap = (w - sum(widths) * scale) / (len(front) + 1)
    cx = x + gap
    for m, width in zip(front, widths):
        mid = cx + width * scale / 2
        size = min(scale, MAX_SCALE.get(m, scale))
        parts.append(FOREGROUND_ART[m](mid + OFFSET.get(m, 0) * scale + rng.uniform(-8, 8), GROUND + 150, size))
        cx += width * scale + gap
    parts.append("</g>")
    parts.append(frame())
    number, verse = plan.verse
    lines = wrap(verse)[:4]
    top, row = 836, 36
    band = 28 + len(lines) * row
    parts.append(ribbon(top, band))
    for k, text_line in enumerate(lines):
        parts.append(f'<text x="{W / 2}" y="{top + 40 + k * row}" text-anchor="middle" font-family="Georgia, serif" '
                     f'font-size="27" fill="{INK}">{escape(text_line)}</text>')
    parts.append(f'<text x="{W / 2}" y="{top + band + 64}" text-anchor="middle" font-family="Georgia, serif" font-size="24" '
                 f'font-style="italic" fill="{INK}">{escape(plan.reference)}:{number} (KJV)</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="Coloring page for {escape(plan.reference)}">'
            f'<title>Colors of Eden: {escape(plan.reference)}</title><rect width="{W}" height="{H}" fill="#fff"/>'
            + "".join(parts) + "</svg>")

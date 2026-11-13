// Original storybook-style line art for coloring pages, drawn from shapes in code. This is the same
// drawing as coe/art.py, for the web page: a US Letter SVG (850 x 1100 view box) with a framed scene of
// layered hills, sky, water and ground, the chapter's things in front and the verse on a ribbon.
// Black outlines with white fills, so every area is a closed space to color.

const W = 850, H = 1100;
const PIC = [40, 40, 770, 760];
const GROUND = 600;
const INK = '#111';
const LINE = 4.5, FINE = 2.5;
const { cos, sin, PI, hypot, max, min } = Math;

const f = (n) => (Math.round(n * 10) / 10).toFixed(1);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const shape = (d, fill = '#fff', width = LINE) =>
  `<path d="${d}" fill="${fill}" stroke="${INK}" stroke-width="${width}" stroke-linejoin="round" stroke-linecap="round"/>`;
const line = (d, width = FINE) => shape(d, 'none', width);
const dot = (x, y, r) => `<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" fill="${INK}"/>`;
const ellipse = (cx, cy, rx, ry, width = LINE, angle = 0) =>
  `<ellipse cx="${f(cx)}" cy="${f(cy)}" rx="${f(rx)}" ry="${f(ry)}" fill="#fff" stroke="${INK}" stroke-width="${width}"${angle ? ` transform="rotate(${f(angle)} ${f(cx)} ${f(cy)})"` : ''}/>`;

/** A seeded random number generator, so the same chapter always draws the same page. */
export function randomFor(seed) {
  let h = 1779033703 ^ seed.length;
  for (let i = 0; i < seed.length; i++) { h = Math.imul(h ^ seed.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
  let a = h >>> 0;
  const next = () => { a = (a + 0x6d2b79f5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  return { uniform: (lo, hi) => lo + (hi - lo) * next() };
}

/** A closed puffy outline (a cloud, a tree's leaves, a sheep's wool): n arcs around an ellipse. */
function scallop(cx, cy, rx, ry, n, bulge = 0.6, start = 0) {
  const pts = Array.from({ length: n }, (_, k) => [cx + rx * cos(start + 2 * PI * k / n), cy + ry * sin(start + 2 * PI * k / n)]);
  let d = `M${f(pts[0][0])} ${f(pts[0][1])} `;
  for (let k = 0; k < n; k++) {
    const [x1, y1] = pts[k], [x2, y2] = pts[(k + 1) % n];
    const r = hypot(x2 - x1, y2 - y1) * bulge;
    d += `A${f(r)} ${f(r)} 0 0 1 ${f(x2)} ${f(y2)} `;
  }
  return d + 'Z';
}

// ---- sky ----
function sun(rng, x = 175, y = 165, r = 50) {
  let rays = '';
  for (let k = 0; k < 16; k++) {
    const a = k * PI / 8, reach = k % 2 === 0 ? 34 : 20;
    rays += shape(`M${f(x + cos(a - .12) * (r + 10))} ${f(y + sin(a - .12) * (r + 10))} L${f(x + cos(a) * (r + 10 + reach))} ${f(y + sin(a) * (r + 10 + reach))} L${f(x + cos(a + .12) * (r + 10))} ${f(y + sin(a + .12) * (r + 10))} Z`, '#fff', 3);
  }
  return rays + ellipse(x, y, r, r) + line(`M${f(x - r * .55)} ${f(y + 8)} a${f(r * .55)} ${f(r * .5)} 0 0 0 ${f(r * 1.1)} 0`);
}
const sparkle = (x, y, r) => line(`M${f(x - r)} ${f(y)} L${f(x + r)} ${f(y)} M${f(x)} ${f(y - r)} L${f(x)} ${f(y + r)}`);
function moon(rng, x = 690, y = 150, r = 46) {
  const inner = r * 1.3;
  return shape(`M${f(x)} ${f(y - r)} A${r} ${r} 0 1 0 ${f(x)} ${f(y + r)} A${f(inner)} ${f(inner)} 0 0 1 ${f(x)} ${f(y - r)} Z`) + sparkle(x - 70, y + 50, 10) + sparkle(x + 40, y + 70, 7);
}
function star(x, y, r) {
  const pts = Array.from({ length: 10 }, (_, k) => { const a = -PI / 2 + k * PI / 5, rr = k % 2 === 0 ? r : r * 0.45; return `${f(x + cos(a) * rr)} ${f(y + sin(a) * rr)}`; });
  return shape('M' + pts.join(' L') + ' Z', '#fff', 3);
}
function stars(rng) {
  let out = '';
  for (let i = 0; i < 6; i++) out += star(rng.uniform(290, 760), rng.uniform(75, 250), rng.uniform(11, 20));
  for (let i = 0; i < 6; i++) out += sparkle(rng.uniform(260, 780), rng.uniform(70, 280), rng.uniform(5, 8));
  return out;
}
function cloud(x, y, s = 1) {
  return shape(scallop(x, y, 85 * s, 34 * s, 9, 0.62, 0.3)) +
    line(`M${f(x - 40 * s)} ${f(y + 6 * s)} q ${f(18 * s)} ${f(-16 * s)} ${f(36 * s)} 0 M${f(x + 10 * s)} ${f(y - 4 * s)} q ${f(16 * s)} ${f(-14 * s)} ${f(32 * s)} 0`);
}
const clouds = (rng) => cloud(rng.uniform(330, 400), 120, 1) + cloud(rng.uniform(560, 620), 215, 0.8);

// ---- land, water and the way through ----
function hill(top, height, bulges) {
  const x0 = 40, x1 = 810, n = bulges.length - 1;
  let d = `M${x0} ${f(top + height)} L${x0} ${f(top + bulges[0])} `;
  for (let k = 0; k < n; k++) {
    const xa = x0 + (x1 - x0) * k / n, xb = x0 + (x1 - x0) * (k + 1) / n, ya = top + bulges[k], yb = top + bulges[k + 1];
    d += `C ${f(xa + (xb - xa) * .35)} ${f(ya - 40)}, ${f(xa + (xb - xa) * .65)} ${f(yb - 40)}, ${f(xb)} ${f(yb)} `;
  }
  return d + `L${x1} ${f(top + height)} Z`;
}
function hills(rng) {
  let out = '';
  for (const [top, rows] of [[GROUND - 170, 3], [GROUND - 95, 4], [GROUND - 25, 3]]) {
    out += shape(hill(top, 320, Array.from({ length: rows + 1 }, () => rng.uniform(-25, 25))));
    for (let i = 0; i < 5; i++) { const x = rng.uniform(80, 770), y = top + rng.uniform(28, 62); out += line(`M${f(x)} ${f(y)} q 14 -8 28 0`); }
  }
  return out;
}
function mountains(rng) {
  const pts = [[40, 430], [150, 300], [260, 380], [390, 250], [520, 360], [640, 280], [810, 400]].map(([x, y]) => [x, y + rng.uniform(-15, 15)]);
  let out = shape(`M40 ${GROUND} ` + pts.map(([x, y]) => `L${f(x)} ${f(y)}`).join(' ') + ` L810 ${GROUND} Z`);
  for (const [x, y] of pts.slice(1, -1)) {
    if (y < 330) out += line(`M${f(x - 34)} ${f(y + 40)} l 14 -8 l 10 10 l 10 -10 l 14 8`);
    out += line(`M${f(x)} ${f(y + 6)} q ${f(rng.uniform(-14, 14))} 60 ${f(rng.uniform(-30, 30))} 120`);
  }
  return out;
}
function waves(rng, top = GROUND + 60) {
  let out = shape(`M40 ${top} C 240 ${top - 14}, 560 ${top + 14}, 810 ${top} L810 800 L40 800 Z`);
  for (let row = 0; row < 4; row++) {
    const y = top + 30 + row * 34;
    for (let x = 40 - (row % 2) * 40; x < 810; x += 80) out += line(`M${f(x)} ${f(y)} q 30 -22 60 0 q -10 -2 -14 -9 q 4 -5 10 -3`, 3);
  }
  return out;
}
function path(rng) {
  const top = GROUND - 120;
  const road = shape(`M405 ${top} C 380 ${top + 70}, 470 ${top + 140}, 400 ${top + 210} C 350 ${top + 260}, 360 770, 320 800 L 545 800 C 520 770, 520 ${top + 260}, 470 ${top + 210} C 540 ${top + 140}, 430 ${top + 70}, 425 ${top} Z`);
  let stones = '';
  for (let i = 0; i < 5; i++) stones += ellipse(rng.uniform(390, 490), rng.uniform(top + 230, 790), rng.uniform(7, 12), rng.uniform(4, 7), FINE);
  return road + stones;
}
function meadow(rng) {
  let out = '';
  for (let i = 0; i < 14; i++) {
    const x = rng.uniform(60, 790), y = rng.uniform(GROUND + 30, 790);
    out += line(`M${f(x)} ${f(y)} q -4 -14 -12 -22 M${f(x)} ${f(y)} q 0 -16 2 -28 M${f(x)} ${f(y)} q 4 -12 12 -20`);
  }
  return out;
}

// ---- things in front (each drawn around a base point x, y on the ground, at scale s) ----
function tree(x, y, s = 1) {
  const trunk = shape(`M${f(x - 34 * s)} ${f(y)} q ${f(16 * s)} ${f(-8 * s)} ${f(20 * s)} ${f(-30 * s)} L${f(x - 12 * s)} ${f(y - 120 * s)} L${f(x + 12 * s)} ${f(y - 120 * s)} L${f(x + 14 * s)} ${f(y - 30 * s)} q ${f(4 * s)} ${f(22 * s)} ${f(20 * s)} ${f(30 * s)} Z`);
  const bark = line(`M${f(x - 4 * s)} ${f(y - 20 * s)} q ${f(-4 * s)} ${f(-30 * s)} 0 ${f(-60 * s)} M${f(x + 6 * s)} ${f(y - 50 * s)} q ${f(4 * s)} ${f(-20 * s)} 0 ${f(-40 * s)}`);
  const leaves = shape(scallop(x, y - 180 * s, 95 * s, 78 * s, 11, 0.6, 0.2));
  const clumps = [[-60, -195], [-10, -230], [20, -165], [-40, -145], [40, -205]].map(([dx, dy]) => line(`M${f(x + dx * s)} ${f(y + dy * s)} q ${f(14 * s)} ${f(-14 * s)} ${f(28 * s)} 0`)).join('');
  return trunk + bark + leaves + clumps;
}
function flower(x, y, s = 1) {
  const head = y - 80 * s;
  const stem = line(`M${f(x)} ${f(y)} q ${f(-6 * s)} ${f(-40 * s)} 0 ${f(-80 * s)}`, 3);
  const leaf = shape(`M${f(x - 2 * s)} ${f(y - 30 * s)} q ${f(26 * s)} ${f(-22 * s)} ${f(40 * s)} ${f(-6 * s)} q ${f(-18 * s)} ${f(18 * s)} ${f(-40 * s)} ${f(6 * s)} Z`, '#fff', 3);
  let petals = '';
  for (let k = 0; k < 8; k++) { const a = k * PI / 4; petals += ellipse(x + cos(a) * 20 * s, head + sin(a) * 20 * s, 15 * s, 8 * s, 3, a * 180 / PI); }
  return stem + leaf + petals + ellipse(x, head, 10 * s, 10 * s, 3) + dot(x, head, 2.5 * s);
}
const flowers = (x, y, s = 1) => flower(x - 48 * s, y + 6 * s, s * 0.85) + flower(x + 46 * s, y + 4 * s, s * 0.9) + flower(x, y, s * 1.05);
function sheep(x, y, s = 1) {
  let legs = '';
  for (const dx of [-48, -22, 22, 46]) {
    const lx = x + dx * s;
    legs += shape(`M${f(lx - 6 * s)} ${f(y - 40 * s)} L${f(lx - 6 * s)} ${f(y - 4 * s)} L${f(lx + 7 * s)} ${f(y - 4 * s)} L${f(lx + 7 * s)} ${f(y - 40 * s)} Z`, '#fff', 3.5);
    legs += shape(`M${f(lx - 7 * s)} ${f(y - 6 * s)} h ${f(15 * s)} v ${f(7 * s)} h ${f(-15 * s)} Z`, INK, 2);
  }
  const wool = shape(scallop(x, y - 75 * s, 78 * s, 44 * s, 13, 0.62));
  const curls = [[-40, -90], [-12, -70], [14, -95], [36, -68], [-30, -60], [2, -108]].map(([dx, dy]) => line(`M${f(x + dx * s)} ${f(y + dy * s)} a ${f(6 * s)} ${f(6 * s)} 0 1 1 ${f(8 * s)} ${f(4 * s)}`, 2.2)).join('');
  const head = shape(`M${f(x + 58 * s)} ${f(y - 100 * s)} q ${f(34 * s)} ${f(-10 * s)} ${f(44 * s)} ${f(16 * s)} q ${f(4 * s)} ${f(30 * s)} ${f(-22 * s)} ${f(36 * s)} q ${f(-26 * s)} ${f(-4 * s)} ${f(-30 * s)} ${f(-24 * s)} Z`);
  const ear = shape(`M${f(x + 64 * s)} ${f(y - 96 * s)} q ${f(-24 * s)} ${f(-6 * s)} ${f(-30 * s)} ${f(10 * s)} q ${f(14 * s)} ${f(8 * s)} ${f(28 * s)} ${f(4 * s)} Z`, '#fff', 3);
  const face = dot(x + 86 * s, y - 86 * s, 3.5 * s) + line(`M${f(x + 92 * s)} ${f(y - 66 * s)} q ${f(4 * s)} ${f(4 * s)} ${f(8 * s)} 0`, 2.2);
  const tail = shape(scallop(x - 82 * s, y - 84 * s, 12 * s, 10 * s, 6, 0.6), '#fff', 3);
  return legs + tail + wool + curls + head + ear + face;
}
// The dove: an original line drawing in flight, facing right: two wings with soft rounded feathers, a
// far one behind the near one, and a fanned tail. Each part is drawn in its own coordinates around the
// bird's middle and placed with place().
const DOVE_FAR_WING = 'M66 2 C 60 -40 50 -86 30 -124 C 56 -134 80 -120 74 -102 C 98 -104 110 -84 98 -70 C 116 -62 116 -40 102 -34 C 108 -18 98 -6 84 -4 Z';
const DOVE_BODY = 'M74 -4 C 76 -36 100 -48 120 -36 C 128 -31 132 -24 133 -18 L 152 -12 L 132 -4 C 130 40 86 84 20 90 C -24 94 -60 86 -88 74 C -100 86 -112 98 -126 104 C -120 94 -116 86 -114 78 C -126 82 -138 82 -146 78 C -136 72 -126 66 -118 60 C -128 56 -136 50 -140 42 C -120 44 -100 46 -84 44 C -50 38 -16 30 14 20 C 42 12 62 6 74 -4 Z';
const DOVE_NEAR_WING = 'M62 12 C 44 -40 10 -92 -40 -130 C -66 -122 -76 -102 -60 -88 C -86 -80 -92 -60 -74 -48 C -98 -40 -100 -16 -80 -8 C -44 6 -12 18 22 24 C 38 22 52 18 62 12 Z';
const DOVE_FEATHERS = 'M-44 -76 C -28 -68 -14 -58 -2 -48 M-56 -36 C -36 -30 -18 -24 0 -18 M66 -88 C 72 -78 76 -70 78 -60';

/** Moves and scales a path written with absolute M, C and L commands: each x y pair goes to (x + px*k, y + py*k). */
export function place(d, x, y, k) {
  return d.replace(/-?\d+(?:\.\d+)?\s+-?\d+(?:\.\d+)?/g, (pair) => {
    const [px, py] = pair.split(/\s+/).map(Number);
    return `${f(x + px * k)} ${f(y + py * k)}`;
  });
}

function dove(x, y, s = 1) {
  y = max(190 + 60 * s, y - 290 * s);                                   // doves fly low in the sky, clear of the sun and clouds
  const k = 0.8 * s;
  return shape(place(DOVE_FAR_WING, x, y, k)) + shape(place(DOVE_BODY, x, y, k))
    + shape(place(DOVE_NEAR_WING, x, y, k)) + line(place(DOVE_FEATHERS, x, y, k), 3)
    + dot(x + 112 * k, y - 24 * k, 5 * k);
}

function fish(x, y, s = 1) {
  y += 20 * s;
  const tail = shape(`M${f(x - 58 * s)} ${f(y)} q ${f(-20 * s)} ${f(-30 * s)} ${f(-40 * s)} ${f(-32 * s)} q ${f(10 * s)} ${f(32 * s)} 0 ${f(64 * s)} q ${f(20 * s)} ${f(-2 * s)} ${f(40 * s)} ${f(-32 * s)} Z`);
  const body = shape(`M${f(x - 60 * s)} ${f(y)} q ${f(60 * s)} ${f(-56 * s)} ${f(120 * s)} 0 q ${f(-60 * s)} ${f(56 * s)} ${f(-120 * s)} 0 Z`);
  const fin = shape(`M${f(x - 10 * s)} ${f(y - 26 * s)} q ${f(14 * s)} ${f(-28 * s)} ${f(40 * s)} ${f(-22 * s)} q ${f(-12 * s)} ${f(12 * s)} ${f(-10 * s)} ${f(24 * s)} Z`, '#fff', 3);
  let scales = '';
  for (const dx of [-30, -12, 6]) for (const dy of [-16, 0]) scales += line(`M${f(x + dx * s)} ${f(y + dy * s)} a ${f(9 * s)} ${f(9 * s)} 0 0 0 0 ${f(16 * s)}`, 2.2);
  const gill = line(`M${f(x + 26 * s)} ${f(y - 20 * s)} q ${f(-10 * s)} ${f(20 * s)} 0 ${f(40 * s)}`, 3);
  return tail + body + fin + scales + gill + dot(x + 40 * s, y - 8 * s, 4 * s);
}
function boat(x, y, s = 1) {
  y -= 20 * s;
  const hull = shape(`M${f(x - 130 * s)} ${f(y - 10 * s)} L${f(x + 130 * s)} ${f(y - 10 * s)} q ${f(-10 * s)} ${f(50 * s)} ${f(-40 * s)} ${f(70 * s)} L${f(x - 90 * s)} ${f(y + 60 * s)} q ${f(-30 * s)} ${f(-20 * s)} ${f(-40 * s)} ${f(-70 * s)} Z`);
  const planks = line(`M${f(x - 118 * s)} ${f(y + 14 * s)} L${f(x + 118 * s)} ${f(y + 14 * s)} M${f(x - 104 * s)} ${f(y + 38 * s)} L${f(x + 104 * s)} ${f(y + 38 * s)}`);
  const house = shape(`M${f(x - 70 * s)} ${f(y - 10 * s)} L${f(x - 70 * s)} ${f(y - 70 * s)} L${f(x + 70 * s)} ${f(y - 70 * s)} L${f(x + 70 * s)} ${f(y - 10 * s)} Z`);
  const roof = shape(`M${f(x - 84 * s)} ${f(y - 70 * s)} L${f(x)} ${f(y - 124 * s)} L${f(x + 84 * s)} ${f(y - 70 * s)} Z`);
  const shingles = line(`M${f(x - 56 * s)} ${f(y - 86 * s)} L${f(x + 56 * s)} ${f(y - 86 * s)} M${f(x - 30 * s)} ${f(y - 103 * s)} L${f(x + 30 * s)} ${f(y - 103 * s)}`);
  const windows = [-34, 8].map((wx) => shape(`M${f(x + wx * s)} ${f(y - 56 * s)} h ${f(26 * s)} v ${f(24 * s)} h ${f(-26 * s)} Z`, '#fff', 3)).join('');
  return hull + planks + house + roof + shingles + windows;
}
function crown(x, y, s = 1) {
  y -= 50 * s;
  const band = shape(`M${f(x - 70 * s)} ${f(y)} L${f(x - 70 * s)} ${f(y - 70 * s)} L${f(x - 38 * s)} ${f(y - 36 * s)} L${f(x)} ${f(y - 86 * s)} L${f(x + 38 * s)} ${f(y - 36 * s)} L${f(x + 70 * s)} ${f(y - 70 * s)} L${f(x + 70 * s)} ${f(y)} Z`);
  const trim = line(`M${f(x - 70 * s)} ${f(y - 18 * s)} L${f(x + 70 * s)} ${f(y - 18 * s)}`, 3);
  const jewels = [-40, 0, 40].map((dx) => ellipse(x + dx * s, y - 9 * s, 8 * s, 6 * s, 3)).join('');
  const tips = [[-70, -76], [0, -93], [70, -76]].map(([dx, dy]) => ellipse(x + dx * s, y + dy * s, 7 * s, 7 * s, 3)).join('');
  return band + trim + jewels + tips;
}
function lamp(x, y, s = 1) {
  y -= 10 * s;
  const handle = line(`M${f(x - 70 * s)} ${f(y - 22 * s)} q ${f(-30 * s)} ${f(-10 * s)} ${f(-20 * s)} ${f(-36 * s)} q ${f(10 * s)} ${f(-10 * s)} ${f(24 * s)} ${f(4 * s)}`, 4);
  const body = shape(`M${f(x - 70 * s)} ${f(y - 20 * s)} q ${f(60 * s)} ${f(-60 * s)} ${f(120 * s)} ${f(-30 * s)} l ${f(24 * s)} ${f(-10 * s)} l ${f(-6 * s)} ${f(18 * s)} q ${f(-50 * s)} ${f(46 * s)} ${f(-138 * s)} ${f(22 * s)} Z`);
  const foot = shape(`M${f(x - 40 * s)} ${f(y - 4 * s)} q ${f(30 * s)} ${f(-14 * s)} ${f(60 * s)} 0 l ${f(6 * s)} ${f(12 * s)} h ${f(-72 * s)} Z`, '#fff', 3.5);
  const flame = shape(`M${f(x + 80 * s)} ${f(y - 58 * s)} q ${f(-22 * s)} ${f(-30 * s)} ${f(6 * s)} ${f(-70 * s)} q ${f(24 * s)} ${f(38 * s)} ${f(-6 * s)} ${f(70 * s)} Z`);
  const inner = line(`M${f(x + 82 * s)} ${f(y - 64 * s)} q ${f(-6 * s)} ${f(-14 * s)} ${f(4 * s)} ${f(-30 * s)}`);
  const deco = line(`M${f(x - 30 * s)} ${f(y - 40 * s)} q ${f(30 * s)} ${f(-14 * s)} ${f(60 * s)} ${f(-6 * s)}`);
  return handle + body + foot + flame + inner + deco;
}
function cup(x, y, s = 1) {
  const foot = shape(`M${f(x - 40 * s)} ${f(y)} q ${f(40 * s)} ${f(-28 * s)} ${f(80 * s)} 0 Z`);
  const stem = shape(`M${f(x - 7 * s)} ${f(y - 60 * s)} L${f(x - 7 * s)} ${f(y - 16 * s)} L${f(x + 7 * s)} ${f(y - 16 * s)} L${f(x + 7 * s)} ${f(y - 60 * s)} Z`);
  const knot = ellipse(x, y - 40 * s, 13 * s, 7 * s, 3);
  const bowl = shape(`M${f(x - 50 * s)} ${f(y - 140 * s)} L${f(x + 50 * s)} ${f(y - 140 * s)} q ${f(4 * s)} ${f(70 * s)} ${f(-50 * s)} ${f(80 * s)} q ${f(-54 * s)} ${f(-10 * s)} ${f(-50 * s)} ${f(-80 * s)} Z`);
  const band = line(`M${f(x - 46 * s)} ${f(y - 112 * s)} q ${f(46 * s)} ${f(12 * s)} ${f(92 * s)} 0`, 3);
  const rim = ellipse(x, y - 140 * s, 50 * s, 9 * s, 3.5);
  const drop = shape(`M${f(x + 44 * s)} ${f(y - 136 * s)} q ${f(10 * s)} ${f(16 * s)} 0 ${f(26 * s)} q ${f(-10 * s)} ${f(-10 * s)} 0 ${f(-26 * s)} Z`, '#fff', 2.5);
  return foot + stem + knot + bowl + band + rim + drop;
}
function heart(x, y, s = 1) {
  y = max(130 + 60 * s, y - 260 * s);
  const outline = (k) => `M${f(x)} ${f(y + 44 * s * k)} C ${f(x - 76 * s * k)} ${f(y - 8 * s * k)}, ${f(x - 44 * s * k)} ${f(y - 76 * s * k)}, ${f(x)} ${f(y - 38 * s * k)} C ${f(x + 44 * s * k)} ${f(y - 76 * s * k)}, ${f(x + 76 * s * k)} ${f(y - 8 * s * k)}, ${f(x)} ${f(y + 44 * s * k)} Z`;
  let rays = '';
  for (let k = 0; k < 10; k++) { const a = k * PI / 5 - PI / 2; rays += line(`M${f(x + cos(a) * 90 * s)} ${f(y + sin(a) * 80 * s)} L${f(x + cos(a) * 112 * s)} ${f(y + sin(a) * 100 * s)}`, 3); }
  return rays + shape(outline(1)) + line(outline(0.6));
}

const BACKGROUND_ART = { sun, moon, stars, clouds, mountains, waves, path };
const FOREGROUND_ART = { tree, flowers, sheep, dove, fish, boat, crown, lamp, cup, heart };
const SKY = ['stars', 'sun', 'moon', 'clouds'];
const SIZES = { tree: 190, flowers: 150, sheep: 220, dove: 240, fish: 200, boat: 270, crown: 150, lamp: 210, cup: 110, heart: 230 };
const OFFSET = { sheep: -10, lamp: -15, dove: -25 };
const MAX_SCALE = { dove: 1.3, heart: 1.3, crown: 1.6, cup: 1.7,     // so they never fill the whole sky
  boat: 1.25, fish: 1.15 };                                           // and the boat and fish keep room around them
// How far each drawing reaches below its base point at scale 1 (most stand on it; the hull and fish hang lower).
const BOTTOM = { boat: 40, fish: 48 };
// Where things sit on water pages, below the front edge of the hills: the boat floats on the waves and
// the fish swims lower down, in the water.
const FLOAT = { boat: 100, fish: 150 };

/** The scale and base height for one thing in front, kept fully inside the frame. */
export function placement(m, scale, water) {
  const size = min(scale, MAX_SCALE[m] ?? scale);
  const base = GROUND + (water ? FLOAT[m] ?? 150 : 150);
  const lowest = PIC[1] + PIC[3] - 18;                                   // just above the frame's bottom edge
  return [size, Math.min(base, lowest - (BOTTOM[m] ?? 0) * size)];
}

export function wrap(text, width = 50) {
  const lines = [];
  let cur = '';
  for (const word of text.split(/\s+/).filter(Boolean)) {
    if (cur && cur.length + 1 + word.length > width) { lines.push(cur); cur = word; } else cur = `${cur} ${word}`.trim();
  }
  return cur ? [...lines, cur] : lines;
}

function frame() {
  const [x, y, w, h] = PIC;
  const curls = [[x + 16, y + 16, 1, 1], [x + w - 16, y + 16, -1, 1], [x + 16, y + h - 16, 1, -1], [x + w - 16, y + h - 16, -1, -1]]
    .map(([cx, cy, dx, dy]) => line(`M${f(cx)} ${f(cy)} q ${f(dx * 26)} ${f(dy * 4)} ${f(dx * 30)} ${f(dy * 30)} q ${f(-dx * 12)} ${f(-dy * 4)} ${f(-dx * 16)} ${f(-dy * 16)}`, 3)).join('');
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="22" fill="none" stroke="${INK}" stroke-width="7"/>` +
    `<rect x="${x + 10}" y="${y + 10}" width="${w - 20}" height="${h - 20}" rx="16" fill="none" stroke="${INK}" stroke-width="2.5"/>` + curls;
}
function ribbon(top, height) {
  const l = 70, r = 780;
  return shape(`M${l + 50} ${f(top + 18)} L${l} ${f(top + 18)} L${l + 24} ${f(top + 18 + height / 2)} L${l} ${f(top + 18 + height)} L${l + 50} ${f(top + 18 + height)} Z`) +
    shape(`M${r - 50} ${f(top + 18)} L${r} ${f(top + 18)} L${r - 24} ${f(top + 18 + height / 2)} L${r} ${f(top + 18 + height)} L${r - 50} ${f(top + 18 + height)} Z`) +
    shape(`M${l + 36} ${f(top)} L${r - 36} ${f(top)} L${r - 36} ${f(top + height)} L${l + 36} ${f(top + height)} Z`);
}

/** The whole coloring page for a plan (from planPage) as an SVG string. Its clip path gets an id of its own,
 * so several pages can sit in one document (a printed booklet) without borrowing each other's. */
export function drawPage(plan, seed = plan.reference) {
  const rng = randomFor(seed);
  const [x, y, w, h] = PIC;
  const clip = `pic-${String(plan.reference).toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
  const parts = [`<clipPath id="${clip}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="22"/></clipPath><g clip-path="url(#${clip})">`];
  for (const m of SKY) if (plan.background.includes(m)) parts.push(BACKGROUND_ART[m](rng));
  if (plan.background.filter((m) => SKY.includes(m)).length < 2) parts.push(clouds(rng));   // something in the sky to color
  if (plan.background.includes('mountains')) parts.push(mountains(rng));
  parts.push(hills(rng));
  if (plan.background.includes('path')) parts.push(path(rng));
  parts.push(plan.background.includes('waves') ? waves(rng) : meadow(rng));
  const front = plan.foreground.slice(0, 3);                                // up to three things, so each has room
  const widths = front.map((m) => SIZES[m] ?? 150);
  const total = widths.reduce((a, b) => a + b, 0);
  const scale = min(1.9, (w - 80) / (total + 50 * (front.length - 1)));
  const gap = (w - total * scale) / (front.length + 1);
  let cx = x + gap;
  front.forEach((m, i) => {
    const mid = cx + widths[i] * scale / 2;
    const [size, base] = placement(m, scale, plan.background.includes('waves'));
    parts.push(FOREGROUND_ART[m](mid + (OFFSET[m] ?? 0) * scale + rng.uniform(-8, 8), base, size));
    cx += widths[i] * scale + gap;
  });
  parts.push('</g>', frame());
  const [number, verse] = plan.verse;
  const lines = wrap(verse).slice(0, 4);
  const top = 836, row = 36, band = 28 + lines.length * row;
  parts.push(ribbon(top, band));
  lines.forEach((t, k) => parts.push(`<text x="${W / 2}" y="${top + 40 + k * row}" text-anchor="middle" font-family="Georgia, serif" font-size="27" fill="${INK}">${esc(t)}</text>`));
  parts.push(`<text x="${W / 2}" y="${top + band + 64}" text-anchor="middle" font-family="Georgia, serif" font-size="24" font-style="italic" fill="${INK}">${esc(plan.reference)}:${number} (WEB)</text>`);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" viewBox="0 0 ${W} ${H}" role="img" aria-label="Coloring page for ${esc(plan.reference)}">` +
    `<title>Colors of Eden: ${esc(plan.reference)}</title><rect width="${W}" height="${H}" fill="#fff"/>` + parts.join('') + '</svg>';
}

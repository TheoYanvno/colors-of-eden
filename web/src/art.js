// Storybook pages, exactly as coe/art.py draws them: a cover, then one page per story with one of the
// drawings to color in a frame, a short paragraph, the lesson in a box and the page number. US Letter, as
// SVG with an 850 x 1100 view box. A test checks every page matches the Python one character for character.
import { findPicture } from './picture.js';
import { chapters } from './storybook.js';

export const W = 850, H = 1100;
const INK = '#111';
const INSIDE = 18;                       // space between a drawing and its frame
const PIC_W = 700, PIC_H = 560;          // the most room a drawing and its frame can take on a story page
const COVER_H = 520;
const TEXT_X = 80;                       // left edge of the paragraph
const ROW = 42;                          // paragraph line height
export const TEXT_WRAP = 50;
const FONT = 'Georgia, serif';

const f = (n) => (Math.round(n * 10) / 10).toFixed(1);
const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

export function wrap(text, width) {
  const lines = [];
  let cur = '';
  for (const word of text.split(/\s+/).filter(Boolean)) {
    if (cur && cur.length + 1 + word.length > width) { lines.push(cur); cur = word; }
    else cur = `${cur} ${word}`.trim();
  }
  return cur ? [...lines, cur] : lines;
}

const frame = (x, y, w, h) =>
  `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" rx="22" fill="none" stroke="${INK}" stroke-width="7"/>` +
  `<rect x="${f(x + 10)}" y="${f(y + 10)}" width="${f(w - 20)}" height="${f(h - 20)}" rx="16" fill="none" stroke="${INK}" stroke-width="2.5"/>`;

const text = (x, y, words, size, anchor = 'middle', style = '') =>
  `<text x="${f(x)}" y="${f(y)}" text-anchor="${anchor}" font-family="${FONT}" font-size="${f(size)}"${style} fill="${INK}">${esc(words)}</text>`;

function pictureBox(pictureId, top, maxH) {
  const pic = findPicture(pictureId);
  const k = Math.min((PIC_W - 2 * INSIDE) / pic.width, (maxH - 2 * INSIDE) / pic.height);
  const w = pic.width * k + 2 * INSIDE, h = pic.height * k + 2 * INSIDE;
  return [(W - w) / 2, top, w, h, k];
}

const drawing = ([x, y, w, h, k], outlines) =>
  `<g transform="translate(${f(x + INSIDE)} ${f(y + INSIDE)}) scale(${k.toFixed(4)})">` +
  `<path d="${outlines}" fill="${INK}" fill-rule="evenodd"/></g>` + frame(x, y, w, h);

const svgPage = (label, parts) =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" viewBox="0 0 ${W} ${H}" ` +
  `role="img" aria-label="Coloring page: ${esc(label)}">` +
  `<title>Colors of Eden: ${esc(label)}</title><rect width="${W}" height="${H}" fill="#fff"/>` + parts.join('') + '</svg>';

/** Where everything on a story page sits (the same plan as coe/art.py's page_layout). */
export function pageLayout(page) {
  const box = pictureBox(page.picture, 136, PIC_H);
  const lines = wrap(page.text, TEXT_WRAP);
  const top = box[1] + box[3] + 52;
  const lessonTop = top + (lines.length - 1) * ROW + 34;
  const lesson = wrap(page.lesson, 46);
  const lessonH = 24 + lesson.length * 34;
  return { box, lines, top, lesson: [lessonTop, lessonH, lesson], bottom: lessonTop + lessonH };
}

/** Story page n (counting from 1) of a book as an SVG string; outlines is the drawing's path data. */
export function drawStoryPage(book, n, outlines) {
  const page = book.pages[n - 1];
  const plan = pageLayout(page);
  const parts = [
    text(W / 2, 78, page.title, 40, 'middle', ' font-weight="bold"'),
    text(W / 2, 112, chapters(book, page), 22, 'middle', ' font-style="italic"'),
    drawing(plan.box, outlines),
  ];
  plan.lines.forEach((line, i) => parts.push(text(TEXT_X, plan.top + i * ROW, line, 28, 'start')));
  const [lessonTop, lessonH, lesson] = plan.lesson;
  parts.push(`<rect x="${f(TEXT_X - 10)}" y="${f(lessonTop)}" width="${f(W - 2 * (TEXT_X - 10))}" height="${f(lessonH)}" rx="14" ` +
    `fill="none" stroke="${INK}" stroke-width="2.5"/>`);
  lesson.forEach((line, i) => parts.push(text(W / 2, lessonTop + 36 + i * 34, line, 26, 'middle', ' font-weight="bold"')));
  parts.push(text(W / 2, H - 34, String(n), 18));
  return svgPage(`${page.title} (${chapters(book, page)})`, parts);
}

export function coverLayout(book) {
  const size = Math.min(72, 1300 / book.label.length);
  const box = pictureBox(book.cover, 290, COVER_H);
  const about = wrap(book.about, 62);
  const top = box[1] + box[3] + 56;
  return { size, box, about, top, bottom: top + (about.length - 1) * 32 + 10 };
}

/** The book's cover: its name, "A Coloring Storybook", a drawing and a sentence about the book. */
export function drawCover(book, outlines) {
  const plan = coverLayout(book);
  const parts = [
    text(W / 2, 100, 'Colors of Eden', 24, 'middle', ' letter-spacing="3"'),
    text(W / 2, 190, book.label, plan.size, 'middle', ' font-weight="bold"'),
    text(W / 2, 244, 'A Coloring Storybook', 30, 'middle', ' font-style="italic"'),
    drawing(plan.box, outlines),
  ];
  plan.about.forEach((line, i) => parts.push(text(W / 2, plan.top + i * 32, line, 22)));
  return svgPage(`${book.label}, a coloring storybook`, parts);
}

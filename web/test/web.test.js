import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { BIBLE, findBook, superBookLink } from '../src/books.js';
import { loadStorybook, chapters } from '../src/storybook.js';
import { drawCover, drawStoryPage, coverLayout, pageLayout, wrap, H, W, TEXT_WRAP } from '../src/art.js';
import { CATALOG, pathData, loadPicture } from '../src/picture.js';

// Windows installs Python as `python` (or `py`); macOS and Linux as `python3`. PYTHON overrides both.
const PY = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
const python = (code) => execFileSync(PY, ['-c', code], { cwd: new URL('../..', import.meta.url), encoding: 'utf8', maxBuffer: 1 << 26 });
const superbook = new URL('../../../superbook/src/books.js', import.meta.url);
const outlinesOf = (id) => pathData(readFileSync(new URL(`../../coe/pictures/${id}.svg`, import.meta.url), 'utf8'));

test('the same 79 books as SuperBook, found by any of their names', async (t) => {
  assert.equal(BIBLE.length, 79);
  assert.equal(findBook('1 kingdoms').label, '1 Kingdoms (1 Samuel)');
  assert.equal(findBook('Psalm').label, 'Psalms');
  assert.throws(() => findBook('Hezekiah'), /no book called/);
  assert.equal(superBookLink(findBook('1 Samuel'), 3), 'https://theoyanvno.github.io/SuperBook/?book=1+Samuel&chapter=3');
  if (!existsSync(superbook)) return t.skip('SuperBook is not checked out next to Colors of Eden');
  const { BIBLE: theirs } = await import(superbook);
  assert.deepEqual(BIBLE.map((b) => [b.id, b.chapters, b.label]), theirs.map(([id, n, label = id]) => [id, n, label]));
});

const STORYBOOK = new URL('../../coe/storybook/', import.meta.url);
const readBook = (b) => ({ ...JSON.parse(readFileSync(new URL(`${encodeURIComponent(b.id)}.json`, STORYBOOK), 'utf8')), label: b.label });

test('every book of the Bible has a storybook, with real chapters and drawings', () => {
  const pictures = new Set(CATALOG.map((c) => c.id));
  for (const b of BIBLE) {
    const book = readBook(b);
    assert.equal(book.book, b.id);
    assert.ok(pictures.has(book.cover), b.label);
    assert.ok(book.pages.length >= 1, b.label);
    for (const p of book.pages) {
      assert.ok(pictures.has(p.picture), `${b.label}: ${p.title}`);
      assert.ok(1 <= p.chapter && p.chapter <= (p.to ?? p.chapter) && (p.to ?? p.chapter) <= b.chapters, `${b.label}: ${p.title}`);
    }
  }
  assert.equal(chapters(readBook(findBook('Genesis')), readBook(findBook('Genesis')).pages[2]), 'Genesis 6\u20139');
});

test('every page fits on letter paper and wrapping keeps every word', () => {
  for (const b of BIBLE) {
    const book = readBook(b);
    assert.ok(coverLayout(book).bottom <= H - 40, b.label);
    for (const p of book.pages) {
      const plan = pageLayout(p);
      assert.ok(plan.bottom <= H - 50, `${b.label}: ${p.title}`);
      assert.ok(plan.box[0] >= 40 && plan.box[0] + plan.box[2] <= W - 40, `${b.label}: ${p.title}`);
      assert.equal(plan.lines.join(' '), p.text.split(/\s+/).join(' '));
      assert.ok(plan.lines.every((line) => line.length <= TEXT_WRAP));
    }
  }
  assert.deepEqual(wrap('one two three four', 9), ['one two', 'three', 'four']);
});

test('every cover and page is drawn exactly like the Python version', (t) => {
  const mine = [];
  for (const b of BIBLE) {
    const book = readBook(b);
    mine.push(drawCover(book, outlinesOf(book.cover)));
    book.pages.forEach((p, i) => mine.push(drawStoryPage(book, i + 1, outlinesOf(p.picture))));
  }
  for (const svg of mine) assert.ok(svg.startsWith('<svg') && !/NaN|undefined/.test(svg));
  let py;
  try {
    // JSON with ASCII escapes, so it reads the same through a Windows console's code page.
    py = JSON.parse(python(`import json, sys
from coe.art import draw_cover, draw_story_page
from coe.storybook import storybook, written
out = []
for b in written():
    book = storybook(b)
    out.append(draw_cover(book))
    out += [draw_story_page(book, n) for n in range(1, len(book["pages"]) + 1)]
sys.stdout.write(json.dumps(out))`));
  } catch { return t.skip('Python is not available'); }
  assert.equal(mine.length, py.length);
  for (const [i, svg] of mine.entries()) assert.equal(svg, py[i], `page ${i}`);
});

test('a storybook is fetched once from the built site and errors explain themselves', async () => {
  const calls = [];
  const ok = async (url) => { calls.push(url); return { ok: true, json: async () => ({ book: '1 Samuel', pages: [] }) }; };
  const sam = findBook('1 Samuel');
  assert.equal((await loadStorybook(sam, ok)).label, '1 Kingdoms (1 Samuel)');
  await loadStorybook(sam, ok);
  assert.deepEqual(calls, ['storybook/1%20Samuel.json']);
  await assert.rejects(loadStorybook(findBook('Ruth'), async () => ({ ok: false })), /Ruth storybook/);
});

test('picture outlines are fetched once from the built site and errors explain themselves', async () => {
  const calls = [];
  const ok = async (url) => { calls.push(url); return { ok: true, text: async () => '<svg><path d="M1 2Z"/></svg>' }; };
  assert.equal(await loadPicture('places/oasis', ok), 'M1 2Z');
  assert.equal(await loadPicture('places/oasis', ok), 'M1 2Z');
  assert.deepEqual(calls, ['pictures/places/oasis.svg']);
  await assert.rejects(loadPicture('places/garden', async () => ({ ok: false })), /Garden picture/);
  assert.throws(() => loadPicture('places/atlantis', ok), /no picture/);
});

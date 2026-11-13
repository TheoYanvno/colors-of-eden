import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { BIBLE, findBook, superBookLink } from '../src/books.js';
import { planPage, motifCounts } from '../src/scenes.js';
import { drawPage, wrap, randomFor, placement } from '../src/art.js';
import { loadChapter, BUNDLED } from '../src/text.js';

const verses = (ref) => BUNDLED[ref].map((t, i) => [i + 1, t]);
const superbook = new URL('../../../superbook/src/books.js', import.meta.url);

test('the same 79 books as SuperBook, found by any of their names', async (t) => {
  assert.equal(BIBLE.length, 79);
  assert.equal(findBook('1 kingdoms').label, '1 Kingdoms (1 Samuel)');
  assert.equal(findBook('Psalm').label, 'Psalms');
  assert.equal(findBook('susanna').id, 'sus');
  assert.throws(() => findBook('Hezekiah'), /no book called/);
  assert.equal(superBookLink(findBook('1 Samuel'), 3), 'https://theoyanvno.github.io/SuperBook/?book=1+Samuel&chapter=3');
  if (!existsSync(superbook)) return t.skip('SuperBook is not checked out next to Colors of Eden');
  const { BIBLE: theirs } = await import(superbook);
  assert.deepEqual(BIBLE.map((b) => [b.id, b.chapters, b.label]), theirs.map(([id, n, label = id]) => [id, n, label]));
});

test('the page plan matches the Python version for the chapters that ship with it', (t) => {
  for (const ref of Object.keys(BUNDLED)) {
    const js = planPage(ref, verses(ref));
    let py;
    try {
      py = JSON.parse(execFileSync('python3', ['-c', `
import json
from coe.scenes import plan_page
from coe.text import Chapter, BUNDLED
book, n = ${JSON.stringify(ref)}.rsplit(' ', 1)
p = plan_page(Chapter(book, int(n), list(enumerate(BUNDLED[${JSON.stringify(ref)}], 1))))
print(json.dumps({"motifs": p.motifs, "background": p.background, "foreground": p.foreground, "verse": list(p.verse)}))`], { cwd: new URL('../..', import.meta.url) }).toString());
    } catch { return t.skip('python3 is not available'); }
    assert.deepEqual({ motifs: js.motifs, background: js.background, foreground: js.foreground, verse: js.verse }, py, ref);
  }
});

test('words point to motifs, and Psalm 23 gets sheep and still waters', () => {
  assert.equal(motifCounts('The shepherd led the flock')['sheep'], 6);
  const plan = planPage('Psalms 23', verses('Psalms 23'));
  assert.ok(plan.foreground.includes('sheep'));
  assert.equal(plan.verse[0], 2);
});

test('a page is a letter-size SVG with the verse and reference, the same every time', () => {
  const plan = planPage('Psalms 23', verses('Psalms 23'));
  const svg = drawPage(plan);
  assert.match(svg, /^<svg [^>]*width="8.5in" height="11in" viewBox="0 0 850 1100"/);
  assert.ok(svg.includes('Psalms 23:2 (WEB)'));
  assert.ok(svg.includes('He makes me lie down in green pastures.'));
  assert.equal(drawPage(plan), svg);
  assert.ok(!/NaN|undefined/.test(svg));
  assert.ok(svg.includes('<clipPath id="pic-psalms-23">') && svg.includes('url(#pic-psalms-23)'));
  assert.ok(!/stroke-width="[^"]*" [^>]*stroke-width=/.test(svg));
  assert.ok(drawPage({ ...plan, verse: [1, 'A <b> & "c"'] }).includes('A &lt;b&gt; &amp; &quot;c&quot;'));
});

test('every motif draws, and long verses wrap to four lines at most', () => {
  for (const m of ['tree', 'flowers', 'sheep', 'dove', 'fish', 'boat', 'crown', 'lamp', 'cup', 'heart']) {
    const svg = drawPage({ reference: 'Test 1', background: ['sun', 'moon', 'stars', 'mountains', 'path', 'waves'], foreground: [m], verse: [1, 'x'] });
    assert.ok(!/NaN|undefined/.test(svg), m);
  }
  assert.deepEqual(wrap('one two three', 7), ['one two', 'three']);
  const r1 = randomFor('a'), r2 = randomFor('a');
  assert.equal(r1.uniform(0, 1), r2.uniform(0, 1));
});

test('chapters load from the text service, fall back to the bundled copy, and explain problems', async () => {
  const calls = [];
  const fake = async (url) => { calls.push(url); return { ok: true, json: async () => ({ verses: [{ chapter: 2, verse: 1, text: 'Tobit  text\n' }] }) }; };
  const tob = await loadChapter('Tobit', 2, fake);
  assert.deepEqual(tob.verses, [[1, 'Tobit text']]);
  assert.equal(calls[0], 'https://bible-api.com/tobit%202?translation=web');
  const offline = async () => { throw new Error('offline'); };
  const ps = await loadChapter('Psalm', 23, offline);
  assert.equal(ps.bundled, true);
  assert.ok(ps.verses[0][1].startsWith('Yahweh is my shepherd'));
  await assert.rejects(loadChapter('Ruth', 1, offline), /internet connection/);
  await assert.rejects(loadChapter('Ruth', 9, offline), /chapters 1 to 4/);
  await assert.rejects(loadChapter('1 Kingdoms', 3, fake), /no verses/);
  assert.ok(calls.at(-1).includes('1%20samuel%203'));
});

test('the boat and fish stay inside the frame, like the Python version', () => {
  const py = JSON.parse(execFileSync('python3', ['-c', `import json; from coe.art import placement, FOREGROUND_ART
print(json.dumps({f"{m}|{w}|{s}": placement(m, s, w) for m in FOREGROUND_ART for w in (False, True) for s in (0.8, 1.33, 1.9)}))`],
    { cwd: new URL('../..', import.meta.url), encoding: 'utf8' }));
  for (const [key, [size, base]] of Object.entries(py)) {
    const [m, w, s] = key.split('|');
    const [jsSize, jsBase] = placement(m, Number(s), w === 'True');
    assert.ok(Math.abs(jsSize - size) < 1e-9 && Math.abs(jsBase - base) < 1e-9, key);
    assert.ok(jsBase + ({ boat: 40, fish: 48 }[m] ?? 0) * jsSize <= 782, key);
  }
});

// Picture pages (the same rules as coe/picture.py): 60 drawings of animals, places and people of the Middle
// East, traced into clean outlines. A chapter that names one at least MIN_MENTIONS times gets that drawing
// as its page. The catalog is bundled; each drawing's outlines are fetched from pictures/<id>.svg when needed.
import CATALOG from '../../coe/pictures/catalog.json' with { type: 'json' };

export { CATALOG };
export const MIN_MENTIONS = 3;

const counts = (text) => {
  const words = new Map();
  for (const w of String(text).toLowerCase().match(/[a-z]+/g) ?? []) words.set(w, (words.get(w) ?? 0) + 1);
  return words;
};

export function findPicture(id) {
  const p = CATALOG.find((c) => c.id === id);
  if (!p) throw new Error(`no picture called "${id}"`);
  return p;
}

/** The picture the chapter names most (at least MIN_MENTIONS times), or null; ties go to the first listed. */
export function choosePicture(text) {
  const words = counts(text);
  let best = null, bestN = MIN_MENTIONS - 1;
  for (const p of CATALOG) {
    const n = p.words.reduce((s, w) => s + (words.get(w) ?? 0), 0);
    if (n > bestN) { best = p.id; bestN = n; }
  }
  return best;
}

/** The short verse that names the picture most (ties go to the earlier verse), or null. */
export function pictureVerse(verses, id, maxChars = 160) {
  const cues = new Set(findPicture(id).words);
  let best = null, bestN = 0;
  for (const [n, text] of verses) {
    const k = (text.toLowerCase().match(/[a-z]+/g) ?? []).filter((w) => cues.has(w)).length;
    if (text.length <= maxChars && k > bestN) { best = [n, text]; bestN = k; }
  }
  return best;
}

/** The outlines (SVG path data) inside a picture file's text. */
export function pathData(svgText) {
  const m = / d="([^"]+)"/.exec(svgText);
  if (!m) throw new Error('that picture file has no outlines');
  return m[1];
}

const cache = new Map();
/** Fetch a picture's outlines from the built site (pictures/<id>.svg), once per picture. */
export function loadPicture(id, fetchFn = globalThis.fetch) {
  findPicture(id);
  if (!cache.has(id)) {
    cache.set(id, fetchFn(`pictures/${id}.svg`).then((r) => {
      if (!r.ok) throw new Error(`couldn't load the ${findPicture(id).label} picture`);
      return r.text();
    }).then(pathData).catch((e) => { cache.delete(id); throw e; }));
  }
  return cache.get(id);
}

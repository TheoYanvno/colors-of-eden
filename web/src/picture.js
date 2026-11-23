// The drawings (the same as coe/picture.py), traced into clean outlines: a scene for most story pages and
// the 60 drawings of animals, places and people of the Middle East used on the covers and the other pages. The catalog is
// bundled; each drawing's outlines are fetched from pictures/<id>.svg
// when a story page needs them.
import CATALOG from '../../coe/pictures/catalog.json' with { type: 'json' };

export { CATALOG };
export function findPicture(id) {
  const p = CATALOG.find((c) => c.id === id);
  if (!p) throw new Error(`no picture called "${id}"`);
  return p;
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

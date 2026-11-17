// The coloring storybooks (the same files coe/storybook.py reads): every book of the Bible told for
// children, one page per story. Each book is fetched from the built site (storybook/<id>.json) when picked.
import { BIBLE } from './books.js';

const cache = new Map();

/** A book's storybook (with its label added), fetched once. */
export function loadStorybook(book, fetchFn = globalThis.fetch) {
  if (!cache.has(book.id)) {
    cache.set(book.id, fetchFn(`storybook/${encodeURIComponent(book.id)}.json`).then((r) => {
      if (!r.ok) throw new Error(`couldn't load the ${book.label} storybook`);
      return r.json();
    }).then((b) => ({ ...b, label: book.label })).catch((e) => { cache.delete(book.id); throw e; }));
  }
  return cache.get(book.id);
}

/** Where a page's story is told: "Genesis 3", or "Genesis 6–9" when it runs over several chapters. */
export const chapters = (book, page) => `${book.label} ${page.chapter}${page.to ? `–${page.to}` : ''}`;

export { BIBLE };

// Chapter text from the World English Bible (public domain), from bible-api.com: the same place SuperBook
// reads it. Chapters are kept for the visit once fetched. Genesis 1 (its opening verses) and Psalm 23 ship
// with the page, so it can always draw something.
import { findBook } from './books.js';

export const BUNDLED = {
  "Genesis 1": [
    "In the beginning, God created the heavens and the earth.",
    "The earth was formless and empty. Darkness was on the surface of the deep and God’s Spirit was hovering over the surface of the waters.",
    "God said, “Let there be light,” and there was light.",
    "God saw the light, and saw that it was good. God divided the light from the darkness.",
    "God called the light “day”, and the darkness he called “night”. There was evening and there was morning, the first day."
  ],
  "Psalms 23": [
    "Yahweh is my shepherd: I shall lack nothing.",
    "He makes me lie down in green pastures. He leads me beside still waters.",
    "He restores my soul. He guides me in the paths of righteousness for his name’s sake.",
    "Even though I walk through the valley of the shadow of death, I will fear no evil, for you are with me. Your rod and your staff, they comfort me.",
    "You prepare a table before me in the presence of my enemies. You anoint my head with oil. My cup runs over.",
    "Surely goodness and loving kindness shall follow me all the days of my life, and I will dwell in Yahweh’s house forever."
  ]
};

const memo = new Map();

/** { book, chapter, reference, verses: [[n, text]], bundled } */
export async function loadChapter(bookName, chapter, fetchFn = globalThis.fetch) {
  const book = findBook(bookName);
  const n = Number(chapter);
  if (!Number.isInteger(n) || n < 1 || n > book.chapters) throw new Error(`${book.label} has chapters 1 to ${book.chapters}.`);
  const reference = `${book.label} ${n}`;
  const key = `${book.id} ${n}`;
  if (memo.has(key)) return memo.get(key);
  try {
    const res = await fetchFn(`https://bible-api.com/${encodeURIComponent(key.toLowerCase())}?translation=web`);
    if (!res.ok) throw new Error(`the text service answered ${res.status}`);
    const body = await res.json();
    const verses = body.verses.filter((v) => Number(v.chapter) === n).map((v) => [Number(v.verse), v.text.replace(/\s+/g, ' ').trim()]);
    if (!verses.length) throw new Error('no verses came back');
    const out = { book, chapter: n, reference, verses, bundled: false };
    memo.set(key, out);
    return out;
  } catch (err) {
    const local = BUNDLED[`${book.label} ${n}`];
    if (local) return { book, chapter: n, reference, verses: local.map((t, i) => [i + 1, t]), bundled: true };
    throw new Error(`Couldn't get ${reference} (${err.message}). Check your internet connection and try again.`);
  }
}

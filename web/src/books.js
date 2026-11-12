// The books of the Bible as SuperBook has them: the Eastern Orthodox canon in Orthodox order, then the 27
// books of the New Testament. SuperBook (https://theoyanvno.github.io/SuperBook/) is the reference for every
// Bible project here, so this is a copy of BIBLE in SuperBook's src/books.js: [id the text API understands,
// chapters, label readers see]. test/books.test.js checks it still matches when SuperBook is checked out
// next to this repo.
export const SUPERBOOK = 'https://theoyanvno.github.io/SuperBook/';

export const BIBLE = [
  ["Genesis", 50],
  ["Exodus", 40],
  ["Leviticus", 27],
  ["Numbers", 36],
  ["Deuteronomy", 34],
  ["Joshua", 24],
  ["Judges", 21],
  ["Ruth", 4],
  ["1 Samuel", 31, "1 Kingdoms (1 Samuel)"],
  ["2 Samuel", 24, "2 Kingdoms (2 Samuel)"],
  ["1 Kings", 22, "3 Kingdoms (1 Kings)"],
  ["2 Kings", 25, "4 Kingdoms (2 Kings)"],
  ["1 Chronicles", 29],
  ["2 Chronicles", 36],
  ["Prayer of Manasses", 1, "Prayer of Manasseh"],
  ["1 Esdras", 9],
  ["Ezra", 10, "2 Esdras (Ezra)"],
  ["Nehemiah", 13],
  ["Tobit", 14],
  ["Judith", 16],
  ["Esther", 10],
  ["1 Maccabees", 16],
  ["2 Maccabees", 15],
  ["3 Maccabees", 7],
  ["Psalms", 150],
  ["Job", 42],
  ["Proverbs", 31],
  ["Ecclesiastes", 12],
  ["Song of Solomon", 8, "Song of Songs"],
  ["Wisdom", 19, "Wisdom of Solomon"],
  ["Sirach", 51],
  ["Hosea", 14],
  ["Amos", 9],
  ["Micah", 7],
  ["Joel", 3],
  ["Obadiah", 1],
  ["Jonah", 4],
  ["Nahum", 3],
  ["Habakkuk", 3],
  ["Zephaniah", 3],
  ["Haggai", 2],
  ["Zechariah", 14],
  ["Malachi", 4],
  ["Isaiah", 66],
  ["Jeremiah", 52],
  ["Baruch", 5],
  ["Lamentations", 5],
  ["Ezekiel", 48],
  ["Daniel", 12],
  ["sus", 1, "Susanna"],
  ["Bel and the Dragon", 1],
  ["4 Maccabees", 18, "4 Maccabees (appendix)"],
  ["Matthew", 28],
  ["Mark", 16],
  ["Luke", 24],
  ["John", 21],
  ["Acts", 28],
  ["Romans", 16],
  ["1 Corinthians", 16],
  ["2 Corinthians", 13],
  ["Galatians", 6],
  ["Ephesians", 6],
  ["Philippians", 4],
  ["Colossians", 4],
  ["1 Thessalonians", 5],
  ["2 Thessalonians", 3],
  ["1 Timothy", 6],
  ["2 Timothy", 4],
  ["Titus", 3],
  ["Philemon", 1],
  ["Hebrews", 13],
  ["James", 5],
  ["1 Peter", 5],
  ["2 Peter", 3],
  ["1 John", 5],
  ["2 John", 1],
  ["3 John", 1],
  ["Jude", 1],
  ["Revelation", 22],
].map(([id, chapters, label = id]) => ({ id, chapters, label }));

const ALIASES = { psalm: 'Psalms', revelations: 'Revelation', 'song of solomon': 'Song of Songs', wisdom: 'Wisdom of Solomon',
  ecclesiasticus: 'Sirach', 'prayer of manasses': 'Prayer of Manasseh', bel: 'Bel and the Dragon', '4 maccabees': '4 Maccabees (appendix)' };

const norm = (s) => String(s ?? '').replace(/\s+/g, ' ').trim().toLowerCase();

// Every name a reader might type: the label, the API id and the names in brackets ("1 Samuel", "1 Kingdoms").
const KEYS = new Map();
for (const b of BIBLE) {
  KEYS.set(norm(b.label), b);
  KEYS.set(norm(b.id), b);
  const m = b.label.match(/^(.*) \((.*)\)$/);
  if (m) { KEYS.set(norm(m[1]), b); if (m[2] !== 'appendix') KEYS.set(norm(m[2]), b); }
}
for (const [k, label] of Object.entries(ALIASES)) KEYS.set(k, BIBLE.find((b) => b.label === label));

export function findBook(name) {
  const b = KEYS.get(norm(name));
  if (!b) throw new Error(`There's no book called "${name}". Try a name like Genesis, Tobit, Psalms or 1 John.`);
  return b;
}

/** SuperBook's reader, opened at this chapter. */
export function superBookLink(book, chapter) {
  return `${SUPERBOOK}?${new URLSearchParams({ book: book.id, chapter: String(chapter) })}`;
}

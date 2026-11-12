// Choosing what to draw for a chapter (the same rules as coe/scenes.py): words in the text point to
// motifs, the motifs mentioned most make the page, and one short verse goes under the picture.

export const MOTIF_WORDS = {
  sun: ['sun', 'light', 'day', 'morning', 'shine', 'shined', 'bright'],
  moon: ['moon', 'night', 'evening'],
  stars: ['star', 'stars', 'heaven', 'heavens', 'firmament'],
  clouds: ['cloud', 'clouds', 'rain', 'sky'],
  waves: ['sea', 'seas', 'waters', 'water', 'deep', 'flood', 'river', 'waves'],
  mountains: ['mountain', 'mountains', 'hill', 'hills', 'valley', 'earth', 'land'],
  tree: ['tree', 'trees', 'garden', 'fruit', 'vine', 'branch', 'seed', 'grass', 'herb'],
  flowers: ['flower', 'flowers', 'lily', 'lilies', 'pastures', 'field', 'fields', 'green'],
  sheep: ['sheep', 'lamb', 'lambs', 'flock', 'shepherd', 'shepherds'],
  dove: ['dove', 'spirit', 'bird', 'birds', 'fowl', 'wings'],
  fish: ['fish', 'fishes', 'whale', 'net', 'nets'],
  boat: ['ship', 'ships', 'boat', 'ark', 'sailed'],
  crown: ['king', 'kings', 'crown', 'throne', 'kingdom', 'reign'],
  lamp: ['lamp', 'lamps', 'candle', 'candlestick', 'lantern'],
  cup: ['cup', 'table', 'bread', 'wine', 'feast'],
  path: ['path', 'paths', 'way', 'walk', 'road', 'journey'],
  heart: ['love', 'loved', 'heart', 'mercy', 'goodness', 'joy'],
};
export const BACKGROUND = new Set(['sun', 'moon', 'stars', 'clouds', 'waves', 'mountains', 'path']);
// Specific things (a shepherd, a dove, a boat) say more than general words like "day", so they count more.
const WEIGHT = { sheep: 3, dove: 3, fish: 3, boat: 3, crown: 3, lamp: 2, cup: 2 };

/** { motif: weighted count }, in MOTIF_WORDS order. */
export function motifCounts(text) {
  const words = new Map();
  for (const w of String(text).toLowerCase().match(/[a-z]+/g) ?? []) words.set(w, (words.get(w) ?? 0) + 1);
  const counts = {};
  for (const [motif, cues] of Object.entries(MOTIF_WORDS)) {
    const n = cues.reduce((sum, w) => sum + (words.get(w) ?? 0), 0);
    if (n) counts[motif] = n * (WEIGHT[motif] ?? 1);
  }
  return counts;
}

/** The short verse that mentions the most chosen motifs (ties go to the earlier verse). */
export function pickVerse(verses, motifs, maxChars = 160) {
  let best = null, bestScore = -1;
  for (const [n, text] of verses) {
    if (text.length > maxChars) continue;
    const c = motifCounts(text);
    const score = motifs.filter((m) => c[m] > 0).length;
    if (score > bestScore) { best = [n, text]; bestScore = score; }
  }
  return best ?? verses.reduce((a, b) => (b[1].length < a[1].length ? b : a));
}

/** { reference, motifs, background, foreground, verse: [n, text] } for a chapter's verses. */
export function planPage(reference, verses, maxMotifs = 5) {
  const counts = motifCounts(verses.map(([, t]) => t).join(' '));
  const order = Object.keys(MOTIF_WORDS);
  let motifs = Object.keys(counts).sort((a, b) => counts[b] - counts[a] || order.indexOf(a) - order.indexOf(b)).slice(0, maxMotifs);
  if (!motifs.length) motifs = ['sun', 'mountains', 'tree', 'flowers'];
  if (!motifs.some((m) => !BACKGROUND.has(m))) motifs.push('tree');       // always something in front to color
  if (!motifs.some((m) => BACKGROUND.has(m))) motifs.unshift('mountains');
  return {
    reference, motifs,
    background: motifs.filter((m) => BACKGROUND.has(m)),
    foreground: motifs.filter((m) => !BACKGROUND.has(m)),
    verse: pickVerse(verses, motifs),
  };
}

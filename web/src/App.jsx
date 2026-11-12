import { useEffect, useMemo, useState } from 'react';
import { BIBLE, findBook, superBookLink } from './books.js';
import { loadChapter } from './text.js';
import { planPage } from './scenes.js';
import { drawPage } from './art.js';

const NEW_TESTAMENT = BIBLE.findIndex((b) => b.id === 'Matthew');

// The chapter to start on: ?book=Psalms&chapter=23 (the same links SuperBook uses), else Psalm 23.
function startingChapter() {
  const q = new URLSearchParams(globalThis.location?.search ?? '');
  try {
    const book = findBook(q.get('book') ?? 'Psalms');
    const n = Number(q.get('chapter'));
    return { book: book.label, chapter: Number.isInteger(n) && n >= 1 && n <= book.chapters ? n : q.has('book') ? 1 : 23 };
  } catch { return { book: 'Psalms', chapter: 23 }; }
}

export default function App() {
  const [pick, setPick] = useState(startingChapter);
  const [state, setState] = useState({ status: 'loading' });
  const book = findBook(pick.book);

  useEffect(() => {
    let live = true;
    setState((s) => ({ ...s, status: 'loading' }));
    try { history.replaceState(null, '', `?${new URLSearchParams({ book: book.id, chapter: String(pick.chapter) })}`); } catch { /* file:// */ }
    loadChapter(pick.book, pick.chapter)
      .then((ch) => live && setState({ status: 'ready', chapter: ch }))
      .catch((err) => live && setState({ status: 'error', message: err.message }));
    return () => { live = false; };
  }, [pick.book, pick.chapter]);

  const ch = state.chapter;
  const plan = useMemo(() => (ch ? planPage(ch.reference, ch.verses) : null), [ch]);
  const svg = useMemo(() => (plan ? drawPage(plan) : ''), [plan]);
  const fileName = plan ? `${plan.reference.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}.svg` : 'page.svg';
  const download = () => {
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
    const a = Object.assign(document.createElement('a'), { href: url, download: fileName });
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  return (
    <>
      <header className="no-print">
        <h1>🎨 Colors of Eden</h1>
        <p>Coloring pages from any chapter of the Orthodox Bible</p>
      </header>
      <main>
        <section className="controls no-print" aria-label="Choose a chapter">
          <label>Book
            <select value={pick.book} onChange={(e) => setPick({ book: e.target.value, chapter: 1 })}>
              <optgroup label="Old Testament">{BIBLE.slice(0, NEW_TESTAMENT).map((b) => <option key={b.id}>{b.label}</option>)}</optgroup>
              <optgroup label="New Testament">{BIBLE.slice(NEW_TESTAMENT).map((b) => <option key={b.id}>{b.label}</option>)}</optgroup>
            </select>
          </label>
          <label>Chapter
            <select value={pick.chapter} onChange={(e) => setPick({ ...pick, chapter: Number(e.target.value) })}>
              {Array.from({ length: book.chapters }, (_, i) => <option key={i + 1} value={i + 1}>{i + 1}</option>)}
            </select>
          </label>
          <div className="buttons">
            <button className="primary" disabled={!svg} onClick={download}>Download SVG</button>
            <a className="button" href={superBookLink(book, pick.chapter)} target="_blank" rel="noreferrer">Read {book.label} {pick.chapter} in SuperBook ↗</a>
          </div>
          <div role="status" aria-live="polite" className="status">
            {state.status === 'loading' && <p className="muted">Reading {book.label} {pick.chapter}…</p>}
            {state.status === 'error' && <p className="error">{state.message}</p>}
            {plan && state.status === 'ready' && (
              <dl className="plan">
                <dt>Behind</dt><dd>{plan.background.join(', ')}</dd>
                <dt>In front</dt><dd>{plan.foreground.slice(0, 3).join(', ')}</dd>
                <dt>Verse {plan.verse[0]}</dt><dd>{plan.verse[1]}</dd>
              </dl>
            )}
            {ch?.bundled && <p className="muted">The text service couldn't be reached, so this uses the copy of {ch.reference} that comes with Colors of Eden{ch.reference === 'Genesis 1' ? ' (its first five verses)' : ''}.</p>}
          </div>
        </section>
        <section className="page" aria-label="Coloring page">
          {svg ? <div className="sheet" dangerouslySetInnerHTML={{ __html: svg }} /> : <div className="sheet empty" />}
        </section>
      </main>
      <footer className="no-print">
        <p>Text: World English Bible (public domain), from <a href="https://bible-api.com/">bible-api.com</a>, in the books and order of the Eastern Orthodox Bible as <a href="https://theoyanvno.github.io/SuperBook/">SuperBook</a> has them. Every drawing is original, made in code.</p>
      </footer>
    </>
  );
}

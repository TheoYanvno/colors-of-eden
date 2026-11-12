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
  const [booklet, setBooklet] = useState({ to: 0, pages: [], status: '' });
  const bookletTo = Math.min(book.chapters, Math.max(pick.chapter, booklet.to || pick.chapter + 4));

  // A booklet: this chapter and the ones after it, one page each, printed together (or saved as one PDF).
  async function printBooklet() {
    setBooklet((b) => ({ ...b, status: 'Getting the chapters ready…', pages: [] }));
    const pages = [];
    try {
      for (let n = pick.chapter; n <= bookletTo; n++) {
        const c = await loadChapter(pick.book, n);
        pages.push({ key: c.reference, svg: drawPage(planPage(c.reference, c.verses)) });
      }
    } catch (err) {
      return setBooklet((b) => ({ ...b, status: err.message }));
    }
    setBooklet((b) => ({ ...b, pages, status: '' }));
  }
  useEffect(() => {
    if (!booklet.pages.length) return;
    document.body.classList.add('printing-booklet');
    const done = () => { document.body.classList.remove('printing-booklet'); setBooklet((b) => ({ ...b, pages: [] })); };
    addEventListener('afterprint', done, { once: true });
    print();
    return () => removeEventListener('afterprint', done);
  }, [booklet.pages]);

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
            <button className="primary" disabled={!svg} onClick={() => print()}>Print or save as PDF</button>
            <button disabled={!svg} onClick={download}>Download SVG</button>
            <a className="button" href={superBookLink(book, pick.chapter)} target="_blank" rel="noreferrer">Read {book.label} {pick.chapter} in SuperBook ↗</a>
          </div>
          <fieldset className="booklet">
            <legend>Booklet</legend>
            <label>{book.label} {pick.chapter} to
              <select value={bookletTo} onChange={(e) => setBooklet((b) => ({ ...b, to: Number(e.target.value) }))}>
                {Array.from({ length: Math.min(book.chapters - pick.chapter + 1, 10) }, (_, i) => pick.chapter + i).map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
            </label>
            <button onClick={printBooklet}>Print booklet ({bookletTo - pick.chapter + 1} page{bookletTo === pick.chapter ? '' : 's'})</button>
            {booklet.status && <p className="muted" role="status">{booklet.status}</p>}
          </fieldset>
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
        <section className="booklet-pages" aria-hidden="true">
          {booklet.pages.map((p) => <div key={p.key} className="sheet" dangerouslySetInnerHTML={{ __html: p.svg }} />)}
        </section>
      </main>
      <footer className="no-print">
        <p>Text: World English Bible (public domain), from <a href="https://bible-api.com/">bible-api.com</a>, in the books and order of the Eastern Orthodox Bible as <a href="https://theoyanvno.github.io/SuperBook/">SuperBook</a> has them. Every drawing is original, made in code.</p>
      </footer>
    </>
  );
}

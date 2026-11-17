import { useEffect, useMemo, useState } from 'react';
import { BIBLE, findBook, superBookLink } from './books.js';
import { loadChapter } from './text.js';
import { planPage } from './scenes.js';
import { drawPage } from './art.js';
import { CATALOG, findPicture, loadPicture, pictureVerse } from './picture.js';

const KINDS = [['animals', 'Animals'], ['places', 'Places'], ['people', 'People']];

const NEW_TESTAMENT = BIBLE.findIndex((b) => b.id === 'Matthew');
const BOOKLET_PAGES = 20;                  // the most chapters one booklet prints

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
  const auto = useMemo(() => (ch ? planPage(ch.reference, ch.verses) : null), [ch]);
  // Picture: 'auto' (the drawing the chapter names, if any), 'none' (drawn in code), or a picture's id.
  const [choice, setChoice] = useState('auto');
  useEffect(() => setChoice('auto'), [pick.book, pick.chapter]);
  const plan = useMemo(() => {
    if (!auto || choice === 'auto') return auto;
    if (choice === 'none') return { ...auto, picture: null };
    return { ...auto, picture: choice, verse: pictureVerse(ch.verses, choice) ?? auto.verse };
  }, [auto, choice, ch]);
  const [outlines, setOutlines] = useState({ id: null, d: null, error: '' });
  useEffect(() => {
    if (!plan?.picture) return;
    let live = true;
    loadPicture(plan.picture)
      .then((d) => live && setOutlines({ id: plan.picture, d, error: '' }))
      .catch((err) => live && setOutlines({ id: plan.picture, d: null, error: err.message }));
    return () => { live = false; };
  }, [plan?.picture]);
  const ready = plan?.picture && outlines.id === plan.picture ? outlines.d : null;
  const svg = useMemo(() => (plan ? drawPage(plan, plan.reference, ready) : ''), [plan, ready]);
  const fileName = plan ? `${plan.reference.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}.svg` : 'page.svg';
  const [booklet, setBooklet] = useState({ to: 0, pages: [], status: '' });
  const bookletTo = Math.min(book.chapters, pick.chapter + BOOKLET_PAGES - 1, Math.max(pick.chapter, booklet.to || pick.chapter + BOOKLET_PAGES - 1));

  // A booklet: this chapter and the ones after it, one page each, printed together (or saved as one PDF).
  async function printBooklet() {
    const total = bookletTo - pick.chapter + 1;
    setBooklet((b) => ({ ...b, status: 'Getting the chapters ready…', pages: [] }));
    const pages = [];
    try {
      for (let n = pick.chapter; n <= bookletTo; n++) {
        setBooklet((b) => ({ ...b, status: `Getting chapter ${n - pick.chapter + 1} of ${total}…${total > 15 ? ' (a long booklet takes up to a minute)' : ''}` }));
        const c = await loadChapter(pick.book, n);
        const p = planPage(c.reference, c.verses);
        const d = p.picture ? await loadPicture(p.picture).catch(() => null) : null;
        pages.push({ key: c.reference, svg: drawPage(p, p.reference, d) });
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
          <label>Picture
            <select value={choice} onChange={(e) => setChoice(e.target.value)}>
              <option value="auto">Automatic{auto ? ` (${auto.picture ? findPicture(auto.picture).label : 'drawn in code'})` : ''}</option>
              <option value="none">Drawn in code</option>
              {KINDS.map(([kind, name]) => (
                <optgroup key={kind} label={name}>
                  {CATALOG.filter((c) => c.id.startsWith(`${kind}/`)).map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
                </optgroup>
              ))}
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
                {Array.from({ length: Math.min(book.chapters - pick.chapter + 1, BOOKLET_PAGES) }, (_, i) => pick.chapter + i).map((n) => <option key={n} value={n}>{n}</option>)}
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
                {plan.picture ? <><dt>Picture</dt><dd>{findPicture(plan.picture).label}</dd></> : <>
                  <dt>Behind</dt><dd>{plan.background.join(', ')}</dd>
                  <dt>In front</dt><dd>{plan.foreground.slice(0, 3).join(', ')}</dd></>}
                <dt>Verse {plan.verse[0]}</dt><dd>{plan.verse[1]}</dd>
              </dl>
            )}
            {plan?.picture && outlines.id === plan.picture && outlines.error && <p className="error">{outlines.error}, so this page is drawn in code.</p>}
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
        <p>Text: World English Bible (public domain), from <a href="https://bible-api.com/">bible-api.com</a>, in the books and order of the Eastern Orthodox Bible as <a href="https://theoyanvno.github.io/SuperBook/">SuperBook</a> has them. Pages are drawn in code, or use one of 60 drawings of animals, places and people of the Middle East, traced into clean line art.</p>
      </footer>
    </>
  );
}

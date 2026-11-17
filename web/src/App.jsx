import { useEffect, useState } from 'react';
import { BIBLE, findBook, superBookLink } from './books.js';
import { loadStorybook, chapters } from './storybook.js';
import { drawCover, drawStoryPage } from './art.js';
import { loadPicture } from './picture.js';

const NEW_TESTAMENT = BIBLE.findIndex((b) => b.id === 'Matthew');

// The book to start on: ?book=Jonah (the same links SuperBook uses), else Genesis.
function startingBook() {
  try { return findBook(new URLSearchParams(globalThis.location?.search ?? '').get('book') ?? 'Genesis').label; }
  catch { return 'Genesis'; }
}

/** Every page of a book as SVG: the cover first, then one page per story. */
async function drawBook(book) {
  const ids = [book.cover, ...book.pages.map((p) => p.picture)];
  const outlines = Object.fromEntries(await Promise.all([...new Set(ids)].map(async (id) => [id, await loadPicture(id)])));
  return [
    { key: 'cover', title: 'Cover', svg: drawCover(book, outlines[book.cover]) },
    ...book.pages.map((p, i) => ({ key: `${i + 1}`, title: `${i + 1}. ${p.title}`, svg: drawStoryPage(book, i + 1, outlines[p.picture]) })),
  ];
}

export default function App() {
  const [label, setLabel] = useState(startingBook);
  const book = findBook(label);
  const [state, setState] = useState({ status: 'loading' });

  useEffect(() => {
    let live = true;
    setState({ status: 'loading' });
    try { history.replaceState(null, '', `?${new URLSearchParams({ book: book.id })}`); } catch { /* file:// */ }
    loadStorybook(book)
      .then(async (sb) => { const pages = await drawBook(sb); if (live) setState({ status: 'ready', book: sb, pages }); })
      .catch((err) => live && setState({ status: 'error', message: err.message }));
    return () => { live = false; };
  }, [book.id]);

  const ready = state.status === 'ready';
  const download = (page) => {
    const url = URL.createObjectURL(new Blob([page.svg], { type: 'image/svg+xml' }));
    const name = `${book.label}-${page.key}`.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    Object.assign(document.createElement('a'), { href: url, download: `${name}.svg` }).click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  return (
    <>
      <header className="no-print">
        <h1>🎨 Colors of Eden</h1>
        <p>A coloring storybook for every book of the Bible</p>
      </header>
      <main>
        <section className="controls no-print" aria-label="Choose a book">
          <label>Book
            <select value={label} onChange={(e) => setLabel(e.target.value)}>
              <optgroup label="Old Testament">{BIBLE.slice(0, NEW_TESTAMENT).map((b) => <option key={b.id}>{b.label}</option>)}</optgroup>
              <optgroup label="New Testament">{BIBLE.slice(NEW_TESTAMENT).map((b) => <option key={b.id}>{b.label}</option>)}</optgroup>
            </select>
          </label>
          <div className="buttons">
            <button className="primary" disabled={!ready} onClick={() => print()}>Print the book or save it as a PDF</button>
            <a className="button" href={superBookLink(book, 1)} target="_blank" rel="noreferrer">Read {book.label} in SuperBook ↗</a>
          </div>
          <div role="status" aria-live="polite" className="status">
            {state.status === 'loading' && <p className="muted">Getting {book.label} ready…</p>}
            {state.status === 'error' && <p className="error">{state.message}. Check your connection and pick the book again.</p>}
            {ready && (
              <>
                <p>{state.book.about}</p>
                <ol className="contents">
                  {state.book.pages.map((p, i) => (
                    <li key={i}><a href={`#page-${i + 1}`}>{p.title}</a> <span className="muted">{chapters(state.book, p).slice(state.book.label.length + 1)}</span></li>
                  ))}
                </ol>
              </>
            )}
          </div>
        </section>
        <section className="book" aria-label={`${book.label} coloring storybook`}>
          {ready ? state.pages.map((p) => (
            <figure key={p.key} id={`page-${p.key}`} className="page">
              <div className="sheet" dangerouslySetInnerHTML={{ __html: p.svg }} />
              <figcaption className="no-print"><button onClick={() => download(p)}>Download this page (SVG)</button></figcaption>
            </figure>
          )) : <div className="sheet empty" />}
        </section>
      </main>
      <footer className="no-print">
        <p>Stories retold for ages 5 to 8. Pictures: drawings of animals, places and people of the Middle East, traced into clean line art. Books in the order of <a href="https://theoyanvno.github.io/SuperBook/">SuperBook</a>, where every chapter can be read in full.</p>
      </footer>
    </>
  );
}

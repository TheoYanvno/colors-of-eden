# 🎨 Colors of Eden

Printable coloring pages from any chapter of the Orthodox Bible. Pick a book and a chapter, and Colors of Eden reads the chapter, chooses what to draw from its words (sheep and a quiet stream for Psalm 23, the sun, moon and waters for Genesis 1), and draws a line-art page with a verse to print and color. When a chapter names one of 60 drawings of animals, places and people of the Middle East (the lions in Daniel 6, Pharaoh in Exodus), the page is that drawing instead.

**Try it:** https://theoyanvno.github.io/colors-of-eden/

**Status:** in progress. The web page and the Python command line both draw pages, and the web page prints them or saves them as PDFs.

![Two storybook coloring pages: Psalm 23 with a cup, a sheep and flowers on rolling hills beside still waters, and Genesis 1 with the sun, the moon and a dove over mountains, hills and waves, each with its verse on a ribbon](docs/examples.png)

## The web page

Pick a book and a chapter and the page is drawn right away, with what's behind, what's in front (or the picture) and the verse it chose. **Picture** leaves the choice automatic, keeps the page drawn in code, or uses any of the 60 drawings, so any chapter can have the lion, the Sea of Galilee or a shepherd. **Print or save as PDF** prints just the page, full size on US Letter paper (choose Save as PDF in the print window for a file), **Download SVG** saves the drawing itself, **Booklet** prints up to 20 chapters in a row as one set of pages (a long one takes up to a minute, because the free text service allows about 15 chapters every 30 seconds), and **Read in SuperBook** opens the same chapter in [SuperBook](https://theoyanvno.github.io/SuperBook/). Links work both ways: `?book=Jonah&chapter=1` opens that chapter here, just as it does in SuperBook.

```bash
npm install
npm start      # build and serve at http://localhost:8000
npm test       # the web page's tests, including a check that it plans pages exactly like the Python version
npm run build  # build into docs/ for GitHub Pages
```

## On Windows

Everything runs on Windows (and macOS or Linux). On Windows, Python is `python` instead of `python3`, and the commands below work as written in the VS Code terminal (PowerShell). Open the folder in VS Code and it offers the recommended extensions (Python, SVG preview); **Terminal > Run Task** has ready-made tasks to install everything, start the web page, run both test suites, draw a page or list the pictures.

You only need Python and Node.js. Re-tracing the picture sheets (rarely needed) also takes `pip install -r tools/requirements.txt`.

## The command line

```bash
python -m coe page Psalms 23     # saves out/psalms-23.svg, ready to print on US Letter paper
python -m coe plan Psalms 23     # shows what the page will show
python -m coe page Daniel 6 --picture animals/lion   # use a drawing (or --picture none)
python -m coe pictures           # the 60 drawings and the words that choose them
```

```
Psalms 23 (World English Bible (public domain))
Background: path, waves
In front:   cup, sheep, flowers
Verse 2: He makes me lie down in green pastures. He leads me beside still waters.
```

## Where the words and pictures come from

- **Books:** the Eastern Orthodox Bible, in the same books, order and names as [SuperBook](https://theoyanvno.github.io/SuperBook/), which is the reference for this project: 52 Old Testament books in Orthodox order (with Tobit, Judith, the Maccabees, Wisdom of Solomon, Sirach, Baruch and the others) and the 27 of the New Testament. Any common name works, so `1 Samuel` and `1 Kingdoms` find the same book. `tests/test_superbook.py` checks the list still matches SuperBook's.
- **Text:** the World English Bible, a public-domain translation, from [bible-api.com](https://bible-api.com/), the same source SuperBook reads. Each chapter is fetched once and cached in `.coe-cache/`. Genesis 1 and Psalm 23 are included so it works offline. Like SuperBook, it can't offer the Letter of Jeremiah, Psalm 151 or the Greek additions to Esther and Daniel, which that free source doesn't have.
- **Drawn pages:** made in code (`coe/art.py`) in a storybook style: a framed scene with layered hills, a sun, moon, stars, clouds, mountains, waves and a winding path behind; trees, flowers, sheep, a dove, fish, a boat, a crown, a lamp, a cup and a heart in front, with texture lines like bark, wool and ripples, and the verse on a ribbon. Every shape is a closed outline, so each area can be colored in.
- **Picture pages:** 60 drawings (20 animals, 20 places, 20 people of the Middle East) from the author's own picture sheets, kept in `coe/pictures/source/`. The sheets are small, so `tools/trace_pictures.py` cuts out each drawing, removes its printed name and traces it with [potrace](https://potrace.sourceforge.net/) into smooth outlines that print sharp at full page size (`coe/pictures/<kind>/<name>.svg`). `coe/pictures/catalog.json` lists the words that choose each one: a chapter needs to name a drawing at least three times (lion, lions, lioness…) for its page to use it.

## Run the tests

```bash
python -m unittest   # the Python version (python3 on macOS or Linux)
npm test             # the web page
```

Built with help from AI coding tools; every feature is reviewed and tested before it ships.

## License

MIT. See [LICENSE](LICENSE).

# 🎨 Colors of Eden

Printable coloring pages from any chapter of the Orthodox Bible. Pick a book and a chapter, and Colors of Eden reads the chapter, chooses what to draw from its words (sheep and a quiet stream for Psalm 23, the sun, moon and waters for Genesis 1), and draws an original line-art page with a verse to print and color.

**Try it:** https://theoyanvno.github.io/colors-of-eden/

**Status:** in progress. The web page and the Python command line both draw pages, and the web page prints them or saves them as PDFs.

![Two storybook coloring pages: Psalm 23 with a cup, a sheep and flowers on rolling hills beside still waters, and Genesis 1 with the sun, the moon and a dove over mountains, hills and waves, each with its verse on a ribbon](docs/examples.png)

## The web page

Pick a book and a chapter and the page is drawn right away, with what's behind, what's in front and the verse it chose. **Print or save as PDF** prints just the page, full size on US Letter paper (choose Save as PDF in the print window for a file), **Download SVG** saves the drawing itself, **Booklet** prints up to 10 chapters in a row as one set of pages, and **Read in SuperBook** opens the same chapter in [SuperBook](https://theoyanvno.github.io/SuperBook/). Links work both ways: `?book=Jonah&chapter=1` opens that chapter here, just as it does in SuperBook.

```bash
npm install
npm start      # build and serve at http://localhost:8000
npm test       # the web page's tests, including a check that it plans pages exactly like the Python version
npm run build  # build into docs/ for GitHub Pages
```

## The command line

```bash
python -m coe page Psalms 23     # saves out/psalms-23.svg, ready to print on US Letter paper
python -m coe plan Psalms 23     # shows what the page will show
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
- **Pictures:** every drawing is original, made in code (`coe/art.py`) in a storybook style: a framed scene with layered hills, a sun, moon, stars, clouds, mountains, waves and a winding path behind; trees, flowers, sheep, a dove, fish, a boat, a crown, a lamp, a cup and a heart in front, with texture lines like bark, wool and ripples, and the verse on a ribbon. No clip art or traced images. Every shape is a closed outline, so each area can be colored in.

## Run the tests

```bash
python -m unittest   # the Python version
npm test             # the web page
```

Built with help from AI coding tools; every feature is reviewed and tested before it ships.

## License

MIT. See [LICENSE](LICENSE).

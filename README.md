# 🎨 Colors of Eden

Printable coloring pages from any Bible chapter. Pick a book and a chapter, and Colors of Eden reads the chapter, chooses what to draw from its words (sheep and a quiet stream for Psalm 23, the sun, moon and waters for Genesis 1), and draws an original line-art page with a verse to print and color.

**Status:** in progress. Choosing what to draw is done; the drawings, the web page and printable PDFs are next.

## Try it

```bash
python -m coe plan Psalms 23
```

```
Psalms 23 (King James Version (public domain))
Background: path
In front:   cup, sheep, flowers, heart
Verse 5: Thou preparest a table before me in the presence of mine enemies: ...
```

## Where the words and pictures come from

- **Text:** the King James Version, which is in the public domain in the United States, from [bible-api.com](https://bible-api.com/). Each chapter is fetched once and cached in `.coe-cache/`. Genesis 1 and Psalm 23 are included so it works offline.
- **Pictures:** every drawing is original, made from simple shapes in code. No clip art or traced images.

## Run the tests

```bash
python -m unittest
```

Built with help from AI coding tools; every feature is reviewed and tested before it ships.

## License

MIT. See [LICENSE](LICENSE).

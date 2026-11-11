# 🎨 Colors of Eden

Printable coloring pages from any Bible chapter. Pick a book and a chapter, and Colors of Eden reads the chapter, chooses what to draw from its words (sheep and a quiet stream for Psalm 23, the sun, moon and waters for Genesis 1), and draws an original line-art page with a verse to print and color.

**Status:** in progress. Choosing what to draw and drawing the pages work; the web page and printable PDFs are next.

![Two storybook coloring pages: Psalm 23 with a cup, a sheep and flowers on rolling hills with a winding path, and Genesis 1 with the sun, the moon and a dove over mountains, hills and waves, each with its verse on a ribbon](docs/examples.png)

## Try it

```bash
python -m coe page Psalms 23     # saves out/psalms-23.svg, ready to print on US Letter paper
python -m coe plan Psalms 23     # shows what the page will show
```

```
Psalms 23 (King James Version (public domain))
Background: path
In front:   cup, sheep, flowers, heart
Verse 5: Thou preparest a table before me in the presence of mine enemies: ...
```

## Where the words and pictures come from

- **Text:** the King James Version, which is in the public domain in the United States, from [bible-api.com](https://bible-api.com/). Each chapter is fetched once and cached in `.coe-cache/`. Genesis 1 and Psalm 23 are included so it works offline.
- **Pictures:** every drawing is original, made in code (`coe/art.py`) in a storybook style: a framed scene with layered hills, a sun, moon, stars, clouds, mountains, waves and a winding path behind; trees, flowers, sheep, a dove, fish, a boat, a crown, a lamp, a cup and a heart in front, with texture lines like bark, wool and ripples, and the verse on a ribbon. No clip art or traced images. Every shape is a closed outline, so each area can be colored in.

## Run the tests

```bash
python -m unittest
```

Built with help from AI coding tools; every feature is reviewed and tested before it ships.

## License

MIT. See [LICENSE](LICENSE).

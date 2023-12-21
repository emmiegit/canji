## <ruby>缶<rp>(</rp><rt>かん</rt><rp>)</rp> 字<rp>(</rp><rt>じ</rt><rp>)</rp></ruby>
<small><em>(Read like "kanji")</em></small>

A system to procedurally generate plausible but nonexistant kanji.

### Execution

This system is set up as a series of scripts to perform each of the requisite steps. These scripts target Python 3.

First we need to initialize the KanjiVG submodule since that's what we use as the basis for our SVG files.

```sh
git submodule init
```

Then, we need to extract and process radicals as separate SVGs. This involves both pulling out component radicals (e.g. 亻or 糹), it also copies full characters like 頑.

```sh
./extract_radicals.py
```

If you need to start over, you can wipe the output data.

```sh
./clean.sh
```

### Development

These scripts are formatted using [Black](https://github.com/psf/black).

### License

Available under the terms of the [GNU Lesser General Public License](LICENSE.md), v2.1 only. All generated SVG files are licensed as [Creative Commons Attribution-ShareAlike 3.0](https://creativecommons.org/licenses/by-sa/3.0/).

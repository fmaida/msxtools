# MSX Tools

Tools that allows to read virtual tape files for the old MSX format (.cas),
manage them and convert them back into an audio file that can be used with the real hardware.

## Usage

```bash
msxtools -i game.rom                            # convert it into game.wav, in the same folder
msxtools -i roms/game.rom -o wav/game.wav       # choose the output file (its folder is created if needed)
msxtools -i game.rom -o game.cas                # write a .cas virtual tape for emulators instead of a WAV
msxtools -i game.rom -o game.zip                # .cas + variants/.wav + _manifest.json in a zip (asks for the texts if no manifest)
msxtools -i game.cas -b 2400                    # choose the bitrate (600-4800 bps, default 2205)
msxtools -i game.cas --block 2                  # export only the second block
msxtools info -i game.cas                       # list the blocks contained in a tape or ROM
msxtools                                        # start the interactive shell
```

### Loading screen

When a ROM is converted, the tape starts with a small BASIC loader that shows a loading screen.
Its texts can be customized with a `_manifest.json` file placed in the same folder as the ROM
(or passed with `-m` / `--manifest`):

```json
{
  "title": "Game title",
  "year": "2026",
  "developer": "Game developer"
}
```

```
GAME TITLE
NOW LOADING - PLEASE WAIT

2026 GAME DEVELOPER
```

All fields are optional: without a title the ROM file name is used. Texts are converted to
upper case, without accents, and cut to 37 characters.

The optional `"filename"` field (1 to 6 letters or digits) sets the names of the files on the
tape: the BASIC loader takes that name, and the ROM parts its first 5 characters followed by
0, 1, 2... (e.g. `"prova"` gives `prova`, `prova0`, `prova1` for a 32KB ROM). Without it, the
loader takes the ROM file name and the parts are called `DATA1`, `DATA2`...

When converting to `.zip` without a manifest, the title, year, developer and file name are
asked on the terminal, and saved in the zip as `_manifest.json`, together with the command
that loads the tape:

```
game.cas
variants/
    game.wav
_manifest.json
```

The `_manifest.json` in the zip ends with the format, target, fidelity and SHA-256 hash
of each file, and with the hash of all of them (existing `"files"` and `"sha_256"` fields of the
input manifest are replaced):

```json
"files": {
  "game.cas": {
    "format": "MSX Virtual Cassette (.cas)",
    "target": "Emulation",
    "fidelity": "low",
    "sha_256": "<sha256>"
  },
  "variants": {
    "game.wav": {
      "format": "Wave Audio File @ 2205bps",
      "target": "Real Hardware",
      "fidelity": "high",
      "sha_256": "<sha256>"
    }
  }
},
"sha_256": "<sha256>"
```

`"fidelity"` tells how close each file is to the original tape: `low` for the `.cas`
(only the data), `medium` for a `.tsx` in `variants` (not generated yet), `high` for the
`.wav` (the whole audio signal).

The last `"sha_256"` covers all the files in the zip except `_manifest.json` (it is
recalculated too). It is the hash of the list written by `sha256sum`, with the files in
the same order as the `"files"` section:

```bash
sha256sum game.cas variants/game.wav | sha256sum
```

Requires Python 3.13 or later.

## Development

The project is managed with [Poetry](https://python-poetry.org/):

```bash
poetry install      # create the virtualenv and install the package + dev dependencies
poetry run pytest   # run the test suite
poetry run msxtools # run the command line tool from the virtualenv
poetry build        # build sdist and wheel into dist/
```

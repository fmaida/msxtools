# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

The project uses Poetry (Python >= 3.13, only runtime dependency: typer).

```bash
poetry install                                        # virtualenv + package + dev deps
poetry run pytest -q                                  # full test suite (~5 s)
poetry run pytest tests/test_zip.py                   # one file
poetry run pytest tests/test.py::test_rom_48k         # one test
poetry run pytest -k manifest                         # tests matching a name
poetry run msxtools -i game.rom -o game.zip           # run the CLI (.wav / .cas / .zip by output extension)
poetry run msxtools info -i game.cas                  # list the blocks of a tape or ROM
poetry run msxtools                                   # interactive shell (cmd.Cmd)
```

There is no linter or formatter configured. pytest collects `tests/test*.py` (including the
plain `tests/test.py`).

## Conventions

- Identifiers, comments and docstrings are in **Italian** (`cassetta`, `blocco`, `esporta`,
  `inserisci_silenzio`, parameters prefixed with `p_`). User-facing messages (CLI output,
  errors, README) are in **English**. Keep both conventions.
- Project errors are raised as `Eccezione` (`src/msxtools/eccezioni.py`), whose `.parameter` is
  the message shown by the CLI/shell.
- Sections inside classes are separated by `# --=-=----...----=-=--` lines.

## Architecture

The package lives in `src/msxtools/`. Everything goes through `Tape` (`tape.py`), a list of
data blocks that is either read from a `.cas` file or built from a ROM, and exported in one
of three formats.

### Blocks and reading `.cas` files
- `datablocks/`: `AsciiFile`, `BasicFile`, `BinaryFile`, `CustomFile` (headerless data), all
  subclasses of `GenericDataBlock`. The block type (`.type`: `"ascii"`, `"basic"`, `"binary"`,
  `"custom"`) comes from the 10 bytes after the header (`datablocks/intestazioni.py`).
- `ricerche.py` (`Ricerca`) scans the raw `.cas` buffer for the 8-byte CAS header
  `1F A6 DE BA CC 13 7D 74` and splits it into blocks. Extra header bytes after type/name are
  preserved (`coda_intestazione`) so tapes are rewritten byte-identical.
- Each block implements two outputs: `parti_cas()` (the parts written to a `.cas`, each after
  an 8-byte-aligned header) and `esporta(p_file)` (writes sync tones, silences and bytes to
  an `Esportazione`).

### Audio export (`datablocks/wav/`)
- `Esportazione` writes an 8-bit mono WAV: `inserisci_bit/byte/stringa` (start bit, 8 data bits,
  2 stop bits), `inserisci_sincronismo(ms)`, `inserisci_silenzio(ms)` (rounded **up** to whole
  bits). `pausa_tra_blocchi` (4000 ms) separates blocks, `pausa_ai_bordi` (500 ms) is added at
  the start and end of every WAV so emulators do not think the file is truncated.
- `Parametri` holds the bitrate (default 2205 bps, 20 samples per bit) and precomputed
  waveforms as **class-level global state**. `Parametri.modifica_bitrate` changes it for the
  whole process; tests that change it must restore it (see the `bitrate_iniziale` fixture in
  `tests/test_zip.py`).

### ROM import (`Tape.importa_rom`, `loader.py`, `caricatore.py`)
A ROM (`.rom` / `.mx1`, up to 48KB) becomes a tape made of:
1. an ASCII BASIC loader (`caricatore.LoaderBasic` / `programma_basic`) that shows the loading
   screen (title, credits, progress bar, estimated wait time) and `BLOAD`s each part;
2. one binary block per 16KB part, loaded at 9000h with a Z80 machine-code loader appended
   (`Loader.binari_*`, source in `initgame/*.ASM`) that copies it to its final page; the last
   one starts the game. 48KB ROMs must have the "AB" header at 4000h.

The loader text depends on the current bitrate (estimated time), so `LoaderBasic.dati` is
recomputed per bitrate. `caricatore.ContaDurata` mimics `Esportazione` to compute durations
without writing audio: **keep it in sync with `Esportazione`** (tests compare it with real WAV
lengths).

### Manifest and zip export
- `manifest.py` (`Manifest`): `_manifest.json` with `title`, `year`, `developer`, optional
  `filename` (1-6 alphanumerics, tape file names). Looked up next to the input file or passed
  with `-m`; used only for ROMs' loading screen. If missing when exporting a zip, it is asked
  interactively (`Manifest.chiedi`).
- `Tape.export_to_zip` writes `<name>.cas`, `variants/<name>.wav` and `_manifest.json`. The
  manifest in the zip is the input manifest (all fields kept, even unknown ones) or the
  generated one (`Manifest.in_dizionario`, with `instructions.loading_command` from
  `Tape.comando_di_caricamento`: `RUN"CAS:"` / `CLOAD` / `BLOAD"CAS:",R` by first block type),
  followed by `files` (per file: `format`, `target`, `fidelity`, `sha_256`; the `.cas` always
  first) and a global `sha_256` (`sha_256_complessivo`: hash of the `sha256sum`-style list in
  the order of `files`). `files` and `sha_256` are always recalculated. README documents the
  format; update it when this changes.

### Front ends
- `cli.py`: typer app (`msxtools.cli:main`). The default command converts (`-i`, `-o`, `-b`,
  `--block`, `-m`); the output format is chosen by the output extension.
- `ui/__init__.py`: the interactive shell (`Ui`, `cmd.Cmd`) with its own `open`/`export`
  commands. Zip export logic is duplicated here (`_manifest_per_zip`): changes to the zip or
  manifest flow usually need to be applied to both `cli.py` and `ui/__init__.py`.

## Tests

`tests/assets/` holds real tapes (`tapes/*.cas`), ROMs and manifests used by the tests;
`tests/test.py` covers tape parsing, ROM import and regressions, `test_zip.py` the zip and
manifest, `test_cli.py` the CLI and shell, `test_caricatore.py` the BASIC loader and duration
estimate. `tests/test.py::convert` writes WAVs to `tests/output/` (git-ignored).

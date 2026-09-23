import json
from pathlib import Path
from typing import Annotated

import typer

from msxtools.tape import Tape
from msxtools.eccezioni import Eccezione
from msxtools.datablocks.wav.parametri import Parametri
from msxtools.manifest import Manifest, NOME_MANIFEST


app = typer.Typer(
    no_args_is_help=False,
    add_completion=False,
)

_INPUT_HELP = ".cas tape, or .rom / .mx1 cartridge"

InputOpt = Annotated[
    Path,
    typer.Option("--input", "-i", exists=True, dir_okay=False, readable=True,
                 metavar="FILE", help=_INPUT_HELP),
]
OutputOpt = Annotated[
    Path | None,
    typer.Option("--output", "-o", dir_okay=False, metavar="FILE",
                 help="Output file: a .wav audio file, a .cas virtual tape for emulators, or a .zip "
                      "with both plus the manifest (default: <input stem>.wav in the input file folder)"),
]
BitrateOpt = Annotated[
    int,
    typer.Option("--bitrate", "-b", min=600, max=4800, help="Bitrate in bps"),
]
ManifestOpt = Annotated[
    Path | None,
    typer.Option("--manifest", "-m", exists=True, dir_okay=False, readable=True, metavar="FILE",
                 help="JSON file with the texts of the ROM loading screen "
                      "(default: " + NOME_MANIFEST + " in the input file folder, if present)"),
]
BlockOpt = Annotated[
    int | None,
    typer.Option("--block", metavar="N", min=1,
                 help="Export only block N (as numbered by 'info')"),
]


# --=-=--------------------------------------------------------------------------=-=--

def _errore(p_messaggio):
    typer.secho("Whoops... something went wrong: {0}".format(p_messaggio),
                fg=typer.colors.RED, err=True)
    raise typer.Exit(1)


def _percorso_manifest(p_input: Path, p_manifest: Path | None) -> Path | None:
    # Il manifest indicato con -m, altrimenti il _manifest.json accanto all'input
    percorso = p_manifest or p_input.parent / NOME_MANIFEST
    return percorso if percorso.is_file() else None


def _manifest(p_input: Path, p_manifest: Path | None) -> Manifest | None:
    # I testi servono solo per la schermata di caricamento delle ROM
    if not Tape.e_una_rom(p_input):
        if p_manifest is not None:
            typer.secho("Manifest ignored: {0} is not a ROM".format(p_input), fg=typer.colors.YELLOW)
        return None

    percorso = _percorso_manifest(p_input, p_manifest)
    if percorso is None:
        return None

    manifest = Manifest.carica(str(percorso))
    typer.echo("Loading screen texts from {0}".format(percorso))
    return manifest


def _manifest_per_zip(p_input: Path, p_manifest: Path | None) -> tuple[Manifest, dict | None]:
    # Nello zip il manifest c'è sempre: se non c'è un file, i testi li chiede all'utente.
    # I campi di un manifest chiesto all'utente (None) si creano dopo aver letto il nastro,
    # perché le istruzioni dipendono dal suo primo blocco. Di un file si tengono tutti
    # i campi, anche quelli che msxtools non usa
    percorso = _percorso_manifest(p_input, p_manifest)
    if percorso is None:
        typer.echo("No manifest found for {0}, please describe the game:".format(p_input.name))
        return Manifest.chiedi(str(p_input), p_nome_file=Tape.e_una_rom(p_input)), None

    manifest = Manifest.carica(str(percorso))
    typer.echo("Manifest from {0}".format(percorso))
    return manifest, json.loads(percorso.read_bytes())


def _carica(p_file: Path, p_manifest: Path | None = None) -> Tape:
    try:
        return Tape(str(p_file), _manifest(p_file, p_manifest))
    except Eccezione as e:
        _errore(e.parameter)


def _converti(p_input: Path, p_output: Path | None, p_bitrate: int, p_blocco: int | None,
              p_manifest: Path | None = None):
    # Se non viene indicato un file di output usa il nome del file di input,
    # senza estensione, seguito da ".wav", nella stessa cartella del file di input
    if p_output is None:
        p_output = p_input.parent / (p_input.stem + ".wav")

    if p_output.resolve() == p_input.resolve():
        _errore("the output file would overwrite the input file {0}".format(p_input))

    # Il formato di uscita dipende dall'estensione: .cas per gli emulatori, .zip con
    # .cas, .wav e manifest, altrimenti WAV
    formato = p_output.suffix.lower()

    if formato == ".zip":
        try:
            manifest, campi_manifest = _manifest_per_zip(p_input, p_manifest)
            cassetta = Tape(str(p_input), manifest if Tape.e_una_rom(p_input) else None)
        except Eccezione as e:
            _errore(e.parameter)
    else:
        cassetta = _carica(p_input, p_manifest)

    if p_blocco is not None and p_blocco > len(cassetta):
        _errore("block {0} does not exist, the tape has only {1} blocks"
                .format(p_blocco, len(cassetta)))

    if formato == ".cas" and p_bitrate != Parametri.bitrate:
        typer.secho("Bitrate ignored: a .cas file has no audio", fg=typer.colors.YELLOW)
    elif p_bitrate != Parametri.bitrate:
        Parametri.modifica_bitrate(p_bitrate)

    # L'utente conta i blocchi da 1, come nell'elenco mostrato da "info"
    indice = p_blocco - 1 if p_blocco is not None else -1

    if formato == ".zip" and campi_manifest is None:
        campi_manifest = manifest.in_dizionario(cassetta.comando_di_caricamento(indice))

    # L'utente può tenere input e output in cartelle separate: se la cartella
    # di output non esiste ancora la crea
    try:
        p_output.parent.mkdir(parents=True, exist_ok=True)
        if formato == ".zip":
            cassetta.export_to_zip(str(p_output), indice, campi_manifest)
        elif formato == ".cas":
            cassetta.export_to_cas(str(p_output), indice)
        else:
            cassetta.export_to_wav(str(p_output), indice)
    except OSError as e:
        _errore("unable to write {0}: {1}".format(p_output, e.strerror or e))

    if formato == ".zip":
        messaggio = "File exported as {0} (CAS + WAV at {1}bps + manifest)"
    elif formato == ".cas":
        messaggio = "File exported as {0}"
    else:
        messaggio = "File exported as {0} at {1}bps"
    typer.secho(messaggio.format(p_output, Parametri.bitrate), fg=typer.colors.GREEN)


# --=-=--------------------------------------------------------------------------=-=--

@app.callback(invoke_without_command=True)
def principale(
        ctx: typer.Context,
        input_file: Annotated[Path | None, typer.Option(
            "--input", "-i", exists=True, dir_okay=False, readable=True,
            metavar="FILE", help=_INPUT_HELP)] = None,
        output_file: OutputOpt = None,
        bitrate: BitrateOpt = Parametri.bitrate,
        block: BlockOpt = None,
        manifest: ManifestOpt = None,
):
    """
    Convert MSX virtual tapes (.cas) or ROMs into WAV audio files.

    Usage: msxtools -i game.rom [-o folder/game.wav]

    Without any option, starts the interactive shell.
    """
    if ctx.invoked_subcommand is not None:
        if input_file is not None or output_file is not None or manifest is not None:
            ctx.fail("put --input / --output after the '{0}' command"
                     .format(ctx.invoked_subcommand))
        return

    if input_file is not None:
        _converti(input_file, output_file, bitrate, block, manifest)
    elif output_file is not None or block is not None or manifest is not None \
            or bitrate != Parametri.bitrate:
        ctx.fail("Missing option '--input' / '-i'.")
    else:
        shell()


@app.command()
def info(input_file: InputOpt):
    """
    List the blocks contained in a tape or ROM.
    """
    cassetta = _carica(input_file)
    try:
        typer.echo(cassetta)
    except Eccezione as e:
        _errore(e.parameter)


@app.command()
def convert(
        input_file: InputOpt,
        output_file: OutputOpt = None,
        bitrate: BitrateOpt = Parametri.bitrate,
        block: BlockOpt = None,
        manifest: ManifestOpt = None,
):
    """
    Convert a tape or ROM into a WAV audio file (same as msxtools -i ...).
    """
    _converti(input_file, output_file, bitrate, block, manifest)


@app.command()
def shell():
    """
    Start the interactive shell.
    """
    from msxtools.ui import Ui
    Ui().cmdloop()


def main():
    app(prog_name="msxtools")

import cmd
import json
from os import getcwd, listdir, makedirs
from os.path import abspath, dirname, expanduser, isdir, isfile, join

import typer

from msxtools.tape import Tape
from msxtools.eccezioni import Eccezione
from msxtools.datablocks.wav.parametri import Parametri
from msxtools.manifest import Manifest, NOME_MANIFEST


ESTENSIONI_SUPPORTATE = (".cas", ".rom", ".mx1")


def _errore(p_messaggio):
    typer.secho(str(p_messaggio), fg=typer.colors.RED, err=True)


class Ui(cmd.Cmd):
    """
    Shell interattiva per caricare cassette (.cas) o ROM ed esportarle in un file WAV
    """

    intro = "MSX Tools interactive shell. Type 'help' for the list of commands."
    prompt = ">>> "

    def __init__(self):
        super().__init__()
        self.cassetta = Tape()
        self.directory = getcwd()
        self.file_aperto = None

    # --=-=--------------------------------------------------------------------------=-=--

    def _percorso(self, p_file):
        return abspath(join(self.directory, expanduser(p_file)))

    # --=-=--------------------------------------------------------------------------=-=--

    def do_cd(self, p_dir=""):
        """cd [DIR] - Show or change the current directory"""

        if p_dir == "":
            typer.echo(self.directory)
        else:
            nuova = self._percorso(p_dir)
            if isdir(nuova):
                self.directory = nuova
            else:
                _errore("No such directory: {0}".format(p_dir))

    def do_ls(self, p_dir=""):
        """ls [DIR] - List directories and supported files (.cas, .rom, .mx1)"""

        p_dir = self._percorso(p_dir)

        try:
            elenco = sorted(listdir(p_dir))
        except OSError as e:
            _errore(e)
            return

        for file in elenco:
            if file.startswith("."):
                continue
            if isdir(join(p_dir, file)):
                typer.echo(file + "/")
            elif file.lower().endswith(ESTENSIONI_SUPPORTATE):
                typer.echo(file)

        typer.echo()

    def do_open(self, p_file):
        """open FILE - Load a .cas tape or a .rom/.mx1 cartridge, replacing the current tape.
        For ROMs, the loading screen texts are read from _manifest.json in the same folder"""

        if not p_file:
            _errore("Usage: open FILE")
            return

        try:
            percorso = self._percorso(p_file)
            # Per le ROM usa i testi del _manifest.json che si trova nella stessa cartella
            manifest = Manifest.cerca(percorso) if Tape.e_una_rom(percorso) else None
            self.cassetta = Tape(percorso, manifest)
            self.file_aperto = percorso
            typer.echo(self.cassetta)
        except Eccezione as e:
            _errore("Whoops... something went wrong: {0}".format(e.parameter))
        except OSError as e:
            _errore(e)

    def do_list(self, _=""):
        """list - Show the blocks contained in the current tape"""

        try:
            typer.echo(self.cassetta)
        except Eccezione as e:
            _errore(e.parameter)

    def do_bitrate(self, p_valore):
        """bitrate [BPS] - Show or change the bitrate used for the WAV export (600-4800)"""

        try:
            p_valore = int(p_valore)
        except ValueError:
            typer.echo("{0}bps".format(Parametri.bitrate))
            return

        if p_valore < 600 or p_valore > 4800:
            _errore("You must provide a bitrate value between 600bps and 4800bps")
        else:
            Parametri.modifica_bitrate(p_valore)

    def do_export(self, p_file):
        """export FILE.wav|FILE.cas|FILE.zip - Export the current tape as a WAV audio file,
        a .cas file, or a .zip with both plus the manifest (_manifest.json in the folder of
        the opened file; if missing, title, year and developer are asked)"""

        formato = p_file.lower()[-4:]
        if len(self.cassetta) == 0:
            _errore("Tape is currently empty, use 'open' first")
            return
        if formato not in (".wav", ".cas", ".zip"):
            _errore("I don't know what to do with {0}".format(p_file))
            return

        percorso = self._percorso(p_file)
        if formato == ".zip":
            try:
                campi_manifest = self._manifest_per_zip()
            except Eccezione as e:
                _errore(e.parameter)
                return
            except typer.Abort:
                _errore("Export cancelled")
                return

        try:
            # Se la cartella di destinazione non esiste ancora la crea
            makedirs(dirname(percorso), exist_ok=True)
            if formato == ".zip":
                self.cassetta.export_to_zip(percorso, -1, campi_manifest)
            elif formato == ".cas":
                self.cassetta.export_to_cas(percorso)
            else:
                self.cassetta.export_to_wav(percorso)
        except OSError as e:
            _errore("Unable to write {0}: {1}".format(p_file, e.strerror or e))
            return

        if formato == ".zip":
            messaggio = "File exported as {0} (CAS + WAV at {1}bps + manifest)"
        elif formato == ".cas":
            messaggio = "File exported as {0}"
        else:
            messaggio = "File exported as {0} at {1}bps"
        typer.secho(messaggio.format(p_file, Parametri.bitrate), fg=typer.colors.GREEN)

    def _manifest_per_zip(self) -> dict:
        # Il _manifest.json accanto al file aperto (già usato da "open" per le ROM),
        # altrimenti titolo, anno e sviluppatore vengono chiesti all'utente
        percorso = join(dirname(self.file_aperto), NOME_MANIFEST)
        if isfile(percorso):
            Manifest.carica(percorso)
            with open(percorso, "rb") as f:
                return json.load(f)

        typer.echo("No manifest found, please describe the game:")
        manifest = Manifest.chiedi(self.file_aperto, p_nome_file=Tape.e_una_rom(self.file_aperto))
        if Tape.e_una_rom(self.file_aperto):
            # La schermata di caricamento deve usare i testi appena inseriti
            self.cassetta = Tape(self.file_aperto, manifest)
        return manifest.in_dizionario(self.cassetta.comando_di_caricamento())

    def do_quit(self, _=""):
        """quit - Exit the shell"""
        return True

    def do_EOF(self, _=""):
        typer.echo()
        return True

    def emptyline(self):
        pass

import json
import os
import unicodedata
from dataclasses import dataclass

from .eccezioni import Eccezione


NOME_MANIFEST = "_manifest.json"

# Cartella dello zip con le altre versioni del nastro (il file audio .wav)
CARTELLA_VARIANTI = "variants"

# Con WIDTH 40 una riga più lunga andrebbe a capo nella schermata di caricamento
LUNGHEZZA_MASSIMA = 37


def testo_per_basic(p_testo: str) -> bytes:
    """
    Prepara un testo per essere scritto con PRINT"..." dal loader in BASIC

    Args:
        p_testo: Il testo da convertire

    Returns:
        Il testo in maiuscolo, senza accenti, senza virgolette (romperebbero il PRINT)
        e lungo al massimo LUNGHEZZA_MASSIMA caratteri (tagliato all'ultima parola intera)
    """
    testo = unicodedata.normalize("NFKD", p_testo.upper())
    testo = testo.encode("ascii", "ignore").decode("ascii")
    testo = " ".join(testo.replace('"', "").split())
    if len(testo) > LUNGHEZZA_MASSIMA:
        # Taglia all'ultima parola intera, se possibile
        taglio = testo[:LUNGHEZZA_MASSIMA + 1].rsplit(" ", 1)[0]
        testo = taglio if " " in testo[:LUNGHEZZA_MASSIMA + 1] else testo[:LUNGHEZZA_MASSIMA]
    return testo.encode("ascii")


def nome_file_valido(p_nome: str) -> bool:
    """
    Indica se un nome può essere usato per i file sul nastro: da 1 a 6 lettere o cifre
    (l'intestazione dei file MSX ha spazio per 6 caratteri)
    """
    return 1 <= len(p_nome) <= 6 and p_nome.isascii() and p_nome.isalnum()


@dataclass
class Manifest:
    """
    Testi da mostrare nella schermata di caricamento, letti da un file _manifest.json
    """

    title: str = ""
    year: str = ""
    developer: str = ""
    # Nome dei file sul nastro (facoltativo): il loader BASIC si chiama così, le
    # parti della ROM con i primi 5 caratteri seguiti da 0, 1, 2...
    filename: str = ""

    # --=-=--------------------------------------------------------------------------=-=--

    @classmethod
    def carica(cls, p_file: str) -> "Manifest":
        """
        Legge un file _manifest.json

        Args:
            p_file: Il percorso al file JSON

        Returns:
            Il manifest letto dal file
        """
        try:
            with open(p_file, encoding="utf-8") as f:
                dati = json.load(f)
        except OSError as e:
            raise Eccezione("Unable to read manifest \"{0}\": {1}".format(p_file, e.strerror or e)) from e
        except ValueError as e:
            raise Eccezione("Manifest \"{0}\" is not valid JSON: {1}".format(p_file, e)) from e

        if not isinstance(dati, dict):
            raise Eccezione("Manifest \"{0}\" must contain a JSON object".format(p_file))

        campi = {}
        for campo in ("title", "year", "developer"):
            valore = dati.get(campo, "")
            # L'anno si può scrivere anche come numero: "year": 2026
            if isinstance(valore, int) and not isinstance(valore, bool):
                valore = str(valore)
            if not isinstance(valore, str):
                raise Eccezione("Manifest \"{0}\": \"{1}\" must be a string".format(p_file, campo))
            campi[campo] = valore.strip()

        nome = dati.get("filename", "")
        if not isinstance(nome, str) or (nome and not nome_file_valido(nome)):
            raise Eccezione("Manifest \"{0}\": \"filename\" must be 1 to 6 letters or digits"
                            .format(p_file))
        campi["filename"] = nome

        return cls(**campi)

    # --=-=--------------------------------------------------------------------------=-=--

    @classmethod
    def cerca(cls, p_file_input: str) -> "Manifest | None":
        """
        Cerca un file _manifest.json nella stessa cartella del file di input

        Args:
            p_file_input: Il percorso della ROM da convertire

        Returns:
            Il manifest, oppure None se nella cartella non c'è
        """
        percorso = os.path.join(os.path.dirname(os.path.abspath(p_file_input)), NOME_MANIFEST)
        if os.path.isfile(percorso):
            return cls.carica(percorso)
        return None

    # --=-=--------------------------------------------------------------------------=-=--

    @classmethod
    def chiedi(cls, p_file_input: str, p_chiedi=None, p_nome_file: bool = True) -> "Manifest":
        """
        Chiede all'utente titolo, anno e sviluppatore del gioco e, se richiesto, il
        nome dei file sul nastro

        Args:
            p_file_input: Il file da convertire: dal suo nome si propongono titolo e
                          nome dei file
            p_chiedi:     La funzione che fa la domanda (di default typer.prompt)
            p_nome_file:  Se chiedere anche il nome dei file sul nastro (serve solo
                          per le ROM, che hanno un loader)

        Returns:
            Il manifest con le risposte
        """
        import typer
        if p_chiedi is None:
            p_chiedi = typer.prompt

        nome_input = os.path.splitext(os.path.basename(p_file_input))[0]
        titolo = " ".join(nome_input.replace("_", " ").replace("-", " ").split())

        manifest = cls(title=p_chiedi("Title", default=titolo).strip(),
                       year=p_chiedi("Year", default="").strip(),
                       developer=p_chiedi("Developer", default="").strip())

        if p_nome_file:
            proposta = "".join(c for c in nome_input if c.isascii() and c.isalnum())[:6]
            while True:
                nome = p_chiedi("File name on tape (1-6 letters or digits)", default=proposta).strip()
                if nome_file_valido(nome):
                    break
                typer.secho("\"{0}\" is not valid: use 1 to 6 letters or digits".format(nome),
                            fg=typer.colors.RED, err=True)
            manifest.filename = nome

        return manifest

    # --=-=--------------------------------------------------------------------------=-=--

    def in_dizionario(self, p_comando: str = None) -> dict:
        """
        Restituisce i campi del manifest, come vanno scritti nel file _manifest.json

        Args:
            p_comando: Il comando con cui caricare il nastro (es. RUN"CAS:"), scritto
                       in coda in "instructions"; se manca le istruzioni non ci sono
        """
        dati = {"title": self.title, "year": self.year, "developer": self.developer}
        if self.filename:
            dati["filename"] = self.filename
        if p_comando:
            dati["instructions"] = {"loading_command": p_comando}
        return dati

    # --=-=--------------------------------------------------------------------------=-=--

    def nomi_nastro(self, p_parti: int) -> tuple[str, list[str]] | None:
        """
        Restituisce i nomi dei file sul nastro: quello del loader BASIC e quelli delle
        parti della ROM (primi 5 caratteri seguiti da 0, 1, 2...)

        Args:
            p_parti: Il numero di parti della ROM

        Returns:
            (loader, [parte0, parte1, ...]), oppure None se il nome non è stato scelto
        """
        if not self.filename:
            return None
        return self.filename, [self.filename[:5] + str(parte) for parte in range(p_parti)]

    # --=-=--------------------------------------------------------------------------=-=--

    def riga_crediti(self) -> str:
        """
        Restituisce la riga in fondo alla schermata di caricamento, es. "2026 SVILUPPATORE"
        """
        return " ".join(parte for parte in (self.year, self.developer) if parte)

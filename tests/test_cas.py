import glob
import os

import pytest
from typer.testing import CliRunner

import msxtools
from msxtools.cli import app
from msxtools.ricerche import Ricerca
from msxtools.datablocks import AsciiFile, BinaryFile
from msxtools.datablocks.intestazioni import Intestazioni

HERE = os.path.dirname(os.path.abspath(__file__))
TAPES = os.path.join(HERE, "assets", "tapes")
ROMS = os.path.join(HERE, "assets", "roms")
HEADER = Intestazioni.blocco_intestazione

# Nastri con residui dello strumento che li ha creati ("ff 00 00 00 00 00 00 00" dopo i
# segmenti ASCII), che l'MSX non legge e che non vengono riscritti
CON_BYTE_SPURI = {"city_connection.cas", "rocket_roger.cas"}
# Nastro rovinato: programmi ASCII senza EOF, che vengono completati quando lo si riscrive
ROVINATI = {"lato-a.cas"}

TUTTI = sorted(os.path.basename(f) for f in glob.glob(os.path.join(TAPES, "*.cas")))


def _blocchi(p_buffer):
    ricerca = Ricerca()
    ricerca.buffer = p_buffer
    blocchi = []
    while not ricerca.eof():
        blocchi.append(ricerca.ricerca_blocco())
    return blocchi


def _riscrivi(p_tape, p_cartella):
    uscita = str(p_cartella / "riscritto.cas")
    p_tape.export_to_cas(uscita)
    with open(uscita, "rb") as f:
        return f.read(), msxtools.Tape(uscita)


@pytest.mark.parametrize("nome", sorted(set(TUTTI) - CON_BYTE_SPURI - ROVINATI))
def test_cas_round_trip_identical(tmp_path, nome):
    originale = os.path.join(TAPES, nome)
    riscritto, _ = _riscrivi(msxtools.Tape(originale), tmp_path)
    with open(originale, "rb") as f:
        assert riscritto == f.read()


@pytest.mark.parametrize("nome", sorted(CON_BYTE_SPURI))
def test_cas_round_trip_without_stray_bytes(tmp_path, nome):
    cassetta = msxtools.Tape(os.path.join(TAPES, nome))
    _, riletta = _riscrivi(cassetta, tmp_path)

    assert [(b.type, b.title, b.dati) for b in riletta] == [(b.type, b.title, b.dati) for b in cassetta]
    # Il testo dei programmi ASCII non contiene più i byte spuri ogni 256 caratteri
    for blocco in cassetta:
        if blocco.type == "ascii":
            assert b"\xff\x00\x00\x00\x00\x00\x00\x00" not in blocco.dati


@pytest.mark.parametrize("nome", TUTTI)
def test_cas_export_is_stable(tmp_path, nome):
    primo, riletta = _riscrivi(msxtools.Tape(os.path.join(TAPES, nome)), tmp_path)
    secondo, _ = _riscrivi(riletta, tmp_path)
    assert primo == secondo


@pytest.mark.parametrize("rom", ["road_fighter.rom", "champion_billiards.rom"])
def test_rom_to_cas(tmp_path, rom):
    cassetta = msxtools.Tape(os.path.join(ROMS, rom))
    dati, riletta = _riscrivi(cassetta, tmp_path)

    assert dati.startswith(HEADER + AsciiFile.intestazione)
    assert [(b.type, b.title) for b in riletta] == [(b.type, b.title) for b in cassetta]
    # Il loader BASIC viene completato con EOF fino a un multiplo di 256 byte
    basic = cassetta[0].dati
    assert riletta[0].dati[:basic.index(b"\x1a") + 1] == basic[:basic.index(b"\x1a") + 1]
    for originale, riletto in zip(cassetta[1:], riletta[1:]):
        # Rileggendo, i byte di allineamento a 8 restano in coda ai dati (l'MSX carica
        # solo da indirizzo iniziale a finale, quindi non li legge)
        lunghezza = len(originale.dati)
        assert riletto.dati[:lunghezza] == originale.dati
        assert riletto.dati[lunghezza:] == b"\x00" * (len(riletto.dati) - lunghezza)
        assert len(riletto.dati) - lunghezza < 8
        assert riletto.indirizzo_iniziale.valore == originale.indirizzo_iniziale.valore
        assert riletto.indirizzo_finale.valore == originale.indirizzo_finale.valore
        assert riletto.indirizzo_esecuzione.valore == originale.indirizzo_esecuzione.valore


def test_cas_headers_aligned_to_8_bytes(tmp_path):
    dati, _ = _riscrivi(msxtools.Tape(os.path.join(ROMS, "champion_billiards.rom")), tmp_path)
    posizione = dati.find(HEADER)
    while posizione >= 0:
        assert posizione % 8 == 0
        posizione = dati.find(HEADER, posizione + 1)


def test_ascii_segments_are_256_bytes():
    # Ogni segmento ha 8 byte spuri dopo i 256 che l'MSX legge
    segmento1 = b"A" * 256 + b"\xff" + b"\x00" * 7
    segmento2 = b"B" * 10 + b"\x1a" * 246 + b"\xff" + b"\x00" * 7
    blocco, = _blocchi(HEADER + AsciiFile.intestazione + b"TEST  "
                       + HEADER + segmento1 + HEADER + segmento2)
    assert blocco.dati == b"A" * 256 + b"B" * 10 + b"\x1a" * 246


def test_ascii_without_eof_ends_at_next_file():
    blocchi = _blocchi(HEADER + AsciiFile.intestazione + b"UNO   " + HEADER + b"A" * 256
                       + HEADER + AsciiFile.intestazione + b"DUE   " + HEADER + b"B\x1a" + b"\x00" * 254)
    assert [(b.type, b.title) for b in blocchi] == [("ascii", "UNO   "), ("ascii", "DUE   ")]
    assert blocchi[0].dati == b"A" * 256


def test_header_extra_bytes_are_kept():
    extra = b"\x00\xff\x00BKB\x00B"
    blocco, = _blocchi(HEADER + BinaryFile.intestazione + b"PRGRAM" + extra
                       + HEADER + bytes([0x00, 0x90, 0x04, 0x90, 0x00, 0x90]) + b"abcde")
    assert blocco.coda_intestazione == extra
    assert blocco.parti_cas()[0] == BinaryFile.intestazione + b"PRGRAM" + extra


# --=-=--------------------------------------------------------------------------=-=--
# Riga di comando e shell

runner = CliRunner()


def test_cli_output_cas(tmp_path):
    uscita = tmp_path / "road.cas"
    risultato = runner.invoke(app, ["-i", os.path.join(ROMS, "road_fighter.rom"),
                                    "-o", str(uscita), "-b", "2400"])
    assert risultato.exit_code == 0, risultato.output
    assert "Bitrate ignored" in risultato.output
    assert uscita.read_bytes().startswith(HEADER)
    assert len(msxtools.Tape(str(uscita))) == 2


def test_cli_output_cas_uppercase_extension(tmp_path):
    uscita = tmp_path / "CONGO.CAS"
    risultato = runner.invoke(app, ["-i", os.path.join(TAPES, "congo.cas"), "-o", str(uscita)])
    assert risultato.exit_code == 0, risultato.output
    assert uscita.read_bytes() == open(os.path.join(TAPES, "congo.cas"), "rb").read()


def test_shell_export_cas(tmp_path):
    from msxtools.ui import Ui

    ui = Ui()
    ui.directory = str(tmp_path)
    ui.onecmd("open " + os.path.join(TAPES, "congo.cas"))
    ui.onecmd("export copia.cas")
    assert (tmp_path / "copia.cas").read_bytes() == open(os.path.join(TAPES, "congo.cas"), "rb").read()

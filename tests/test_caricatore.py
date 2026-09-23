import os
import re
import wave

import pytest
from typer.testing import CliRunner

import msxtools
from msxtools.caricatore import durata_caricamento, messaggio_di_attesa
from msxtools.cli import app
from msxtools.datablocks.wav.parametri import Parametri

HERE = os.path.dirname(os.path.abspath(__file__))
ROMS = os.path.join(HERE, "assets", "roms")

runner = CliRunner()


@pytest.fixture(autouse=True)
def bitrate_predefinito():
    # Il bitrate è globale: ogni test riparte da quello predefinito
    Parametri.modifica_bitrate(2205)
    yield
    Parametri.modifica_bitrate(2205)


def _durata_wav(p_file):
    with wave.open(str(p_file)) as w:
        return w.getnframes() / w.getframerate()


def _attesa(p_cassetta):
    righe = dict(re.findall(rb'LOCATE\d+,(\d+):PRINT"([^"]*)"', p_cassetta[0].dati))
    return righe[b"7"], righe[b"8"]


@pytest.mark.parametrize("rom", ["road_fighter.rom", "champion_billiards.rom"])
@pytest.mark.parametrize("bitrate", [1200, 2205, 3600])
def test_estimate_matches_wav(tmp_path, rom, bitrate):
    Parametri.modifica_bitrate(bitrate)
    cassetta = msxtools.Tape(os.path.join(ROMS, rom))

    # Tutto il nastro meno il loader BASIC: restano la pausa dopo il loader, le parti
    # della ROM e le pause fra una parte e l'altra
    cassetta.export_to_wav(str(tmp_path / "tutto.wav"))
    cassetta.export_to_wav(str(tmp_path / "loader.wav"), 0)
    atteso = _durata_wav(tmp_path / "tutto.wav") - _durata_wav(tmp_path / "loader.wav")

    assert durata_caricamento(cassetta[1:], bitrate) == pytest.approx(atteso, abs=1 / bitrate)


def test_estimate_text():
    assert messaggio_di_attesa(222, 2205) == b"3m 42s @ 2205bps"
    assert messaggio_di_attesa(221.2, 2205) == b"3m 42s @ 2205bps"  # arrotondato per eccesso
    assert messaggio_di_attesa(65, 1200) == b"1m 05s @ 1200bps"
    assert messaggio_di_attesa(9.5, 4800) == b"0m 10s @ 4800bps"


def test_loading_screen_shows_estimate():
    cassetta = msxtools.Tape(os.path.join(ROMS, "champion_billiards.rom"))
    titolo, attesa = _attesa(cassetta)
    assert titolo == b"Estimated wait time:"
    atteso = messaggio_di_attesa(durata_caricamento(cassetta[1:], 2205), 2205)
    assert attesa == atteso
    assert re.fullmatch(rb"\d+m \d\ds @ 2205bps", attesa)


def test_estimate_follows_bitrate_changed_later():
    cassetta = msxtools.Tape(os.path.join(ROMS, "champion_billiards.rom"))
    _, a_2205 = _attesa(cassetta)

    # Il bitrate cambia dopo aver letto la ROM (come con -b o il comando "bitrate")
    Parametri.modifica_bitrate(1200)
    _, a_1200 = _attesa(cassetta)
    assert a_1200.endswith(b"@ 1200bps")

    def secondi(p_testo):
        minuti, sec = re.match(rb"(\d+)m (\d+)s", p_testo).groups()
        return int(minuti) * 60 + int(sec)

    assert secondi(a_1200) > secondi(a_2205)


def test_cli_bitrate_in_loading_screen(tmp_path):
    uscita = tmp_path / "x.zip"
    manifest = tmp_path / "m.json"
    manifest.write_text('{"title": "Champion Billiards"}')
    risultato = runner.invoke(app, ["-i", os.path.join(ROMS, "champion_billiards.rom"),
                                    "-m", str(manifest), "-o", str(uscita), "-b", "2400"])
    assert risultato.exit_code == 0, risultato.output

    import zipfile
    with zipfile.ZipFile(uscita) as archivio:
        cas = archivio.read("x.cas")
    assert b"@ 2400bps" in cas


def test_loading_screen_still_centered():
    cassetta = msxtools.Tape(os.path.join(ROMS, "champion_billiards.rom"))
    posizioni = re.findall(rb'LOCATE(\d+),(\d+):PRINT"([^"]*)"', cassetta[0].dati)
    righe = sorted({int(r) for _, r, _ in posizioni})
    assert righe[0] == 23 - righe[-1]
    for colonna, _, testo in posizioni[:6]:
        sinistra = int(colonna)
        assert (40 - sinistra - len(testo)) - sinistra in (0, 1), testo

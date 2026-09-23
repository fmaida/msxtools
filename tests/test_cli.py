import json
import os

import pytest
from typer.testing import CliRunner

from msxtools.cli import app

HERE = os.path.dirname(os.path.abspath(__file__))
CONGO = os.path.join(HERE, "assets", "tapes", "congo.cas")

runner = CliRunner()


@pytest.fixture(autouse=True)
def cartella_di_lavoro(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_convert_default_output(cartella_di_lavoro):
    # Senza --output il WAV va nella stessa cartella del file di input
    cartella_input = cartella_di_lavoro / "input"
    cartella_input.mkdir()
    cassetta = cartella_input / "congo.cas"
    cassetta.write_bytes(open(CONGO, "rb").read())

    risultato = runner.invoke(app, ["convert", "-i", str(cassetta), "--block", "1"])
    assert risultato.exit_code == 0, risultato.output
    assert (cartella_input / "congo.wav").is_file()
    assert not (cartella_di_lavoro / "congo.wav").exists()


@pytest.mark.parametrize("opzione", ["-o", "--output"])
def test_convert_output(cartella_di_lavoro, opzione):
    risultato = runner.invoke(app, ["convert", "--input", CONGO, opzione, "tape.wav",
                                    "--block", "1"])
    assert risultato.exit_code == 0, risultato.output
    assert (cartella_di_lavoro / "tape.wav").is_file()
    assert not (cartella_di_lavoro / "congo.wav").exists()


def test_convert_missing_input():
    risultato = runner.invoke(app, ["convert"])
    assert risultato.exit_code != 0


def test_convert_separate_folders(cartella_di_lavoro):
    # -i cartella_uno/file.cas -o cartella_due/file.wav, con cartella_due non ancora esistente
    cartella_uno = cartella_di_lavoro / "cartella_uno"
    cartella_uno.mkdir()
    (cartella_uno / "file.cas").write_bytes(open(CONGO, "rb").read())

    risultato = runner.invoke(app, ["convert", "-i", "cartella_uno/file.cas",
                                    "-o", "cartella_due/file.wav", "--block", "1"])
    assert risultato.exit_code == 0, risultato.output
    assert (cartella_di_lavoro / "cartella_due" / "file.wav").is_file()
    assert not (cartella_uno / "file.wav").exists()


def test_convert_output_not_writable(cartella_di_lavoro):
    # Un file al posto della cartella di output: errore leggibile, non un traceback
    (cartella_di_lavoro / "occupato").write_text("")

    risultato = runner.invoke(app, ["convert", "-i", CONGO, "-o", "occupato/file.wav",
                                    "--block", "1"])
    assert risultato.exit_code == 1
    assert "unable to write" in risultato.output


def test_top_level_input_output(cartella_di_lavoro):
    # msxtools -i cartella_uno/file.cas -o cartella_due/file.wav, senza sottocomando
    risultato = runner.invoke(app, ["-i", CONGO, "-o", "cartella_due/file.wav", "--block", "1"])
    assert risultato.exit_code == 0, risultato.output
    assert (cartella_di_lavoro / "cartella_due" / "file.wav").is_file()


def test_top_level_output_without_input():
    risultato = runner.invoke(app, ["-o", "file.wav"])
    assert risultato.exit_code == 2
    assert "--input" in risultato.output


def test_output_same_as_input(cartella_di_lavoro):
    cassetta = cartella_di_lavoro / "congo.cas"
    originale = open(CONGO, "rb").read()
    cassetta.write_bytes(originale)

    risultato = runner.invoke(app, ["-i", "congo.cas", "-o", "./congo.cas"])
    assert risultato.exit_code == 1
    assert "overwrite the input" in risultato.output
    assert cassetta.read_bytes() == originale


def test_shell_export_creates_folder(cartella_di_lavoro):
    from msxtools.ui import Ui

    ui = Ui()
    ui.onecmd("open " + CONGO)
    ui.onecmd("export cartella_nuova/congo.wav")
    assert (cartella_di_lavoro / "cartella_nuova" / "congo.wav").is_file()


# --=-=--------------------------------------------------------------------------=-=--
# Testi della schermata di caricamento letti da _manifest.json

ROAD_FIGHTER = os.path.join(HERE, "assets", "roms", "road_fighter.rom")


def _cartella_gioco(cartella, p_manifest=None):
    gioco = cartella / "gioco"
    gioco.mkdir()
    (gioco / "road_fighter.rom").write_bytes(open(ROAD_FIGHTER, "rb").read())
    if p_manifest is not None:
        (gioco / "_manifest.json").write_text(p_manifest, encoding="utf-8")
    return gioco


def _loader_basic(p_rom, p_manifest=None):
    import msxtools
    return msxtools.Tape(str(p_rom), p_manifest)[0].dati


def test_manifest_next_to_rom(cartella_di_lavoro):
    gioco = _cartella_gioco(cartella_di_lavoro, json.dumps(
        {"title": "Titolo del gioco", "year": "2026", "developer": "Sviluppatore del gioco"}))

    risultato = runner.invoke(app, ["-i", str(gioco / "road_fighter.rom")])
    assert risultato.exit_code == 0, risultato.output
    assert "_manifest.json" in risultato.output

    from msxtools import Manifest
    dati = _loader_basic(gioco / "road_fighter.rom", Manifest.cerca(str(gioco / "road_fighter.rom")))
    assert b'PRINT"TITOLO DEL GIOCO"' in dati
    assert b'PRINT"NOW LOADING - PLEASE WAIT"' in dati
    assert b'PRINT"2026 SVILUPPATORE DEL GIOCO"' in dati
    assert b"MASTROPIERO" not in dati


def test_manifest_texts_are_made_basic_safe():
    from msxtools import Manifest
    manifest = Manifest(title='Città "segreta" di un titolo davvero troppo lungo per lo schermo',
                        year="1986", developer="Konami")
    dati = _loader_basic(ROAD_FIGHTER, manifest)
    assert b'PRINT"CITTA SEGRETA DI UN TITOLO DAVVERO"' in dati
    assert b'PRINT"1986 KONAMI"' in dati

    # Una parola sola più lunga dello schermo viene tagliata a 37 caratteri
    manifest = Manifest(title="A" * 50)
    assert b'PRINT"' + b"A" * 37 + b'"' in _loader_basic(ROAD_FIGHTER, manifest)


@pytest.mark.parametrize("contenuto, titolo, crediti", [
    ('{"title": "Solo titolo"}', b"SOLO TITOLO", b"(C) 2016-20 MASTROPIERO"),
    ('{"year": 2026}', b"ROAD FIGHTER", b"2026"),
    ('{"developer": "Konami"}', b"ROAD FIGHTER", b"KONAMI"),
    ('{}', b"ROAD FIGHTER", b"(C) 2016-20 MASTROPIERO"),
])
def test_manifest_partial(cartella_di_lavoro, contenuto, titolo, crediti):
    from msxtools import Manifest
    gioco = _cartella_gioco(cartella_di_lavoro, contenuto)
    dati = _loader_basic(gioco / "road_fighter.rom", Manifest.cerca(str(gioco / "road_fighter.rom")))
    assert b'PRINT"' + titolo + b'"' in dati
    assert b'PRINT"' + crediti + b'"' in dati


def test_manifest_explicit_option(cartella_di_lavoro):
    (cartella_di_lavoro / "testi.json").write_text('{"title": "Da opzione"}', encoding="utf-8")
    gioco = _cartella_gioco(cartella_di_lavoro, '{"title": "Dalla cartella"}')

    risultato = runner.invoke(app, ["-i", str(gioco / "road_fighter.rom"), "-m", "testi.json"])
    assert risultato.exit_code == 0, risultato.output
    assert "testi.json" in risultato.output


@pytest.mark.parametrize("contenuto, messaggio", [
    ("{non è json", "not valid JSON"),
    ('["title"]', "must contain a JSON object"),
    ('{"title": ["a"]}', '"title" must be a string'),
])
def test_manifest_invalid(cartella_di_lavoro, contenuto, messaggio):
    gioco = _cartella_gioco(cartella_di_lavoro, contenuto)
    risultato = runner.invoke(app, ["-i", str(gioco / "road_fighter.rom")])
    assert risultato.exit_code == 1
    assert messaggio in risultato.output
    assert not (gioco / "road_fighter.wav").exists()


def test_manifest_ignored_for_tapes(cartella_di_lavoro):
    (cartella_di_lavoro / "testi.json").write_text('{"title": "X"}', encoding="utf-8")
    risultato = runner.invoke(app, ["-i", CONGO, "-m", "testi.json", "-o", "congo.wav",
                                    "--block", "1"])
    assert risultato.exit_code == 0, risultato.output
    assert "Manifest ignored" in risultato.output


def test_shell_open_uses_manifest(cartella_di_lavoro):
    from msxtools.ui import Ui
    gioco = _cartella_gioco(cartella_di_lavoro, '{"title": "Dalla shell"}')

    ui = Ui()
    ui.onecmd("open " + str(gioco / "road_fighter.rom"))
    assert b'PRINT"DALLA SHELL"' in ui.cassetta[0].dati

import hashlib
import io
import json
import os
import wave
import zipfile

import pytest
from typer.testing import CliRunner

import msxtools
from msxtools.cli import app
from msxtools.datablocks.wav.parametri import Parametri

HERE = os.path.dirname(os.path.abspath(__file__))
ROMS = os.path.join(HERE, "assets", "roms")
TAPES = os.path.join(HERE, "assets", "tapes")
MANIFEST = b'{\n  "title": "Road Fighter",\n  "year": 1984,\n  "developer": "Konami",\n  "extra": "x"\n}\n'

runner = CliRunner()


@pytest.fixture(autouse=True)
def cartella_di_lavoro(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def bitrate_iniziale():
    # Il bitrate è globale: un test che esporta a un'altra velocità non deve
    # cambiarlo per i test successivi
    bitrate = Parametri.bitrate
    yield
    if Parametri.bitrate != bitrate:
        Parametri.modifica_bitrate(bitrate)


def _gioco(p_cartella, p_sorgente, p_manifest=None):
    gioco = p_cartella / "gioco"
    gioco.mkdir()
    destinazione = gioco / os.path.basename(p_sorgente)
    destinazione.write_bytes(open(p_sorgente, "rb").read())
    if p_manifest is not None:
        (gioco / "_manifest.json").write_bytes(p_manifest)
    return destinazione


def _contenuto(p_zip):
    with zipfile.ZipFile(p_zip) as archivio:
        return {info.filename: (info.compress_type, archivio.read(info.filename))
                for info in archivio.infolist()}


def _hash(p_contenuto, p_nome, p_bitrate=2205):
    # La sezione "files" che il manifest deve riportare, con gli hash SHA-256
    # calcolati sui file dello zip
    def sha256(p_file):
        return hashlib.sha256(p_contenuto[p_file][1]).hexdigest()
    return {
        p_nome + ".cas": {"format": "MSX Virtual Cassette (.cas)", "target": "Emulation",
                          "fidelity": "low", "sha_256": sha256(p_nome + ".cas")},
        "variants": {
            p_nome + ".wav": {"format": "Wave Audio File @ {0}bps".format(p_bitrate),
                              "target": "Real Hardware", "fidelity": "high",
                              "sha_256": sha256("variants/" + p_nome + ".wav")}}}


def _sha_256_totale(p_contenuto, p_nome):
    # Come "sha256sum x.cas variants/x.wav | sha256sum" (l'ordine della sezione "files"),
    # sui file letti dallo zip
    elenco = "".join("{0}  {1}\n".format(hashlib.sha256(p_contenuto[file][1]).hexdigest(), file)
                     for file in (p_nome + ".cas", "variants/" + p_nome + ".wav"))
    return hashlib.sha256(elenco.encode()).hexdigest()


def _loader_basic(p_cas):
    cassetta = msxtools.Tape()
    cassetta._ricerca.buffer = p_cas
    blocco = cassetta._ricerca.ricerca_blocco()
    return blocco.dati


def test_zip_with_manifest_next_to_rom(cartella_di_lavoro):
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"), MANIFEST)
    risultato = runner.invoke(app, ["-i", str(rom), "-o", "uscita/pacchetto.zip"])
    assert risultato.exit_code == 0, risultato.output
    assert "Title" not in risultato.output  # nessuna domanda: il manifest c'è

    contenuto = _contenuto(cartella_di_lavoro / "uscita" / "pacchetto.zip")
    # .cas e .wav prendono il nome dello zip, il manifest si chiama sempre _manifest.json
    assert set(contenuto) == {"pacchetto.cas", "variants/pacchetto.wav", "_manifest.json"}
    assert all(tipo == zipfile.ZIP_DEFLATED for tipo, _ in contenuto.values())

    # Il manifest ha tutti i campi di quello originale, più "files"
    assert json.loads(contenuto["_manifest.json"][1]) == {
        **json.loads(MANIFEST), "files": _hash(contenuto, "pacchetto"),
        "sha_256": _sha_256_totale(contenuto, "pacchetto")}

    # Il .cas è quello che si otterrebbe esportando direttamente, con i testi del manifest
    atteso = msxtools.Tape(str(rom), msxtools.Manifest.cerca(str(rom))).cas_in_bytes()
    assert contenuto["pacchetto.cas"][1] == atteso
    assert b'PRINT"1984 KONAMI"' in _loader_basic(atteso)

    with wave.open(io.BytesIO(contenuto["variants/pacchetto.wav"][1])) as w:
        assert w.getnframes() > 0


def test_zip_is_compressed(cartella_di_lavoro):
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"), MANIFEST)
    runner.invoke(app, ["-i", str(rom), "-o", "pacchetto.zip"])
    with zipfile.ZipFile("pacchetto.zip") as archivio:
        wav = archivio.getinfo("variants/pacchetto.wav")
        assert wav.compress_size < wav.file_size / 5


def test_zip_manifest_from_option(cartella_di_lavoro):
    # Un manifest con un altro nome finisce nello zip come _manifest.json
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"))
    (cartella_di_lavoro / "road_fighter.json").write_bytes(MANIFEST)
    risultato = runner.invoke(app, ["-i", str(rom), "-m", "road_fighter.json", "-o", "x.zip"])
    assert risultato.exit_code == 0, risultato.output
    campi = json.loads(_contenuto("x.zip")["_manifest.json"][1])
    assert campi.pop("files")
    assert campi.pop("sha_256")
    assert campi == json.loads(MANIFEST)


def test_zip_asks_for_manifest(cartella_di_lavoro):
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"))
    risultato = runner.invoke(app, ["-i", str(rom), "-o", "x.zip"],
                              input="Titolo del gioco\n2026\nSviluppatore\nprova\n")
    assert risultato.exit_code == 0, risultato.output
    assert "Title" in risultato.output

    contenuto = _contenuto("x.zip")
    assert json.loads(contenuto["_manifest.json"][1]) == {
        "title": "Titolo del gioco", "year": "2026", "developer": "Sviluppatore",
        "filename": "prova",
        "instructions": {"loading_command": 'RUN"CAS:"'},
        "files": _hash(contenuto, "x"), "sha_256": _sha_256_totale(contenuto, "x")}

    # I testi inseriti finiscono anche nella schermata di caricamento
    basic = _loader_basic(contenuto["x.cas"][1])
    assert b'PRINT"TITOLO DEL GIOCO"' in basic
    assert b'PRINT"2026 SVILUPPATORE"' in basic


def test_zip_asks_for_manifest_defaults(cartella_di_lavoro):
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"))
    risultato = runner.invoke(app, ["-i", str(rom), "-o", "x.zip"], input="\n\n\n\n")
    assert risultato.exit_code == 0, risultato.output

    # Il nome proposto per i file è quello della ROM, solo lettere e cifre, max 6
    contenuto = _contenuto("x.zip")
    assert json.loads(contenuto["_manifest.json"][1]) == {
        "title": "road fighter", "year": "", "developer": "", "filename": "roadfi",
        "instructions": {"loading_command": 'RUN"CAS:"'},
        "files": _hash(contenuto, "x"), "sha_256": _sha_256_totale(contenuto, "x")}
    basic = _loader_basic(contenuto["x.cas"][1])
    assert b'PRINT"ROAD FIGHTER"' in basic
    assert b'PRINT"(C) 2016-20 MASTROPIERO";' in basic


def test_zip_asks_for_manifest_stdin_closed(cartella_di_lavoro):
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"))
    risultato = runner.invoke(app, ["-i", str(rom), "-o", "x.zip"], input="")
    assert risultato.exit_code != 0
    assert not (cartella_di_lavoro / "x.zip").exists()


@pytest.mark.parametrize("cassetta, comando", [
    ("congo.cas", 'RUN"CAS:"'),
    ("kuma_logo.cas", "CLOAD"),
    ("chuckie_egg.cas", 'BLOAD"CAS:",R'),
])
def test_zip_asks_for_manifest_tape_instructions(cartella_di_lavoro, cassetta, comando):
    # Le istruzioni dipendono dal primo blocco del nastro
    sorgente = _gioco(cartella_di_lavoro, os.path.join(TAPES, cassetta))
    risultato = runner.invoke(app, ["-i", str(sorgente), "-o", "x.zip"], input="\n\n\n")
    assert risultato.exit_code == 0, risultato.output

    manifest = json.loads(_contenuto("x.zip")["_manifest.json"][1])
    assert manifest["instructions"] == {"loading_command": comando}
    assert list(manifest)[-3:] == ["instructions", "files", "sha_256"]  # in coda
    # Il .cas è sempre il primo, anche se "x.cas" viene dopo "variants"
    assert list(manifest["files"]) == ["x.cas", "variants"]
    assert list(manifest["files"]["x.cas"]) == ["format", "target", "fidelity", "sha_256"]


def test_tape_load_command_of_selected_block():
    # congo.cas: ASCII, poi binario
    cassetta = msxtools.Tape(os.path.join(TAPES, "congo.cas"))
    assert cassetta.comando_di_caricamento() == 'RUN"CAS:"'
    assert cassetta.comando_di_caricamento(1) == 'BLOAD"CAS:",R'
    assert msxtools.Tape().comando_di_caricamento() is None


def test_zip_replaces_files_of_input_manifest(cartella_di_lavoro):
    # "files" e "sha_256" già presenti nel manifest letto vengono sostituiti da quelli calcolati
    vecchio = {"title": "Road Fighter",
               "files": {"vecchio.cas": "0" * 64, "vecchio.wav": "1" * 64},
               "sha_256": "2" * 64,
               "developer": "Konami"}
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"),
                 json.dumps(vecchio).encode())
    risultato = runner.invoke(app, ["-i", str(rom), "-o", "x.zip"])
    assert risultato.exit_code == 0, risultato.output

    contenuto = _contenuto("x.zip")
    campi = json.loads(contenuto["_manifest.json"][1])
    assert campi == {"title": "Road Fighter", "developer": "Konami",
                     "files": _hash(contenuto, "x"), "sha_256": _sha_256_totale(contenuto, "x")}
    assert list(campi)[-2:] == ["files", "sha_256"]
    # Il manifest di input resta com'era
    assert json.loads((rom.parent / "_manifest.json").read_bytes()) == vecchio


def test_sha_256_complessivo_like_sha256sum():
    # Valore calcolato con: sha256sum game.cas variants/game.wav | sha256sum
    # (game.cas contiene "cassetta", variants/game.wav contiene "audio")
    from msxtools.tape import sha_256_complessivo
    hash_file = {"game.cas": hashlib.sha256(b"cassetta").hexdigest(),
                 "variants/game.wav": hashlib.sha256(b"audio").hexdigest()}
    assert sha_256_complessivo(hash_file) == \
        "9135de65690344ede15ff2159985eacc88a1a5eb420df7778c2bf89b021ffade"
    # L'ordine è quello indicato, non quello alfabetico
    invertito = dict(reversed(hash_file.items()))
    assert sha_256_complessivo(invertito) != sha_256_complessivo(hash_file)


def test_zip_from_tape_includes_manifest(cartella_di_lavoro):
    cassetta = _gioco(cartella_di_lavoro, os.path.join(TAPES, "congo.cas"), MANIFEST)
    risultato = runner.invoke(app, ["-i", str(cassetta), "-o", "CONGO.ZIP"])
    assert risultato.exit_code == 0, risultato.output
    assert "Manifest ignored" not in risultato.output

    contenuto = _contenuto("CONGO.ZIP")
    assert set(contenuto) == {"CONGO.cas", "variants/CONGO.wav", "_manifest.json"}
    assert contenuto["CONGO.cas"][1] == open(os.path.join(TAPES, "congo.cas"), "rb").read()


def test_zip_bitrate_and_block(cartella_di_lavoro):
    cassetta = _gioco(cartella_di_lavoro, os.path.join(TAPES, "congo.cas"), MANIFEST)
    risultato = runner.invoke(app, ["-i", str(cassetta), "-o", "x.zip", "-b", "2400", "--block", "1"])
    assert risultato.exit_code == 0, risultato.output

    contenuto = _contenuto("x.zip")
    with wave.open(io.BytesIO(contenuto["variants/x.wav"][1])) as w:
        assert w.getframerate() == 2400 * 20
    solo_primo = msxtools.Tape(str(cassetta)).cas_in_bytes(0)
    assert contenuto["x.cas"][1] == solo_primo
    # Il formato del wav riporta il bitrate usato
    assert json.loads(contenuto["_manifest.json"][1])["files"] == _hash(contenuto, "x", 2400)


def test_shell_export_zip_asks_for_manifest(cartella_di_lavoro, monkeypatch):
    from msxtools.ui import Ui

    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"))
    risposte = iter(["Dalla shell", "1985", "Konami", "shell"])
    monkeypatch.setattr("typer.prompt", lambda *a, **k: next(risposte))

    ui = Ui()
    ui.onecmd("open " + str(rom))
    ui.onecmd("export pacchetto.zip")

    contenuto = _contenuto(cartella_di_lavoro / "pacchetto.zip")
    campi = json.loads(contenuto["_manifest.json"][1])
    assert campi["title"] == "Dalla shell"
    assert campi["instructions"] == {"loading_command": 'RUN"CAS:"'}
    assert campi["files"] == _hash(contenuto, "pacchetto")
    assert b'PRINT"DALLA SHELL"' in _loader_basic(contenuto["pacchetto.cas"][1])
    assert [b.title for b in ui.cassetta] == ["shell ", "shell0"]


# --=-=--------------------------------------------------------------------------=-=--
# Nome dei file sul nastro scelto nel wizard


def _titoli(p_cas):
    ricerca = msxtools.Tape()
    ricerca._ricerca.buffer = p_cas
    blocchi = []
    while not ricerca._ricerca.eof():
        blocchi.append(ricerca._ricerca.ricerca_blocco())
    return [(b.type, b.title) for b in blocchi]


def test_wizard_file_name_32k(cartella_di_lavoro):
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "champion_billiards.rom"))
    risultato = runner.invoke(app, ["-i", str(rom), "-o", "x.zip"],
                              input="Titolo\n2026\nDev\nprova\n")
    assert risultato.exit_code == 0, risultato.output

    contenuto = _contenuto("x.zip")
    assert _titoli(contenuto["x.cas"][1]) == [
        ("ascii", "prova "), ("binary", "prova0"), ("binary", "prova1")]
    assert json.loads(contenuto["_manifest.json"][1])["filename"] == "prova"


def test_wizard_file_name_48k_rejects_invalid(cartella_di_lavoro):
    dati = bytearray(49152)
    dati[0x4000:0x4002] = b"AB"
    rom = cartella_di_lavoro / "gioco48.rom"
    rom.write_bytes(bytes(dati))

    # "mentina" ha 7 caratteri e "ab-c" contiene un trattino: vengono rifiutati
    risultato = runner.invoke(app, ["-i", str(rom), "-o", "x.zip"],
                              input="Titolo\n2026\nDev\nmentina\nab-c\nmentin\n")
    assert risultato.exit_code == 0, risultato.output
    assert risultato.output.count("is not valid") == 2

    # 6 caratteri: le parti usano i primi 5 seguiti dalla cifra
    assert _titoli(_contenuto("x.zip")["x.cas"][1]) == [
        ("ascii", "mentin"), ("binary", "menti0"), ("binary", "menti1"), ("binary", "menti2")]


def test_wizard_no_file_name_for_tapes(cartella_di_lavoro):
    cassetta = _gioco(cartella_di_lavoro, os.path.join(TAPES, "congo.cas"))
    risultato = runner.invoke(app, ["-i", str(cassetta), "-o", "x.zip"], input="Congo\n1983\nSega\n")
    assert risultato.exit_code == 0, risultato.output
    assert "File name" not in risultato.output
    assert "filename" not in json.loads(_contenuto("x.zip")["_manifest.json"][1])


def test_manifest_file_name_used_for_wav(cartella_di_lavoro):
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"),
                 b'{"title": "Road Fighter", "filename": "rf"}')
    risultato = runner.invoke(app, ["-i", str(rom), "-o", "x.cas"])
    assert risultato.exit_code == 0, risultato.output
    assert _titoli((cartella_di_lavoro / "x.cas").read_bytes()) == [
        ("ascii", "rf    "), ("binary", "rf0   ")]


@pytest.mark.parametrize("nome", ["troppolungo", "a b", "", "città"])
def test_manifest_invalid_file_name(cartella_di_lavoro, nome):
    rom = _gioco(cartella_di_lavoro, os.path.join(ROMS, "road_fighter.rom"),
                 json.dumps({"title": "X", "filename": nome}).encode())
    risultato = runner.invoke(app, ["-i", str(rom), "-o", "x.wav"])
    if nome == "":
        # Un nome vuoto equivale a non sceglierlo: nomi come prima
        assert risultato.exit_code == 0, risultato.output
    else:
        assert risultato.exit_code == 1
        assert "must be 1 to 6 letters or digits" in risultato.output


def test_without_file_name_names_are_unchanged():
    cassetta = msxtools.Tape(os.path.join(ROMS, "champion_billiards.rom"))
    assert [b.title for b in cassetta] == ["champi", "DATA1 ", "DATA2 "]

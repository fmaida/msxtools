import math
import os
import signal
import wave

import pytest

import msxtools
from msxtools.ricerche import Ricerca
from msxtools.datablocks import AsciiFile, BinaryFile
from msxtools.datablocks.intestazioni import Intestazioni
from msxtools.datablocks.wav import Esportazione
from msxtools.loader import Loader

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(HERE, "output")


def convert(p_file):
    filename = os.path.join(HERE, "assets", "tapes", p_file)
    cas = msxtools.Tape(filename)
    print(cas)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cas.export_to_wav(os.path.join(OUTPUT_DIR, "output.wav"))

    return cas


def convert_rom(p_file):
    filename = os.path.join(HERE, "assets", "roms", p_file)
    cas = msxtools.Tape(filename)
    print(cas)
    # cas.export_to_wav()

    return cas


def test_barnstormer():
    cas = convert("barnstormer.cas")
    assert len(cas) == 2


def test_brian_jacks():
    cas = convert("brian_jacks_superstar.cas")
    assert cas[0].type == "ascii"
    assert len(cas) == 3


def test_chuckie_egg():
    cas = convert("chuckie_egg.cas")
    assert cas[0].type == "binary"
    assert len(cas) == 2


def test_city_connection():
    cas = convert("city_connection.cas")
    assert cas[0].type == "ascii"
    assert len(cas) == 5


def test_congo():
    cas = convert("congo.cas")
    assert cas[0].type == "ascii"
    assert cas[1].type == "binary"
    assert len(cas) == 4


def test_disc_warrior():
    cas = convert("disc_warrior.cas")
    assert len(cas) == 3


def test_hustler():
    cas = convert("hustler.cas")
    assert len(cas) == 1


def test_kuma_logo():
    cas = convert("kuma_logo.cas")
    assert cas[0].type == "basic"
    assert len(cas) == 1


def test_le_mans():
    cas = convert("le_mans.cas")
    assert len(cas) == 2


def test_les_flics():
    cas = convert("les_flics.cas")
    assert len(cas) == 3


def test_rocket_roger():
    cas = convert("rocket_roger.cas")
    assert len(cas) == 4


def test_special_operations():
    cas = convert("special_operations.cas")
    assert cas[0].type == "ascii"
    assert cas[1].type == "basic"
    assert cas[2].type == "binary"
    assert cas[3].type == "basic"
    assert len(cas) == 4


def test_speed_king():
    cas = convert("speed_king.cas")
    assert cas[0].type == "ascii"
    assert len(cas) == 3


def test_ultra_chess():
    cas = convert("ultra_chess.cas")
    assert cas[0].type == "ascii"
    assert len(cas) == 2


def test_vestron():
    cas = convert("vestron.cas")
    assert cas[0].type == "binary"
    assert len(cas) == 1


def test_xyzolog():
    cas = convert("xyzolog.cas")
    assert cas[0].type == "binary"
    assert len(cas) == 1


def test_athletic_land():
    cas = convert_rom("athletic_land.rom")
    assert cas[0].type == "ascii"
    assert len(cas[0].title) == 6
    assert cas[1].type == "binary"
    assert len(cas[1].title) == 6
    assert len(cas) == 2


def test_road_fighter():
    cas = convert_rom("road_fighter.mx1")
    assert cas[0].type == "ascii"
    assert len(cas[0].title) == 6
    assert cas[1].type == "binary"
    assert len(cas[1].title) == 6
    assert len(cas) == 2


def test_rom_title_from_filename():
    cas = convert_rom("champion_billiards.rom")
    assert b'PRINT"CHAMPION BILLIARDS"' in cas[0].dati

    cas = convert_rom("athletic_land.rom")
    assert b'PRINT"ATHLETIC LAND"' in cas[0].dati
    assert b"CHAMPION BILLIARDS" not in cas[0].dati
    assert b"SEGA" not in cas[0].dati


def test_rom_32k(tmp_path):
    rom = tmp_path / "big_game.rom"
    rom.write_bytes(bytes(32768))
    cas = msxtools.Tape(str(rom))
    assert len(cas) == 3
    assert cas[1].type == "binary"
    assert cas[2].type == "binary"


@pytest.mark.parametrize("size", [49153, 65536])
def test_rom_too_big(tmp_path, size):
    rom = tmp_path / "huge_game.rom"
    rom.write_bytes(bytes(size))
    with pytest.raises(msxtools.Eccezione, match="only ROMs up to 48KB"):
        msxtools.Tape(str(rom))


def test_rom_48k(tmp_path):
    pagine = [bytes([0x10]) * 16384, b"AB" + bytes([0x11]) * 16382, bytes([0x12]) * 16384]
    rom = tmp_path / "game48.rom"
    rom.write_bytes(b"".join(pagine))
    cas = msxtools.Tape(str(rom))

    assert len(cas) == 4
    # Ordine di caricamento: pagina 1, pagina 0, pagina 2 (che avvia il gioco)
    for blocco, pagina, loader in zip(cas[1:], [pagine[1], pagine[0], pagine[2]],
                                      [Loader.binari_32k_4000h, Loader.binari_48k_0000h,
                                       Loader.binari_48k_8000h]):
        assert blocco.dati == pagina + loader
        assert blocco.indirizzo_iniziale.valore == 0x9000
        assert blocco.indirizzo_esecuzione.valore == 0xD000


@pytest.mark.parametrize("size", [32769, 49152])
def test_rom_48k_without_header_at_4000h(tmp_path, size):
    rom = tmp_path / "game48.rom"
    rom.write_bytes(b"AB" + bytes(size - 2))
    with pytest.raises(msxtools.Eccezione, match="mapped at 0000h-BFFFh"):
        msxtools.Tape(str(rom))


# --=-=--------------------------------------------------------------------------=-=--
# Regressioni

HEADER = Intestazioni.blocco_intestazione
DATI_BINARIO = bytes([0x00, 0x90, 0x04, 0x90, 0x00, 0x90]) + b"abcde"


class FintaEsportazione:
    """Registra i byte scritti, un elenco per ogni segnale di sincronismo"""

    def __init__(self):
        self.segmenti = []

    def inserisci_sincronismo(self, p_durata):
        self.segmenti.append([])

    def inserisci_stringa(self, p_stringa):
        self.segmenti[-1].extend(p_stringa)

    def inserisci_byte(self, p_byte):
        self.segmenti[-1].append(p_byte)

    def inserisci_silenzio(self, p_durata):
        pass


def _blocchi(p_buffer):
    ricerca = Ricerca()
    ricerca.buffer = p_buffer
    blocchi = []
    while not ricerca.eof():
        blocchi.append(ricerca.ricerca_blocco())
    return blocchi


@pytest.mark.parametrize("size", [8192, 16384, 32768])
def test_rom_exec_address_points_to_loader(tmp_path, size):
    rom = tmp_path / "game.rom"
    rom.write_bytes(bytes([0xAA]) * size)
    cas = msxtools.Tape(str(rom))

    for blocco in cas[1:]:
        inizio = blocco.indirizzo_iniziale.valore
        esecuzione = blocco.indirizzo_esecuzione.valore
        # I loader copiano la ROM da 0x9000 e sono accodati subito dopo la ROM
        assert inizio == 0x9000
        assert esecuzione == inizio + min(size, 16384)
        assert blocco.dati[esecuzione - inizio] == 0xF3  # DI, prima istruzione del loader


@pytest.mark.parametrize("size", [256, 600, 1000])
def test_ascii_export_segments_are_256_bytes(size):
    blocco = AsciiFile()
    blocco.title = "TEST"
    blocco.dati = b"A" * (size - 1) + b"\x1a"

    finta = FintaEsportazione()
    blocco.esporta(finta)

    dati = finta.segmenti[1:]  # il primo è l'intestazione del file
    assert all(len(segmento) == 256 for segmento in dati)
    assert bytes(sum(dati, []))[:size] == blocco.dati


def test_truncated_ascii_tape_does_not_hang():
    def scaduto(*_):
        raise TimeoutError("ricerca_blocco non termina")

    precedente = signal.signal(signal.SIGALRM, scaduto)
    signal.alarm(5)
    try:
        blocchi = _blocchi(HEADER + AsciiFile.intestazione + b"TEST  " + HEADER + b"10 PRINT 1\r\n")
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, precedente)

    assert blocchi[0].type == "ascii"
    assert blocchi[0].dati == b"10 PRINT 1\r\n"


def test_non_ascii_title_round_trip():
    blocco, = _blocchi(HEADER + BinaryFile.intestazione + b"GAM\xe9  " + HEADER + DATI_BINARIO)
    assert blocco.type == "binary"
    assert blocco.titolo_in_bytes() == b"GAM\xe9  "


def test_rom_with_non_ascii_name(tmp_path):
    rom = tmp_path / "città.rom"
    rom.write_bytes(bytes(16384))
    cas = msxtools.Tape(str(rom))
    cas.export_to_wav(str(tmp_path / "citta.wav"))
    assert b'PRINT"CITTA"' in cas[0].dati


def test_junk_before_first_header():
    blocchi = _blocchi(b"JUNK" + HEADER + BinaryFile.intestazione + b"GAME  " + HEADER + DATI_BINARIO)
    assert [blocco.type for blocco in blocchi] == ["custom", "binary"]
    assert blocchi[0].dati == b"JUNK"
    assert blocchi[1].dati == b"abcde"


def test_header_without_data():
    blocco, = _blocchi(HEADER + BinaryFile.intestazione + b"GAME  ")
    assert blocco.type == "binary"
    assert blocco.title == "GAME  "
    assert len(blocco) == 0


def test_invalid_tape_message(tmp_path):
    with pytest.raises(msxtools.Eccezione, match="Unable to read tape"):
        msxtools.Tape(str(tmp_path / "missing.cas"))


def test_rimuovi():
    cas = msxtools.Tape(os.path.join(HERE, "assets", "tapes", "congo.cas"))
    secondo = cas[1]
    cas.rimuovi(0)
    assert len(cas) == 3
    assert cas[0] is secondo
    with pytest.raises(msxtools.Eccezione):
        cas.rimuovi(10)


def test_export_with_explicit_current_bitrate(tmp_path):
    # Alla prima esportazione le forme d'onda devono essere calcolate
    # anche se il bitrate richiesto è quello già impostato
    from msxtools.datablocks.wav.parametri import Parametri
    Parametri.wave_bit_0 = []
    Parametri.wave_bit_1 = []
    Parametri.wave_silenzio = []

    file_wav = tmp_path / "bit.wav"
    suono = Esportazione(str(file_wav), Parametri.bitrate)
    suono.inserisci_byte(0x55)
    suono.chiudi()

    with wave.open(str(file_wav)) as w:
        assert w.getnframes() > 0


def test_wav_starts_and_ends_with_silence(tmp_path):
    # Il file non deve finire esattamente con l'ultimo bit, altrimenti gli
    # emulatori lo considerano troncato
    cas = msxtools.Tape(os.path.join(HERE, "assets", "tapes", "barnstormer.cas"))
    file_wav = tmp_path / "bordi.wav"
    cas.export_to_wav(str(file_wav))

    with wave.open(str(file_wav)) as w:
        # Il silenzio è arrotondato per eccesso: dura almeno pausa_ai_bordi
        bordo = math.ceil(w.getframerate() * Esportazione.pausa_ai_bordi / 1000)
        assert set(w.readframes(bordo)) == {128}
        w.setpos(w.getnframes() - bordo)
        assert set(w.readframes(bordo)) == {128}


@pytest.mark.parametrize("size, totale", [(8192, 1), (16384, 1), (32768, 2), (49152, 3)])
def test_rom_loader_shows_progress_bar(tmp_path, size, totale):
    dati = bytearray(size)
    if size > 32768:
        dati[0x4000:0x4002] = b"AB"
    rom = tmp_path / "game.rom"
    rom.write_bytes(bytes(dati))
    cas = msxtools.Tape(str(rom))

    # Un blocco binario per ogni parte, e il loader BASIC le conta tutte
    assert len(cas) == totale + 1
    basic = cas[0].dati

    # Schermata centrata verticalmente: titolo e "NOW LOADING" sulle righe 4 e 5,
    # barra sulla 12 e percentuali sulla 13, crediti sulla 19 senza a capo
    assert b',4:PRINT"GAME"\r\n' in basic
    assert b',5:PRINT"NOW LOADING - PLEASE WAIT":' in basic
    assert b',7:PRINT"Estimated wait time:":' in basic
    assert b',19:PRINT"(C) 2016-20 MASTROPIERO";\r\n' in basic

    # Barra vuota centrata sulla riga 16, poi il primo BLOAD
    # con sotto le percentuali: 0% all'inizio, 50% a metà, 100% alla fine
    assert b'5 LOCATE7,12:PRINT"[........................]";:LOCATE8,13:PRINT"0%         50%      100%";\r\n' \
           b'6 BLOAD"cas:",R\r\n' in basic

    # Nessun ciclo: una riga per ogni parte successiva, che riempie 12 / parti caselle
    # con CHR$(219) e carica subito la parte seguente
    riempimento = 24 // totale
    for parte in range(1, totale):
        riga = "{0} LOCATE{1},12:PRINT\"".format(6 + parte, 8 + (parte - 1) * riempimento).encode() \
               + b"\xdb" * riempimento + b'";:BLOAD"cas:",R\r\n'
        assert riga in basic
    assert b"FOR" not in basic
    assert basic.count(b'BLOAD"cas:",R') == totale
    assert basic.rstrip(b"\x00").endswith(b"\r\n\x1a")


def _barra_dopo_ogni_parte(p_basic):
    """Esegue a mano le righe della barra e restituisce la barra dopo ogni parte caricata"""
    import re
    barra = list("[" + "." * 24 + "]")
    stati = []
    for riga in re.findall(rb"^\d+ (?:LOCATE(\d+),12:PRINT\"(\xdb+)\";:)?BLOAD", p_basic, re.M)[1:]:
        colonna, piene = riga
        if colonna:
            for k in range(len(piene)):
                barra[int(colonna) - 7 + k] = "#"
        stati.append("".join(barra))
    return stati


@pytest.mark.parametrize("parti, attese", [
    (1, []),
    (2, ['[############............]']),
    (3, ['[########................]', '[################........]']),
    (4, ['[######..................]', '[############............]', '[##################......]']),
    # ROM da 128Kb: 8 parti da 16Kb, 3 caselle ciascuna
    (8, ['[###.....................]', '[######..................]', '[#########...............]', '[############............]', '[###############.........]', '[##################......]', '[#####################...]']),
])
def test_loader_progress_bar_parts(parti, attese):
    basic = msxtools.Tape.programma_basic(b"GAME", b"2026 DEV", parti)
    assert basic.count(b'BLOAD"cas:",R') == parti
    assert _barra_dopo_ogni_parte(basic) == attese


def test_loader_progress_bar_more_parts_than_cells():
    basic = msxtools.Tape.programma_basic(b"GAME", b"2026 DEV", 32)
    assert basic.count(b'BLOAD"cas:",R') == 32
    stati = _barra_dopo_ogni_parte(basic)
    assert len(stati) == 31
    assert stati[-1] == "[" + "#" * 23 + ".]"


def test_loader_progress_bar_limits():
    with pytest.raises(msxtools.Eccezione, match="at least 1 block"):
        msxtools.Tape.programma_basic(b"GAME", b"2026 DEV", 0)


def test_loader_percentages_under_bar():
    import re
    basic = msxtools.Tape.programma_basic(b"GAME", b"2026 DEV", 2)
    riga_barra = re.search(rb'LOCATE(\d+),12:PRINT"(\[[^"]*\])"', basic)
    riga_perc = re.search(rb'LOCATE(\d+),13:PRINT"([^"]*)"', basic)

    schermo = {12: [" "] * 40, 13: [" "] * 40}
    for riga, m in ((12, riga_barra), (13, riga_perc)):
        for k, c in enumerate(m[2].decode()):
            schermo[riga][int(m[1]) + k] = c
    barra, perc = "".join(schermo[12]), "".join(schermo[13])

    prima, ultima = barra.index("[") + 1, barra.index("]") - 1
    meta = (prima + ultima + 1) // 2  # prima casella della seconda metà
    assert perc.index("0%") == prima
    assert perc.index("50%") == meta - 1
    assert perc.index("100%") + 3 == ultima


def test_loader_screen_vertically_centered():
    import re
    basic = msxtools.Tape.programma_basic(b"GAME", b"2026 DEV", 2)
    righe = sorted({int(r) for r in re.findall(rb"LOCATE\d+,(\d+):PRINT", basic)})
    # Righe libere sopra e sotto il testo sulle 24 dello schermo
    assert righe[0] == 23 - righe[-1]


def test_loader_screen_horizontally_centered():
    import re
    basic = msxtools.Tape.programma_basic(b"GAME", b"2026 DEV", 2)
    for colonna, testo in re.findall(rb'LOCATE(\d+),\d+:PRINT"([^"]*)"', basic)[:4]:
        # Colonne libere a sinistra e a destra sulle 40 di WIDTH 40 (al massimo 1 di differenza)
        sinistra = int(colonna)
        destra = 40 - sinistra - len(testo)
        assert destra - sinistra in (0, 1), testo

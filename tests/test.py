import os
import msxtools


def convert(p_file):
    filename = os.path.join(os.getcwd(), "assets", "tapes", p_file)
    cas = msxtools.Tape(filename)
    print(cas)
    cas.export_to_wav(os.path.join(os.path.dirname(__file__), "output", "output.wav"))

    return cas


def convert_rom(p_file):
    filename = os.path.join(os.getcwd(), "assets", "roms", p_file)
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

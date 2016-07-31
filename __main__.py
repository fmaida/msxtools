#!/usr/bin/env python

import os

import msx
from ui import Ui


def get_rom(p_file):
    return os.path.join(os.getcwd(), "roms", p_file)


def get_output(p_file=""):
    return os.path.join(os.getcwd(), "output", p_file)


if __name__ == '__main__':

    """

    # Test

    from cronometro import Cronometro

    # --=-=--------------------------------------------------------------------------=-=--

    # Cronometro.reset()

    mia_cassetta = msx.Cassetta()

    try:
        # mia_cassetta.load(os.getcwd() + "/tapes/ROADF.CAS")
        # mia_cassetta.load(os.getcwd() + "/tapes/berretti_verdi.cas")
        # mia_cassetta.load(os.getcwd() + "/tapes/guttblaster.cas")
        # mia_cassetta.load(os.getcwd() + "/tapes/lazy_jones.cas")
        # mia_cassetta.load(os.getcwd() + "/tapes/pacmania.cas")
        # mia_cassetta.load(os.getcwd() + "/tapes/chase_hq_lato_a.cas")
        # mia_cassetta.load(os.getcwd() + "/tapes/boulder_dash.cas")
        # mia_cassetta.load(os.getcwd() + "/tapes/introduzione_al_basic.cas")
        # mia_cassetta.load(os.getcwd() + "/tapes/msx_computer_magazine_06.cas")
        # mia_cassetta.load(os.getcwd() + "/tapes/Shamus.cas")
        # mia_cassetta.load(os.getcwd() + "/tapes/NV08B.CAS")

        # ROM da 8kb
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/super_cobra.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/super_snake.rom")

        # ROM da 16kb
        # mia_cassetta.importa_rom(get_rom("athletic_land.rom"))
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/road_fighter.rom")

        # ROM da 32kb
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/brother_adventure.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/block_hole.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/elevator_action.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/flashpoint.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/superboy.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/wonderboy.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/thexder.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/tritorn.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/twinbee.rom")

    # except msx.Eccezione as ex:
    #    print("Whoops... something went wrong:\n{}".format(ex))

    print(Cronometro.verifica())

    print(mia_cassetta)

    """


    """
    # print("{0}\n----------------------------------\n{1} Bytes\n\n"
    #       .format(mia_cassetta.cassetta[0].dati, len(mia_cassetta.cassetta[0])))

    # print(mia_cassetta.cassetta[1].dati) # 0x9000,0xd1a3, 0xd000

    mia_cassetta.cassetta[0].titolo = "game1"
    # mia_cassetta.cassetta[0].esporta_file(get_output())

    # mia_cassetta.cassetta[1].titolo = "game2"
    # mia_cassetta.cassetta[1].esporta_file(os.path.join(os.getcwd(), "export"))

    mia_cassetta.esporta(get_output("output.wav"))

    print(Cronometro.verifica())
    """

    # ui = Ui()
    # ui.cmdloop()

    cas = msx.Cassetta()
    cas.load(os.getcwd() + "/tapes/puf_puf.cas")
    print(cas)
    cas.cassetta[2].esporta_file(get_output())
    # esporta("output.wav")

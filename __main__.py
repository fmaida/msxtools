import os

import msxtape
#from ui import Ui
#from cronometro import Cronometro


def get_rom(p_file):
    return os.path.join(os.getcwd(), "roms", p_file)


def get_output(p_file=""):
    return os.path.join(os.getcwd(), "output", p_file)


if __name__ == '__main__':

    # Test

    # --=-=--------------------------------------------------------------------------=-=--

    mia_cassetta = msxtools.Cassetta()

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
        mia_cassetta.importa_rom(os.getcwd() + "/roms/athland.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/brother_adventure.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/block_hole.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/elevator_action.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/flashpoint.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/superboy.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/wonderboy.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/thexder.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/tritorn.rom")
        # mia_cassetta.importa_rom(os.getcwd() + "/roms/twinbee.rom")

    except msxtools.Eccezione as ex:
    	print("Whoops... something went wrong:\n{}".format(ex))

    #print(Cronometro.verifica())

    print(mia_cassetta)
    mia_cassetta.esporta(get_output("output.wav"))
    quit()
    
    # print("{0}\n----------------------------------\n{1} Bytes\n\n"
    #       .format(mia_cassetta.cassetta[0].dati, len(mia_cassetta.cassetta[0])))

    # print(mia_cassetta.cassetta[1].dati) # 0x9000,0xd1a3, 0xd000

    #mia_cassetta._cassetta[1].titolo = "game1"
    #mia_cassetta._cassetta[1].esporta_file(os.path.join(os.getcwd(), "output"))

    #mia_cassetta._cassetta[2].titolo = "game2"
    #mia_cassetta._cassetta[2].esporta_file(os.path.join(os.getcwd(), "output"))

    #mia_cassetta.esporta(get_output("output.wav"))

    #print(Cronometro.verifica())
    

    # ui = Ui()
    # ui.cmdloop()
    
    #Cronometro.reset()

    # cas = msx.Cassetta()
    # cas.load(os.getcwd() + "/tapes/guttblaster.cas")
    # cas.importa_rom(os.getcwd() + "/roms/block_hole.rom")
    # print(cas)
    # print(str(cas._cassetta[0].dati))
    # print(str(len(cas._cassetta[0].dati)))
    # print(str(cas._cassetta[1].esporta_file (get_output())))
    # print(str(cas.cassetta[2].dati))
    # print(str(cas.cassetta[136].dati))
    # cas.esporta(get_output("output.wav"))
    # esporta("output.wav")

    # print(Cronometro.verifica())

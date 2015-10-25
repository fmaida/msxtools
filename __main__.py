#!/usr/bin/env python

import os

import msx


if __name__ == '__main__':

	# Test

	from cronometro import Cronometro

	# --=-=--------------------------------------------------------------------------=-=--

	Cronometro.reset()

	"""
	# Legge il file dal disco
	f = open(os.getcwd() + "/initgame/rloader.bin", "rb")
	buffer = f.read()
	f.close()
	print(buffer)
	print()
	# print(buffer[7:])
	quit()
	"""

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

		# blocco.importa(os.getcwd() + "/roms/super_cobra.rom")
		programma = "10 SCREEN 2 : CLS : KEY OFF\r\n20 PRINT \"GAME IS LOADING - www.ka7.eu\"\r\n30 BLOAD\"CAS:\",R\r\n40 BLOAD\"CAS:\",R\r\n"
		#mia_cassetta.importa_ascii("LOADER", programma)
		mia_cassetta.importa_rom(os.getcwd() + "/roms/antarctic_adventure.rom")

	except msx.Eccezione as ex:
		print("Whoops... something went wrong:\n{}".format(ex))


	print(Cronometro.verifica())

	print(mia_cassetta)

	# print("{0}\n----------------------------------\n{1} Bytes\n\n".format(mia_cassetta.cassetta[0].dati, len(mia_cassetta.cassetta[0])))

	# print(mia_cassetta.cassetta[1].dati) # 0x9000,0xd1a3, 0xd000

	mia_cassetta.cassetta[0].esporta_file(os.path.join(os.getcwd(), "export"))

	# mia_cassetta.esporta_wav()

	print(Cronometro.verifica())

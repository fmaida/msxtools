#!/usr/bin/env python

import os

import msx


if __name__ == '__main__':

	# Test

	from cronometro import Cronometro

	# --=-=--------------------------------------------------------------------------=-=--

	Cronometro.reset()

	mia_cassetta = msx.Cassetta()
	try:
		# mia_cassetta.load(os.getcwd() + "/tapes/berretti_verdi.cas")
		# mia_cassetta.load(os.getcwd() + "/tapes/guttblaster.cas")
		# mia_cassetta.load(os.getcwd() + "/tapes/lazy_jones.cas")
		mia_cassetta.load(os.getcwd() + "/tapes/pacmania.cas")
	 	# mia_cassetta.load(os.getcwd() + "/tapes/chase_hq_lato_a.cas")
		# mia_cassetta.load(os.getcwd() + "/tapes/boulder_dash.cas")
		# mia_cassetta.load(os.getcwd() + "/tapes/introduzione_al_basic.cas")
		# mia_cassetta.load(os.getcwd() + "/tapes/msx_computer_magazine_06.cas")
		# mia_cassetta.load(os.getcwd() + "/tapes/Shamus.cas")
		# mia_cassetta.load(os.getcwd() + "/tapes/NV08B.CAS")
	except msx.Eccezione as ex:
		print("Whoops... something went wrong:\n{}".format(ex))


	print(Cronometro.verifica())

	print(mia_cassetta)

	#print("{0}\n----------------------------------\n{1} Bytes\n\n".format(mia_cassetta.cassetta[0].dati, len(mia_cassetta.cassetta[0])))

	mia_cassetta.esporta()

	print(Cronometro.verifica())

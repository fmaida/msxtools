#!/usr/bin/env python

import os

import msx


if __name__ == '__main__':

	# Test

	import time

	start_time = time.time()

	mia_cassetta = msx.Cassetta()
	try:
		# mia_cassetta.load(os.getcwd() + "/tapes/introduzione_al_basic.cas")
		mia_cassetta.load(os.getcwd() + "/tapes/ROADF.CAS")
		# mia_cassetta.load(os.getcwd() + "/tapes/Shamus.cas")
		# mia_cassetta.load(os.getcwd() + "/tapes/NV08B.CAS")
	except msx.Eccezione as ex:
		print("Whoops... something went wrong:\n{}".format(ex))


	print()
	print(mia_cassetta)

	print("{0}\n----------------------------------\n{1} Bytes\n\n".format(mia_cassetta.cassetta[0].dati, len(mia_cassetta.cassetta[0])))

	print("--- {0:.3} seconds ---".format(time.time() - start_time))

	mia_cassetta.esporta()

	print("--- {0:.3} seconds ---".format(time.time() - start_time))
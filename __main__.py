#!/usr/bin/env python

import os

import msx

mia_cassetta = msx.Cassetta()
try:
    mia_cassetta.load(os.getcwd() + "/tapes/msx_computer_magazine_06.cas")
    # mia_cassetta.load(os.getcwd() + "/tapes/ROADF.CAS")
    # mia_cassetta.load(os.getcwd() + "/tapes/Shamus.cas")
    # mia_cassetta.load(os.getcwd() + "/tapes/NV08B.CAS")
except msx.Eccezione as ex:
    print("Whoops... something went wrong:\n{}".format(ex))

print()
print(mia_cassetta)
mia_cassetta.esporta()

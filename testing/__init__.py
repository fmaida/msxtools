import os
import unittest

import msx


class MieiTest(unittest.TestCase):

    def converti_cassetta(self, p_file):
        cas = msx.Cassetta()
        cas.load(os.path.join(os.getcwd(), "..", "tapes", p_file))
        cas.esporta()

        return cas

    def test_conversione_01(self):
        cas = self.converti_cassetta("avventura_citta.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 1)

    def test_conversione_02(self):
        cas = self.converti_cassetta("batman_the_movie_lato_a.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 16)

    def test_conversione_03(self):
        cas = self.converti_cassetta("batman_the_movie_lato_b.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 9)

    def test_conversione_04(self):
        cas = self.converti_cassetta("berretti_verdi.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 19)

    def test_conversione_05(self):
        cas = self.converti_cassetta("boulder_dash.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 10)

    def test_conversione_06(self):
        cas = self.converti_cassetta("chase_hq_lato_a.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 15)

    def test_conversione_07(self):
        cas = self.converti_cassetta("chase_hq_lato_b.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 12)

    def test_conversione_08(self):
        cas = self.converti_cassetta("guttblaster.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 11)

    def test_conversione_09(self):
        cas = self.converti_cassetta("introduzione_al_basic.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 54)

    def test_conversione_10(self):
        cas = self.converti_cassetta("lazy_jones.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 7)

    def test_conversione_11(self):
        cas = self.converti_cassetta("msx_computer_magazine_06.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 11)

    def test_conversione_12(self):
        cas = self.converti_cassetta("msx_computer_magazine_12.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 13)

    def test_conversione_13(self):
        cas = self.converti_cassetta("NV08B.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 140)

    def test_conversione_14(self):
        cas = self.converti_cassetta("pacmania.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 6)

    def test_conversione_15(self):
        cas = self.converti_cassetta("puf_puf.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 3)

    def test_conversione_16(self):
        cas = self.converti_cassetta("wec_le_mans.cas")
        print(str(cas) + "\n")
        self.assertEqual(len(cas), 4)

import os
import unittest

import msxtools


class MSXTests(unittest.TestCase):

    @staticmethod
    def convert(p_file):
        filename = os.path.join(os.getcwd(), "tests", "assets", "tapes", p_file)
        cas = msxtools.Tape(filename)
        print(cas)
        # cas.export_to_wav()

        return cas

    @staticmethod
    def convert_rom(p_file):
        filename = os.path.join(os.getcwd(), "tests", "assets", "roms", p_file)
        cas = msxtools.Tape(filename)
        print(cas)
        # cas.export_to_wav()

        return cas

    def test_barnstormer(self):
        cas = self.convert("barnstormer.cas")
        self.assertEqual(len(cas), 2)

    def test_brian_jacks(self):
        cas = self.convert("brian_jacks_superstar.cas")
        self.assertIn("ASCII", str(cas[0]))
        self.assertEqual(len(cas), 3)

    def test_chuckie_egg(self):
        cas = self.convert("chuckie_egg.cas")
        self.assertIn("Binary", str(cas[0]))
        self.assertEqual(len(cas), 2)

    def test_city_connection(self):
        cas = self.convert("city_connection.cas")
        self.assertIn("ASCII", str(cas[0]))
        self.assertEqual(len(cas), 5)

    def test_congo(self):
        cas = self.convert("congo.cas")
        self.assertIn("ASCII", str(cas[0]))
        self.assertIn("Binary", str(cas[1]))
        self.assertEqual(len(cas), 4)

    def test_disc_warrior(self):
        cas = self.convert("disc_warrior.cas")
        self.assertEqual(len(cas), 3)

    def test_hustler(self):
        cas = self.convert("hustler.cas")
        self.assertEqual(len(cas), 1)

    def test_kuma_logo(self):
        cas = self.convert("kuma_logo.cas")
        self.assertIn("Basic", str(cas[0]))
        self.assertEqual(len(cas), 1)

    def test_le_mans(self):
        cas = self.convert("le_mans.cas")
        self.assertEqual(len(cas), 2)

    def test_les_flics(self):
        cas = self.convert("les_flics.cas")
        self.assertEqual(len(cas), 3)

    def test_rocket_roger(self):
        cas = self.convert("rocket_roger.cas")
        self.assertEqual(len(cas), 4)

    def test_special_operations(self):
        cas = self.convert("special_operations.cas")
        self.assertIn("ASCII", str(cas[0]))
        self.assertIn("Basic", str(cas[1]))
        self.assertIn("Binary", str(cas[2]))
        self.assertIn("Basic", str(cas[3]))
        self.assertEqual(len(cas), 4)

    def test_speed_king(self):
        cas = self.convert("speed_king.cas")
        self.assertIn("ASCII", str(cas[0]))
        self.assertEqual(len(cas), 3)

    def test_ultra_chess(self):
        cas = self.convert("ultra_chess.cas")
        self.assertIn("ASCII", str(cas[0]))
        self.assertEqual(len(cas), 2)

    def test_vestron(self):
        cas = self.convert("vestron.cas")
        self.assertIn("Binary", str(cas[0]))
        self.assertEqual(len(cas), 1)

    def test_xyzolog(self):
        cas = self.convert("xyzolog.cas")
        self.assertIn("Binary", str(cas[0]))
        self.assertEqual(len(cas), 1)

    def test_athletic_land(self):
        cas = self.convert_rom("athletic_land.rom")
        self.assertIn("ASCII", str(cas[0]))
        self.assertIn("Binary", str(cas[1]))
        self.assertEqual(len(cas), 2)

    def test_road_fighter(self):
        cas = self.convert_rom("road_fighter.mx1")
        self.assertIn("ASCII", str(cas[0]))
        self.assertIn("Binary", str(cas[1]))
        self.assertEqual(len(cas), 2)

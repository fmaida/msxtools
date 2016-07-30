import cmd
from os import getcwd, listdir
from os.path import join, isdir

import msx
from msx.wav.parametri import Parametri


class Ui(cmd.Cmd):

    prompt = ">>> "

    def __init__(self):
        super().__init__()
        self.cassetta = msx.Cassetta()
        self.directory = getcwd()

    def do_cd(self, p_dir=""):

        if p_dir == "":
            print(self.directory)
        else:
            self.directory = join(self.directory, p_dir)

    def do_ls(self, p_dir=""):

        if p_dir == "":
            p_dir = self.directory
        else:
            p_dir = join(self.directory, p_dir)

        for file in listdir(p_dir):
            if file.endswith(".cas") or \
                    file.endswith(".bin") or \
                    file.endswith(".asc") or \
                    file.endswith(".bas") or \
                    file.endswith(".rom"):
                print(file)
            elif isdir(file):
                if not file.startswith("."):
                    print(file + "/")

        print()

    def do_open(self, p_file):
        # try:
            if p_file.endswith(".cas"):
                self.cassetta.load(join(self.directory, p_file))
                print(self.cassetta)
            elif p_file.endswith(".rom"):
                self.cassetta.importa_rom(join(self.directory, p_file))
                print("ROM '{0}' has been loaded".format(p_file))
        # except msx.Eccezione as e:
        #    print("Fatal error: " + str(e.parameter))

    def do_bitrate(self, p_valore):
        try:
            p_valore = int(p_valore)
            if p_valore >= 0:
                if p_valore < 600 or p_valore > 4800:
                    print("You must provide a bitrate value between 600bps and 4800bps")
                else:
                    Parametri.modifica_bitrate(p_valore)
            else:
                print("{0}bps".format(Parametri.bitrate))
        except:
            print("{0}bps".format(Parametri.bitrate))
            pass

    def do_export(self, p_file):

        if p_file.endswith(".wav"):
            self.cassetta.esporta(join(self.directory, p_file))
            print("File exported as {0} at {1}bps".format(p_file, Parametri.bitrate))
        else:
            print("I don't know what to do with {0}".format(p_file))

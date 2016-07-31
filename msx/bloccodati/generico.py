from ..intestazioni import Intestazioni
from ..tipi import TipiDiBlocco
from ..wav import Esportazione


class BloccoDati:
    """
    Questa classe gestisce la struttura di un blocco delle cassette MSX.
    Un blocco può contenere un file di tipo ASCII, Binario, Basic o custom.
    """

    intestazione = b""

    # --=-=--------------------------------------------------------------------------=-=--

    def __init__(self, p_titolo="", p_dati=""):
        """
        Costruttore della classe

        Returns:
            None
        """
        self._titolo = ""
        self.titolo = p_titolo  # Titolo del file
        self._dati = b""
        self.dati = p_dati  # Dati che compongono il file memorizzato

    # --=-=--------------------------------------------------------------------------=-=--

    @property
    def titolo(self):
        return self._titolo

    @titolo.setter
    def titolo(self, titolo):
        if len(titolo) > 6:
            titolo = titolo[0:6]
        self._titolo = titolo.ljust(6, " ")

    # --=-=--------------------------------------------------------------------------=-=--

    @property
    def dati(self):
        return self._dati

    @dati.setter
    def dati(self, p_valore):
        self._dati = p_valore

    # --=-=--------------------------------------------------------------------------=-=--

    def esporta(self, p_file: Esportazione):
        pass

    # --=-=--------------------------------------------------------------------------=-=--

    def __len__(self):
        """
        Restituisce la lunghezza di un blocco dati

        Returns:
            La lunghezza del blocco dati
        """
        return len(self.dati)

    # --=-=--------------------------------------------------------------------------=-=--

    def __str__(self):
        """
        Offre una rappresentazione visuale del blocco dati

        Returns:
            Una stringa di testo
        """

        tipo = self.__class__.__name__
        if tipo == "FileAscii":
            tipo = "ASCII"
        elif tipo == "FileBasic":
            tipo = "Basic"
        elif tipo == "FileBinario":
            tipo = "Binary"
        else:
            tipo = "Custom"

        if self.titolo != "":
            temp = "\"{0}\" ({1})  [ {2} Bytes ] ".format(self.titolo, tipo.ljust(6), str(len(self.dati)).rjust(6))
        else:
            temp = "{0} ({1})  [ {2} Bytes ]".format(8 * " ", tipo.ljust(6), str(len(self.dati)).rjust(6))
        return temp

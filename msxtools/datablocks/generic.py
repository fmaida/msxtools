from ..intestazioni import Intestazioni
from ..tipi import TipiDiBlocco
from ..wav import Esportazione


class GenericDataBlock:
    """
    Questa classe gestisce la struttura di un blocco delle cassette MSX.
    Un blocco può contenere un file di tipo ASCII, Binario, Basic o custom.
    """

    intestazione = b""

    # --=-=--------------------------------------------------------------------------=-=--

    @property
    def type(self):
        return "generic"

    @property
    def title(self):
        return self._titolo

    @title.setter
    def title(self, titolo):
        if len(titolo) > 6:
            titolo = titolo[0:6]
        self._titolo = titolo.ljust(6, " ")

    @property
    def dati(self):
        return self._dati

    @dati.setter
    def dati(self, p_valore):
        self._dati = p_valore

    # --=-=--------------------------------------------------------------------------=-=--

    def __init__(self, p_titolo="", p_dati=""):
        """
        Costruttore della classe

        Returns:
            None
        """
        self._titolo = ""
        self.title = p_titolo  # Titolo del file
        self._dati = b""
        self.dati = p_dati  # Dati che compongono il file memorizzato

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
        if tipo == "AsciiFile":
            tipo = "ASCII"
        elif tipo == "BasicFile":
            tipo = "Basic"
        elif tipo == "BinaryFile":
            tipo = "Binary"
        else:
            tipo = "Custom"

        file_length = "{:,}".format(len(self.dati))

        if tipo != "Custom":
            temp = "\"{0}\" ( {1} )  [ {2} Bytes ] ".format(self.title,
                                                            self.type.capitalize().ljust(6),
                                                            file_length.rjust(7))
        else:
            temp = "( Data Block )".ljust(21) + "[ {} Bytes ]".format(file_length.rjust(7))
        return temp

    # --=-=--------------------------------------------------------------------------=-=--

    def __add__(self, p_altro_blocco):
        """
        Aggiunge altri dati in coda al blocco

        Args:
            p_altro_blocco: L'altro blocco con i dati da aggiungere

        Returns:
            Se stesso
        """
        self.dati += p_altro_blocco.dati
        return self

import os

# from .intestazioni import Intestazioni
from .bloccodati import FileBinario, FileAscii
from .loader import Loader
from .eccezioni import Eccezione
from .ricerche import Ricerca
from .wav import Esportazione


class Tape:
    """
    _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_
    MSX TAPE class - Reads and writes on a virtual tape file (.CAS)
    Version 1.0
    _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_
    """

    # --=-=--------------------------------------------------------------------------=-=--

    def __init__(self, p_file: str = None):
        """
        Costruttore della classe

        Returns:
            None
        """

        # Inizializza i vari array, per partire con una nuova cassetta
        self._cassetta = []  # Array che contiene i blocchi di dati che compongono la cassetta
        self._ricerca = Ricerca()  # Buffer dati in cui immagazzina temporaneamente il file .cas da analizzare
        self.indice = -1
        self.posizione = -1
        self._ricerca = Ricerca()

        if p_file:
            if p_file.lower().endswith('.rom') or \
               p_file.lower().endswith('.mx1'):
                self.importa_rom(p_file)
            else:
                self.load(p_file)

    # --=-=--------------------------------------------------------------------------=-=--

    def load(self, p_file):
        """
        Carica un file cas in memoria

        Args:
            p_file:	Il percorso al file .CAS da caricare

        Returns:

        """

        #try:

        # Legge il file .CAS dal disco
        f = open(p_file, "rb")
        self._ricerca.buffer = f.read()
        # self.posizione = -1
        f.close()

        # Finchè resta qualcosa nel buffer da analizzare...
        while not self._ricerca.eof():
            # Con quello che gli rimane del buffer va alla ricerca del
            # primo blocco che riesce a trovare
            blocco = self._ricerca.ricerca_blocco()

            # Aggiunge il blocco che ha trovato alla cassetta
            self._cassetta.append(blocco)

        #except:
        #    raise Eccezione("Unable to find any tape called \"{0}\"".format(p_file))

    # --=-=--------------------------------------------------------------------------=-=--

    def aggiungi(self, p_blocco):
        """
        Aggiunge un nuovo blocco-dati alla cassetta

        Args:
          p_blocco: I dati effettivi del blocco

        Returns:
            None
        """
        self._cassetta.append(p_blocco)

    # --=-=--------------------------------------------------------------------------=-=--

    def importa_rom(self, p_nome_file):


        blocco_loader = FileAscii()
        blocco_loader.titolo = os.path.splitext(os.path.basename(p_nome_file))[0]
        blocco_loader.dati = b'1 POKE&HFBB0,1:POKE&HFBB1,1:KEYOFF:SCREEN0:WIDTH 40:COLOR15,8,8\r\n3 LOCATE12,9:PRINT" NOW LOADING "\r\n4 LOCATE14,12:PRINT"PLEASE WAIT"\r\n5 LOCATE6,18:PRINT"Loader made in 2017 by Kaiko"\r\n6 BLOAD"cas:",R\r\n7 GOTO 6\r\n\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

        self.aggiungi(blocco_loader)

        # Legge il file .ROM dal disco
        f = open(p_nome_file, "rb")
        buffer = f.read()
        f.close()

        """
        0..1) C348
        2..3) 9000
        4..5) 0000
        6..7) 0000
        8..9) 0000
        """

        programma = []
        if len(buffer) <= 16384:
            programma.append(buffer)
        elif len(buffer) <= 32768:
            programma.append(buffer[:16384])
            programma.append(buffer[16384:])
        elif len(buffer) <= 49152:
            programma.append(buffer[:16384])
            programma.append(buffer[16384:32768])
            programma.append(buffer[32768:])
        else:
            # Non supportato
            pass

        for indice, elemento in enumerate(programma):
            blocco = FileBinario()
            blocco.titolo = "DATA" + str(indice + 1)  # os.path.splitext(os.path.basename(p_nome_file))[0]

            if len(programma) == 1:
                a = Loader.binari_16k_4000h
            else:
                if indice == 0:
                    a = Loader.binari_32k_4000h
                elif indice == 1:
                    a = Loader.binari_32k_8000h
                elif indice == 2:
                    a = b"" # Loader.binari_48k_C000h

            blocco.importa_rom(elemento, a)

            self.aggiungi(blocco)

        """
        a = len(Loader.binari_32k_4000h)
        b = len(Loader.binari_32k_8000h)

        ind = 0
        ind2 = 0
        while ind < len(buffer):

            blocco = FileBinario()

            blocco.titolo = os.path.splitext(os.path.basename(p_nome_file))[0]

            a = buffer[ind:ind + 16384]
            b = len(a)
            c = int(a[2])
            d = int(a[3])
            e = hex(c) + hex(d)
            if ind2 == 0:
                blocco.importa(buffer[ind:ind + 16384], Loader.binari_32k_4000h)
            else:
                blocco.importa(buffer[ind:ind + 16384], Loader.binari_32k_8000h)

            self.aggiungi(blocco)

            ind += 16384
            ind2 += 1
        """

    # --=-=--------------------------------------------------------------------------=-=--

    def importa_ascii(self, p_titolo, p_dati):

        blocco = FileAscii()
        blocco.titolo = p_titolo
        blocco.dati = p_dati

        self.aggiungi(blocco)

    # --=-=--------------------------------------------------------------------------=-=--

    def rimuovi(self, p_indice):
        """
        Rimuove un blocco specifico dalla cassetta

        Args:
            p_indice: Indice del blocco da rimuovere

        Returns:
            None se risce ad eliminare il blocco, altrimenti solleva un'eccezione
        """

        if p_indice < len(self.cassetta):
            self.cassetta.remove(p_indice)
        else:
            raise Eccezione("The tape element you want to remove is out of bounds")

    # --=-=--------------------------------------------------------------------------=-=--

    def export_to_wav(self, p_nome_file="output.wav", p_numero_file=-1):
        """
        Test

        Args:
            p_nome_file:   Percorso e nome del file WAV da creare
            p_numero_file: Se indicato esporta solo il numero di file selezionato

        Returns:
            None
        """

        suono = Esportazione(p_nome_file)
        if p_numero_file < 0:
            for ind, blocco in enumerate(self._cassetta):
                blocco.esporta(suono)
                if ind < (len(self._cassetta) - 1):
                    suono.inserisci_silenzio(4000)
        else:
            self._cassetta[p_numero_file].esporta(suono)
        suono.chiudi()

    # --=-=--------------------------------------------------------------------------=-=--

    def __len__(self):
        """
        Restituisce il numero di blocchi contenuti nella cassetta

        Returns:
            Un numero intero che indica il numero dei blocchi contenuti nella cassetta
        """
        return len(self.lista_blocchi)

    # --=-=--------------------------------------------------------------------------=-=--

    def __str__(self):
        """
        Fa un elenco dettagliato di tutti i blocchi presenti nella cassetta

        Returns:
            Una stringa con l'elenco dettagliato di tutti i blocchi presenti
            all'interno della cassetta
        """

        temp = ""
        if len(self._cassetta) > 0:
            temp += "TAPE CONTENT:\n"
            temp += "-" * 39 + "\n"
            for indice, elemento in enumerate(self._cassetta):
                temp += "{0}) {1}\n".format(str(indice + 1).rjust(2), str(elemento))
            temp += "-" * 39 + "\n"
            temp += "{0} Files found\n".format(str(len(self._cassetta))).rjust(40)
            return temp
        else:
            raise Eccezione("Tape is currently empty")

    # --=-=--------------------------------------------------------------------------=-=--

    def __repr__(self):
        return str(self)

    # --=-=--------------------------------------------------------------------------=-=--

    def __len__(self):
        """
        Returns the length of a tape expressed in number of files

        Returns:
            integer
        """
        return len(self._cassetta)

    # --=-=--------------------------------------------------------------------------=-=--

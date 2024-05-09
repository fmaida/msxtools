import os

# from .intestazioni import Intestazioni
from datablocks import BinaryFile, AsciiFile
from loader import Loader
from eccezioni import Eccezione
from ricerche import Ricerca
from datablocks.wav import Esportazione
from datablocks.strumenti import Indirizzo


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
                # ROM
                self.importa_rom(p_file)
            else:
                # CAS file
                self.load(p_file)

    # --=-=--------------------------------------------------------------------------=-=--

    def load(self, p_file):
        """
        Carica un file cas in memoria

        Args:
            p_file:	Il percorso al file .CAS da caricare

        Returns:

        """

        try:

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
                self.add(blocco)

        except:
            raise Eccezione("Unable to find any tape called \"{0}\"".format(p_file))

    # --=-=--------------------------------------------------------------------------=-=--

    def add(self, p_blocco):
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

        title = [
            b"CHAMPION BILLIARDS",
            b"NOW LOADING - PLEASE WAIT",
            b"(C) 1986 SEGA, (C) 2016-20 MASTROPIERO",
        ]
        cols = [
            str(int(37/2 - len(title[0])/2)).encode("ascii"),
            str(int(37/2 - len(title[1])/2)).encode("ascii"),
            str(int(37/2 - len(title[2])/2)).encode("ascii"),
        ]

        blocco_loader = AsciiFile()
        blocco_loader.title = os.path.splitext(os.path.basename(p_nome_file))[0]
        blocco_loader.dati  = b'1 POKE&HFBB0,1:POKE&HFBB1,1:KEYOFF:SCREEN0:WIDTH 40:COLOR15,8,8\r\n'
        blocco_loader.dati += b'2 LOCATE' + cols[0] + b',8:PRINT"' + title[0] + b'"\r\n'
        blocco_loader.dati += b'3 LOCATE' + cols[1] + b',9:PRINT"' + title[1] + b'"\r\n'
        blocco_loader.dati += b'4 LOCATE' + cols[2] + b',18:PRINT"' + title[2] + b'"\r\n'
        #blocco_loader.dati += b'5 LOCATE' + str(int(37/2 - len(title)/2)).encode("ascii") + b',18:PRINT"' + title + b'"\r\n"'
        blocco_loader.dati += b'6 BLOAD"cas:",R\r\n7 GOTO 6\r\n\x1a'
        while len(blocco_loader.dati) < 256:
            blocco_loader.dati += b"\x00"

        self.add(blocco_loader)

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
        inizio = None
        esecuzione = None
        if len(buffer) <= 16384:
            programma.append(buffer)
            inizio = Indirizzo(0xA000)
            esecuzione = Indirizzo(0xC000)
        elif len(buffer) <= 32768:
            programma.append(buffer[:16384])
            programma.append(buffer[16384:])
            inizio = Indirizzo(0x9000)
            esecuzione = Indirizzo(0xD000)

        elif len(buffer) <= 49152:
            programma.append(buffer[:16384])
            programma.append(buffer[16384:32768])
            programma.append(buffer[32768:])
        else:
            # Non supportato
            pass

        for indice, elemento in enumerate(programma):
            blocco = BinaryFile()
            blocco.title = "DATA" + str(indice + 1)  # os.path.splitext(os.path.basename(p_nome_file))[0]

            if len(programma) == 1:
                a = Loader.binari_16k_4000h
            else:
                if indice == 0:
                    a = Loader.binari_32k_4000h
                elif indice == 1:
                    a = Loader.binari_32k_8000h
                elif indice == 2:
                    a = b""  # Loader.binari_48k_C000h

            blocco.importa_rom(elemento, a,
                               indirizzo_inizio=inizio, indirizzo_esecuzione=esecuzione)

            self.add(blocco)

        """
        a = len(Loader.binari_32k_4000h)
        b = len(Loader.binari_32k_8000h)

        ind = 0
        ind2 = 0
        while ind < len(buffer):

            blocco = BinaryFile()

            blocco.title = os.path.splitext(os.path.basename(p_nome_file))[0]

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

        blocco = AsciiFile()
        blocco.title = p_titolo
        blocco.dati = p_dati

        self.add(blocco)

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

    def export_to_wav(self, p_file="output.wav", p_file_index=-1):
        """
        Test

        Args:
            p_file:       Percorso e nome del file WAV da creare
            p_file_index: Se indicato esporta solo il numero di file
                          selezionato

        Returns:
            None
        """

        suono = Esportazione(p_file)
        if p_file_index < 0:
            for ind, blocco in enumerate(self._cassetta):
                blocco.esporta(suono)
                if ind < (len(self._cassetta) - 1):
                    suono.inserisci_silenzio(4000)
        else:
            self._cassetta[p_file_index].esporta(suono)
        suono.chiudi()

    # --=-=--------------------------------------------------------------------------=-=--

    def __len__(self):
        """
        Restituisce il numero di blocchi contenuti nella cassetta

        Returns:
            Un numero intero che indica il numero dei blocchi contenuti nella cassetta
        """
        return len(self._cassetta)

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
            # temp += "TAPE CONTENT:\n"
            temp += "-" * 42 + "\n"
            for indice, elemento in enumerate(self._cassetta):
                temp += "{0}. {1}\n".format(str(indice + 1).rjust(2), str(elemento))
            temp += "-" * 42 + "\n"

            if len(self._cassetta) > 1:
                total = "{0} Files found\n"
            else:
                total = "{0} File found\n"

            temp += total.format(str(len(self._cassetta))).rjust(42)

            return temp
        else:
            raise Eccezione("Tape is currently empty")

    # --=-=--------------------------------------------------------------------------=-=--

    def __repr__(self):
        return str(self)

    # --=-=--------------------------------------------------------------------------=-=--

    def __getitem__(self, p_value):
        return self._cassetta[p_value]

    # --=-=--------------------------------------------------------------------------=-=--

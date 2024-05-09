import os

from datablocks.generic import GenericDataBlock
from datablocks.intestazioni import Intestazioni
from datablocks.wav import Esportazione
from datablocks.strumenti import Indirizzo


class BinaryFile(GenericDataBlock):

    intestazione = b"\xd0" * 10  # chr(int(0xD0)) * 10

    # --=-=--------------------------------------------------------------------------=-=--

    @property
    def type(self):
        return "binary"

    # --=-=--------------------------------------------------------------------------=-=--

    def __init__(self, p_titolo="", p_dati=""):
        super().__init__(p_titolo, p_dati)
        self.indirizzo_iniziale = Indirizzo()
        self.indirizzo_finale = Indirizzo()
        self.indirizzo_esecuzione = Indirizzo()

    # --=-=--------------------------------------------------------------------------=-=--

    @property
    def dati(self):
        return self._dati

    @dati.setter
    def dati(self, p_valore):
        if p_valore != "":
            self.indirizzo_iniziale.importa(p_valore[0:2])
            self.indirizzo_finale.importa(p_valore[2:4])
            self.indirizzo_esecuzione.importa(p_valore[4:6])
        self._dati = p_valore[6:]

    # --=-=--------------------------------------------------------------------------=-=--

    def importa_rom(self, p_buffer: bytearray, p_loader: bytearray,
                    indirizzo_inizio, indirizzo_esecuzione):
        # Legge l'indirizzo di esecuzione


        self.indirizzo_iniziale = indirizzo_inizio  # Indirizzo(0xC000)  # 0xA000  # int("A000", 16)
        self.indirizzo_finale = Indirizzo(self.indirizzo_iniziale.valore + (len(p_buffer) + len(p_loader) - 1))  # 0xD038
        if p_loader != b"":
            self.indirizzo_esecuzione = indirizzo_esecuzione  # self.indirizzo_iniziale.valore + len(p_buffer))  # 0xD000
        else:
            self.indirizzo_esecuzione = Indirizzo(self.indirizzo_finale.valore - len(p_loader) + 10)  # Indirizzo(0x4010)

        temp = p_buffer + p_loader

        self._dati = temp

    # --=-=--------------------------------------------------------------------------=-=--

    def importa2(self, p_file):
        # Legge il file .CAS dal disco
        f = open(p_file, "rb")
        buffer = f.read()
        f.close()

        # Cambia il titolo prendendolo dal nome del file
        self.title = os.path.splitext(os.path.basename(p_file))[0]

        indirizzo_iniziale = Indirizzo(0x9000)  # 0xA000  # int("A000", 16)
        indirizzo_esecuzione = indirizzo_iniziale + len(buffer)  # C000

        temp = Intestazioni.blocco_intestazione + FileBinario.intestazione + \
               self.title.encode("ascii") + Intestazioni.blocco_intestazione

        # Indirizzo di partenza

        indirizzo = indirizzo_iniziale
        temp2 = hex(indirizzo)
        temp2 = temp2[2:]
        temp2 = temp2.rjust(4, "0")  # PadL(cTemp2, 4, "0")
        a = temp2[2:4]
        b = temp2[0:2]
        valore1 = int(temp2[2:4], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
        valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

        temp += bytes([valore1, valore2])

        # Indirizzo finale (Indirizzo di partenza + Lunghezza file - 1)

        indirizzo += len(buffer) + len(Loader.test1) - 1
        temp2 = hex(indirizzo)
        temp2 = temp2[2:]
        temp2 = temp2.rjust(4, "0")  # PadL(cTemp2, 4, "0")
        valore1 = int(temp2[2:4], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
        valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

        temp += bytes([valore1, valore2])

        # Indirizzo di esecuzione del file

        indirizzo = indirizzo_esecuzione
        temp2 = hex(indirizzo)
        temp2 = temp2[2:]
        temp2 = temp2.rjust(4, "0")  # PadL(cTemp2, 4, "0")
        valore1 = int(temp2[2:4], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
        valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

        temp += bytes([valore1, valore2])

        # Ora può aggiungere la ROM vera e propria (o una sua porzione) al file

        temp += buffer + Loader.test1

        self.dati = temp

    # --=-=--------------------------------------------------------------------------=-=--

    def esporta_file(self, p_percorso):
        file_esportato = os.path.join(p_percorso, self.title.strip() + ".bin")

        # Apre il file sul disco
        f = open(file_esportato, "wb")

        temp = b""

        temp += bytes([0xFE])  # bytes([int("FE", 16)])
        temp += self.indirizzo_iniziale.get()
        temp += self.indirizzo_finale.get()
        temp += self.indirizzo_esecuzione.get()

        temp += self.dati

        f.write(temp)

        f.close()

    # --=-=--------------------------------------------------------------------------=-=--

    def esporta(self, p_file: Esportazione):

        p_file.inserisci_sincronismo(2500)  # Tre secondi

        intestazione = self.intestazione + self.title.encode("ascii")

        p_file.inserisci_stringa(intestazione)

        p_file.inserisci_silenzio(1000)

        p_file.inserisci_sincronismo(1500)  # Tre/quarti di secondo

        p_file.inserisci_stringa(self.indirizzo_iniziale.get())
        p_file.inserisci_stringa(self.indirizzo_finale.get())
        p_file.inserisci_stringa(self.indirizzo_esecuzione.get())

        p_file.inserisci_stringa(self.dati)

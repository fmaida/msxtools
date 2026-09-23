from .generic import GenericDataBlock
from .intestazioni import Intestazioni
from .wav import Esportazione


class AsciiFile(GenericDataBlock):

    intestazione = b"\xea" * 10

    # --=-=--------------------------------------------------------------------------=-=--

    @property
    def type(self):
        return "ascii"

    # --=-=--------------------------------------------------------------------------=-=--

    def parti_cas(self) -> list[bytes]:
        # Come sul nastro: intestazione con il nome, poi segmenti da 256 byte con
        # l'ultimo completato con EOF
        return [self.intestazione + self.titolo_in_bytes() + self.coda_intestazione] + \
               [self.dati[inizio:inizio + 256].ljust(256, b"\x1a")
                for inizio in range(0, len(self.dati), 256)]

    # --=-=--------------------------------------------------------------------------=-=--

    def esporta(self, p_file: Esportazione):

        p_file.inserisci_sincronismo(2500)  # Tre secondi

        intestazione = self.intestazione + self.titolo_in_bytes() + self.coda_intestazione

        p_file.inserisci_stringa(intestazione)

        p_file.inserisci_silenzio(1000)

        p_file.inserisci_sincronismo(1500)  # Tre/quarti di secondo

        # L'MSX legge i file ASCII in segmenti da 256 byte, ognuno preceduto da un
        # breve segnale di sincronismo. L'ultimo segmento viene completato con EOF
        for inizio in range(0, len(self.dati), 256):
            if inizio > 0:
                p_file.inserisci_silenzio(500)
                p_file.inserisci_sincronismo(1000)
            segmento = self.dati[inizio:inizio + 256]
            p_file.inserisci_stringa(segmento.ljust(256, b"\x1a"))

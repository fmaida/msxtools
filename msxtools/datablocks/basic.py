from .generic import GenericDataBlock
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class BasicFile(GenericDataBlock):

    intestazione = b"\xd3" * 10  # chr(int(0xD3)) * 10

    # --=-=--------------------------------------------------------------------------=-=--

    @property
    def type(self):
        return "basic"

    # --=-=--------------------------------------------------------------------------=-=--

    def esporta(self, p_file: Esportazione):

        p_file.inserisci_sincronismo(2500)  # Tre secondi

        intestazione = self.intestazione + self.titolo.encode("ascii")

        p_file.inserisci_stringa(intestazione)

        p_file.inserisci_silenzio(1000)

        p_file.inserisci_sincronismo(1500)  # Tre/quarti di secondo

        p_file.inserisci_stringa(self.dati)

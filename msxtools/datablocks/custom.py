import os

from .generic import GenericDataBlock
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class CustomFile(GenericDataBlock):

    # --=-=--------------------------------------------------------------------------=-=--

    def esporta(self, p_file: Esportazione):
        p_file.inserisci_sincronismo(2500)  # Tre secondi

        p_file.inserisci_stringa(self.dati)
        pass

    # --=-=--------------------------------------------------------------------------=-=--

    def esporta_file(self, p_percorso):
        file_esportato = os.path.join(p_percorso, "custom.cus")

        # Apre il file sul disco
        f = open(file_esportato, "wb")

        temp = b""

        temp += self.dati

        f.write(temp)

        f.close()

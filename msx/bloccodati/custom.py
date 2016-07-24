from .generico import BloccoDati
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class FileCustom(BloccoDati):

    # --=-=--------------------------------------------------------------------------=-=--

    def esporta(self, p_file: Esportazione):
        p_file.inserisci_sincronismo(2500)  # Tre secondi

        p_file.inserisci_stringa(self.dati)
        pass

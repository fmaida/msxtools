from .generico import BloccoDati
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class FileBasic(BloccoDati):

	intestazione = b"\xd3" * 10  # chr(int(0xD3)) * 10

	# --=-=--------------------------------------------------------------------------=-=--

	def esporta(self, p_file: Esportazione):

		p_file.inserisci_sincronismo(2500)  # Tre secondi

		intestazione = self.intestazione + self.titolo.encode("ascii")

		p_file.inserisci_stringa(intestazione)

		p_file.inserisci_silenzio(750)

		p_file.inserisci_sincronismo(1000)  # Tre/quarti di secondo

		p_file.inserisci_stringa(self.dati)

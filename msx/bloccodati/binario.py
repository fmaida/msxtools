from .generico import BloccoDati
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class FileBinario(BloccoDati):

	intestazione = b"\xd0" * 10  # chr(int(0xD0)) * 10

	# --=-=--------------------------------------------------------------------------=-=--

	def esporta(self, p_file: Esportazione):

		p_file.inserisci_sincronismo(2000)  # Tre secondi

		intestazione = self.intestazione + self.titolo.encode("ascii")

		p_file.inserisci_stringa(intestazione)

		p_file.inserisci_silenzio(750)

		p_file.inserisci_sincronismo(1000)  # Tre/quarti di secondo

		p_file.inserisci_stringa(self.dati)
		pass

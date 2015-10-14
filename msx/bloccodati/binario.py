import os

from .generico import BloccoDati
from ..loader import Loader
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class FileBinario(BloccoDati):

	intestazione = b"\xd0" * 10  # chr(int(0xD0)) * 10

	# --=-=--------------------------------------------------------------------------=-=--

	def importa(self, p_file):

		# Legge il file .CAS dal disco
		f = open(p_file, "rb")
		buffer = f.read()
		f.close()

		self.titolo = os.path.splitext(os.path.basename(p_file))[0]

		indirizzo_iniziale = int("A000", 16)
		indirizzo_esecuzione = indirizzo_iniziale + len(buffer) # C000

		temp = Intestazioni.blocco_intestazione + FileBinario.intestazione + \
			   self.titolo.encode("ascii") + Intestazioni.blocco_intestazione

		# Indirizzo di partenza

		indirizzo = indirizzo_iniziale
		temp2 = hex(indirizzo)
		temp2 = temp2[2:]
		temp2 = temp2.rjust(4, "0") # PadL(cTemp2, 4, "0")
		valore1 = int(temp2[3:5], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
		valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

		temp += bytes([valore1, valore2])

		# Indirizzo finale (Indirizzo di partenza + Lunghezza file - 1)

		indirizzo += len(buffer) + len(Loader.binari_8k_4000h) - 1
		temp2 = hex(indirizzo)
		temp2 = temp2[2:]
		temp2 = temp2.rjust(4, "0") # PadL(cTemp2, 4, "0")
		valore1 = int(temp2[3:5], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
		valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

		temp += bytes([valore1, valore2])

		# Ora può aggiungere la ROM vera e propria (o una sua porzione) al file

		temp += buffer + Loader.binari_8k_4000h

		self.dati = temp


	# --=-=--------------------------------------------------------------------------=-=--

	def esporta(self, p_file: Esportazione):

		p_file.inserisci_sincronismo(2500)  # Tre secondi

		intestazione = self.intestazione + self.titolo.encode("ascii")

		p_file.inserisci_stringa(intestazione)

		p_file.inserisci_silenzio(1000)

		p_file.inserisci_sincronismo(1500)  # Tre/quarti di secondo

		p_file.inserisci_stringa(self.dati)
		pass

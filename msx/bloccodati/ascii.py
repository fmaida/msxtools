from .generico import BloccoDati
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class FileAscii(BloccoDati):

	intestazione = b"\xea" * 10

	# --=-=--------------------------------------------------------------------------=-=--

	def esporta(self, p_file: Esportazione):

		p_file.inserisci_sincronismo(2500)  # Tre secondi

		intestazione = self.intestazione + self.titolo.encode("ascii")

		p_file.inserisci_stringa(intestazione)

		p_file.inserisci_silenzio(750)

		p_file.inserisci_sincronismo(1000)  # Tre/quarti di secondo

		ind = 0
		continua = True
		temp = ""
		p_file.inserisci_stringa(self.dati)
		while continua:
			if ind < (len(self.dati)):
				a = self.dati[ind:ind+1]
				b = ord(a)
				temp += a.decode("ascii").replace(chr(26), "[FINE]")
				#p_file.inserisci_byte(a)
			else:
				#p_file.inserisci_byte(26)
				temp += "[FINE]"
				continua = False
			ind += 1

		# print("\"{0}\"\n--------------------------------".format(temp))
		# print("{0} Bytes".format(len(temp) - len("[FINE]")))

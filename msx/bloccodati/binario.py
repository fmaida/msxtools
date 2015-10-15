from .generico import BloccoDati
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class FileBinario(BloccoDati):

	intestazione = b"\xd0" * 10  # chr(int(0xD0)) * 10

	# --=-=--------------------------------------------------------------------------=-=--

	def __indirizzo(self, p_valore: int):
		valore_a = int(str(p_valore)[2:4], 16)
		valore_b = int(str(p_valore)[4:7], 16)
		return bytes([valore_b, valore_a])

	def importa(self, p_buffer, p_loader):

		# Legge l'indirizzo di esecuzione

		indirizzo_iniziale = hex(0x9000)  # 0xA000  # int("A000", 16)
		indirizzo_finale = hex(0x9000 + len(p_buffer) + len(p_loader) - 1)  # 0xD038H
		indirizzo_esecuzione = hex(0x9000 + len(p_buffer))

		temp = b""
		temp += self.__indirizzo(indirizzo_iniziale)
		temp += self.__indirizzo(indirizzo_finale)
		temp += self.__indirizzo(indirizzo_esecuzione)

		temp += p_buffer + p_loader

		self.dati = temp

	def importa2(self, p_file):

		# Legge il file .CAS dal disco
		f = open(p_file, "rb")
		buffer = f.read()
		f.close()

		self.titolo = os.path.splitext(os.path.basename(p_file))[0]

		indirizzo_iniziale = 0x9000  # 0xA000  # int("A000", 16)
		indirizzo_esecuzione = indirizzo_iniziale + len(buffer)  # C000

		temp = Intestazioni.blocco_intestazione + FileBinario.intestazione + \
			   self.titolo.encode("ascii") + Intestazioni.blocco_intestazione

		# Indirizzo di partenza

		indirizzo = indirizzo_iniziale
		temp2 = hex(indirizzo)
		temp2 = temp2[2:]
		temp2 = temp2.rjust(4, "0") # PadL(cTemp2, 4, "0")
		a = temp2[2:4]
		b = temp2[0:2]
		valore1 = int(temp2[2:4], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
		valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

		temp += bytes([valore1, valore2])
		gigetto = bytes([valore1, valore2])

		# Indirizzo finale (Indirizzo di partenza + Lunghezza file - 1)

		c = len(Loader.test1)
		l = len(buffer)
		indirizzo += len(buffer) + len(Loader.test1) - 1
		m = hex(indirizzo)  # Dovrebbe essere 0xD038
		temp2 = hex(indirizzo)
		temp2 = temp2[2:]
		temp2 = temp2.rjust(4, "0") # PadL(cTemp2, 4, "0")
		a = temp2[2:4]
		b = temp2[0:2]
		valore1 = int(temp2[2:4], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
		valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

		temp += bytes([valore1, valore2])
		gigetto = bytes([valore1, valore2])

		# Indirizzo di esecuzione del file

		indirizzo = indirizzo_esecuzione
		temp2 = hex(indirizzo)
		temp2 = temp2[2:]
		temp2 = temp2.rjust(4, "0") # PadL(cTemp2, 4, "0")
		a = temp2[2:4]
		b = temp2[0:2]
		valore1 = int(temp2[2:4], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
		valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

		temp += bytes([valore1, valore2])

		# Ora può aggiungere la ROM vera e propria (o una sua porzione) al file

		temp += buffer + Loader.test1

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

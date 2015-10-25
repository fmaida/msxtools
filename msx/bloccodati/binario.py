import os

from .generico import BloccoDati
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class FileBinario(BloccoDati):

	intestazione = b"\xd0" * 10  # chr(int(0xD0)) * 10

	# --=-=--------------------------------------------------------------------------=-=--

	def __init__(self, p_titolo = "", p_dati = ""):
		super().__init__(p_titolo, p_dati)
		self.indirizzo_iniziale = 0x0000
		self.indirizzo_finale = 0x0000
		self.indirizzo_esecuzione = 0x0000

	# --=-=--------------------------------------------------------------------------=-=--

	def __indirizzo(self, p_valore: int, p_inverti=True):
		temp = hex(p_valore)
		valore_a = int(str(temp)[2:4], 16)
		valore_b = int(str(temp)[4:7], 16)
		if p_inverti:
			return bytes([valore_b, valore_a])
		else:
			return bytes([valore_a, valore_b])

	# --=-=--------------------------------------------------------------------------=-=--

	def importa(self, p_buffer, p_loader):

		# Legge l'indirizzo di esecuzione

		self.indirizzo_iniziale = 0x9000  # 0xA000  # int("A000", 16)
		self.indirizzo_finale = 0x9000 + len(p_buffer) + len(p_loader) - 1  # 0xD038
		self.indirizzo_esecuzione = 0x9000  # + len(p_buffer))  # 0xD000

		temp = b""

		"""
		0..1) C348
		2..3) 9000
		4..5) 0000
		6..7) 0000
		8..9) 0000
		"""

		temp += bytes([0xC3, 0x30])  # bytes([int("C3", 16), int("30", 16)])
		temp += self.__indirizzo(self.indirizzo_iniziale)
		temp += self.__indirizzo(self.indirizzo_finale)
		temp += self.__indirizzo(self.indirizzo_iniziale + len(p_loader))

		crc = 0
		for elemento in p_buffer:
			crc += elemento

		temp += bytes([int(crc/256/256)])  # self.__indirizzo(crc)

		temp += p_loader[9:]
		temp += p_buffer

		self.dati = temp

	def importa2(self, p_file):

		# Legge il file .CAS dal disco
		f = open(p_file, "rb")
		buffer = f.read()
		f.close()

		# Cambia il titolo prendendolo dal nome del file
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

		# Indirizzo finale (Indirizzo di partenza + Lunghezza file - 1)

		indirizzo += len(buffer) + len(Loader.test1) - 1
		temp2 = hex(indirizzo)
		temp2 = temp2[2:]
		temp2 = temp2.rjust(4, "0") # PadL(cTemp2, 4, "0")
		valore1 = int(temp2[2:4], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
		valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

		temp += bytes([valore1, valore2])

		# Indirizzo di esecuzione del file

		indirizzo = indirizzo_esecuzione
		temp2 = hex(indirizzo)
		temp2 = temp2[2:]
		temp2 = temp2.rjust(4, "0") # PadL(cTemp2, 4, "0")
		valore1 = int(temp2[2:4], 16)  # Val("&h" + Mid(cTemp2, 3, 2))
		valore2 = int(temp2[0:2], 16)  # Val("&h" + Mid(cTemp2, 1, 2))

		temp += bytes([valore1, valore2])

		# Ora può aggiungere la ROM vera e propria (o una sua porzione) al file

		temp += buffer + Loader.test1

		self.dati = temp

	# --=-=--------------------------------------------------------------------------=-=--

	def esporta_file(self, p_percorso):

		file_esportato = os.path.join(p_percorso, self.titolo.strip() + ".bin")

		# Apre il file sul disco
		f = open(file_esportato, "wb")

		temp = b""

		temp += bytes([0xFE])  # bytes([int("FE", 16)])
		temp += self.__indirizzo(self.indirizzo_iniziale)
		temp += self.__indirizzo(self.indirizzo_finale)
		temp += self.__indirizzo(self.indirizzo_esecuzione)

		temp += self.dati

		f.write(temp)

		f.close()

	# --=-=--------------------------------------------------------------------------=-=--

	def esporta_wav(self, p_file: Esportazione):

		p_file.inserisci_sincronismo(2500)  # Tre secondi

		intestazione = self.intestazione + self.titolo.encode("ascii")

		p_file.inserisci_stringa(intestazione)

		p_file.inserisci_silenzio(1000)

		p_file.inserisci_sincronismo(1500)  # Tre/quarti di secondo

		p_file.inserisci_stringa(self.dati)

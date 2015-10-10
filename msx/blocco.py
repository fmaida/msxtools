from .intestazioni import Intestazioni
from .tipi import TipiDiBlocco
from .wav import Esportazione


class BloccoDati:
	"""
	Questa classe gestisce la struttura di un blocco delle cassette MSX.
	Un blocco può contenere un file di tipo ASCII, Binario, Basic o custom.
	"""

	def __init__(self, p_titolo = "", p_tipo = TipiDiBlocco.BLOCCO_CUSTOM, p_dati = ""):
		"""
		Costruttore della classe

		Returns:
			None
		"""
		self.titolo = p_titolo  # Titolo del file
		self.tipo = p_tipo  # Tipo del file
		self.dati = p_dati  # Dati che compongono il file memorizzato

	def importa(self, p_dati_grezzi):
		"""
		Importa il primo blocco dati che trova a partire dai dati grezzi

		Args:
		    p_dati_grezzi: Dati grezzi da cui estrae un blocco da importare

		Returns:
			Un indice al primo byte successivo alla fine del blocco che ha trovato,
			in modo da poter richiamare nuovamente la funzione importa per cercare
			il blocco successivo.
		"""

		inizio_intestazione = len(Intestazioni.blocco_intestazione)

		# Il blocco inizia con un'intestazione ?
		if Intestazioni.contiene_intestazione(p_dati_grezzi):

			# Si. Vuol dire che al 99% si tratta di un blocco ASCII, Basic o Binario

			# Ceca di individuare l'inizio e la fine della parte dati
			inizio_dati = p_dati_grezzi.find(Intestazioni.blocco_intestazione, inizio_intestazione)
			fine_dati = p_dati_grezzi.find(Intestazioni.blocco_intestazione,
										   inizio_dati + len(Intestazioni.blocco_intestazione))

			# Se non trova la fine dei dati vuol dire che è arrivato alla fine della
			# cassetta e non ci sono altre intestazioni da trovare. Prende come dimensione
			# massima la lunghezza complessiva del blocco
			if fine_dati < 0:
				fine_dati = len(p_dati_grezzi)

			# print("Intestazione: {0}-{1} - Dati: {1}-{2}".format(str(inizio_intestazione), str(inizio_dati), str(fine_dati)))

			# Cerca il tipo del file
			tipo_blocco = p_dati_grezzi[inizio_intestazione:inizio_intestazione + 10]
			if tipo_blocco == Intestazioni.blocco_file_ascii:
				self.tipo = TipiDiBlocco.FILE_ASCII
			elif tipo_blocco == Intestazioni.blocco_file_basic:
				self.tipo = TipiDiBlocco.FILE_BASIC
			elif tipo_blocco == Intestazioni.blocco_file_binario:
				self.tipo = TipiDiBlocco.FILE_BINARIO
			else:
				self.tipo = TipiDiBlocco.BLOCCO_CUSTOM

			# Cerca il titolo del file
			if self.tipo != TipiDiBlocco.BLOCCO_CUSTOM:
				inizio_titolo = inizio_intestazione + len(tipo_blocco)
				fine_titolo = inizio_titolo + 6
				self.titolo = p_dati_grezzi[inizio_titolo:fine_titolo].decode("ascii")

			# Memorizza il blocco dati
			self.dati = p_dati_grezzi[inizio_dati:fine_dati]

		else:
			# No. Non ha un'intestazione... allora è per forza un blocco custom
			self.tipo = TipiDiBlocco.BLOCCO_CUSTOM
			self.dati = p_dati_grezzi

		return fine_dati

	def esporta(self, p_file: Esportazione):

		if self.tipo == TipiDiBlocco.FILE_ASCII:
			self.esporta_file_ascii(p_file)
		elif self.tipo == TipiDiBlocco.FILE_BINARIO:
			self.esporta_file_binario(p_file)
		elif self.tipo == TipiDiBlocco.FILE_BASIC:
			self.esporta_file_basic(p_file)
		else:
			self.esporta_blocco_custom(p_file)

	def esporta_file_ascii(self, p_file: Esportazione):

		p_file.inserisci_sincronismo(2000)  # Tre secondi

		intestazione = Intestazioni.blocco_file_ascii + self.titolo.ljust(6, " ").encode("ascii")

		for elemento in intestazione:
			p_file.inserisci_byte(elemento)

		p_file.inserisci_silenzio(750)

		p_file.inserisci_sincronismo(1000)  # Tre/quarti di secondo

		ind = 0
		continua = True
		while continua:
			stringa = self.dati[ind:ind+8]
			if stringa == Intestazioni.blocco_intestazione:
				p_file.inserisci_silenzio(500)
				p_file.inserisci_sincronismo(1000)
				ind += 8
			else:
				a = self.dati[ind:ind+1]
				if ind < len(self.dati):
					p_file.inserisci_byte(self.dati[ind:ind+1])
				else:
					p_file.inserisci_byte(bytes([26]))
					continua = False
				ind += 1

	def esporta_file_binario(self, p_file: Esportazione):
		# TODO
		pass

	def esporta_file_basic(self, p_file: Esportazione):
		# TODO
		pass

	def esporta_blocco_custom(self, p_file: Esportazione):
		# TODO
		pass

	def __len__(self):
		"""
		Restituisce la lunghezza di un blocco dati

		Returns:
			La lunghezza del blocco dati
		"""
		return len(self.dati)

	def __str__(self):
		"""
		Offre una rappresentazione visuale del blocco dati

		Returns:
			Una stringa di testo
		"""

		tipo = ""
		if self.tipo == TipiDiBlocco.FILE_ASCII:
			tipo = "ASCII"
		elif self.tipo == TipiDiBlocco.FILE_BASIC:
			tipo = "Basic"
		elif self.tipo == TipiDiBlocco.FILE_BINARIO:
			tipo = "Binary"
		else:
			tipo = "Custom"

		if self.titolo != "":
			temp = "\"{0}\" ({1})  [ {2} Bytes ] ".format(self.titolo, tipo.ljust(6), str(len(self.dati)).rjust(6))
		else:
			temp = "{0} ({1})  [ {2} Bytes ]".format(8 * " ", tipo.ljust(6), str(len(self.dati)).rjust(6))
		return temp

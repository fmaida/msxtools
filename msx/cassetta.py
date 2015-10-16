import os

from .bloccodati import FileAscii, FileBasic, FileBinario, FileCustom
from .intestazioni import Intestazioni
from .loader import Loader
from .eccezioni import Eccezione
from .wav import Esportazione


class Cassetta:
	"""
    _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_
    MSX TAPE class - Reads and writes on a virtual tape file (.CAS)
    Version 1.0
    _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_
    """

	# --=-=--------------------------------------------------------------------------=-=--

	def __init__(self):
		"""
		Costruttore della classe

		Returns:
			None
		"""

		# Inizializza i vari array, per partire con una nuova cassetta
		self.cassetta = []  # Array che contiene i blocchi di dati che compongono la cassetta
		self.buffer = ""  # Buffer dati in cui immagazzina temporaneamente il file .cas da analizzare
		self.indice = -1

	# --=-=--------------------------------------------------------------------------=-=--

	def load(self, p_file):
		"""
		Carica un file cas in memoria

		Args:
			p_file:	Il percorso al file .CAS da caricare

		Returns:

		"""

		self.buffer = ""
		#try:

		# Legge il file .CAS dal disco
		f = open(p_file, "rb")
		self.buffer = f.read()
		self.posizione = -1
		f.close()

		blocco = self.estrai_blocchi()
		# while not blocco is None:
		#	# Memorizza il blocco
		# 	blocco = self.estrai_prossimo_blocco()

		#except:
		#	raise Eccezione("Unable to find any tape called \"{0}\"".format(p_file))

	# --=-=--------------------------------------------------------------------------=-=--

	def estrai_blocchi(self):
		"""
		Tenta di estrarre dal buffer uno o più blocchi dati (Ascii, Basic, Binario o custom)

		Returns:
			None
		"""

		# Finchè resta qualcosa nel buffer da analizzare...
		while len(self.buffer) > 0:

			# Con quello che gli rimane del buffer va alla ricerca del
			# primo blocco che riesce a trovare
			fine_blocco, blocco = self.importa(self.buffer)

			# Aggiunge il blocco che ha trovato alla cassetta
			self.cassetta.append(blocco)

			# Riduce il buffer togliendo tutto il blocco che ha appena scovato
			self.buffer = self.buffer[fine_blocco:len(self.buffer)]

	# --=-=--------------------------------------------------------------------------=-=--

	def aggiungi(self, p_blocco):
		"""
		Aggiunge un nuovo blocco-dati alla cassetta

		Args:
		  p_titolo:	Titolo del blocco
		  p_tipo:   Tipo del blocco (ASCII / Basic / Oggetto)
		  P_blocco: I dati effettivi del blocco

		Returns:
			None
		"""
		self.cassetta.append(p_blocco)

	# --=-=--------------------------------------------------------------------------=-=--

	def rimuovi(self, p_indice):
		"""
		Rimuove un blocco specifico dalla cassetta

		Args:
			p_indice: Indice del blocco da rimuovere

		Returns:
			None se risce ad eliminare il blocco, altrimenti solleva un'eccezione
		"""

		if p_indice < len(self.cassetta):
			self.cassetta.remove(p_indice)
		else:
			raise Eccezione("The tape element you want to remove is out of bounds")

	# --=-=--------------------------------------------------------------------------=-=--

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

		# Il blocco inizia con un'intestazione ?
		if Intestazioni.contiene_intestazione(p_dati_grezzi):

			# Si. Vuol dire che si tratta di un blocco ASCII, Basic, Binario o custom

			inizio_intestazione = len(Intestazioni.blocco_intestazione)

			# print("Intestazione: {0}-{1} - Dati: {1}-{2}".format(str(inizio_intestazione), str(inizio_dati), str(fine_dati)))

			# Cerca il tipo del file
			tipo_blocco = p_dati_grezzi[inizio_intestazione:inizio_intestazione + 10]
			if tipo_blocco == FileAscii.intestazione:
				blocco = FileAscii()
			elif tipo_blocco == FileBasic.intestazione:
				blocco = FileBasic()
			elif tipo_blocco == FileBinario.intestazione:
				blocco = FileBinario()
			else:
				blocco = FileCustom()

			# Cerca il titolo del file
			if blocco.__class__.__name__ != "FileCustom":
				inizio_titolo = inizio_intestazione + len(tipo_blocco)
				fine_titolo = inizio_titolo + 6
				blocco.titolo = p_dati_grezzi[inizio_titolo:fine_titolo].decode("ascii")
			else:
				blocco._titolo = ""

			# Cerca di individuare l'inizio e la fine della parte dati
			if blocco.__class__.__name__ != "FileCustom":
				inizio_dati = p_dati_grezzi.find(Intestazioni.blocco_intestazione, inizio_intestazione) + len(Intestazioni.blocco_intestazione)
			else:
				inizio_dati = inizio_intestazione

			fine_dati = p_dati_grezzi.find(Intestazioni.blocco_intestazione,
										   inizio_dati + len(Intestazioni.blocco_intestazione))

			# Se non trova la fine dei dati vuol dire che è arrivato alla fine della
			# cassetta e non ci sono altre intestazioni da trovare. Prende come dimensione
			# massima la lunghezza complessiva del blocco
			if fine_dati < 0:
				fine_dati = len(p_dati_grezzi)

			# Memorizza il blocco dati
			blocco.dati = p_dati_grezzi[inizio_dati:fine_dati]

		else:
			# No. Non ha un'intestazione... allora è per forza un blocco custom
			blocco = FileCustom()
			blocco.dati = p_dati_grezzi

		return fine_dati, blocco

	# --=-=--------------------------------------------------------------------------=-=--

	def importa_rom(self, p_nome_file):

		# Legge il file .ROM dal disco
		f = open(p_nome_file, "rb")
		buffer = f.read()
		f.close()

		a = len(Loader.binari_32k_4000h)
		b = len(Loader.binari_32k_8000h)

		ind = 0
		ind2 = 0
		while ind < len(buffer):

			blocco = FileBinario()

			blocco.titolo = os.path.splitext(os.path.basename(p_nome_file))[0]

			a = buffer[ind:ind + 16384]
			b = len(a)
			c = int(a[2])
			d = int(a[3])
			e = hex(c) + hex(d)
			if ind2 == 0:
				blocco.importa(buffer[ind:ind + 16384], Loader.binari_32k_4000h)
			else:
				blocco.importa(buffer[ind:ind + 16384], Loader.binari_32k_8000h)

			self.aggiungi(blocco)

			ind += 16384
			ind2 += 1

	# --=-=--------------------------------------------------------------------------=-=--

	def importa_ascii(self, p_titolo, p_dati):

		blocco = FileAscii()
		blocco.titolo = p_titolo
		blocco.dati = p_dati

		self.aggiungi(blocco)

	# --=-=--------------------------------------------------------------------------=-=--

	def esporta(self, p_numero_file=-1, p_nome_file="output.wav"):
		"""
		Test

		Args:
		    p_nome_file: Percorso e nome del file WAV da creare

		Returns:
			None
		"""

		suono = Esportazione(p_nome_file)
		if p_numero_file < 0:
			for ind, blocco in enumerate(self.cassetta):
				blocco.esporta(suono)
				if ind < (len(self.cassetta) - 1):
					suono.inserisci_silenzio(4000)
		else:
			self.cassetta[p_numero_file].esporta(suono)
		suono.chiudi()

	# --=-=--------------------------------------------------------------------------=-=--

	def __len__(self):
		"""
		Restituisce il numero di blocchi contenuti nella cassetta

		Returns:
			Un numero intero che indica il numero dei blocchi contenuti nella cassetta
		"""
		return len(self.lista_blocchi)

	# --=-=--------------------------------------------------------------------------=-=--

	def __str__(self):
		"""
		Fa un elenco dettagliato di tutti i blocchi presenti nella cassetta

		Returns:
			Una stringa con l'elenco dettagliato di tutti i blocchi presenti
			all'interno della cassetta
		"""

		temp = ""
		if len(self.cassetta) > 0:
			temp += "TAPE CONTENT:\n"
			temp += "-" * 39 + "\n"
			for indice, elemento in enumerate(self.cassetta):
				temp += "{0}) {1}\n".format(str(indice + 1).rjust(2), str(elemento))
			temp += "-" * 39 + "\n"
			temp += "{0} Files found\n".format(str(len(self.cassetta))).rjust(40)
			return temp
		else:
			raise Eccezione("Tape is empty")

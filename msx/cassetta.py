from typing import TypeVar

from .blocco import BloccoDati
from .intestazioni import Intestazioni
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
			# ..crea un nuovo blocco dati
			blocco = BloccoDati()

			# Con quello che gli rimane del buffer va alla ricerca del
			# primo blocco che riesce a trovare
			fine_blocco = blocco.importa(self.buffer)

			# Aggiunge il blocco che ha trovato alla cassetta
			self.cassetta.append(blocco)

			# Riduce il buffer togliendo tutto il blocco che ha appena scovato
			self.buffer = self.buffer[fine_blocco:len(self.buffer)]

	# --=-=--------------------------------------------------------------------------=-=--

	def aggiungi(self, p_titolo, p_tipo, p_blocco):
		"""
		Aggiunge un nuovo blocco-dati alla cassetta

		Args:
		  p_titolo:	Titolo del blocco
		  p_tipo:   Tipo del blocco (ASCII / Basic / Oggetto)
		  P_blocco: I dati effettivi del blocco

		Returns:
			None
		"""
		self.lista_blocchi.append({"titolo": p_titolo, "tipo": p_tipo, "blocco": p_blocco})

	# --=-=--------------------------------------------------------------------------=-=--

	def rimuovi(self, p_indice):
		"""
		Rimuove un blocco specifico dalla cassetta

		Args:
			p_indice: Indice del blocco da rimuovere

		Returns:
			None se risce ad eliminare il blocco, altrimenti solleva un'eccezione
		"""

		if p_indice < len(self.lista_blocchi):
			self.lista_blocchi.remove(p_indice)
		else:
			raise Eccezione("The tape element you want to remove is out of bounds")

	# --=-=--------------------------------------------------------------------------=-=--

	def esporta(self, p_nome_file="output.wav"):
		"""
		Test

		Args:
		    p_nome_file: Percorso e nome del file WAV da creare

		Returns:
			None
		"""

		suono = Esportazione(p_nome_file)
		for blocco in self.cassetta:
			blocco.esporta(suono)
		# suono.test()
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

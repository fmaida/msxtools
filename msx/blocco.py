from .intestazioni import Intestazioni
from .tipi import TipiDiBlocco


class BloccoCassetta:
	"""
	Questa classe gestisce la struttura di un blocco delle cassette MSX
	"""

	def __init__(self, p_titolo = "", p_tipo = TipiDiBlocco.BLOCCO_CUSTOM, p_dati = ""):
		"""
		Costruttore della classe

		Returns:
			None
		"""
		self.titolo = p_titolo
		self.tipo = p_tipo
		self.dati = p_dati

	def importa(self, p_blocco):

		inizio_intestazione = len(Intestazioni.blocco_intestazione)

		# Il blocco inizia con un'intestazione ?
		if p_blocco[0:inizio_intestazione] == Intestazioni.blocco_intestazione:

			# Si. Vuol dire che al 99% si tratta di un blocco ASCII, Basic o Binario

			# Ceca di individuare l'inizio e la fine della parte dati
			inizio_dati = p_blocco.find(Intestazioni.blocco_intestazione, inizio_intestazione)
			fine_dati = p_blocco.find(Intestazioni.blocco_intestazione,
									  inizio_dati + len(Intestazioni.blocco_intestazione))

			# Se non trova la fine dei dati vuol dire che è arrivato alla fine della
			# cassetta e non ci sono altre intestazioni da trovare. Prende come dimensione
			# massima la lunghezza complessiva del blocco
			if fine_dati < 0:
				fine_dati = len(p_blocco)

			# print("Intestazione: {0}-{1} - Dati: {1}-{2}".format(str(inizio_intestazione), str(inizio_dati), str(fine_dati)))

			# Cerca il tipo del file
			tipo_blocco = p_blocco[inizio_intestazione:inizio_intestazione + 10]
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
				self.titolo = p_blocco[inizio_titolo:fine_titolo].decode("ascii")

			# Memorizza il blocco dati
			self.dati = p_blocco[inizio_dati:fine_dati]

		else:
			# No. Non ha un'intestazione... allora è per forza un blocco custom
			self.tipo = TipiDiBlocco.BLOCCO_CUSTOM
			self.dati = p_blocco

		return fine_dati

	def esporta(self):
		# TODO
		pass

	def __str__(self):
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

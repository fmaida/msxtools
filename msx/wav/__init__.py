from ..intestazioni import Intestazioni
from .parametri import Parametri

import wave


# 1200 x 9 campionamenti (minimo) = 10.800hz
# 2400 x 9 campionamenti (minimo) = 21.600hz
# 4800 x 9 campionamenti (minimo) = 43.200hz

class Esportazione:

	def __init__(self, p_file_output = "output.wav"):
		Parametri.ricalcola_onde()
		self.file_audio = wave.open(p_file_output, "w")
		self.file_audio.setparams((1, 1, Parametri.frequenza, 0, 'NONE', 'not compressed'))

	# --=-=--------------------------------------------------------------------------=-=--

	def inserisci_bit(self, p_bit:int):
		"""
		Se alla frequenza di 48000hz per ogni secondo devo creare 48.000 campionamenti,
		per trasmettere 2400 bit al secondo dovrei fare 48000 / 2400 per sapere quanti
		campionamenti devo usare per trasmettere ogni singolo bit (20)
		"""

		if p_bit == 0:
			self.file_audio.writeframes(bytes(Parametri.wave_bit_0))

		elif p_bit == 1:
			self.file_audio.writeframes(bytes(Parametri.wave_bit_1))

	# --=-=--------------------------------------------------------------------------=-=--

	def inserisci_byte(self, p_byte):
		"""
		Prende un byte (che viene passato alla funzione come parametro)
		e lo scrive nel file WAV sotto forma di forme d'onda. Se è un 1 lo
		scrive con due onde corte, se è uno 0 lo scrive con un onda lunga
		(che essendo per l'appunto lunga dura esattamente come due onde corte)
		"""

		# Un bit di start
		self.inserisci_bit(0)

		# Otto bit di dati
		for ind in range(8):
			if (p_byte & 1) == 0:
				self.inserisci_bit(0)
			else:
				self.inserisci_bit(1)
			p_byte >>= 1  # Bitwise.ShiftRight(P_nByte, 1)

		# Due bit di stop
		self.inserisci_bit(1)
		self.inserisci_bit(1)

	# --=-=--------------------------------------------------------------------------=-=--

	def inserisci_silenzio(self, p_durata:float):

		# campionamenti = frequenza / bitrate

		# devo fare 360° in 20 campionamenti (48000 / 24)

		for ind in range(int(Parametri.bitrate * (p_durata / 1000))):
			self.file_audio.writeframes(bytes(Parametri.wave_silenzio))

	# --=-=--------------------------------------------------------------------------=-=--

	def inserisci_sincronismo(self, p_durata:float):

		# campionamenti = frequenza / bitrate

		# devo fare 360° in 20 campionamenti (48000 / 24)

		for ind in range(int(Parametri.bitrate * (p_durata / 1000))):
			self.inserisci_bit(1)

	# --=-=--------------------------------------------------------------------------=-=--

	def test(self):
		"""
		Esegue un test creando un file con un programmino in Basic
		codificato in formato ASCII
		"""

		self.inserisci_sincronismo(2000)  # Tre secondi

		intestazione = Intestazioni.blocco_file_ascii + b"PROVA "

		for elemento in intestazione:
			self.inserisci_byte(elemento)

		self.inserisci_silenzio(750)

		self.inserisci_sincronismo(1000)  # Tre/quarti di secondo

		stringa = b"10 PRINT \"CIAO A TUTTI BELLI E BRUTTI\"\x1a"
		stringa = stringa.ljust(256, bytes([26]))
		for elemento in stringa:
			self.inserisci_byte(elemento)

		self.chiudi()

	# --=-=--------------------------------------------------------------------------=-=--

	def chiudi(self):
		"""
		Chiude il file wave aperto
		"""

		self.file_audio.close()




if __name__ == '__main__':

	# Test

	import time
	start_time = time.time()

	suono = Esportazione()
	suono.test()

	print("--- {0:.3} secondi ---".format(time.time() - start_time))

	# os.system("open " + os.getcwd() + "/output.wav")
	# os.system("/Applications/openMSX.app/Contents/MacOS/openmsx -cassetteplayer /Users/Scala/Documents/Progetti/Progetti\ Python/prova-wave/output.wav")

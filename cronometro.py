import time


class Cronometro:
	"""
	Questa classe mi serve per cronometrare i tempi dell'applicazione e confrontarli
	"""

	# --=-=--------------------------------------------------------------------------=-=--

	@staticmethod
	def reset():
		"""
		Resetta il cronometro

		Returns:
			None
		"""
		Cronometro.start_time = time.time()

	# --=-=--------------------------------------------------------------------------=-=--

	@staticmethod
	def verifica():
		"""
		Verifica i tempi del cronometro fino ad ora

		Returns:
			Una stringa contenente il tempo passato fra l'ultima verifica e questa
		"""

		temp = "\n--- {0:.4f} secondi ---\n".format(time.time() - Cronometro.start_time)
		Cronometro.start_time = time.time()
		return temp
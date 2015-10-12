class Parametri:
	"""
	Questa classe gestisce i parametri del file wav che verrà creato per ospitare
	i file dell'MSX. Inoltre per comodità d'uso creo anche degli array con al loro interno
	la ricostruzione delle forme d'onda quadre che mi occorre scrivere nel file per rappresentare
	gli zeri e gli uni. Faccio questo perchè fare copia e incolla dei valori da un array in
	memoria al disco è MOLTO PIU' VELOCE che creare ogni volta la forma d'onda in tempo reale!
	"""

	frequenza = 19200  # 19.200hz
	bitrate = 2400  # 1200bps
	ampiezza = 0.9  # 90% dell'ampiezza massima

	campionamenti = frequenza / bitrate
	passo = int(campionamenti / 4)

	wave_silenzio = []
	wave_bit_0 = []
	wave_bit_1 = []

	# --=-=--------------------------------------------------------------------------=-=--

	@staticmethod
	def ricalcola_onde():
		"""
		Ricalcola le forme d'onda quadre in base ai nuovi valori di bitrate / baud
		e frequenza

		Returns:
			None
		"""

		# Considera che per rappresentare l'ampiezza in un file wav a 8 bit come questo
		# posso inserire un valore fra 0 e 255. Il valore di silenzio è il 128, tutto quello
		# che sta sopra a 128 è positivo, tutto quello che sta sotto a 128 è negativo.

		# Calcola le ampiezze massime e minime che potranno avere le forme d'onda, in base
		# al parametro ampiezza

		max = int(255 * Parametri.ampiezza)
		min = 255 - max

		# Ricalcola il silenzio, rappresentato da una linea piatta

		Parametri.wave_silenzio = []
		for i in range(int(Parametri.campionamenti)):
			Parametri.wave_silenzio.append(128)

		# Ricalcola la forma d'onda per rappresentare un bit a 0

		Parametri.wave_bit_0 = []
		for i in range(Parametri.passo * 2):
			Parametri.wave_bit_0.append(min)
		for i in range(Parametri.passo * 2):
			Parametri.wave_bit_0.append(max)

		# Ricalcola la forma d'onda per rappresentare un bit a 1
		# Per fare un 1 ci vogliono due forme d'onda al doppio
		# della frequenza. Es: se trasmetto a 2400bps le onde per
		# rappresentare l'1 devono essere a 4800.

		Parametri.wave_bit_1 = []
		for i in range(Parametri.passo):
			Parametri.wave_bit_1.append(min)
		for i in range(Parametri.passo):
			Parametri.wave_bit_1.append(max)
		for i in range(Parametri.passo):
			Parametri.wave_bit_1.append(min)
		for i in range(Parametri.passo):
			Parametri.wave_bit_1.append(max)

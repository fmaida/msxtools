class Intestazioni:

	blocco_intestazione = b"\x1f\xa6\xde\xba\xcc\x13}t"

	blocco_file_binario = b"\xd0" * 10  # chr(int(0xD0)) * 10
	blocco_file_basic = b"\xd3" * 10  # chr(int(0xD3)) * 10
	blocco_file_ascii = b"\xea" * 10  # chr(int(0xEA)) * 10

	@staticmethod
	def contiene_intestazione(p_dati):
		"""
		Verifica se un una stringa contenente bytes inizia con un blocco di
		intestazione MSX

		Args:
		    p_dati: stringa di bytes da analizzare

		Returns:
			True se la stringa di bytes inizia con l'intestazione ricercata,
			altrimenti False
		"""

		inizio_intestazione = len(Intestazioni.blocco_intestazione)
		return (p_dati[0:inizio_intestazione] == Intestazioni.blocco_intestazione)

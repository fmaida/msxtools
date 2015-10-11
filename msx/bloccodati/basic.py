from .generico import BloccoDati
from ..intestazioni import Intestazioni
from ..wav import Esportazione


class FileBasic(BloccoDati):

	intestazione = b"\xd3" * 10  # chr(int(0xD3)) * 10

	# --=-=--------------------------------------------------------------------------=-=--

	def esporta(self, p_file: Esportazione):

		# DA FARE
		pass

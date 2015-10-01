class Eccezione(Exception):
	"""
	Custom exception made for sending customized messages when something goes wrong
	"""

	def __init__(self, p_valore):
		""" Class constructor """
		self.parameter = p_valore

	def __str__(self):
		return repr(self.parameter)
class Intestazioni:

		blocco_intestazione = b"\x1f\xa6\xde\xba\xcc\x13}t"
		# blocco_intestazione = chr(int(0x1F)) + chr(int(0xA6)) + chr(int(0xDE))
		# blocco_intestazione += chr(int(0xBA)) + chr(int(0xCC)) + chr(int(0x13))
		# blocco_intestazione += chr(int(0x7D)) + chr(int(0x74))

		blocco_file_binario = b"\xd0" * 10  # chr(int(0xD0)) * 10
		blocco_file_basic = b"\xd3" * 10  # chr(int(0xD3)) * 10
		blocco_file_ascii = b"\xea" * 10  # chr(int(0xEA)) * 10

		# for i in range(10):
		# Intestazioni.blocco_file_binario += chr(int(0xD0)) # str_pad("", 10, chr(int(0xD0)));
		# Intestazioni.blocco_file_basic  += chr(int(0xD3))
		# Intestazioni.blocco_file_ascii  += chr(int(0xEA))

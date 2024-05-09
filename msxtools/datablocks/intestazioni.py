class Intestazioni:

    blocco_intestazione = b"\x1f\xa6\xde\xba\xcc\x13}t"
    lunghezza_intestazione = len(blocco_intestazione)
    lunghezza_blocco_tipo = 10  # Tanto sono tutti e tre pari a 10 bytes

    blocco_file_binario = b"\xd0" * lunghezza_blocco_tipo  # chr(int(0xD0)) * 10
    blocco_file_basic = b"\xd3" * lunghezza_blocco_tipo    # chr(int(0xD3)) * 10
    blocco_file_ascii = b"\xea" * lunghezza_blocco_tipo    # chr(int(0xEA)) * 10


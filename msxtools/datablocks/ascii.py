from datablocks.generic import GenericDataBlock
from datablocks.intestazioni import Intestazioni
from datablocks.wav import Esportazione


class AsciiFile(GenericDataBlock):

    intestazione = b"\xea" * 10

    # --=-=--------------------------------------------------------------------------=-=--

    @property
    def type(self):
        return "ascii"

    # --=-=--------------------------------------------------------------------------=-=--

    def esporta(self, p_file: Esportazione):

        p_file.inserisci_sincronismo(2500)  # Tre secondi

        intestazione = self.intestazione + self.title.encode("ascii")

        p_file.inserisci_stringa(intestazione)

        p_file.inserisci_silenzio(1000)

        p_file.inserisci_sincronismo(1500)  # Tre/quarti di secondo

        ind = 0
        conto = 0
        continua = True
        temp = b""
        # p_file.inserisci_stringa(self.dati)
        while continua:
            if ind < (len(self.dati)):
                a = self.dati[ind:ind + 1]
                b = ord(a)
                p_file.inserisci_byte(b)
                temp += a
                if conto > 255:
                    #if a == b"\n":
                        #print("-----------------------------")
                        #print(temp)
                        #print("=============================")
                        #temp = b""
                    p_file.inserisci_silenzio(500)
                    p_file.inserisci_sincronismo(1000)
                    conto = 0
            else:
                # p_file.inserisci_byte(26)
                # temp += "[FINE]"
                if conto > 0:
                    while conto < 255:
                        p_file.inserisci_byte(26)  # EOF
                        temp += b"\x1a"
                        conto += 1
                continua = False
            ind += 1
            conto += 1

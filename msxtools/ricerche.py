from .intestazioni import Intestazioni
from .bloccodati import FileAscii, FileBasic, FileBinario, FileCustom


class Ricerca:

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, p_dati:bytes):
        self._buffer = p_dati
        if len(self._buffer) > 0:
            self._posizione = 0
        else:
            self._posizione = -1

    # --=-=--------------------------------------------------------------------------=-=--

    def __init__(self):

        self._posizione = -1
        self._buffer = b""

    # --=-=--------------------------------------------------------------------------=-=--

    def ricerca_blocco(self):
        """
        Ricerca il primo blocco dati che trova a partire dai dati grezzi

        Returns:
            Un indice al primo byte successivo alla fine del blocco che ha trovato,
            in modo da poter richiamare nuovamente la funzione importa per cercare
            il blocco successivo.
        """

        # Il blocco inizia con un'intestazione ?
        if self.contiene_intestazione():

            # Si. Vuol dire che si tratta di un blocco ASCII, Basic, Binario o custom
            blocco = self.verifica_tipo_blocco()

            # Cerca il titolo del file (6 caratteri)
            if blocco.tipo is not FileCustom:
                inizio_titolo = Intestazioni.lunghezza_intestazione \
                                + Intestazioni.lunghezza_blocco_tipo
                blocco.titolo = self.buffer[inizio_titolo:inizio_titolo + 6].decode("ascii")
            else:
                blocco._titolo = ""

            # Cerca di individuare l'inizio e la fine della parte dati
            if blocco.tipo is not FileCustom:
                inizio_dati = self.buffer.find(Intestazioni.blocco_intestazione, Intestazioni.lunghezza_intestazione) \
                              + Intestazioni.lunghezza_intestazione
            else:
                inizio_dati = Intestazioni.lunghezza_intestazione

            fine_dati = self.buffer.find(Intestazioni.blocco_intestazione,
                                         inizio_dati + Intestazioni.lunghezza_intestazione)

            # Se non trova la fine dei dati vuol dire che è arrivato alla fine della
            # cassetta e non ci sono altre intestazioni da trovare. Prende come dimensione
            # massima la lunghezza complessiva del blocco
            if fine_dati < 0:
                fine_dati = len(self.buffer)

            # Memorizza il blocco dati
            blocco.dati = self.buffer[inizio_dati:fine_dati]

            # Elimina dal buffer tutto quello che ha analizzato finora
            # (Riduce il buffer togliendo tutto il blocco che ha appena scovato)
            self.buffer = self.buffer[fine_dati:]

        else:
            # No. Non ha un'intestazione... allora è per forza un blocco custom
            blocco = FileCustom()
            blocco.dati = self.buffer

            # Elimina dal buffer tutto quello che ha analizzato finora
            # (Riduce il buffer togliendo tutto il blocco che ha appena scovato)
            self.buffer = b""

        # Ora, prima di restituire il blocco controlla che il blocco che ha
        # appena rilevato è di tipo ASCII e se il blocco finisce con un carattere
        # di EOF
        if blocco.tipo is FileAscii:
            # print(blocco.dati)
            contiene_eof = blocco.dati.find(b"\x1a") >= 0
            while not contiene_eof:
                altro_blocco = self.ricerca_blocco()
                blocco += altro_blocco
                contiene_eof = altro_blocco.dati.find(b"\x1a") >= 0
        return blocco

    # --=-=--------------------------------------------------------------------------=-=--

    def contiene_intestazione(self):
        """
        Verifica se un una stringa contenente bytes inizia con un blocco di
        intestazione MSX

        Args:
            p_dati: stringa di bytes da analizzare

        Returns:
            True se la stringa di bytes inizia con l'intestazione ricercata,
            altrimenti False
        """

        return self.buffer[:Intestazioni.lunghezza_intestazione] == Intestazioni.blocco_intestazione

    # --=-=--------------------------------------------------------------------------=-=--

    def verifica_tipo_blocco(self):

        inizio = Intestazioni.lunghezza_intestazione

        # print("Intestazione: {0}-{1} - Dati: {1}-{2}".format(str(inizio_intestazione),
        # str(inizio_dati), str(fine_dati)))

        # Cerca il tipo del file
        tipo_blocco = self.buffer[inizio:inizio + 10]

        if tipo_blocco == FileAscii.intestazione:
            return FileAscii()
        elif tipo_blocco == FileBasic.intestazione:
            return FileBasic()
        elif tipo_blocco == FileBinario.intestazione:
            return FileBinario()
        else:
            return FileCustom()

    # --=-=--------------------------------------------------------------------------=-=--

    def eof(self) -> bool:
        """
        Indica se è arrivato al termine del file

        Returns:
            True se è arrivato al termine
        """

        return len(self.buffer) == 0

    # --=-=--------------------------------------------------------------------------=-=--
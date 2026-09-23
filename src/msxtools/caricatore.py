import math

from .datablocks import AsciiFile
from .datablocks.wav import Esportazione
from .datablocks.wav.parametri import Parametri
from .eccezioni import Eccezione


# --=-=--------------------------------------------------------------------------=-=--

def programma_basic(p_titolo: bytes, p_crediti: bytes, p_parti: int,
                    p_attesa: bytes = None) -> bytes:
    """
    Crea il loader in BASIC (in formato ASCII) che mostra la schermata di
    caricamento e carica una dopo l'altra le parti della ROM

    Args:
        p_titolo:  Il titolo del gioco, già pronto per il PRINT
        p_crediti: La riga in fondo allo schermo (anno e sviluppatore)
        p_parti:   Il numero di parti (blocchi binari) da caricare
        p_attesa:  Il tempo di caricamento stimato (es. b"3m 42s @ 2205bps"), mostrato
                   sotto "NOW LOADING"; se manca la riga non compare

    Returns:
        Il programma, terminato dal carattere di fine file (1Ah)
    """

    # La barra è "[" + 24 caselle + "]" e si riempie con CHR$(219), il blocco pieno
    # del set di caratteri MSX internazionale. Dopo la parte K di N le caselle piene
    # sono 24 * K / N (arrotondato per difetto): 24 si divide esattamente per 2, 3,
    # 4, 6 e 8 parti (fino a una ROM da 128Kb), quindi i passi sono tutti uguali
    caselle = 24
    if p_parti < 1:
        raise Eccezione("The loading screen needs at least 1 block, not {0}".format(p_parti))

    # Schermata (24 righe): titolo e "NOW LOADING", 6 righe vuote, la barra di
    # avanzamento con sotto le percentuali, 5 righe vuote e i crediti. Il blocco è
    # alto 16 righe e viene centrato verticalmente (righe 4-19)
    altezza = 16
    riga_titolo = (24 - altezza) // 2
    riga_barra = str(riga_titolo + 8).encode("ascii")
    riga_percentuali = str(riga_titolo + 9).encode("ascii")
    riga_crediti = str(riga_titolo + altezza - 1).encode("ascii")
    righe = [p_titolo, b"NOW LOADING - PLEASE WAIT", p_crediti, b"[" + b"." * caselle + b"]"]
    # Testi centrati sulle 40 colonne impostate da WIDTH 40
    cols = [str((40 - len(riga)) // 2).encode("ascii") for riga in righe]
    col_barra = int(cols[3])

    # Percentuali sotto la barra: "0%" sotto la prima casella, "50%" con le cifre
    # a cavallo della metà, "100%" che finisce sotto l'ultima casella
    percentuali = bytearray(b" " * caselle)
    for colonna, testo in ((0, b"0%"), (caselle // 2 - 1, b"50%"), (caselle - 4, b"100%")):
        percentuali[colonna:colonna + len(testo)] = testo
    percentuali = bytes(percentuali).rstrip()

    basic  = b'1 POKE&HFBB0,1:POKE&HFBB1,1:KEYOFF:SCREEN0:WIDTH 40:COLOR15,8,8\r\n'
    basic += b'2 LOCATE' + cols[0] + b',' + str(riga_titolo).encode("ascii") \
             + b':PRINT"' + righe[0] + b'"\r\n'
    basic += b'3 LOCATE' + cols[1] + b',' + str(riga_titolo + 1).encode("ascii") \
             + b':PRINT"' + righe[1] + b'"'
    if p_attesa:
        # Tempo stimato sulle righe 7 e 8, nello spazio vuoto sotto "NOW LOADING"
        for scarto, testo in ((3, b"Estimated wait time:"), (4, p_attesa)):
            basic += b':LOCATE' + str((40 - len(testo)) // 2).encode("ascii") + b',' \
                     + str(riga_titolo + scarto).encode("ascii") + b':PRINT"' + testo + b'"'
    basic += b'\r\n'
    # Il ";" finale evita l'a capo (e lo scorrimento dello schermo se la riga è l'ultima)
    basic += b'4 LOCATE' + cols[2] + b',' + riga_crediti + b':PRINT"' + righe[2] + b'";\r\n'
    basic += b'5 LOCATE' + cols[3] + b',' + riga_barra + b':PRINT"' + righe[3] + b'";:LOCATE' \
             + str(col_barra + 1).encode("ascii") + b',' + riga_percentuali \
             + b':PRINT"' + percentuali + b'";\r\n'
    basic += b'6 BLOAD"cas:",R\r\n'

    # Una riga per ogni parte successiva, senza cicli né calcoli: tra la fine di
    # una parte e il BLOAD della successiva il BASIC deve metterci il meno possibile,
    # altrimenti il nastro potrebbe superare l'intestazione del blocco seguente.
    # Posizione e caratteri pieni sono già scritti nel programma
    for parte in range(1, p_parti):
        gia_piene = caselle * (parte - 1) // p_parti
        riempimento = caselle * parte // p_parti - gia_piene
        riga = str(6 + parte).encode("ascii") + b' '
        # Con più di 24 parti alcune non aggiungono caselle: resta solo il BLOAD
        if riempimento > 0:
            riga += b'LOCATE' + str(col_barra + 1 + gia_piene).encode("ascii") \
                    + b',' + riga_barra + b':PRINT"' + b"\xdb" * riempimento + b'";:'
        basic += riga + b'BLOAD"cas:",R\r\n'

    return basic + b"\x1a"


# --=-=--------------------------------------------------------------------------=-=--

class ContaDurata:
    """
    Si comporta come Esportazione, ma invece di scrivere il file WAV conta quanto
    durerebbe, in "tempi di bit": un bit, o un tratto di silenzio lungo quanto un bit,
    dura 1 / bitrate secondi (vedi Parametri)
    """

    def __init__(self, p_bitrate: int):
        self.bitrate = p_bitrate
        self.tempi = 0

    def inserisci_bit(self, p_bit: int):
        self.tempi += 1

    def inserisci_byte(self, p_byte):
        # Bit di start, 8 bit di dati e 2 bit di stop
        self.tempi += 11

    def inserisci_stringa(self, p_stringa):
        self.tempi += 11 * len(p_stringa)

    def inserisci_silenzio(self, p_durata: float):
        self.tempi += math.ceil(self.bitrate * p_durata / 1000)

    def inserisci_sincronismo(self, p_durata: float):
        self.tempi += int(self.bitrate * (p_durata / 1000))

    @property
    def secondi(self) -> float:
        return self.tempi / self.bitrate


def durata_caricamento(p_blocchi, p_bitrate: int) -> float:
    """
    Calcola quanto dura sul nastro il caricamento dei blocchi, ognuno preceduto dalla
    pausa che lo separa dal blocco precedente (come in Tape.export_to_wav)

    Args:
        p_blocchi: I blocchi da caricare
        p_bitrate: La velocità di trasmissione in bps

    Returns:
        La durata in secondi
    """
    conta = ContaDurata(p_bitrate)
    for blocco in p_blocchi:
        conta.inserisci_silenzio(Esportazione.pausa_tra_blocchi)
        blocco.esporta(conta)
    return conta.secondi


def messaggio_di_attesa(p_secondi: float, p_bitrate: int) -> bytes:
    """
    Formatta il tempo di attesa per la schermata di caricamento, es. b"3m 42s @ 2205bps"
    (i secondi sono arrotondati per eccesso)
    """
    minuti, secondi = divmod(math.ceil(p_secondi), 60)
    return "{0}m {1:02d}s @ {2}bps".format(minuti, secondi, p_bitrate).encode("ascii")


# --=-=--------------------------------------------------------------------------=-=--

class LoaderBasic(AsciiFile):
    """
    Il loader in BASIC che precede le parti di una ROM sul nastro. Il programma mostra
    il tempo di caricamento stimato, che dipende dal bitrate: per questo viene ricreato
    quando serve, con il bitrate del momento (che si può cambiare dopo aver letto la ROM)
    """

    def __init__(self, p_titolo: bytes, p_crediti: bytes, p_blocchi: list):
        """
        Args:
            p_titolo:  Il titolo del gioco, già pronto per il PRINT
            p_crediti: La riga in fondo allo schermo (anno e sviluppatore)
            p_blocchi: I blocchi binari con le parti della ROM, nell'ordine di caricamento
        """
        self._titolo_gioco = p_titolo
        self._crediti = p_crediti
        self._blocchi = p_blocchi
        self._cache = {}
        super().__init__()

    @property
    def dati(self):
        bitrate = Parametri.bitrate
        if bitrate not in self._cache:
            attesa = messaggio_di_attesa(durata_caricamento(self._blocchi, bitrate), bitrate)
            programma = programma_basic(self._titolo_gioco, self._crediti, len(self._blocchi), attesa)
            # Come i loader salvati dall'MSX, occupa almeno un segmento intero
            self._cache[bitrate] = programma.ljust(256, b"\x00")
        return self._cache[bitrate]

    @dati.setter
    def dati(self, p_valore):
        # Il programma è sempre ricreato dai dati del gioco: le assegnazioni si ignorano
        pass

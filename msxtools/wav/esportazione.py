from ..intestazioni import Intestazioni
from .parametri import Parametri

import wave


# 1200 x 9 campionamenti (minimo) = 10.800hz
# 2400 x 9 campionamenti (minimo) = 21.600hz
# 4800 x 9 campionamenti (minimo) = 43.200hz


class Esportazione:

    max_buffer = 32768  # 32Kb

    def __init__(self, p_file_output="output.wav", p_bitrate:int = -1):
        """
        Costruttore della classe

        Args:
            p_file_output:	Percorso e nome del file WAV che dovrà creare
                            ed in cui dovrà esportare i file.

        Returns:
            None
        """

        # Prima di cominciare decide la velocità a cui dovranno essere scritti i file
        # nel file wave. Più è veloce, minore sarà la durata richiesta all'MSX per
        # caricare un file.
        # Parametri.bitrate = 1200

        # Ora che ha scelto il bitrate gli faccio preparare all'interno di alcuni
        # array le forme d'onda quadre per rappresentare gli zeri e gli uni da
        # scrivere all'interno del file wave. Questo perchè se dovessi generarli ogni
        # volta in tempo reale ci impiegherebbe un sacco di tempo, mentre se invece faccio
        # così, creo degli array in memoria e poi dico al programma di scrivere il
        # contenuto degli array su disco ci mette MOLTO MENO!
        if p_bitrate != Parametri.bitrate:
            if p_bitrate <= 0:
                p_bitrate = Parametri.bitrate
            else:
                Parametri.bitrate = p_bitrate
            Parametri.ricalcola_onde()

        # Apre il file wav sul disco e si prepara a scriverci dentro
        self.file_audio = wave.open(p_file_output, "w")

        # Inizializza il file wav con la frequenza richiesta
        self.file_audio.setparams((1, 1, Parametri.frequenza, 0, 'NONE', 'not compressed'))

        self.buffer = []

    # --------------------------------------------------------------------------------

    def inserisci_bit(self, p_bit: int):
        """
        Inserisce un bit (0 o 1) nel file wave, come forma d'onda a 1200 o 2400baud
        (se la velocità di trasmissione è impostata a 1200baud), oppure come forma
        d'onda a 2400 o 4800baud (se la velocità di trasmissione è impostata a
        2400baud)

        Args:
            p_bit: Il bit da scrivere nel file wave (0 oppure 1)

        Returns:
            None
        """

        # Anzichè dover scrivere ogni volta la forma d'onda quadra, la creo una volta
        # per tutte all'interno della classe parametri prima di iniziare, e poi
        # dico al programma di fare copia e incolla dalla classe al file WAV.
        # Per ulteriori informazioni vedi le note in parametri.py

        # Invece di scrivere direttamente sul file WAV (operazione MOLTO LENTA se fatta byte per byte)
        # si tiene in un array un buffer di valori da scrivere sul file. Quando la lunghezza di questo
        # array supera una certa dimensione (regolata da Esportazione.max_buffer) li scrive finalmente
        #  sul file e svuota il buffer. Se termina l'esportazione con Esportazione.chiudi() scrive tutti
        # i dati rimanenti nel buffer sul file.

        if p_bit == 0:
            self.buffer.extend(Parametri.wave_bit_0)  # self.file_audio.writeframes(bytes(Parametri.wave_bit_0))

        elif p_bit == 1:
            self.buffer.extend(Parametri.wave_bit_1)  # self.file_audio.writeframes(bytes(Parametri.wave_bit_1))

        if len(self.buffer) >= Esportazione.max_buffer:
            self.file_audio.writeframes(bytes(self.buffer))
            self.buffer = []

    # --------------------------------------------------------------------------------

    def inserisci_byte(self, p_byte):
        """
        Prende un byte (che viene passato alla funzione come parametro)
        e lo scrive nel file WAV sotto forma di forme d'onda.
        E' importante ricordarsi che per lo standard MSX, per ogni byte da scrivere
        bisogna farlo anticipare da un bit di start (valore 0) e farlo finire
        con due bit di stop (valore 1). Se ad esempio sto facendo un file wav alla
        velocità di 1200baud (parlo di velocità di lettura per l'MSX) dovrà introdurre
        il byte con un bit di start a 1200baud/bps, e farlo terminare con due bit
        di stop a 2400baud/bps.

        Args:
            p_byte: Il byte da scrivere nel file wav

        Returns:
            None
        """

        # Inserisce un bit di start
        self.inserisci_bit(0)

        # Otto bit di dati
        for ind in range(8):
            if (p_byte & 1) == 0:
                self.inserisci_bit(0)
            else:
                self.inserisci_bit(1)
            p_byte >>= 1  # Bitwise.ShiftRight(P_nByte, 1)

        # Inserisce due bit di stop
        self.inserisci_bit(1)
        self.inserisci_bit(1)

    # --------------------------------------------------------------------------------

    def inserisci_stringa(self, p_stringa):

        for elemento in p_stringa:
            self.inserisci_byte(elemento)

    # --------------------------------------------------------------------------------

    def inserisci_silenzio(self, p_durata: float):
        """
        Inserisce un intervallo di silenzio all'interno del file wav. Spesso
        serve mettere del silenzio fra un file e l'altro, in modo da dare il
        tempo all'MSX di processare i dati appena caricati.

        Args:
            p_durata: Durata del silenzio espressa in millisecondi

        Returns:
            None
        """

        # Parametri.bitrate rappresenta il numero di bit che possono essere
        # trasmessi in un secondo. Il silenzio per come l'ho strutturato io
        # è un segnale piatto che dura quanto un normale bit. Se ad esempio
        # voglio creare un silenzio che duri 2 secondi a 1200baud/bps ad
        # esempio devo inserire nel file wav il silenzio
        # per 1200 (baud) x 2 (secondi) = 2400 volte.
        # Ecco da dove nasce il conto del ciclo for.

        for ind in range(int(Parametri.bitrate * (p_durata / 1000))):
            self.buffer.extend(Parametri.wave_silenzio)  # self.file_audio.writeframes(bytes(Parametri.wave_silenzio))

        # Se il buffer è abbastanza pieno, li scrive nel file wav
        # (il che è molto più veloce che scrivere byte per byte sul file wav)
        if len(self.buffer) >= Esportazione.max_buffer:
            self.file_audio.writeframes(bytes(self.buffer))
            self.buffer = []

    # --------------------------------------------------------------------------------

    def inserisci_sincronismo(self, p_durata: float):
        """
        Inserisce un segnale di sincronismo nel file wav. Sentire il segnale
        di sincronismo serve all'MSX per capire che sta per arrivare un file.

        Args:
            p_durata: Durata del segnale di sincronismo espressa in millisecondi

        Returns:
            None
        """

        # Parametri.bitrate rappresenta il numero di bit che possono essere
        # trasmessi in un secondo. Siccome il segnale di sincronismo è composto
        # da tanti bit di valore 1, per creare un segnale di sincronismo che
        # dura 2 secondi a 1200baud/bps ad esempio devo inserire nel file wav
        # il bit 1 per 1200 (baud) x 2 (secondi) = 2400 volte.
        # Ecco da dove nasce il conto del ciclo for.

        for ind in range(int(Parametri.bitrate * (p_durata / 1000))):
            self.inserisci_bit(1)

    # --------------------------------------------------------------------------------

    def test(self):
        """
        Esegue un test creando un file con un programmino in Basic
        codificato in formato ASCII
        """

        self.inserisci_sincronismo(2000)  # Tre secondi

        intestazione = Intestazioni.blocco_file_ascii + b"PROVA "

        for elemento in intestazione:
            self.inserisci_byte(elemento)

        self.inserisci_silenzio(750)

        self.inserisci_sincronismo(1000)  # Tre/quarti di secondo

        stringa = b"10 PRINT \"CIAO A TUTTI BELLI E BRUTTI\"\x1a"
        stringa = stringa.ljust(256, bytes([26]))
        for elemento in stringa:
            self.inserisci_byte(elemento)

        self.chiudi()

    # --------------------------------------------------------------------------------

    def chiudi(self):
        """
        Chiude il file wave aperto
        """

        if len(self.buffer) != 0:
            self.file_audio.writeframes(bytes(self.buffer))
            self.buffer = []

        self.file_audio.close()


if __name__ == '__main__':
    # Test

    import time

    start_time = time.time()

    suono = Esportazione()
    suono.test()

    print("--- {0:.3} secondi ---".format(time.time() - start_time))

    # os.system("open " + os.getcwd() + "/output.wav")
    # os.system("/Applications/openMSX.app/Contents/MacOS/openmsx -cassetteplayer "
    #           + "/Users/Scala/Documents/Progetti/Progetti\ Python/prova-wave/output.wav")

import hashlib
import json
import os
import tempfile
import zipfile

# from .intestazioni import Intestazioni
from .datablocks import BinaryFile, AsciiFile
from .loader import Loader
from .eccezioni import Eccezione
from .ricerche import Ricerca
from .datablocks.wav import Esportazione
from .datablocks.wav.parametri import Parametri
from .datablocks.strumenti import Indirizzo
from .manifest import Manifest, CARTELLA_VARIANTI, NOME_MANIFEST, testo_per_basic
from .datablocks.intestazioni import Intestazioni
from .caricatore import LoaderBasic, programma_basic


def sha_256_complessivo(p_hash: dict) -> str:
    """
    Calcola l'hash SHA-256 di un insieme di file, a partire dai loro hash: è l'hash
    dell'elenco scritto da sha256sum, una riga "<sha256>  <percorso>" per ogni file,
    nell'ordine in cui sono indicati (quello della sezione "files" del manifest).
    Si verifica con: sha256sum game.cas variants/game.wav | sha256sum

    Args:
        p_hash: Per ogni percorso (es. "variants/game.wav") il suo hash SHA-256, in ordine

    Returns:
        L'hash SHA-256 complessivo
    """
    elenco = "".join("{0}  {1}\n".format(hash_file, percorso) for percorso, hash_file in p_hash.items())
    return hashlib.sha256(elenco.encode("utf-8")).hexdigest()


class Tape:
    """
    _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_
    MSX TAPE class - Reads and writes on a virtual tape file (.CAS)
    Version 1.0
    _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_
    """

    # --=-=--------------------------------------------------------------------------=-=--

    def __init__(self, p_file: str = None, p_manifest: Manifest = None):
        """
        Costruttore della classe

        Args:
            p_file:     Il file .CAS da leggere, oppure la ROM (.ROM / .MX1) da importare
            p_manifest: Per le ROM, i testi da mostrare nella schermata di caricamento

        Returns:
            None
        """

        # Inizializza i vari array, per partire con una nuova cassetta
        self._cassetta = []  # Array che contiene i blocchi di dati che compongono la cassetta
        self._ricerca = Ricerca()  # Buffer dati in cui immagazzina temporaneamente il file .cas da analizzare
        self.indice = -1
        self.posizione = -1
        self._ricerca = Ricerca()

        if p_file:
            if self.e_una_rom(p_file):
                # ROM
                self.importa_rom(p_file, p_manifest)
            else:
                # CAS file
                self.load(p_file)

    # --=-=--------------------------------------------------------------------------=-=--

    def load(self, p_file):
        """
        Carica un file cas in memoria

        Args:
            p_file:	Il percorso al file .CAS da caricare

        Returns:

        """

        try:
            # Legge il file .CAS dal disco
            with open(p_file, "rb") as f:
                self._ricerca.buffer = f.read()
        except OSError as e:
            raise Eccezione("Unable to read tape \"{0}\": {1}".format(p_file, e.strerror or e)) from e

        try:
            # Finchè resta qualcosa nel buffer da analizzare...
            while not self._ricerca.eof():
                # Con quello che gli rimane del buffer va alla ricerca del
                # primo blocco che riesce a trovare
                blocco = self._ricerca.ricerca_blocco()

                # Aggiunge il blocco che ha trovato alla cassetta
                self.add(blocco)
        except Exception as e:
            raise Eccezione("\"{0}\" is not a valid MSX tape ({1})".format(p_file, e)) from e

    # --=-=--------------------------------------------------------------------------=-=--

    def add(self, p_blocco):
        """
        Aggiunge un nuovo blocco-dati alla cassetta

        Args:
          p_blocco: I dati effettivi del blocco

        Returns:
            None
        """
        self._cassetta.append(p_blocco)

    # --=-=--------------------------------------------------------------------------=-=--

    @staticmethod
    def e_una_rom(p_file) -> bool:
        """
        Indica se un file è una ROM (.ROM / .MX1) anziché una cassetta
        """
        return str(p_file).lower().endswith((".rom", ".mx1"))

    # --=-=--------------------------------------------------------------------------=-=--

    @staticmethod
    def _titolo_rom(p_nome_file):
        """
        Ricava dal nome del file il titolo da mostrare nella schermata di caricamento

        Args:
            p_nome_file: Il percorso al file .ROM

        Returns:
            Il titolo in maiuscolo, senza caratteri che romperebbero il PRINT del BASIC
        """
        titolo = os.path.splitext(os.path.basename(p_nome_file))[0]
        return testo_per_basic(titolo.replace("_", " ").replace("-", " "))

    # --=-=--------------------------------------------------------------------------=-=--

    programma_basic = staticmethod(programma_basic)

    # --=-=--------------------------------------------------------------------------=-=--

    def importa_rom(self, p_nome_file, p_manifest: Manifest = None):

        # Legge il file .ROM dal disco
        f = open(p_nome_file, "rb")
        buffer = f.read()
        f.close()

        nome_rom = os.path.basename(p_nome_file)

        # I loader in linguaggio macchina sanno gestire ROM fino a 48Kb
        if len(buffer) > 49152:
            raise Eccezione("ROM \"{0}\" is {1} bytes long, only ROMs up to 48KB are supported"
                            .format(nome_rom, len(buffer)))

        # Le ROM oltre i 32Kb sono mappate in 0000h-BFFFh, con l'intestazione "AB"
        # all'inizio della pagina 1 (offset 4000h). Quelle mappate in 4000h-FFFFh
        # (intestazione all'offset 0) non si possono caricare: la pagina 3 è
        # occupata dall'area di sistema del BIOS
        if len(buffer) > 32768 and buffer[0x4000:0x4002] != b"AB":
            raise Eccezione("ROM \"{0}\" is not a 48KB ROM mapped at 0000h-BFFFh "
                            "(no \"AB\" header at offset 4000h), it can't be loaded from tape"
                            .format(nome_rom))

        # I testi della schermata di caricamento arrivano dal manifest, se c'è;
        # altrimenti il titolo si ricava dal nome del file
        manifest = p_manifest or Manifest()

        # Ogni parte da 16Kb viene caricata a 9000h insieme al loader che la copia
        # nella pagina giusta. L'ultimo loader avvia il gioco, gli altri tornano al
        # BASIC, che carica la parte successiva
        if len(buffer) <= 16384:
            programma = [(buffer, Loader.binari_16k_4000h)]
        elif len(buffer) <= 32768:
            programma = [(buffer[:16384], Loader.binari_32k_4000h),
                         (buffer[16384:], Loader.binari_32k_8000h)]
        else:
            # La pagina 0 va in RAM al posto del BIOS, che però serve per leggere la
            # cassetta: viene copiata prima dell'ultima parte, e il BIOS rimesso subito
            programma = [(buffer[0x4000:0x8000], Loader.binari_32k_4000h),
                         (buffer[0x0000:0x4000], Loader.binari_48k_0000h),
                         (buffer[0x8000:], Loader.binari_48k_8000h)]

        # Nomi dei file sul nastro: quelli scelti nel manifest, altrimenti il nome
        # della ROM per il loader e DATA1, DATA2... per le parti
        nomi = manifest.nomi_nastro(len(programma))
        if nomi is None:
            nomi = (os.path.splitext(os.path.basename(p_nome_file))[0],
                    ["DATA" + str(indice + 1) for indice in range(len(programma))])

        blocchi = []
        for indice, (elemento, a) in enumerate(programma):
            blocco = BinaryFile()
            blocco.title = nomi[1][indice]

            # I loader copiano la ROM a partire da 0x9000 (LD HL,9000h), e il loader
            # viene accodato subito dopo la ROM: l'esecuzione deve partire da lì
            inizio = Indirizzo(0x9000)
            esecuzione = Indirizzo(inizio.valore + len(elemento))
            blocco.importa_rom(elemento, a,
                               indirizzo_inizio=inizio, indirizzo_esecuzione=esecuzione)

            blocchi.append(blocco)

        # Il loader BASIC mostra il tempo di caricamento delle parti che lo seguono,
        # calcolato con il bitrate del momento in cui la cassetta viene esportata
        blocco_loader = LoaderBasic(
            testo_per_basic(manifest.title) or self._titolo_rom(p_nome_file),
            testo_per_basic(manifest.riga_crediti()) or b"(C) 2016-20 MASTROPIERO",
            blocchi)
        blocco_loader.title = nomi[0]

        self.add(blocco_loader)
        for blocco in blocchi:
            self.add(blocco)

        """
        a = len(Loader.binari_32k_4000h)
        b = len(Loader.binari_32k_8000h)

        ind = 0
        ind2 = 0
        while ind < len(buffer):

            blocco = BinaryFile()

            blocco.title = os.path.splitext(os.path.basename(p_nome_file))[0]

            a = buffer[ind:ind + 16384]
            b = len(a)
            c = int(a[2])
            d = int(a[3])
            e = hex(c) + hex(d)
            if ind2 == 0:
                blocco.importa(buffer[ind:ind + 16384], Loader.binari_32k_4000h)
            else:
                blocco.importa(buffer[ind:ind + 16384], Loader.binari_32k_8000h)

            self.aggiungi(blocco)

            ind += 16384
            ind2 += 1
        """

    # --=-=--------------------------------------------------------------------------=-=--

    def importa_ascii(self, p_titolo, p_dati):

        blocco = AsciiFile()
        blocco.title = p_titolo
        blocco.dati = p_dati

        self.add(blocco)

    # --=-=--------------------------------------------------------------------------=-=--

    def rimuovi(self, p_indice):
        """
        Rimuove un blocco specifico dalla cassetta

        Args:
            p_indice: Indice del blocco da rimuovere

        Returns:
            None se risce ad eliminare il blocco, altrimenti solleva un'eccezione
        """

        if -len(self._cassetta) <= p_indice < len(self._cassetta):
            del self._cassetta[p_indice]
        else:
            raise Eccezione("The tape element you want to remove is out of bounds")

    # --=-=--------------------------------------------------------------------------=-=--

    def cas_in_bytes(self, p_file_index=-1) -> bytes:
        """
        Restituisce la cassetta nel formato .CAS, il formato usato dagli emulatori

        Args:
            p_file_index: Se indicato esporta solo il numero di file
                          selezionato

        Returns:
            Il contenuto del file .CAS
        """

        blocchi = self._cassetta if p_file_index < 0 else [self._cassetta[p_file_index]]

        cassetta = bytearray()
        for blocco in blocchi:
            for parte in blocco.parti_cas():
                if blocco.intestazione_cas:
                    # Le intestazioni devono iniziare a una posizione multipla di 8
                    cassetta += b"\x00" * (-len(cassetta) % 8)
                    cassetta += Intestazioni.blocco_intestazione
                cassetta += parte

        return bytes(cassetta)

    # --=-=--------------------------------------------------------------------------=-=--

    def export_to_cas(self, p_file="output.cas", p_file_index=-1):
        """
        Scrive la cassetta in un file .CAS, il formato usato dagli emulatori

        Args:
            p_file:       Percorso e nome del file .CAS da creare
            p_file_index: Se indicato esporta solo il numero di file
                          selezionato

        Returns:
            None
        """

        with open(p_file, "wb") as f:
            f.write(self.cas_in_bytes(p_file_index))

    # --=-=--------------------------------------------------------------------------=-=--

    def export_to_zip(self, p_file="output.zip", p_file_index=-1, p_manifest: dict = None):
        """
        Crea un archivio .ZIP (compressione massima) con la cassetta in formato .CAS,
        la sua versione audio .WAV nella cartella variants e, se indicato, il manifest.
        I file .CAS e .WAV prendono il nome dell'archivio (es. gioco.zip -> gioco.cas,
        variants/gioco.wav)

        Args:
            p_file:       Percorso e nome del file .ZIP da creare
            p_file_index: Se indicato esporta solo il numero di file
                          selezionato
            p_manifest:   I campi del manifest, salvato come _manifest.json con in
                          coda "files": formato, destinazione e hash SHA-256 di ogni
                          file dello zip, con le cartelle come oggetti annidati, e
                          "sha_256": l'hash di tutti i file (vedi sha_256_complessivo).
                          "files" e "sha_256" già presenti vengono sostituiti

        Returns:
            None
        """

        nome = os.path.splitext(os.path.basename(p_file))[0]
        nome_cas = nome + ".cas"
        nome_wav = nome + ".wav"

        with tempfile.TemporaryDirectory() as cartella:
            file_wav = os.path.join(cartella, nome + ".wav")
            self.export_to_wav(file_wav, p_file_index)
            cas = self.cas_in_bytes(p_file_index)

            with zipfile.ZipFile(p_file, "w", compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=9) as archivio:
                archivio.writestr(nome_cas, cas)
                archivio.write(file_wav, CARTELLA_VARIANTI + "/" + nome_wav)
                if p_manifest is not None:
                    hash_cas = hashlib.sha256(cas).hexdigest()
                    with open(file_wav, "rb") as f:
                        hash_wav = hashlib.file_digest(f, "sha256").hexdigest()
                    dati = {chiave: valore for chiave, valore in p_manifest.items()
                            if chiave not in ("files", "sha_256")}
                    # Il .cas va sempre per primo, anche se in ordine alfabetico verrebbe
                    # dopo "variants": per questo il JSON si scrive senza sort_keys
                    dati["files"] = {
                        nome_cas: {
                            "format": "MSX Virtual Cassette (.cas)",
                            "target": "Emulation",
                            "fidelity": Tape.fedelta_dei_formati[".cas"],
                            "sha_256": hash_cas,
                        },
                        CARTELLA_VARIANTI: {
                            nome_wav: {
                                "format": "Wave Audio File @ {0}bps".format(Parametri.bitrate),
                                "target": "Real Hardware",
                                "fidelity": Tape.fedelta_dei_formati[".wav"],
                                "sha_256": hash_wav,
                            },
                        },
                    }
                    # Stesso ordine della sezione "files"
                    dati["sha_256"] = sha_256_complessivo(
                        {nome_cas: hash_cas, CARTELLA_VARIANTI + "/" + nome_wav: hash_wav})
                    archivio.writestr(NOME_MANIFEST, (json.dumps(dati, indent=2, ensure_ascii=False)
                                                      + "\n").encode("utf-8"))

    # --=-=--------------------------------------------------------------------------=-=--

    def export_to_wav(self, p_file="output.wav", p_file_index=-1):
        """
        Test

        Args:
            p_file:       Percorso e nome del file WAV da creare
            p_file_index: Se indicato esporta solo il numero di file
                          selezionato

        Returns:
            None
        """

        suono = Esportazione(p_file)
        try:
            suono.inserisci_silenzio(Esportazione.pausa_ai_bordi)
            if p_file_index < 0:
                for ind, blocco in enumerate(self._cassetta):
                    blocco.esporta(suono)
                    if ind < (len(self._cassetta) - 1):
                        suono.inserisci_silenzio(Esportazione.pausa_tra_blocchi)
            else:
                self._cassetta[p_file_index].esporta(suono)
            suono.inserisci_silenzio(Esportazione.pausa_ai_bordi)
        finally:
            suono.chiudi()

    # --=-=--------------------------------------------------------------------------=-=--

    def __len__(self):
        """
        Restituisce il numero di blocchi contenuti nella cassetta

        Returns:
            Un numero intero che indica il numero dei blocchi contenuti nella cassetta
        """
        return len(self._cassetta)

    # --=-=--------------------------------------------------------------------------=-=--

    def __str__(self):
        """
        Fa un elenco dettagliato di tutti i blocchi presenti nella cassetta

        Returns:
            Una stringa con l'elenco dettagliato di tutti i blocchi presenti
            all'interno della cassetta
        """

        temp = ""
        if len(self._cassetta) > 0:
            # temp += "TAPE CONTENT:\n"
            temp += "-" * 42 + "\n"
            for indice, elemento in enumerate(self._cassetta):
                temp += "{0}. {1}\n".format(str(indice + 1).rjust(2), str(elemento))
            temp += "-" * 42 + "\n"

            if len(self._cassetta) > 1:
                total = "{0} Files found\n"
            else:
                total = "{0} File found\n"

            temp += total.format(str(len(self._cassetta))).rjust(42)

            return temp
        else:
            raise Eccezione("Tape is currently empty")

    # --=-=--------------------------------------------------------------------------=-=--

    def __repr__(self):
        return str(self)

    # --=-=--------------------------------------------------------------------------=-=--

    def __getitem__(self, p_value):
        return self._cassetta[p_value]

    # --=-=--------------------------------------------------------------------------=-=--

    # Comando con cui l'MSX carica un nastro, in base al tipo del primo blocco
    comandi_di_caricamento = {
        "ascii": 'RUN"CAS:"',
        "basic": "CLOAD",
        "binary": 'BLOAD"CAS:",R',
    }

    # Fedeltà al nastro originale di ogni formato, scritta nella sezione "files" del
    # manifest: il .cas conserva solo i dati, il .tsx anche la temporizzazione dei
    # blocchi, il .wav è il segnale audio completo
    fedelta_dei_formati = {".cas": "low", ".tsx": "medium", ".wav": "high"}

    def comando_di_caricamento(self, p_file_index=-1) -> str | None:
        """
        Restituisce il comando con cui caricare la cassetta (o solo il blocco indicato)

        Args:
            p_file_index: Se indicato considera solo il numero di file selezionato

        Returns:
            Il comando, oppure None se il primo blocco non ha un'intestazione MSX
            (es. un blocco custom, caricato dal blocco precedente)
        """
        if not self._cassetta:
            return None
        blocco = self._cassetta[p_file_index if p_file_index >= 0 else 0]
        return Tape.comandi_di_caricamento.get(blocco.type)

    # --=-=--------------------------------------------------------------------------=-=--

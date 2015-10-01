#!/usr/bin/env python
#prova
import os
import luigi


class MSXTape():

    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_
    # MSX TAPE class - Reads and writes on a virtual tape file (.CAS)
    # Version 1.0
    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_


    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_
    # GLOBAL PROPERTIES DECLARATION	
    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_

    MSX_FILE_NOT_FOUND, MSX_BINARY_FILE, MSX_BASIC_FILE, \
    MSX_ASCII_FILE, MSX_CUSTOM_BLOCK = range(5)

    HEADER = None

    DECLARE_BINARY_FILE = None
    DECLARE_BASIC_FILE = None
    DECLARE_ASCII_FILE = None

    G_nFilePos = None
    G_nFileType = None

    nOrder = None
    cTitle = None
    nType = None
    nBegin = None
    nEnd = None
    nStart = None
    nSize = None
    cData = None
    lDeleted = None

    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ 

    def __init__(self):

        # Il costruttore della classe, che inizializza il valore di alcune variabili utilizzate
        # all'interno della classe. Ad esempio G_Intestazione che contiene la serie di bytes (8)
        # utilizzata nel formato CAS per inserire un segnale di sincronizzazione per l'MSX
        # (Quella cosa che ascoltando l'audio all'inizio di un file fa BIIIIIIIIIIIIIIIIIIIIP...
        # Poi DECLARE_BINARY_FILE, Basic e ASCII che contengono i dieci byte che fanno capire nel
        # file CAS se quello che segue ? un File Binario, Basic o ASCII. */

        self.HEADER  = chr(int("0x1F")) . chr(int("0xA6")) . chr(int("0xDE"))
        self.HEADER += chr(int("0xBA")) . chr(int("0xCC")) . chr(int("0x13"))
        self.HEADER += chr(int("0x7D")) . chr(int("0x74"));

        self.DECLARE_BINARY_FILE = ""
        self.DECLARE_BASIC_FILE  = ""
        self.DECLARE_ASCII_FILE  = ""
        for nInd in xrange(0, 10): self.DECLARE_BINARY_FILE += chr(int("0xD0")) # str_pad("", 10, chr(int("0xD0")));
        for nInd in xrange(0, 10): self.DECLARE_BASIC_FILE  += chr(int("0xD3"))
        for nInd in xrange(0, 10): self.DECLARE_ASCII_FILE  += chr(int("0xEA"))

        # Inizializza i vari array, per partire con una nuova cassetta 
        self.newTape()	

    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_

    def newTape(self):

        # Azzera gli array e di fatto crea una nuova cassetta

        self.nOrder = 0
        self.cTitle = None
        self.nType = 0
        self.nBegin = 0
        self.nEnd = 0
        self.nStart = 0
        self.nSize = 0
        self.cData = None
        self.lDeleted = False

    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_

    def open(self, P_cFile):

        # Apre un file

        self.oFile .oFile = None
        self.cStream = ""
        self.nValue = 0

        P_cFile = os.path.join(os.getcwd(), P_cFile)

        if(os.path.exists(P_cFile)):

            oFile = open(P_cFile, "rb")

            cStream = oFile.read(8192)
            while (cStream != None):
                cStream += oFile.read(8192)

            oFile.close()

        return self.openStream(cStream)

    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_

    def openStream(P_cStream):

        # Scompone un file CAS in tanti files che andranno negli array

        nPos1 = 0
        nPos2 = 0
        nPos3 = 0
        nHeaderCount = 0
        nTypeFile = MSXTape.MSX_FILE_NOT_FOUND
        cTemp = ""
        cSlice = ""
        cSubSlice = ""
        lKeepSearching = True
        lCercaSottoporzioni = False
        lFirstHeaderFound = False

        # Cerca la prima intestazione

        nPos1 = self.seekHeader(P_cStream)

        while ( (nPos1 != False) and (lKeepSearching) ): # { // || ( ! lIntestazioneInizialeTrovata ) ) {

            lFirstHeaderFound = true;

            # Cerca la posizione dell'intestazione successiva
            # Con il parametro finale di CercaIntestazione settato su True,
            # gli dico di restituirmi sempre e comunque un valore, anche se 
            # non trova un'intestazione (mi da la fine del file in questo caso)

            #echo "nPos1 = " . $nPos1 . "<br/>";
            nPos2 = self.seekHeader(P_cStream, nPos1 + 1, True)
            #echo "nPos2 = " . $nPos2 . "<br/>"
            if(nPos2 == False): nPos2 = len(P_cStream)
            if (nPos2 != False ):

                # Tutto quello che sta nel mezzo fra un'intestazione e l'altra 
                # ? il corpo del file da catalogare

                cSlice = P_cStream[nPos1:(nPos2 - nPos1 + 1)]
                cSubSlice = ""

                nTypeFile = self.returnBlockType(cSlice)

                if (nTypeFile == MSXTape.MSX_BINARY_FILE):

                    # A questo punto sta trattando un file binario. Parte dal presupposto 
                    # che dei blocchi custom di codice devono essere preceduti da almeno un 
                    # file binario che faccia da "loader". Non è sempre detto che sia così...
                    # soprattutto con alcuni lati B delle cassette che contengono solo
                    # blocchi custom 

                    lSeekSubSlices = True
                    nHeaderCount = 0
                    nPos3 = 0
                    nPos3 = cSlice.rfind(MSXTape.HEADER, nPos3) # STRPOS serve a cercare una sottostringa in PHP

                    while ( (nPos3 >= 0) and (lSeekSubSlices) ):

                        nHeaderCount += 1

                        if (nHeaderCount > 2):

                            cSubSlice = cSlice[nPos3:(len(cSlice) - nPos3 + 1)]
                            cSlice = cSlice[0,:(nPos3 - 1)]
                            lSeekSubSlices = False

                        else:

                            nPos3 += 1
                            nPos3 = cSlice[MSXTape.HEADER: nPos3]

                        # End While

                        a = self.returnBlockType(cSlice)
                        self.addBlock(cSlice)
                        a = self.returnBlockType(cSlice)

                        if (cSubSlice != ""):

                            # C'è anche una sezione di custom data da aggiungere

                            self.addBlock(cSubSlice)

                        else:

                            # Non è un file binario, quindi lo aggiunge senza chiedersi se 
                            # in mezzo al file ci siano o meno dei blocchi custom

                            self.addBlock(cSlice)

                        # End If

                        # Se è arrivato al termine del file, si ricorda di
                        # terminare l'analisi una volta concluso il ciclo

                        if (nPos2 >= len(P_cStream)): lKeepSearching = False

                    # End While

                else:

                    # Smette di cercare

                    lKeepSearching = False

                # End If

                # Cerca la prossima intestazione da analizzare

                nPos1 = self.seekHeader(P_cStream, nPos2)

            # End If

        # End While

        return lFirstHeaderFound

    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_

    def seekHeader(P_cStream = "", P_nStartPos = 0, lAlwaysReturnValue = False):

        # Cerca all'interno del file .CAS l'intestazione del file

        nPos = 0
        cTemp = ""
        nStartingHeaderPos = 0
        lHeaderFound = false
        nType = MSXTape.MSX_FILE_NOT_FOUND

        nPos = P_cStream.rfind(MSXTape.HEADER, P_nStartPos)

        while ((nPos >= 0) and (not lHeaderFound)):

            # Se trova l'intestazione, prova a cercare l'altra parte di header che 
            # segnala se il file che segue è un binario, basic o ASCII

            nType = self.returnBlockType(P_cStream, nPos)

            if ( ( nType != MSXTape.MSX_FILE_NOT_FOUND) and (nType != MSXTape.MSX_CUSTOM_BLOCK) ):

                nStartingHeaderPos = nPos
                lHeaderFound = True

            else:

                nPos = P_cStream.rfind(MSXTape.HEADER, nPos + 1)

            # End If

        # End While

        if (not lHeaderFound):

            # Se non ha trovato una nuova intestazione, decide il da farsi a seconda del 
            # parametro lRestituisciComunqueValore che gli è stato passato... ritorna come 
            # valore 0 oppure la lunghezza massima del file, se è necessario

            if (lAlwaysReturnValue):
                nStartingHeaderPos = len(P_cStream)
            else:
                nStartingHeaderPos = 0
            # End If

        # End If

        # Inserisce in queste due variabili la posizione in bytes in cui si trova  
        # l'intestazione ed il tipo del file trovato 
        # (mi tocca farlo perchè non posso restituire due variabili)

        self.G_nFilePos = nStartingHeaderPos
        self.G_nFileType = nType

        return self.G_nFilePos


    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_

    def returnBlockType(P_cStream, P_nStartPos = 0):

        # Restituisce il tipo di file

        cTemp = ""
        nType = MSXTape.MSX_FILE_NOT_FOUND

        # Nello standard MSX il tipo di file viene indicato con un carattere ripetuto 
        # per 10 volte subito dopo il segnale di sincronismo (il BIIIIIP) per cui è
        # necessario che prenda i 10 caratteri successivi a quello di partenza e li 
        # analizzi

        if ( (P_nStartPos + len(MSXTape.HEADER) + 10) < strlen(P_cStream) ):
            cTemp = P_cStream[P_nStartPos + len(MSXTape.HEADER):10]
        # End If

        if (cTemp == MSXTape.DECLARE_BINARY_FILE):
            nType = MSXTape.MSX_BINARY_FILE
        elif (cTemp == MSXTape.DECLARE_BASIC_FILE):
            nType = MSXTape.MSX_BASIC_FILE
        elif (cTemp == MSXTape.DECLARE_ASCII_FILE):
            nType = MSXTape.MSX_ASCII_FILE
        else:
            nType = MSXTape.MSX_CUSTOM_BLOCK

        # End If

        return nType

    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_

    def returnBlockTitle(P_cStream):

        return P_cStream[len(self.HEADER) + 10:6]

    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_

    def addBlock(P_cStream):

        # Aggiunge un nuovo file agli array

        nInd = 0
        nPos1 = 0
        nPos2 = 0
        cSlice = ""

        if(self.cTitle == None):

            # Azzera gli array e di fatto crea una nuova cassetta

            nMaxBlocks = 0

            nOrder = array()
            cTitle = array()
            nType = array()
            nBegin = array()
            nEnd = array()
            nStart = array()
            nSize = array()
            cData = array()
            lDeleted = array()

        else:

            $nMaxBlocks = count($this->cTitle);

            array_push($this->nOrder, 0);
            array_push($this->cTitle, "");
            array_push($this->nType, self::MSX_FILE_NOT_FOUND);
            array_push($this->nSize, 0);
            array_push($this->cData, "");
            array_push($this->lDeleted, false);			

        }

        if ($this->returnBlockType($P_cStream) != self::MSX_CUSTOM_BLOCK) {

            # Non è un blocco di dati custom, per cui SICURAMENTE lo può
            # trattare come un unico file da aggiungere all'array
            # Vede qual'è l'ultimo elemento dell'array, per appendere di seguito 
            # il nuovo record

            $this->nOrder[$nMaxBlocks] = $nMax;
            $this->lDeleted[$nMaxBlocks] = false;
            $this->nType[$nMaxBlocks] = $this->returnBlockType($P_cStream);
            if ( ( $this->nType[$nMaxBlocks] != self::MSX_CUSTOM_BLOCK )
                 && ($this->nType[$nMaxBlocks] != self::MSX_FILE_NOT_FOUND) ) {
                     $this->cTitle[$nMaxBlocks] = $this->returnBlockTitle($P_cStream);
                     } else {
                         $this->cTitle[$nMaxBlocks] = "";				
                         } /* End If */

            $this->cData[$nMaxBlocks] = $P_cStream;
            $this->nSize[$nMaxBlocks] = strlen($this->cData[$nMaxBlocks]) - 33;

            } else {

                # E' un blocco di dati custom, per cui è costretto ad analizzarlo per 
                # capire se ci siano uno o più sottoblocchi da aggiungere all'array

                # Vede qual'? l'ultimo elemento dell'array, per appendere di seguito 
                # il nuovo record

                $nPos1 = strpos($P_cStream, $this->HEADER, 0);

            while ($nPos1 !== false) {

                # Cerca la posizione dell'intestazione successiva. Con il parametro 
                # finale di CercaIntestazione settato su True, gli dico di restituirmi
                # sempre e comunque un valore, anche se non trova un'intestazione
                # (mi da la fine del file in questo caso) */

                $nPos2 = strpos($P_cStream, $this->HEADER, $nPos1 + 1);

                if ($nPos2 !== false) {

                    # Tutto quello che sta nel mezzo fra un'intestazione
                    # e l'altra è il corpo del file da catalogare

                    $cSlice = substr($P_cStream, $nPos1, $nPos2 - $nPos1 + 1);
                    $nPos1 = $nPos2;

                    } else {

                        $cSlice = substr($P_cStream, $nPos1, strlen($P_cStream) - $nPos1 + 1);
                        $nPos1 = false;

                        } /* End If */

                $this->nOrder[$nMaxBlocks] = $nMaxBlocks;
                $this->lDeleted[$nMaxBlocks] = false;
                $this->nType[$nMaxBlocks] = self::MSX_CUSTOM_BLOCK;
                $this->cTitle[$nMaxBlocks] = "";

                $this->cData[$nMaxBlocks] = $cSlice;
                $this->nSize[$nMaxBlocks] = strlen($this->cData[$nMaxBlocks]) - 9;

                $nMaxBlocks = count($this->cTitle);

                array_push($this->nOrder, 0);
                array_push($this->cTitle, "");
                array_push($this->nType, self::MSX_FILE_NOT_FOUND);
                array_push($this->nSize, 0);
                array_push($this->cData, "");
                array_push($this->lDeleted, false);			

                } # End While

            if ($this->cTitle != None):
                array_pop($this->nOrder);
                array_pop($this->cTitle);
                array_pop($this->nType);
                array_pop($this->nSize);
                array_pop($this->cData);
                array_pop($this->lDeleted);			
            # End If 

        # End If

    # End Def

    # _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_

    def XMLData():

        $nInd = 0;
        $xmlDoc = new SimpleXMLElement("<tape></tape>");
        $xmlTape = null;
        $xmlBlock = null;

        $xmlDoc->addAttribute("count", (count($this->cTitle)) );

        while($nInd < count($this->cTitle)) {

            /* Scrive qualcosa sullo schermo */

            $xmlBlock = $xmlDoc->addChild("block");

            if($this->cTitle[$nInd] != "") $xmlBlock->addChild("title", trim($this->cTitle[$nInd]));

            switch ($this->nType[$nInd]) {
                case self::MSX_BINARY_FILE:
                $xmlBlock->addChild("type", "binary");
            break;
            case self::MSX_BASIC_FILE:
                $xmlBlock->addChild("type", "basic");
                break;
            case self::MSX_ASCII_FILE:
                $xmlBlock->addChild("type", "ascii");
                break;
            case self::MSX_CUSTOM_BLOCK:
                $xmlBlock->addChild("type", "custom");
                break;
            }
            $xmlBlock->addChild("length", ($this->nSize[$nInd]));

            $nInd++;

        }

        return $xmlDoc;

        }

        /* _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ _-=-_-=-_ */

}


/* This tiny piece of code is needed only for testing purposes */
/*
$t1 = microtime();
$pippo = new MSXTape();
$pippo->open("tapes/PACLAND.CAS");
$pluto = $pippo->XMLData();

echo("INSIDE THIS TAPE:<br/><br/>");
foreach($pluto->block as $block) {
    if($block->title != "") echo(chr(34) . $block->title . chr(34) . " (" . $block->type . ")");
    else echo("Custom Block");
    echo(" (" . $block->length . " bytes)<br/>");
}
//file_put_contents('output.xml', $pluto->asXML());
$t2 = microtime() - $t1;
echo("<br/><br/>Elapsed time: " . $t2);
*/
echo "Finito";
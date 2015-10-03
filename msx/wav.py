Const G_PI = 3.14159265358979323846264338327950

Private G_Dichiarazione_File_ASCII As String
Private G_Dichiarazione_File_Basic As String
Private G_Dichiarazione_File_Binario As String
G_Intestazione As String
G_Intestazione_Corta As Integer
G_Intestazione_Lunga As Integer
G_nBaudRate As Double
G_nFrequenzaOutput As Double
G_Onda_Corta As Integer
G_Onda_Lunga As Integer
G_Silenzio_Breve As Int32
G_Silenzio_Lungo As Int32

# ------------------------------------------------------------------------------

Protected Function BigEndianLong(P_nValore As Int32) As String

	' Restituisce un valore numerico nel formato "Big Endian" di Intel. Serve per memorizzar e alcuni parametri nell'intestazione
	' del file WAV che viene creato, che vanno memorizzati nel file in questa maniera
	' Big Endian Long scrive un numero su 4 byte. Es: 12345678 viene scritto come 78, 56 , 34, 12

	Dim cTemp As String, cTemp2 As String Dim nInd As Integer
	cTemp = Varie.PadL(Trim(Hex(P_nValore)), 8, "0")
	For nInd = 1 To 8 Step 2
	cTemp2 = Chr(Val("&h" + Mid(cTemp, nInd, 2))) + cTemp2
	Next nInd
	Return cTemp2

End Function

# ------------------------------------------------------------------------------

Protected Function BigEndianShort(P_nValore As Integer) As String

	' Restituisce un valore numerico nel formato "Big Endian" di Intel. Serve per memorizzar e alcuni parametri nell'intestazione
	' del file WAV che viene creato, che vanno memorizzati nel file in questa maniera
	' Big Endian Short scrive un numero su 2 byte. Es: 1234 viene scritto come 34, 12

	Dim cTemp As String, cTemp2 As String Dim nInd As Integer
	cTemp = Varie.PadL(Trim(Hex(P_nValore)), 4, "0")
	For nInd = 1 To 4 Step 2
		cTemp2 = Chr(Val("&h" + Mid(cTemp, nInd, 2))) + cTemp2
	Next nInd
	Return cTemp2

End Function

# ------------------------------------------------------------------------------

Sub Constructor()

	' Il costruttore della classe, che inizializza il valore di alcune variabili utilizzate all'interno della classe
	' Ad esempio G_Intestazione che contiene la serie di bytes (8) utilizzata nel formato CA S per inserire un segnale di sincronizzazione per l'MSX
	' (Quella cosa che ascoltando l'audio all'inizio di un file fa BIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIP
	' Poi G_Dichiarazione_File_Binario, Basic e ASCII che contengono i dieci byte che fanno capire nel file CAS se quello che segue è un
	' File Binario, Basic o ASCII.

	G_Intestazione = ChrB(Val("&h1F")) + ChrB(Val("&hA6")) + ChrB(Val("&hDE")) + ChrB(V al("&hBA")) + ChrB(Val("&hCC")) + ChrB(Val("&h13")) + ChrB(Val("&h7D")) + ChrB(Val(" &h74"))
	G_Dichiarazione_File_Binario = PadL("", 10, ChrB(Val("&hD0"))) G_Dichiarazione_File_Basic = PadL("", 10, ChrB(Val("&hD3"))) G_Dichiarazione_File_ASCII = PadL("", 10, ChrB(Val("&hEA")))

End Sub

# ------------------------------------------------------------------------------

Private Function FormattaNomeFile(ByVal P_cNomeFile As String) As String

	' Controlla il nome del file... se è più di sei caratteri lo taglia, se è meno di sei caratteri a ggiunge degli spazi al nome

	P_cNomeFile = Trim(P_cNomeFile)
	If ( Len(P_cNomeFile) > 6 ) Then
		P_cNomeFile = Mid(P_cNomeFile, 1, 6) Else
		If ( Len(P_cNomeFile) < 6 ) Then
			P_cNomeFile = Varie.PadR(P_cNomeFile, 6)
		End If
	End If
	Return P_cNomeFile

End Function

# ------------------------------------------------------------------------------

Private Sub InserisciByte(P_oFile As BinaryStream, ByVal P_nByte As Int64)

	' Prende un byte (che viene passato alla funzione come parametro) e lo scrive nel file W AV sotto forma di forme d'onda.
	' Se è un 1 lo scrive con due onde corte, se è uno 0 lo scrive con un onda lunga (che es sendo lunga dura esattamente come due
	' onde corte)

	Dim nInd As Integer Dim nValore As Int64

	' Un bit di start
	InserisciOnda(P_oFile, G_Onda_Lunga)

	' Otto bit di dati
	For nInd = 0 To 7
		nValore = (P_nByte And 1)
		If (P_nByte And 1) = 1 Then
			InserisciOnda(P_oFile, G_Onda_Corta)
			InserisciOnda(P_oFile, G_Onda_Corta)
		Else
			InserisciOnda(P_oFile, G_Onda_Lunga)
		End If
		P_nByte = Bitwise.ShiftRight(P_nByte, 1)
	Next nInd

	' Due bit di stop
	For nInd = 0 To 3
		InserisciOnda(P_oFile, G_Onda_Corta)
	Next nInd

End Sub

# ------------------------------------------------------------------------------

Private Function InserisciDati(P_oFile As BinaryStream, P_cDati As String, P_lIgnoraRisincronizzazioni As Boolean = False) As Boolean

	' Inserisce i dati nel file WAV, cioè praticamente tutto quello che c'è da scrivere del file t ranne il segnale di sincronizzazione iniziale
	' (il BIIIIIIIIIIIIIIIIIIIP iniziale), l'intestazione che contiene il tipo di file (Binario, Basic e ASCI I), il nome del file e le pause

	Dim nInd As Integer
	Dim cProssimiOttoCaratteri As String
	Dim lEOF As Boolean = False

	nInd = 1
	While (nInd <= LenB(P_cDati))
		If (P_lIgnoraRisincronizzazioni) Then

			' Se gli è stato detto che deve ignorare le risincronizzazioni all'interno dei dati (ad esempio se sta scrivendo il contenuto di
			' un file binario o di un custom block), scrive byte per byte tutto il contenuto d el file senza pensarci sopra
			InserisciByte(P_oFile, AscB(MidB(P_cDati, nInd, 1)))

		Else

			' Se invece gli è stato detto che deve stare attento alle risincronizzazioni all'int erno dei dati (ad esempio con i files ASCII e Basic)
			' prima di scrivere ogni byte, si piglia quello ed i sette bytes consecutivi per ve rificare che non siano una risincronizzazione.
			' Ma prima di poter fare quel controllo deve prima verificare che ci siano ancor a 8 bytes da controllare prima della fine del file.
			If ( (nInd + 8) <= Len(P_cDati) ) Then
				' Si piglia il byte attuale + i sette successivi per controllare che non sia un a risincronizzazione
				cProssimiOttoCaratteri = MidB(P_cDati, nInd, 8)
				If (cProssimiOttoCaratteri = G_Intestazione) Then

					' Si... è proprio una risincronizzazione! E' necessario reinserire un bre ve silenzio e quindi una nuova intestazione (IL BIIIIIIIIP),
					' prima di poter continuare a scrivere i prossimi dati
					InserisciSilenzio(P_oFile, G_Silenzio_Breve)
					InserisciIntestazione(P_oFile, G_Intestazione_Corta)

					' Salta in toto il blocco della risincronizzazione. Perchè salta 7 anzich è 8 (che sarebbe la lunghezza di un segnale di
					' risincronizzazione) ? Perchè nInd salta ancora di una posizione dop o il termine di questa istruzione If
					nInd = nInd + 7
				Else

					' No... falso allarme, è un byte per conto suo... e allora bisogna scrive rlo sul WAV
					InserisciByte(P_oFile, AscB(MidB(P_cDati, nInd, 1)))
					If ( (MidB(P_cDati, nInd, 1)) = Chr(31) ) Then
						lEOF = True
					End If
				End If
			Else
				' Se per caso mancano 7 o meno bytes alla fine del file è impossibile che all'interno ci sia un segnale di sincronismo (che occupa
				' 8 bytes), quindi non se ne preoccupa e scrive i dati sul file WAV.
				InserisciByte(P_oFile, AscB(MidB(P_cDati, nInd, 1)))

				If ( (MidB(P_cDati, nInd, 1)) = Chr(31) ) Then
					lEOF = True
				End If

			End If
		End If
		' Passa ad analizzare il byte successivo
		nInd = nInd + 1
	Wend

	Return lEOF

End Function

# ------------------------------------------------------------------------------

Sub InserisciFileMSX(P_oFile As BinaryStream, P_cNomeFile As String, P_cTipoFile As eTipiFil esMSX, P_cDati As String)

	' Scrive un file MSX intero sul file WAV, comprese le intestazioni e le pause

	Dim cParteIntestazione As String = ""
	Dim cParteDati As String = ""
	Dim lIgnoraSincronizzazioni As Boolean = False Dim lEOF As Boolean = False
	Dim nPosIntestazione As Int32

	' Verifica che il nome del file non superi i sei caratteri (il massimo consentito dallo stand ard MSX)
	P_cNomeFile = FormattaNomeFile(P_cNomeFile)

	' Prima di cominciare a scrivere, analizza il tipo di file... ' \

	Select Case (P_cTipoFile)

		Case eTipiFilesMSX.File_MSX_ASCII

			' Se deve scrivere un file in formato ASCII, piglia i dati e toglie via i primi 32 bytes.
			' Perchè toglie via i primi 32 bytes? Perchè i primi 8 sono il segnale di sincronismo ( il BIIIIIIIIIIIIP iniziale),
			' poi ce ne sono altri 10 che specificano il tipo di file che sta per essere caricato (B asic, ASCII o Binario), quindi
			' seguono 6 caratteri con il nome del programma, ed infine altri 8 caratteri con un n uovo segnale di sincronismo (Altro BIIIIIIIIIP)
			' In totale fa 8 + 10 + 6 + 8 = 32, il che significa che i primi trentadue caratteri (in R ealBasic la stringa comincia dall'elemento 1)
			' sono formati da queste cose che non ci servono e che quindi sono da eliminare, q uindi si partirà dal 33esimo carattere
			cParteIntestazione = cParteIntestazione + G_Dichiarazione_File_ASCII + P_cNomeFi le
			nPosIntestazione = InStrB(2, P_cDati, G_Intestazione) + LenB(G_Intestazione) cParteDati = RightB(P_cDati, LenB(P_cDati) - nPosIntestazione + 1)

			' Siccome è un file ASCII, ogni tanto all'interno dei dati c'è una risincronizzazione. S i segna che ne deve tenere conto quando scrive
			' il file sul WAV.
			lIgnoraSincronizzazioni = False

		Case eTipiFilesMSX.File_MSX_Basic

			' Idem con patate per quanto già detto per il formato ASCII... bisogna strippare via i primi 32 caratteri
			cParteIntestazione = cParteIntestazione + G_Dichiarazione_File_Basic + P_cNomeFi le
			nPosIntestazione = InStrB(2, P_cDati, G_Intestazione) + LenB(G_Intestazione) cParteDati = RightB(P_cDati, LenB(P_cDati) - nPosIntestazione + 1)
			' Idem come sopra per la risincronizzazione
			lIgnoraSincronizzazioni = False

		Case eTipiFilesMSX.File_MSX_Binario

			' Idem con patate per quanto già detto per il formato Basic e ASCII... strippiamo via bla bla bla...
			cParteIntestazione = cParteIntestazione + G_Dichiarazione_File_Binario + P_cNome File
			nPosIntestazione = InStrB(2, P_cDati, G_Intestazione) + LenB(G_Intestazione) cParteDati = RightB(P_cDati, LenB(P_cDati) - nPosIntestazione + 1)
			' I file binari invece non dovrebbero avere segnali di risincronizzazione all'interno d ei dati, quindi si annota che dovrà
			' ignorarli se per caso ne trovasse qualcuno
			lIgnoraSincronizzazioni = True

		Else

			' Ecco... qui invece la situazione è leggermente diversa... in un blocco custom (che non si chiama "custom" per caso)
			' C'è solo il segnale di sincronismo iniziale (il BIIIIIIIIIIIIP) a cui seguono direttamente tutti i dati.
			' E' necessario quindi rimuovere i primi 8 caratteri di sincronismo, partendo così dal carattere N. 9 in poi

			cParteIntestazione = ""
			cParteDati = RightB(P_cDati, LenB(P_cDati) - 9 + 1)

			' Anche nei blocchi custom non ci dovrebbero essere segnali di risincronizzazione durante i dati, quindi si annota il fatto
			' di ignorarli, se per caso si presentassero
			lIgnoraSincronizzazioni = True

	End Select

	' Ok, siamo pronti a scrivere i dati veri e propri. A questo punto se dobbiamo scrivere su l file WAV un file binario, basic o ASCII
	' inseriamo una prima intestazione con i dati. A livello sonoro sarà qualcosa del tipo BIIIII IIP + <Tipo file> + <Nome File> + [SILENZIO]
	If(cParteIntestazione <> "") Then
		InserisciIntestazione(P_oFile, G_Intestazione_Lunga)
		lEOF = InserisciDati(P_oFile, cParteIntestazione, lIgnoraSincronizzazioni)
		InserisciSilenzio(P_oFile, G_Silenzio_Breve)
	End If

	' A questo punto possiamo scrivere i dati veri e propri del file. Dovremo inserire un altro segnale di sincronismo (BIIIIIIIIIP) e quindi
	' i dati veri e propri
	InserisciIntestazione(P_oFile, G_Intestazione_Corta)
	lEOF = InserisciDati(P_oFile, cParteDati)

End Sub

# ------------------------------------------------------------------------------

Private Sub InserisciIntestazione(P_oFile As BinaryStream, P_nDurataMillisecondi As Integer) ' Inserisce una forma d'onda che rappresenta il segnale di sincronismo per l'MSX (il BIIIII IIIIIIIIIIIIP iniziale che precede ogni file)

	Dim nInd As Integer
	nInd = 0
	While (nInd < ( P_nDurataMillisecondi * (G_nBaudRate / 1200) * 2.5 ))
		InserisciOnda(P_oFile, G_Onda_Corta)
		nInd = nInd + 1
	Wend

End Sub

# ------------------------------------------------------------------------------

Sub InserisciIntestazioneWAV(P_oFile As BinaryStream, P_nLunghezza As Int64)

	' Inserisce l'intestazione del file WAV. E' un blocco di dati che va scritto necessariament e all'inizio del file WAV, altrimenti il file
	' non viene riconosciuto correttamente come file audio. P_nLunghezza indica la lunghez za complessiva in bytes del file audio.

	P_oFile.Write("RIFF" + BigEndianLong(P_nLunghezza - 8) + "WAVE" + "fmt " + BigEndian Long(16) + BigEndianShort(1) + BigEndianShort(1) + BigEndianLong(G_nFrequenzaOut put) + BigEndianLong(G_nFrequenzaOutput) + BigEndianShort(1) + BigEndianShort(8) + "data" + BigEndianLong(P_nLunghezza - 44))

End Sub

# ------------------------------------------------------------------------------

Private Sub InserisciOnda(P_oFile As BinaryStream, P_nFrequenza As Integer) ' Inserisce una forma d'onda sinusoidale nel file WAV

	Dim nInd As Int32
	Dim nLunghezza As Double = G_nFrequenzaOutput / ( G_nBaudRate * ( P_nFrequenza / 1200 ) )
	Dim nScala As Double = (2.0 * G_PI) / nLunghezza

	nInd = 0
	While(nInd< nLunghezza)
		P_oFile.WriteByte( 128 - ( Sin( nInd * nScala ) * 127 ) )
		nInd = nInd + 1
	Wend

End Sub

# ------------------------------------------------------------------------------

Sub InserisciSilenzio(P_oFile As BinaryStream, P_nLunghezzaMillisecondi As Integer)

	' Inserisce del silenzio nel file WAV

	Dim nInd As Integer
	nInd = 0
	While (nInd < ( P_nLunghezzaMillisecondi * (G_nFrequenzaOutput / 1200) ))
		P_oFile.WriteByte(128)
		nInd = nInd + 1
	Wend

End Sub

# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
    ' Il costruttore della classe, che inizializza il valore di alcune variabili utilizzate all'interno della classe
  ' Ad esempio G_Intestazione che contiene la serie di bytes (8) utilizzata nel formato CAS per inserire un segnale di sincronizzazione per l'MSX
  ' (Quella cosa che ascoltando l'audio all'inizio di un file fa BIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIP
  ' Poi G_Dichiarazione_File_Binario, Basic e ASCII che contengono i dieci byte che fanno capire nel file CAS se quello che segue è un
  ' File Binario, Basic o ASCII.

  G_Intestazione = ChrB(Val("&h1F")) + ChrB(Val("&hA6")) + ChrB(Val("&hDE")) + ChrB(Val("&hBA")) + ChrB(Val("&hCC")) + ChrB(Val("&h13")) + ChrB(Val("&h7D")) + ChrB(Val("&h74"))
  G_Dichiarazione_File_Binario = PadL("", 10, ChrB(Val("&hD0")))
  G_Dichiarazione_File_Basic = PadL("", 10, ChrB(Val("&hD3")))
  G_Dichiarazione_File_ASCII = PadL("", 10, ChrB(Val("&hEA")))

  ' Loader binari MSX

  G_Loader_Binari_8K_4000H = ""
  G_Loader_Binari_8K_4000H = G_Loader_Binari_8K_4000H + ChrB(243) + ChrB(58) + ChrB(255) + ChrB(255) + ChrB(47) + ChrB(245) + ChrB(230) + ChrB(240)
  G_Loader_Binari_8K_4000H = G_Loader_Binari_8K_4000H + ChrB(71) + ChrB(7) + ChrB(7) + ChrB(7) + ChrB(7) + ChrB(176) + ChrB(50) + ChrB(255)
  G_Loader_Binari_8K_4000H = G_Loader_Binari_8K_4000H + ChrB(255) + ChrB(219) + ChrB(168) + ChrB(245) + ChrB(230) + ChrB(240) + ChrB(71) + ChrB(7)
  G_Loader_Binari_8K_4000H = G_Loader_Binari_8K_4000H + ChrB(7) + ChrB(7) + ChrB(7) + ChrB(176) + ChrB(211) + ChrB(168) + ChrB(33) + ChrB(0)
  G_Loader_Binari_8K_4000H = G_Loader_Binari_8K_4000H + ChrB(160) + ChrB(17) + ChrB(0) + ChrB(0) + ChrB(1) + ChrB(0) + ChrB(32) + ChrB(237)
  G_Loader_Binari_8K_4000H = G_Loader_Binari_8K_4000H + ChrB(176) + ChrB(33) + ChrB(0) + ChrB(0) + ChrB(17) + ChrB(0) + ChrB(32) + ChrB(1)
  G_Loader_Binari_8K_4000H = G_Loader_Binari_8K_4000H + ChrB(0) + ChrB(160) + ChrB(237) + ChrB(176) + ChrB(241) + ChrB(211) + ChrB(168) + ChrB(241)
  G_Loader_Binari_8K_4000H = G_Loader_Binari_8K_4000H + ChrB(50) + ChrB(255) + ChrB(255) + ChrB(199)

  G_Loader_Binari_16K_4000H = ""
  G_Loader_Binari_16K_4000H = G_Loader_Binari_16K_4000H + ChrB(243)
  G_Loader_Binari_16K_4000H = G_Loader_Binari_16K_4000H + ChrB(58) + ChrB(255) + ChrB(255) + ChrB(47) + ChrB(230) + ChrB(240) + ChrB(71) + ChrB(15)
  G_Loader_Binari_16K_4000H = G_Loader_Binari_16K_4000H + ChrB(15) + ChrB(176) + ChrB(50) + ChrB(255) + ChrB(255) + ChrB(205) + ChrB(56) + ChrB(1)
  G_Loader_Binari_16K_4000H = G_Loader_Binari_16K_4000H + ChrB(71) + ChrB(15) + ChrB(15) + ChrB(176) + ChrB(205) + ChrB(59) + ChrB(1) + ChrB(33)
  G_Loader_Binari_16K_4000H = G_Loader_Binari_16K_4000H + ChrB(0) + ChrB(144) + ChrB(17) + ChrB(0) + ChrB(64) + ChrB(1) + ChrB(0) + ChrB(64)
  G_Loader_Binari_16K_4000H = G_Loader_Binari_16K_4000H + ChrB(237) + ChrB(176) + ChrB(58) + ChrB(123) + ChrB(254) + ChrB(254) + ChrB(201) + ChrB(40)
  G_Loader_Binari_16K_4000H = G_Loader_Binari_16K_4000H + ChrB(11) + ChrB(253) + ChrB(42) + ChrB(71) + ChrB(243) + ChrB(221) + ChrB(33) + ChrB(41)
  G_Loader_Binari_16K_4000H = G_Loader_Binari_16K_4000H + ChrB(64) + ChrB(205) + ChrB(28) + ChrB(0) + ChrB(42) + ChrB(2) + ChrB(64) + ChrB(233)

  G_Loader_Binari_16K_8000H = ""
  G_Loader_Binari_16K_8000H = G_Loader_Binari_16K_8000H + ChrB(243)
  G_Loader_Binari_16K_8000H = G_Loader_Binari_16K_8000H + ChrB(33) + ChrB(0) + ChrB(144) + ChrB(17) + ChrB(0) + ChrB(128) + ChrB(1) + ChrB(0)
  G_Loader_Binari_16K_8000H = G_Loader_Binari_16K_8000H + ChrB(64) + ChrB(237) + ChrB(176) + ChrB(58) + ChrB(123) + ChrB(254) + ChrB(254) + ChrB(201)
  G_Loader_Binari_16K_8000H = G_Loader_Binari_16K_8000H + ChrB(40) + ChrB(11) + ChrB(253) + ChrB(42) + ChrB(71) + ChrB(243) + ChrB(221) + ChrB(33)
  G_Loader_Binari_16K_8000H = G_Loader_Binari_16K_8000H + ChrB(41) + ChrB(64) + ChrB(205) + ChrB(28) + ChrB(0) + ChrB(42) + ChrB(2) + ChrB(128)
  G_Loader_Binari_16K_8000H = G_Loader_Binari_16K_8000H + ChrB(233)

  G_Loader_Binari_32K_4000H = ""
  G_Loader_Binari_32K_4000H = G_Loader_Binari_32K_4000H + ChrB(243)
  G_Loader_Binari_32K_4000H = G_Loader_Binari_32K_4000H + ChrB(58) + ChrB(255) + ChrB(255) + ChrB(47) + ChrB(50) + ChrB(56) + ChrB(208) + ChrB(230)
  G_Loader_Binari_32K_4000H = G_Loader_Binari_32K_4000H + ChrB(240) + ChrB(71) + ChrB(15) + ChrB(15) + ChrB(176) + ChrB(50) + ChrB(255) + ChrB(255)
  G_Loader_Binari_32K_4000H = G_Loader_Binari_32K_4000H + ChrB(205) + ChrB(56) + ChrB(1) + ChrB(50) + ChrB(55) + ChrB(208) + ChrB(71) + ChrB(15)
  G_Loader_Binari_32K_4000H = G_Loader_Binari_32K_4000H + ChrB(15) + ChrB(176) + ChrB(205) + ChrB(59) + ChrB(1) + ChrB(33) + ChrB(0) + ChrB(144)
  G_Loader_Binari_32K_4000H = G_Loader_Binari_32K_4000H + ChrB(17) + ChrB(0) + ChrB(64) + ChrB(1) + ChrB(0) + ChrB(64) + ChrB(237) + ChrB(176)
  G_Loader_Binari_32K_4000H = G_Loader_Binari_32K_4000H + ChrB(58) + ChrB(55) + ChrB(208) + ChrB(205) + ChrB(59) + ChrB(1) + ChrB(58) + ChrB(56)
  G_Loader_Binari_32K_4000H = G_Loader_Binari_32K_4000H + ChrB(208) + ChrB(50) + ChrB(255) + ChrB(255) + ChrB(251) + ChrB(201) + ChrB(0) + ChrB(0)

  G_Loader_Binari_32K_8000H = ""
  G_Loader_Binari_32K_8000H = G_Loader_Binari_32K_8000H + ChrB(243)
  G_Loader_Binari_32K_8000H = G_Loader_Binari_32K_8000H + ChrB(58) + ChrB(255) + ChrB(255) + ChrB(47) + ChrB(230) + ChrB(240) + ChrB(71) + ChrB(15)
  G_Loader_Binari_32K_8000H = G_Loader_Binari_32K_8000H + ChrB(15) + ChrB(176) + ChrB(50) + ChrB(255) + ChrB(255) + ChrB(205) + ChrB(56) + ChrB(1)
  G_Loader_Binari_32K_8000H = G_Loader_Binari_32K_8000H + ChrB(71) + ChrB(15) + ChrB(15) + ChrB(176) + ChrB(205) + ChrB(59) + ChrB(1) + ChrB(33)
  G_Loader_Binari_32K_8000H = G_Loader_Binari_32K_8000H + ChrB(0) + ChrB(144) + ChrB(17) + ChrB(0) + ChrB(128) + ChrB(1) + ChrB(0) + ChrB(64)
  G_Loader_Binari_32K_8000H = G_Loader_Binari_32K_8000H + ChrB(237) + ChrB(176) + ChrB(58) + ChrB(123) + ChrB(254) + ChrB(254) + ChrB(201) + ChrB(40)
  G_Loader_Binari_32K_8000H = G_Loader_Binari_32K_8000H + ChrB(11) + ChrB(253) + ChrB(42) + ChrB(123) + ChrB(254) + ChrB(221) + ChrB(33) + ChrB(41)
  G_Loader_Binari_32K_8000H = G_Loader_Binari_32K_8000H + ChrB(64) + ChrB(205) + ChrB(28) + ChrB(0) + ChrB(42) + ChrB(2) + ChrB(64) + ChrB(233)

  ' Inizializza i vari array, per partire con una nuova cassetta

  Me.Nuova

  # ----------------------------------------------------------------------------------------------

  ' Importa un file Binario all'interno della sua struttura
  
  Dim cTemp As String, nInd As Integer
  Dim cTemp2 As String, nIndirizzo As Integer, nValore1 As Integer, nValore2 As Integer
  Dim nIndPassaggi As Integer, nPassaggi As Integer, nPosInizio As Int32, nLunghezzaDati As Int32
  Dim nIndirizzoMemoriaIniziale As Integer
  Dim nIndirizzoMemoriaEsecuzione As Integer
  
  
  ' Controlla il nome del file... se è più di sei caratteri lo taglia, se è meno di sei caratteri aggiunge degli spazi al nome
  
  P_cTitolo = FormattaNomeFile(P_cTitolo)
  
  ' Controlla il tipo di ROM da caricare
  
  If ( LenB(P_cCodiceBinario) > 8192) Then
    
    ' ROM da 16Kb (o peggio)
    
    If ( LenB(P_cCodiceBinario) <= 16384 ) Then
      nIndirizzoMemoriaIniziale = Val("&h9000")
      nIndirizzoMemoriaEsecuzione = Val("&hD000") 'nIndirizzoMemoriaIniziale + LenB(P_cCodiceBinario) 'C000
      G_Loader_Binario = G_Loader_Binari_16K_8000H
      nPassaggi = 1
    Else
      nIndirizzoMemoriaIniziale = Val("&h9000")
      nIndirizzoMemoriaEsecuzione = Val("&hD000") 'nIndirizzoMemoriaIniziale + LenB(P_cCodiceBinario) 'C000
      G_Loader_Binario = G_Loader_Binari_32K_4000H
      nPassaggi = 2
    End If
    
  Else
    
    ' ROM da 8Kb
    
    nIndirizzoMemoriaIniziale = Val("&hA000")
    nIndirizzoMemoriaEsecuzione = nIndirizzoMemoriaIniziale + LenB(P_cCodiceBinario) 'C000
    
  End If
  
  nPosInizio = 1
  nLunghezzaDati = 0
  For nIndPassaggi = 1 To nPassaggi
    
    If (nIndPassaggi = 1) Then 
      G_Loader_Binario = G_Loader_Binari_32K_4000H
    Else
      G_Loader_Binario = G_Loader_Binari_32K_8000H
    End If
    
    nPosInizio = nPosInizio + nLunghezzaDati
    nLunghezzaDati =  16384
    
    ' Assembla il tutto con l'intestazione e tutto l'ambaradan, quindi la passa alla funzione di scomposizione perchè lo memorizzi
    ' negli array
    
    cTemp = G_Intestazione + G_Dichiarazione_File_Binario + P_cTitolo + G_Intestazione 
    
    ' Indirizzo di partenza
    
    nIndirizzo = nIndirizzoMemoriaIniziale
    cTemp2 = Hex(nIndirizzo)
    cTemp2 = PadL(cTemp2, 4, "0")
    nValore1 = Val("&h" + Mid(cTemp2, 3, 2))
    nValore2 = Val("&h" + Mid(cTemp2, 1, 2))
    'MsgBox(cTemp2 + " = " +  Str(nValore1) + " + " + Str(nValore2))
    
    cTemp = cTemp + ChrB(nValore1) + ChrB(nValore2) 
    
    ' Indirizzo finale (Indirizzo di partenza + Lunghezza file - 1)
    
    nIndirizzo = nIndirizzo + LenB(MidB(P_cCodiceBinario, nPosInizio, nLunghezzaDati)) + LenB(G_Loader_Binario) - 1
    cTemp2 = Hex(nIndirizzo)
    cTemp2 = PadL(cTemp2, 4, "0")
    nValore1 = Val("&h" + Mid(cTemp2, 3, 2))
    nValore2 = Val("&h" + Mid(cTemp2, 1, 2))
    'MsgBox(cTemp2 + " = " +  Str(nValore1) + " + " + Str(nValore2))
    
    cTemp = cTemp + ChrB(nValore1) + ChrB(nValore2)
    
    ' Indirizzo di esecuzione del file
    
    nIndirizzo = nIndirizzoMemoriaEsecuzione
    cTemp2 = Hex(nIndirizzo)
    cTemp2 = PadL(cTemp2, 4, "0")
    nValore1 = Val("&h" + Mid(cTemp2, 3, 2))
    nValore2 = Val("&h" + Mid(cTemp2, 1, 2))
    'MsgBox(cTemp2 + " = " +  Str(nValore1) + " + " + Str(nValore2))
    
    cTemp = cTemp + ChrB(nValore1) + ChrB(nValore2)
    
    
    ' Ora può aggiungere la ROM vera e propria (o una sua porzione) al file
    
    MsgBox(Str(LenB(MidB(P_cCodiceBinario, nPosInizio, nLunghezzaDati))))
    cTemp = cTemp + MidB(P_cCodiceBinario, nPosInizio, nLunghezzaDati) + G_Loader_Binario 
    
    Scomponi(cTemp)
    
  Next nIndPassaggi

  # ---------------------------------------------------------------------------------------------

    ' Importa un file ASCII all'interno della sua struttura

  Dim cTemp As String, cTemp2 As String
  Dim nInd As Integer, nPos As Integer
  Dim nPasso As Integer = 256


  P_cTitolo = FormattaNomeFile(P_cTitolo)

  ' Se per andare a capo nel testo viene usato solo il carattere ASCII 10 (Return), aggiunge di suo anche il carattere ASCII 13 (New Line)

  nPos = InStrB(P_cCodiceAscii, Chr(10))
  If(nPos > 0) Then
    If ( (nPos - 1) > 0 ) Then
      If( MidB(P_cCodiceAscii, nPos - 1, 1) <> ChrB(13) ) Then
        P_cCodiceAscii = ReplaceAllB(P_cCodiceAscii, ChrB(10), ChrB(13) + ChrB(10))
      End If
    End If
  End If

  ' Aggiunge dei caratteri per fare blocchi da 256 caratteri (non so perchè serva, ma altrimenti non funziona)

  cTemp2 = ""
  For nInd = 1 To LenB(P_cCodiceAscii) Step nPasso
    If( (nInd + nPasso) < LenB(P_cCodiceAscii) ) Then
      cTemp2 = cTemp2 + MidB(P_cCodiceAscii, nInd, nPasso) + G_Intestazione
    Else
      cTemp2 = cTemp2 + PadR(MidB(P_cCodiceAscii, nInd, LenB(P_cCodiceAscii) - nInd + 1), (nPasso - 1), Chr(26)) + Chr(31)
    End If
  Next nInd

  ' Assembla il tutto con l'intestazione e tutto l'ambaradan, quindi la passa alla funzione di scomposizione perchè lo memorizzi
  ' negli array

  cTemp = G_Intestazione + G_Dichiarazione_File_ASCII + P_cTitolo + G_Intestazione + cTemp2

  Scomponi(cTemp)
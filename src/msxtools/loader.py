class Loader:
    # loader 8kb (C) Alexey Podrezov
    # loader 16/32kb (C) Edison Antonio Pires de Moraes

    # Ricordati che quando importi i file ASM devi eliminare i primi sette bytes
    # i primi 7 bytes = 0xFE + 2 x Indirizzo partenza + 2 x Indirizzo fine
    # + 2 x Indirizzo esecuzione

    binari_16k_4000h = b"\xf3:\xff\xff/\xe6\xf0G\x0f\x0f\xb02\xff\xff\xcd8\x01G\x0f" \
                       b"\x0f\xb0\xcd;\x01!\x00\x90\x11\x00@\x01\x00@\xed\xb0:{\xfe" \
                       b"\xfe\xc9(\x0b\xfd*G\xf3\xdd!)@\xcd\x1c\x00*\x02@\xe9"

    # binari_16k_4000h = b':\xff\xff/\xe6\xf0G\x0f\x0f\xb02\xff\xff' \
    #                    b'\xcd8\x01G\x0f\x0f\xb0\xcd;\x01!\x00\x90\x11\x00@\x01\x00@\xed\xb0:{' \
    #                    b'\xfe\xfe\xc9(\x0b\xfd*G\xf3\xdd!)@\xcd\x1c\x00*\x02@\xe9'

    binari_16k_8000h = b'\xf3!\x00\x90\x11\x00\x80\x01\x00@\xed\xb0:{' \
                       b'\xfe\xfe\xc9(\x0b\xfd*G\xf3\xdd!)@\xcd\x1c\x00*\x02\x80\xe9'

    binari_32k_4000h = b'\xf3:\xff\xff/28\xd0\xe6\xf0G\x0f\x0f\xb02\xff\xff\xcd8\x0127\xd0G\x0f\x0f\xb0\xcd;\x01!\x00\x90\x11\x00@\x01\x00@\xed\xb0:7\xd0\xcd;\x01:8\xd02\xff\xff\xfb\xc9\x00\x00'

    binari_32k_8000h = b'\xf3:\xff\xff/\xe6\xf0G\x0f\x0f\xb02\xff\xff\xcd8\x01G\x0f\x0f\xb0\xcd;\x01!\x00\x90\x11\x00\x80\x01\x00@\xed\xb0:{\xfe\xfe\xc9(\x0b\xfd*{\xfe\xdd!)@\xcd\x1c\x00*\x02@\xe9'

    # Loader per la pagina 0 delle ROM da 48kb (0000h-BFFFh). Copia i 16kb caricati
    # a 9000h nella RAM della pagina 0, poi rimette il BIOS e torna al BASIC, che
    # potrà così caricare il blocco successivo dalla cassetta.
    # La RAM viene cercata nello slot (e sottoslot) della pagina 3.
    #
    #         DI
    #         IN   A,(0A8h)
    #         LD   D,A            ; D = registro degli slot primari originale
    #         RLCA
    #         RLCA
    #         AND  3
    #         LD   C,A            ; C = slot primario della RAM (pagina 3)
    #         ADD  A,0C1h
    #         LD   L,A
    #         LD   H,0FCh         ; HL = EXPTBL + slot
    #         BIT  7,(HL)
    #         JR   Z,NOEXP        ; slot non espanso: niente sottoslot
    #         LD   A,(0FFFFh)
    #         CPL
    #         LD   E,A            ; E = registro dei sottoslot originale
    #         AND  0FCh
    #         LD   B,A
    #         LD   A,E
    #         RLCA
    #         RLCA
    #         AND  3
    #         OR   B
    #         LD   (0FFFFh),A     ; sottoslot pagina 0 = sottoslot pagina 3
    # NOEXP:  LD   A,D
    #         AND  0FCh
    #         OR   C
    #         OUT  (0A8h),A       ; pagina 0 = RAM
    #         PUSH DE
    #         LD   HL,9000h
    #         LD   DE,0000h
    #         LD   BC,4000h
    #         LDIR
    #         POP  DE
    #         LD   A,D
    #         OUT  (0A8h),A       ; pagina 0 = BIOS
    #         RLCA
    #         RLCA
    #         AND  3
    #         ADD  A,0C1h
    #         LD   L,A
    #         LD   H,0FCh
    #         BIT  7,(HL)
    #         JR   Z,FINE
    #         LD   A,E
    #         LD   (0FFFFh),A     ; ripristina i sottoslot
    # FINE:   EI
    #         RET
    binari_48k_0000h = bytes([
        0xF3, 0xDB, 0xA8, 0x57, 0x07, 0x07, 0xE6, 0x03, 0x4F, 0xC6, 0xC1, 0x6F,
        0x26, 0xFC, 0xCB, 0x7E, 0x28, 0x11, 0x3A, 0xFF, 0xFF, 0x2F, 0x5F, 0xE6,
        0xFC, 0x47, 0x7B, 0x07, 0x07, 0xE6, 0x03, 0xB0, 0x32, 0xFF, 0xFF, 0x7A,
        0xE6, 0xFC, 0xB1, 0xD3, 0xA8, 0xD5, 0x21, 0x00, 0x90, 0x11, 0x00, 0x00,
        0x01, 0x00, 0x40, 0xED, 0xB0, 0xD1, 0x7A, 0xD3, 0xA8, 0x07, 0x07, 0xE6,
        0x03, 0xC6, 0xC1, 0x6F, 0x26, 0xFC, 0xCB, 0x7E, 0x28, 0x04, 0x7B, 0x32,
        0xFF, 0xFF, 0xFB, 0xC9,
    ])

    # Loader finale per le ROM da 48kb: come binari_32k_8000h, ma prima di avviare il
    # gioco mette tutte le pagine dello slot della RAM sul sottoslot della pagina 3
    # (l'equivalente della POKE -1,(15-PEEK(-1)\16)*17 per gli MSX2). Così un gioco che
    # porta la pagina 0 sul proprio slot cambiando solo lo slot primario trova la RAM
    # (con i suoi 16kb) e non, per esempio, la SubROM nel sottoslot 3-0.
    #
    #         DI
    #         LD   A,(0FFFFh)
    #         CPL
    #         AND  0C0h           ; sottoslot della pagina 3
    #         LD   B,A
    #         RRCA
    #         RRCA
    #         OR   B              ; ... anche per la pagina 2
    #         LD   B,A
    #         RRCA
    #         RRCA
    #         RRCA
    #         RRCA
    #         OR   B              ; ... e per le pagine 1 e 0
    #         LD   (0FFFFh),A
    #         (segue binari_32k_8000h dalla scelta degli slot primari in poi)
    binari_48k_8000h = bytes([
        0xF3, 0x3A, 0xFF, 0xFF, 0x2F, 0xE6, 0xC0, 0x47, 0x0F, 0x0F, 0xB0, 0x47,
        0x0F, 0x0F, 0x0F, 0x0F, 0xB0, 0x32, 0xFF, 0xFF,
    ]) + binari_32k_8000h[14:]

    binari_8k_4000h = bytes([243, 58, 255, 255, 47, 245, 230, 240, 71,
                             7, 7, 7, 7, 176, 50, 255, 255, 219, 168,
                             245, 230, 240, 71, 7, 7, 7, 7, 176, 211,
                             168, 33, 0, 160, 17, 0, 0, 1, 0, 32, 237,
                             176, 33, 0, 0, 17, 0, 32, 1, 0, 160, 237,
                             176, 241, 211, 168, 241, 50, 255, 255, 199])

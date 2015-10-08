class Parametri:

    frequenza = 19200  # 19.200hz
    bitrate = 1200  # 1200bps
    ampiezza = 0.9  # 90% dell'ampiezza massima

    campionamenti = frequenza / bitrate
    passo = int(campionamenti / 4)

    # --=-=--------------------------------------------------------------------------=-=--

    @staticmethod
    def ricalcola_onde():

        max = int(255 * Parametri.ampiezza)
        min = 255 - max

        # Ricalcola il silenzio

        Parametri.wave_silenzio = []
        for i in range(int(Parametri.campionamenti)):
            Parametri.wave_silenzio.append(128)

        Parametri.wave_bit_0 = []
        for i in range(Parametri.passo * 2):
            Parametri.wave_bit_0.append(min)
        for i in range(Parametri.passo * 2):
            Parametri.wave_bit_0.append(max)

        Parametri.wave_bit_1 = []
        for i in range(Parametri.passo):
            Parametri.wave_bit_1.append(min)
        for i in range(Parametri.passo):
            Parametri.wave_bit_1.append(max)
        for i in range(Parametri.passo):
            Parametri.wave_bit_1.append(min)
        for i in range(Parametri.passo):
            Parametri.wave_bit_1.append(max)

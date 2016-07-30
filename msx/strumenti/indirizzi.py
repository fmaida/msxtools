class Indirizzo:

    def __init__(self, p_valore: int = 0x0000):
        self.valore = 0
        self.valore_a = 0
        self.valore_b = 0
        self.imposta(p_valore)

    def imposta(self, p_valore: int):
        self.valore = p_valore
        temp = (hex(p_valore))[2:]  # Elimina dalla stringa lo "0x" iniziale. Es: "0x123f" -> "123f"
        temp = temp.zfill(4)  # Aggiunge zeri davanti al numero se è inferiore alle quattro cifre
        self.valore_a = int(str(temp)[0:2], 16)
        self.valore_b = int(str(temp)[2:4], 16)

    def get(self, p_inverti: bool = True) -> bytes:

        if p_inverti:
            return bytes([self.valore_b, self.valore_a])
        else:
            return bytes([self.valore_a, self.valore_b])

    def __add__(self, p_altro):
        self.imposta(self.valore + p_altro)
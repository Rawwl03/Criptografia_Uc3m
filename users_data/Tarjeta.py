

class Tarjeta:

    def __init__(self, user, datos, nonce, saldo):
        self.propietario = user
        self.cifrado = datos
        self.nonce_tarj = nonce
        self.saldo = saldo



class Tarjeta:

    def __init__(self, user, datos, nonce, salt_used, saldo):
        self.propietario = user
        self.cifrado = datos
        self.nonce_tarj = nonce
        self.salt_used = salt_used
        self.saldo = saldo

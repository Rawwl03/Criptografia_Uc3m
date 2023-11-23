
class User:
    def __init__(self, nombre, hash, salt, rol):
        self.username = nombre
        self.hash = hash
        self.salt = salt
        self.role = rol
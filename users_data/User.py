
class User:
    def __init__(self, nombre, hash, salt):
        self.username = nombre
        self.hash = hash
        self.salt = salt

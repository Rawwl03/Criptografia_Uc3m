
class User:
    def __init__(self, nombre, hash, id, salt):
        self.username = nombre
        self.hash = hash
        self.id = id
        self.salt = salt
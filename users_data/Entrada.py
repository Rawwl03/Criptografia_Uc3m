import hashlib


class Entrada:

    def __init__(self, pelicula, hora, sala, fila, asiento, cliente):
        self.pelicula = pelicula
        self.hora = hora
        self.sala = sala
        self.fila = fila
        self.asiento = asiento
        self.cliente = cliente
        self.id = hashlib.md5(self.__str__().encode()).hexdigest()

    def __str__(self):
        return "Entrada-> "+ self.__dict__

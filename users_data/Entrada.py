import base64, json


class Entrada:

    def __init__(self, pelicula, hora, sala, fila, asiento, cliente):
        self.pelicula = pelicula
        self.hora = hora
        self.sala = sala
        self.fila = fila
        self.asiento = asiento
        self.cliente = cliente
        self.id = self.__str__()

    def __str__(self):
        return base64.b64encode(json.dumps(self.__dict__).encode('utf-8'))

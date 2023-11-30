import base64, json


class Entrada:

    def __init__(self, pelicula, hora, sala, fila, asiento, cliente):
        self.pelicula = pelicula
        self.hora = hora
        self.sala = sala
        self.fila = fila
        self.asiento = asiento
        self.cliente = cliente
        self.id = self.obtener_id()

    """Función para obtener un id codificado a partir de los datos de la entrada"""
    def obtener_id(self):
        return base64.b64encode(json.dumps(self.__dict__).encode('utf-8'))

    """Función para cuando se imprima la información de una entrada"""
    def __str__(self):
        return "Película: "+self.pelicula+", Hora: "+self.hora+", Sala: "+str(self.sala)+", Fila: "+str(self.fila)+", Asiento: "+str(self.asiento)+", Cliente: "+self.cliente
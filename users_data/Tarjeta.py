from json_py.json_tarjetas import Json_tarjetas

class Tarjeta:

    def __init__(self, user, datos, id):
        self.propietario = user
        self.cifrado = datos
        self.json = Json_tarjetas()
        self.guardar_tarjeta(id)

    def guardar_tarjeta(self, id):
        Json_tarjetas.registrar_tarjeta([self.propietario, self.cifrado], id)

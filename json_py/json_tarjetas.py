from .Json_class import Json

ruta_json = "datos/tarjetas.json"
class Json_tarjetas(Json):

    def __init__(self):
        super().__init__(ruta_json)

    def registrar_tarjeta(self, tarjeta, id):
        self.cargar_datos()
        self._data_list.append(tarjeta)
        self.actualizar_json()

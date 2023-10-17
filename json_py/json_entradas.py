from .Json_class import Json

ruta_json = "datos/entradas.json"
class Json_entradas(Json):

    def __init__(self):
        super().__init__(ruta_json)

    def registrar_entrada(self, entrada):
        self.cargar_datos()
        self._data_list.append(entrada.__dict__)
        self.actualizar_json()


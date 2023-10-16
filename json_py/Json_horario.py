from .Json_class import Json

ruta_json = "datos/horario_salas.json"
class Json_horario(Json):

    def __init__(self):
        super().__init__(ruta_json)



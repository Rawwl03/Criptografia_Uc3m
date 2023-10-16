from .Json_class import Json

ruta_json = "datos/log_proceso-cifrados.json"
class json_log(Json):

    def __init__(self):
        super().__init__(ruta_json)

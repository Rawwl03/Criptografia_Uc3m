import json

class Json:
    def __init__(self, ruta: str):
        self.ruta_json = ruta
        self.data_list = []
        self.cargar_datos()

    def cargar_datos(self) -> None:
        try:
            with open(self.ruta_json, "r", encoding="utf-8", newline="") as file:
                self._data_list = json.load(file)
        except FileNotFoundError:
            # file is not found , so  init my data_list
            self._data_list = []
        except json.JSONDecodeError as exception:
            raise "JSON Decode Error - Wrong JSON Format" from exception

    def actualizar_json(self):
        try:
            with open(self.ruta_json, "w", encoding="utf-8", newline="") as file:
                json.dump(self._data_list, file, indent=2)
        except FileNotFoundError as exception:
            raise "Wrong file or file path" from exception

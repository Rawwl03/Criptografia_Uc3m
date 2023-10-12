import json
from User import User

class Json_users:
    def __init__(self):
        self.ruta_json = "datos/users_registered.json"
        self._data_list = []
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

    def contr_check(self, id:int, hash) -> bool:
        if self._data_list[id]["hash"] == str(hash):
            return True
        return False

    def buscar_user(self, user:str) -> (bool, int, int):
        for usuario in self._data_list:
            if usuario["username"] == user:
                return True, usuario["id"], usuario["salt"]
        return False, None, None

    def actualizar_json(self):
        try:
            with open(self.ruta_json, "w", encoding="utf-8", newline="") as file:
                json.dump(self._data_list, file, indent=2)
        except FileNotFoundError as exception:
            raise "Wrong file or file path" from exception

    def registrar_user(self, usuario_reg: User):
        self.cargar_datos()
        self._data_list.append(usuario_reg.__dict__)
        self.actualizar_json()

    def cont_ret(self, id):
        return self._data_list[id]["hash"]

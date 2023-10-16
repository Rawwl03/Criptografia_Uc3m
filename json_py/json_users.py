from .Json_class import Json

ruta_json = "datos/users_registered.json"
class Json_users(Json):

    def __init__(self):
        super().__init__(ruta_json)

    def contr_check(self, id:int, hash) -> bool:
        if self._data_list[id]["hash"] == str(hash):
            return True
        return False

    def buscar_user(self, user:str) -> (bool, int, int):
        for usuario in self._data_list:
            if usuario["username"] == user:
                return True, usuario["id"], usuario["salt"]
        return False, None, None

    def registrar_user(self, usuario_reg):
        self.cargar_datos()
        self._data_list.append(usuario_reg.__dict__)
        self.actualizar_json()

    def cont_ret(self, id):
        return self._data_list[id]["hash"]

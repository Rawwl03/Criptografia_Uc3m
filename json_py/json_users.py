from .Json_class import Json

ruta_json = "datos/users_registered.json"
class Json_users(Json):

    def __init__(self):
        super().__init__(ruta_json)

    def buscar_user(self, user:str):
        for usuario in self._data_list:
            if usuario["username"] == user:
                return True
        return False

    def registrar_user(self, usuario_reg):
        self.cargar_datos()
        self._data_list.append(usuario_reg.__dict__)
        self.actualizar_json()

    def cont_ret(self, id):
        return self._data_list[id]["hash"]

    def id_ret(self, usuario):
        for user in self._data_list:
            if user["username"]==usuario:
                return user["id"]

    def salt_ret(self, id):
        return self._data_list[id]["salt"]

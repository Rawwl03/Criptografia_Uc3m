from .Json_class import Json

ruta_json = "datos/tarjetas.json"
class Json_tarjetas(Json):

    def __init__(self):
        super().__init__(ruta_json)

    def registrar_tarjeta(self, tarjeta):
        self.cargar_datos()
        self._data_list.append(tarjeta.__dict__)
        self.actualizar_json()

    def tarjetas_user(self, user):
        tarjetas_user = []
        for tarjeta in self._data_list:
            if tarjeta["propietario"] == user:
                tarjetas_user.append(tarjeta)
        return tarjetas_user

    def actualizar_saldo(self, saldo_nuevo, tarjeta_user):
        for tarjeta in self._data_list:
            if tarjeta==tarjeta_user:
                tarjeta["saldo"] = saldo_nuevo
        self.actualizar_json()

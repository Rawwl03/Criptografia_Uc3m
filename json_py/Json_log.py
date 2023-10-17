from .Json_class import Json
from datetime import datetime

ruta_json = "datos/log_proceso-cifrados.json"
class json_log(Json):

    def __init__(self):
        super().__init__(ruta_json)

    def add_log_cifrado(self, data_c):
        self.cargar_datos()
        fecha_actual = datetime.now()
        proceso = "Proceso de cifrado completado el dia "+str(fecha_actual.day)+"/"+str(
            fecha_actual.month)+"/"+str(fecha_actual.year)+" a las "+str(fecha_actual.hour)+":"+str(
            fecha_actual.hour)+". Algoritmo usado: AESGCM (utilizacion de nonce). El resultado obtenido de cifrar "\
                  +data_c[0]+" ha sido "+data_c[1]
        self._data_list.append(proceso)
        self.actualizar_json()

    def add_log_descifrado(self, data_c):
        self.cargar_datos()
        fecha_actual = datetime.now()
        proceso = "Proceso de descifrado completado el dia " + str(fecha_actual.day) + "/" + str(
            fecha_actual.month) + "/" + str(fecha_actual.year) + " a las " + str(fecha_actual.hour) + ":" + str(
            fecha_actual.hour) + ". Algoritmo usado: AESGCM (utilizacion de nonce). El resultado obtenido de descifrar "\
                 + data_c[1] + " ha sido "+data_c[0]
        self._data_list.append(proceso)
        self.actualizar_json()
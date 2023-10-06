import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from json_users import Json_users
from User import User
from freezegun import freeze_time
from cryptography.exceptions import InvalidKey
from Cine import Cine

class Terminal:

    @freeze_time("2023-10-02")
    def __init__(self):
        self.database = Json_users()
        self.cine = Cine()

    def sys_inicio(self):
        accedido = False
        while not accedido:
            print("Seleccione una opción para acceder al sistema")
            acceso = input("Registro || Acceder\n")
            if acceso.lower() == "registro":
                CR = self.registro()
                if CR == 0:
                    print("Registro realizado con éxito\n")
                else:
                    print("Error durante el registro")
            elif acceso.lower() == "acceder":
                user_accedido = self.acceder()
                if user_accedido:
                    accedido = True
                    print("Bienvenido a CINESA, " + user_accedido)
                self.accion_cine(user_accedido)
            else:
                print("Tienes que registrarte o acceder con una cuenta")

    def acceder(self):
        i = 0
        while i < 3:
            username = input("Introduce tu usuario. Si quiere salir escriba EXIT\n")
            if username.upper() == "EXIT":
                return None
            existe, id, salt_user = self.database.buscar_user(username)
            if not existe:
                print("Este usuario no se encuentra registrado, ¿desea probar con otro nombre?")
                decision = input("SI || NO\n")
                if decision.upper() == "NO":
                    i += 3
                else:
                    i += 1
                if i >= 3:
                    print("Saliendo del sistema")
                    return None
            else:
                i = 0
                while i < 3:
                    contrasena_h = input("Introduce la contraseña\n")
                    cont_store = self.database.cont_ret(id-1)
                    prueba, salt_2 = self.encriptar_clave(contrasena_h, False, salt_user.encode('latin-1'))
                    validada = self.validate_contrs(cont_store.encode('latin-1'), contrasena_h, salt_user.encode('latin-1'))
                    if validada:
                        return username
                    else:
                        print("La contraseña es incorrecta, inténtelo de nuevo")
                        i += 1
                    if i >= 3:
                        print("Saliendo del sistema")
                        return None

    def registro(self):
        username = input("Introduce tu nombre de usuario deseado. Si quiere salir escriba EXIT\n")
        if username.upper() == "EXIT":
            return -1
        existe, id, salt = self.database.buscar_user(username)
        if existe:
            print("Este nombre de usuario ya ha sido registrado, introduzca otro")
        else:
            registro_correcto = False
            while not registro_correcto:
                c_validada = False
                while not c_validada:
                    contrasena_h = input("Introduzca una contraseña para tu cuenta. La contraseña deberá tener más de 8 caracteres y al menos un número y una letra mayúscula. Si desea salir, escriba EXIT\n")
                    if contrasena_h.upper() == "EXIT":
                        return -1
                    if self.aprobacion_clave(contrasena_h):
                        c_validada = True
                contrasena_h, salt_new = self.encriptar_clave(contrasena_h)
                contrasena_h2 = input("La clave introducida es válida. Repita la contraseña de nuevo\n")
                if self.validate_contrs(contrasena_h, contrasena_h2, salt_new):
                    registro_correcto = True
                    print("La contraseña ha sido validada")
                else:
                    print("Las contraseñas no son iguales, escríbalas correctamente otra vez")
            new_user = User(username, contrasena_h.decode('latin-1'), len(self.database._data_list) + 1, salt_new.decode('latin-1'))
            self.database.registrar_user(new_user)
            return 0

    def aprobacion_clave(self, contrasena:str):
        if len(contrasena)<8:
            return False
        contador_mayus = 0
        contador_nums = 0
        for letra in contrasena:
            if ord(letra)>47 and ord(letra)<58:
                contador_nums += 1
            elif ord(letra)>64 and ord(letra)<91:
                contador_mayus += 1
        if contador_nums > 0 and contador_mayus > 0:
            return True
        return False

    def encriptar_clave(self, clave:str, new=True, salt=None):
        if new:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=30000)
        key = kdf.derive(clave.encode())
        return key, salt

    def validate_contrs(self, contr_hash, contr_str, salt):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=30000)
        try:
            kdf.verify(contr_str.encode(), contr_hash)
        except InvalidKey:
            print("Las contraseñas no coinciden")
            return False
        return True

    def accion_cine(self, user_accedido):
        salir_sys = False
        while not salir_sys:
            print("¿Que acción desea realizar, "+ user_accedido+"?")
            accion = input("Cartelera || Comprar || Salir\n")
            if accion.lower() == "cartelera":
                print("Estas son nuestras películas disponibles:")
                for i in range(0, len(self.cine.peliculas_disponibles)-1):
                    print("-"+str(i+1)+"-"+self.cine.peliculas_disponibles[i].nombre+", duración -> "+str(self.cine.peliculas_disponibles[i].duracion)+" minutos")
                info_add = False
                bucle_info = False
                while not bucle_info:
                    decision = input("¿Desea ver información sobre alguna película en concreto, " + user_accedido + "? SI || NO\n")
                    if decision.lower() == "si":
                        peli = input("Seleccione el número de la película que quieras ver\n")
                        try:
                            num = int(peli)
                            if num > 0 and num < 15:
                                bucle_info = True
                                info_add = True
                            else:
                                print("El numero introducido está fuera de rango, escribe de nuevo un número entre el 1 y el 14 según la película de la que quieras saber más")
                        except ValueError:
                            print("No has introducido un numero")
                    elif decision.lower() == "no":
                        bucle_info = True
                    else:
                        print("No has seleccionado una opción correctamente, inténtelo de nuevo")
                if info_add:
                    print("-----"+self.cine.peliculas_disponibles[num-1].nombre+"-----\n-Duración de la película: "+str(self.cine.peliculas_disponibles[num-1].duracion)+" minutos\n-Información sobre la película: "+self.cine.peliculas_disponibles[num-1].descripcion+"\n-Horarios para ver la película " + self.cine.peliculas_disponibles[num-1].nombre + ":")
                    self.disponibilidad_pelicula(self.cine.peliculas_disponibles[num-1])
            elif accion.lower()=="comprar":
                print("Hay que definir esta operacion")
            elif accion.lower()=="salir":
                print("Saliendo del sistema, ¡hasta otra, "+user_accedido+"!")
                salir_sys = True
            else:
                print("Acción no válida en el sistema, introduzca de nuevo la acción correctamente")

    def disponibilidad_pelicula(self, pelicula):
        for i in range(0, self.cine.num_salas):
            dicc_horas = self.cine.salas[i].peliculas_dia.keys()
            for clave in dicc_horas:
                if self.cine.salas[i].peliculas_dia[clave] == pelicula.nombre:
                    print("->Sala "+str(i+1)+"| Hora: "+clave)

if __name__ == "__main__":
    term_1 = Terminal()
    term_1.sys_inicio()



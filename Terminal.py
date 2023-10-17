import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from json_py.json_users import Json_users
from users_data.User import User
from freezegun import freeze_time
from cryptography.exceptions import InvalidKey
from cinema_structure.Cine import Cine
from users_data.Tarjeta import Tarjeta
from json_py.json_tarjetas import Json_tarjetas

class Terminal:

    @freeze_time("2023-10-02")
    def __init__(self):
        self.database_users = Json_users()
        self.database_tarjetas = Json_tarjetas()
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
            existe = self.database_users.buscar_user(username)
            id = self.database_users.id_ret(username)
            salt_user = self.database_users.salt_ret(id-1)
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
                    cont_store = self.database_users.cont_ret(id-1)
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
        existe= self.database_users.buscar_user(username)
        if existe:
            print("Este nombre de usuario ya ha sido registrado, introduzca otro")
        else:
            registro_correcto = False
            while not registro_correcto:
                c_validada = False
                while not c_validada:
                    contrasena_h = input("Introduzca una contraseña para tu cuenta. La contraseña deberá tener más de 10 caracteres y al menos un número y una letra mayúscula. Si desea salir, escriba EXIT\n")
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
            new_user = User(username, contrasena_h.decode('latin-1'), len(self.database_users._data_list) + 1, salt_new.decode('latin-1'))
            self.database_users.registrar_user(new_user)
            return 0

    def aprobacion_clave(self, contrasena:str):
        if len(contrasena)<10:
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
                self.acc_cartelera(user_accedido)
            elif accion.lower()=="comprar":
                self.acc_compra(user_accedido)
            elif accion.lower()=="salir":
                print("Saliendo del sistema, ¡hasta otra, "+user_accedido+"!")
                salir_sys = True
            else:
                print("Acción no válida en el sistema, introduzca de nuevo la acción correctamente")

    def acc_cartelera(self, user_accedido):
        print("Estas son nuestras películas disponibles:")
        self.mostrar_peliculas()
        info_add = False
        bucle_info = False
        while not bucle_info:
            decision = input(
                "¿Desea ver información sobre alguna película en concreto, " + user_accedido + "? SI || NO\n")
            if decision.lower() == "si":
                numero_c = False
                while not numero_c:
                    peli = input("Seleccione el número de la película que quieras ver\n")
                    try:
                        num = int(peli)
                        if num > 0 and num < 15:
                            bucle_info = True
                            info_add = True
                            numero_c = True
                        else:
                            print(
                                "El numero introducido está fuera de rango, escribe de nuevo un número entre el 1 y el 14 según la película de la que quieras saber más")
                    except ValueError:
                        print("No has introducido un numero")
            elif decision.lower() == "no":
                bucle_info = True
            else:
                print("No has seleccionado una opción correctamente, inténtelo de nuevo")
        if info_add:
            self.info_pelicula(num)

    def acc_compra(self, user_accedido):
        print("Las películas disponibles son las siguientes:")
        self.mostrar_peliculas()
        numero_c = False
        while not numero_c:
            peli = input("Seleccione el número de la película que quieras ver. Si quiere salir, escriba EXIT\n")
            if peli.upper() == "EXIT":
                return 0
            else:
                try:
                    num = int(peli)
                    if num > 0 and num < 15:
                        peli_selec = self.cine.peliculas_disponibles[num-1]
                        print("Horarios disponibles para la pelicula " + peli_selec.nombre)
                        entradas = self.disponibilidad_pelicula(peli_selec)
                        if len(entradas)>0:
                            numero_c = True
                        else:
                            print("No hay entradas disponibles para la película "+peli_selec.nombre)
                    else:
                        print("El numero introducido está fuera de rango, escribe de nuevo un número entre el 1 y el 14 según la película de la que quieras saber más")
                except ValueError:
                    print("No has introducido un numero")
        ent_comprada = False
        seleccion = False
        while not ent_comprada:
            confirmacion = False
            while not seleccion:
                entrada_selec = input("¿Que entrada quieres comprar? Escriba el número correspondiente a la entrada que desea (Entre 1 y "+str(len(entradas))+"). Si quiere salir, escriba EXIT\n")
                if entrada_selec.upper() == "EXIT":
                    return 0
                else:
                    try:
                        id = int(entrada_selec)
                        if id < 1 or id > len(entradas):
                            print("Por favor, introduzca una entrada válida en el rango 1-"+str(len(entradas)))
                        else:
                            seleccion = True
                    except ValueError:
                        print("No has introducido un valor correcto")
            while not confirmacion:
                print("-Entrada seleccionada-\nPelícula: " + peli_selec.nombre + "\nSala: " + str(entradas[id-1][1]) + "\nHora: " + entradas[id-1][2])
                ent_correcta = input("¿Desea comprar esta entrada? SI||NO\n")
                if ent_correcta.upper() == "SI":
                        print("El precio de la entrada son 8€, se procederá al pago con tarjeta")
                        ent_comprada = True
                        confirmacion = True
                elif ent_correcta.upper() == "NO":
                        print("Horarios disponibles para la pelicula " + peli_selec.nombre)
                        self.disponibilidad_pelicula(peli_selec)
                        seleccion = False
                        confirmacion = True
                else:
                        print("Para continuar con la compra, introduzca SI o NO, por favor")
        tarjetas_user = self.database_tarjetas.tarjetas_user(user_accedido)
        if len(tarjetas_user) == 0:
            print("Usted no tiene tarjetas guardadas, deberá guardar una primero para realizar el pago")
            decision_tomada = False
            while not decision_tomada:
                decision = input("¿Desea continuar? SI||NO\n")
                if decision.upper() == "SI":
                    self.cifrado_tarjeta(user_accedido)
                    decision_tomada = True
                elif decision.upper() == "NO":
                    return 0
                else:
                    print("Porfavor, escriba la decisión que desees tomar correctamente")
        pago = False
        while not pago:
            acc_tarj = input("¿Qué quiere acción quiere realizar con las tarjetas? Guardar||Seleccionar||EXIT\n")
            if acc_tarj.upper() == "GUARDAR":
                self.cifrado_tarjeta(user_accedido)
            elif acc_tarj.upper() == "SELECCIONAR":
                tarjeta_input = self.datos_tarjeta(user_accedido)
                tarjeta_db = self.validar_tarjeta(tarjeta_input, user_accedido)
                if tarjeta_db:
                    pago_finished = self.pago(tarjeta_db)
                    if not pago_finished:
                        print("Esta tarjeta no tiene suficiente saldo para comprar una entrada, seleccione o guarde una tarjeta con saldo suficiente, porfavor")
                    else:
                        pago = True
            else:
                return 0
        print("El pago de 8€ para la entrada de la película "+ peli_selec.nombre+" ha sido realizado, gracias por su compra "+user_accedido)

    def pago(self, tarjeta):
        saldo = int(tarjeta["saldo"])
        if saldo < 8:
            return False
        else:
            self.database_tarjetas.actualizar_saldo(saldo-8, tarjeta)
            return True

    def disponibilidad_pelicula(self, pelicula):
        entradas = []
        for i in range(0, len(self.cine.salas)):
            dicc_horas = self.cine.salas[i].peliculas_dia.keys()
            for clave in dicc_horas:
                if self.cine.salas[i].peliculas_dia[clave] == pelicula.nombre:
                    print("-> Sala "+str(i+1)+" | Hora: "+clave)
                    entradas.append((pelicula.nombre, i+1, clave))
        return entradas

    def info_pelicula(self, num):
        print("-----" + self.cine.peliculas_disponibles[num - 1].nombre + "-----\n-Duración de la película: " + str(
            self.cine.peliculas_disponibles[num - 1].duracion) + " minutos\n-Información sobre la película: " +
              self.cine.peliculas_disponibles[num - 1].descripcion + "\n-Horarios para ver la película " +
              self.cine.peliculas_disponibles[num - 1].nombre + ":")
        self.disponibilidad_pelicula(self.cine.peliculas_disponibles[num - 1])

    def mostrar_peliculas(self):
        for i in range(0, len(self.cine.peliculas_disponibles) - 1):
            print("-" + str(i + 1) + "-" + self.cine.peliculas_disponibles[i].nombre + ", duración -> " + str(self.cine.peliculas_disponibles[i].duracion) + " minutos")

    def cifrado_tarjeta(self, user_accedido):
        id = self.database_users.id_ret(user_accedido)
        nonce = os.urandom(12)
        datos = self.datos_tarjeta(user_accedido)
        contrasena = self.database_users.cont_ret(id-1)
        aes = AESGCM(contrasena.encode('latin-1'))
        tarj_cifr = aes.encrypt(nonce, datos.encode('latin-1'), None)
        tarjeta = Tarjeta(user_accedido, tarj_cifr.decode('latin-1'), nonce.decode('latin-1'), 30)
        self.database_tarjetas.registrar_tarjeta(tarjeta)
        print("La tarjeta es válida y ha sido guardada")

    def descifrar_tarj(self, tarj_guardada):
        nonce = tarj_guardada["nonce_tarj"].encode('latin-1')
        cyphertext = tarj_guardada["cifrado"].encode('latin-1')
        id = self.database_users.id_ret(tarj_guardada["propietario"])
        key = self.database_users.cont_ret(id-1)
        aes = AESGCM(key.encode('latin-1'))
        desc = aes.decrypt(nonce, cyphertext, None)
        return desc.decode('latin-1')

    def datos_tarjeta(self, user_accedido):
        validacion = False
        while not validacion:
            num_tarj = input(user_accedido+", introduzca el número de su tarjeta (16 dígitos)\n")
            if self.validar_num_tarj(num_tarj):
                validacion = True
        validacion = False
        while not validacion:
            fecha_tarj = input(user_accedido + ", introduzca la fecha de caducidad de su tarjeta en formato mes/año\n")
            if self.validar_fecha_tarj(fecha_tarj):
                validacion = True
        validacion = False
        while not validacion:
            cvv_tarj = input(user_accedido + ", introduzca el número de su tarjeta (3 dígitos)\n")
            if self.validar_cvv_tarj(cvv_tarj):
                validacion = True
        datos = num_tarj+"-"+fecha_tarj+"-"+cvv_tarj
        return datos
    def validar_num_tarj(self, num_tarj):
        if len(num_tarj)!=16:
            print("El código introducido no tiene formato correcto")
            return False
        for num in num_tarj:
            if ord(num)<48 or ord(num)>57:
                print("El código introducido no tiene formato correcto")
                return False
        return True

    def validar_fecha_tarj(self, fecha_tarj):
        if len(fecha_tarj)!=7:
            print("El código introducido no tiene formato correcto")
            return False
        for i in range(0,len(fecha_tarj)-1):
            if i == 2:
                if fecha_tarj[i] != "/":
                    print("El código introducido no tiene formato correcto")
                    return False
            else:
                if ord(fecha_tarj[i]) < 48 or ord(fecha_tarj[i]) > 57:
                    print("El código introducido no tiene formato correcto")
                    return False
        month = fecha_tarj[:2]
        year = fecha_tarj[3:]
        if int(month) < 1 or int(month) > 12:
            print("El mes introducido no es válido")
            return False
        if int(year) < 2024 or int(year) > 2031:
            print("El año introducido no es válido")
            return False
        return True

    def validar_cvv_tarj(self, cvv_tarj):
        if len(cvv_tarj) != 3:
            print("El código introducido no tiene formato correcto")
            return False
        for num in cvv_tarj:
            if ord(num) < 48 or ord(num) > 57:
                print("El código introducido no tiene formato correcto")
                return False
        return True

    def validar_tarjeta(self, tarjeta_input, user_accedido):
        for tarjeta in self.database_tarjetas._data_list:
            if user_accedido == tarjeta["propietario"]:
                descrifrado = self.descifrar_tarj(tarjeta)
                if descrifrado == tarjeta_input:
                    return tarjeta
        return None


if __name__ == "__main__":
    term_1 = Terminal()
    term_1.sys_inicio()



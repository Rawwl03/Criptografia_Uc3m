import os, base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from users_data.User import User
from freezegun import freeze_time
from cryptography.exceptions import InvalidKey
from users_data.Tarjeta import Tarjeta
from Database import Database
from users_data.Entrada import Entrada


"""VARIABLES GLOBALES"""
contrasena_sys = ""


"Clase en la que se ejecutan todas las operaciones necesarias para el funcionamiento"
class Terminal:

    @freeze_time("2023-10-02")
    def __init__(self):
        self.db = Database()

    """Función de inicio de la terminal. Tendrás que registrarte (crear user que no este ya registrado y escribir contraseña válida)
    o acceder con una cuenta existente (escribir usuario y contraseña respectivos). Una vez accedido, se pasa a acc_cine, 
    pasando el user que ha accedido como parámetro"""
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
                    """El salt y el hash de la contraseña del usuario rotan cada vez que el usuario accede al sistema"""
                    self.rotacion_claves(user_accedido)
            else:
                print("Tienes que registrarte o acceder con una cuenta")
        print("Bienvenido a CINESA, " + user_accedido)
        self.accion_cine(user_accedido)

    """Esta función valida los datos introducidos y los comprueba con los existentes en la base de datos, para así permitir
    el acceso al sistema con ese perfil. La contraseña introducida será cifrada y validada con la existente en la base de datos.
    Si todo ha ido correctamente, se devolverá a sys_inicio el usuario que ha accedido. Si no, significa que el usuario ha decidido
    salir de la fase de registro."""
    def acceder(self):
        global contrasena_sys
        i = 0
        while i < 3:
            username = input("Introduce tu usuario. Si quiere salir escriba EXIT\n")
            if username.upper() == "EXIT":
                return False
            user = self.db.existe_user(username)
            if len(user) == 0:
                print("Este usuario no se encuentra registrado, ¿desea probar con otro nombre?")
                decision = input("SI || NO\n")
                if decision.upper() == "NO":
                    return False
                else:
                    i += 1
                if i >= 3:
                    print("Saliendo del sistema")
                    return False
            else:
                i = 0
                while i < 3:
                    contrasena_h = input("Introduce la contraseña\n")
                    cont_store = base64.b64decode(user[0][1])
                    salt_user = base64.b64decode(user[0][2])
                    validada = self.validate_contrs(cont_store, contrasena_h, salt_user)
                    if validada:
                        contrasena_sys = contrasena_h
                        return username
                    else:
                        print("La contraseña es incorrecta, inténtelo de nuevo")
                        i += 1
                    if i >= 3:
                        print("Saliendo del sistema de acceso")
                        return False

    """Función encargada de la fase de registro de usuarios. Se encargar de recibir datos correctos, cifrar la contraseña dada,
     y guardar los datos necesarios en la base de datos para que este usuario pueda acceder posteriormente al sistema. Si todo 
     funciona correctamente, devolverá 0. Si no, significa que el usuario ha decidido salir de la fase de registro."""
    def registro(self):
        username = input("Introduce tu nombre de usuario deseado. Si quiere salir escriba EXIT\n")
        if username.upper() == "EXIT":
            return -1
        user = self.db.existe_user(username)
        if len(user) != 0:
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
            new_user = User(username, base64.b64encode(contrasena_h), base64.b64encode(salt_new))
            self.db.anadir_user_registered(new_user)
            return 0

    """Valida la contraseña introducida como input en el registro de usuario. Características de validación:
     Mínimo 10 caracteres, al menos un número y al menos una mayúscula."""
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

    """Se encarga de encriptar la clave mediante un str introducido (contraseña en input). Va a ser encriptada mediante la función 
    PBKDF2HMAC, que usará el algoritmo SHA256 y un salt introducido, realizará 30000 iteraciones y devuelve un hash de 32 bytes.
    La función devuelve el hash obtenido y el salt utilizado"""
    def encriptar_clave(self, clave:str, new=True, salt=None):
        if new:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=30000)
        key = kdf.derive(clave.encode())
        return key, salt

    """Se encargar de comprobar que la contraseña input de acceso es igual a la contraseña almacenada (hash). Utiliza la misma función
    de derivación que para cifrar, con el salt de la contraseña guardada para que pueda dar el mismo resultado. La función kdf.verify necesita dos parámetros de tipo bytes,
    cifra contr_str (input, pero hay que transformar en bytes) y lo compara con contr_hash. Si no son iguales, salatará un error de tipo InvalidKey. Devuelve True si son iguales."""
    def validate_contrs(self, contr_hash, contr_str, salt):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=30000)
        try:
            kdf.verify(contr_str.encode(), contr_hash)
        except InvalidKey:
            print("Las contraseñas no coinciden")
            return False
        return True

    """Continuación de sys_inicio tras el acceso de user_accedido, aquí se pretende registrar la acción solicitada entre las 
    disponibles y proceder a realizar esa operación. Hay 4 definidas."""
    def accion_cine(self, user_accedido):
        salir_sys = False
        while not salir_sys:
            print("¿Que acción desea realizar, "+ user_accedido+"?")
            accion = input("Cartelera || Comprar || Perfil || Salir\n")
            if accion.lower() == "cartelera":
                self.acc_cartelera(user_accedido)
            elif accion.lower()=="comprar":
                self.acc_compra(user_accedido)
            elif accion.lower()=="perfil":
                self.acc_perfil(user_accedido)
            elif accion.lower()=="salir":
                print("Saliendo del sistema, ¡hasta otra, "+user_accedido+"!")
                salir_sys = True
                self.db.cerrar_base()
            else:
                print("Acción no válida en el sistema, introduzca de nuevo la acción correctamente")

    """La función se encarga de mostrar las películas que hay disponibles para ver, y además puede mostrar inforación adicional
    sobre la película deseada en cuanto a sus horarios disponibles o información adicional."""
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

    """En esta función se lleva a cabo el proceso de compra de entradas. Sigue el siguiente proceso: selección de película deseada
    (y muestra disponibles), selección de asiento deseado (y muestra disponibles), menú tarjeta (guardar, seleccionar y borrar),
    selección de tarjeta y pago de la entrada. Se guarda la entrada seleccionada en la base de datos."""
    def acc_compra(self, user_accedido):
        #Se muestran y se selecciona la película deseada"
        print("Las películas disponibles son las siguientes:")
        self.mostrar_peliculas()
        peliculas = self.db.consultar_peliculas()
        numero_c = False
        while not numero_c:
            peli = input("Seleccione el número de la película que quieras ver. Si quiere salir, escriba EXIT\n")
            if peli.upper() == "EXIT":
                return 0
            else:
                try:
                    num = int(peli)
                    if num > 0 and num < 15:
                        peli_selec = peliculas[num-1]
                        print("Horarios disponibles para la pelicula " + peli_selec[0])
                        entradas = self.disponibilidad_pelicula(peli_selec)
                        if len(entradas)>0:
                            numero_c = True
                        else:
                            print("No hay entradas disponibles para la película "+peli_selec[0])
                    else:
                        print("El numero introducido está fuera de rango, escribe de nuevo un número entre el 1 y el 14 según la película de la que quieras saber más")
                except ValueError:
                    print("No has introducido un numero")
        #Se procede a la selección de horario para la película que se desea ver
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
                print("-Entrada seleccionada-\nPelícula: " + peli_selec[0] + "\nSala: " + str(entradas[id-1][0]) + "\nHora: " + entradas[id-1][1])
                ent_correcta = input("¿Desea comprar esta entrada? SI||NO\n")
                if ent_correcta.upper() == "SI":
                        #Se procede a la selección de asiento, que devuelve si se ha seleccionado uno y el asiento seleccionado
                        seleccion_check, asiento = self.seleccion_asiento(entradas[id-1])
                        if seleccion_check == 0:
                            print("Horarios disponibles para la pelicula " + peli_selec[0])
                            entradas = self.disponibilidad_pelicula(peli_selec)
                        elif seleccion_check:
                            print("El precio de la entrada son 8€, se procederá al pago con tarjeta")
                            ent_comprada = True
                            confirmacion = True
                elif ent_correcta.upper() == "NO":
                        print("Horarios disponibles para la pelicula " + peli_selec[0])
                        self.disponibilidad_pelicula(peli_selec)
                        seleccion = False
                        confirmacion = True
                else:
                        print("Para continuar con la compra, introduzca SI o NO, por favor")
        tarjetas_user = self.db.select_tarjetas(user_accedido)
        #Caso en el que el usuario no tiene tarjetas guardadas, se necesita al menos una para realizar el pago
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
        #Selección de tarjeta (o guardar una, o borrarla), realización del pago y guardar tarjeta en la base de datos
        pago = False
        while not pago:
            acc_tarj = input("¿Qué quiere acción quiere realizar con las tarjetas? Guardar || Seleccionar || Borrar || EXIT\n")
            if acc_tarj.upper() == "GUARDAR":
                self.cifrado_tarjeta(user_accedido)
            elif acc_tarj.upper() == "SELECCIONAR":
                tarjeta_db = self.validar_tarjeta(user_accedido)
                if tarjeta_db:
                    pago_finished = self.pago(tarjeta_db)
                    if not pago_finished:
                        print("Esta tarjeta no tiene suficiente saldo para comprar una entrada, seleccione o guarde una tarjeta con saldo suficiente, porfavor")
                    else:
                        pago = True
                        entrada = Entrada(peli_selec[0], entradas[id-1][1], entradas[id-1][0], asiento[1], asiento[0], user_accedido)
                        self.db.anadir_entrada(entrada)
                else:
                    print("Los datos introducidos no corresponden a ninguna tarjeta de tu propiedad, si no la has guardado con anterioridad, porfavor, hazlo")
            elif acc_tarj.upper() == "BORRAR":
                tarjetas = self.mostrar_tarjetas(user_accedido)
                if len(tarjetas)>0:
                    borrado = False
                    while not borrado:
                        selec = self.borrar_tarjeta(tarjetas)
                        if not selec:
                            return 0
                        else:
                            borrado = True
                    print("Tarjeta borrada correctamente de la base de datos")
            elif acc_tarj.upper() == "EXIT":
                return 0
            else:
                print("Introduzca una operación válida")
        print("El pago de 8€ para la entrada de la película "+ peli_selec[0]+" ha sido realizado, gracias por su compra "+user_accedido)

    """Función que tiene la gestión del perfil de user_accedido. Se pueden realizar 6 acciones."""
    def acc_perfil(self, user_accedido):
        accion = False
        while not accion:
            print("¿Que acción deseas realizar en tu perfil?")
            acc = input("Guardar (tarjeta) || Borrar (tarjeta) || Cambiar (contraseña) || Entradas || Tarjetas || EXIT\n")
            if acc.lower() == "guardar":
                self.cifrado_tarjeta(user_accedido)
            elif acc.lower() == "borrar":
                tarjetas = self.mostrar_tarjetas(user_accedido)
                if len(tarjetas)>0:
                    borrado = False
                    while not borrado:
                        selec = self.borrar_tarjeta(tarjetas)
                        if selec == "EXIT":
                            return 0
                        elif selec:
                            borrado = True
                    print("La tarjeta ha sido borrada con éxito")
            elif acc.lower() == "cambiar":
                print("Hay que definir el cambio de contraseña")
            elif acc.lower() == "entradas":
                self.mostrar_entradas(user_accedido)
            elif acc.lower() == "tarjetas":
                self.mostrar_tarjetas(user_accedido)
            elif acc.lower() == "exit":
                return 0
            else:
                print("Acción introducida no válida")

    """Recibe una tarjeta, que es la seleccionada como método de pago, y se realiza el pago restándole  8 al saldo de la tarjeta seleccionada.
    Si no tiene saldo, no se realiza el pago y se devuelve False. Si se realiza, se devuelve True."""
    def pago(self, tarjeta):
        saldo = tarjeta[4]
        if saldo < 8:
            return False
        else:
            self.db.actualizar_saldo(tarjeta[1], saldo - 8)
            return True

    """Recibe un número, que se corresponde con la película seleccionada para ver más inforamción. Esta información se imprime
    en la terminal (Duración, Descripción, Horarios disponibles)"""
    def info_pelicula(self, num):
        peliculas = self.db.consultar_peliculas()
        print("-----" + peliculas[num - 1][0] + "-----\n-Duración de la película: " + str(
            peliculas[num - 1][1]) + " minutos\n-Información sobre la película: " +
              peliculas[num - 1][2] + "\n-Horarios para ver la película " +
              peliculas[num - 1][0] + ":")
        self.disponibilidad_pelicula(peliculas[num - 1])

    """Tras recibir como parámetro una película, se muestran los horarios disponibles de esa película en cada sala y hora. 
    Devuelve todas las entradas_posibles para en acc_compra poder seleccionar el horario que se desee."""
    def disponibilidad_pelicula(self, pelicula):
        entradas_posibles = self.db.horarios_peli(pelicula)
        for entrada in entradas_posibles:
                print("-> Sala "+str(entrada[0])+" | Hora: "+entrada[1])
        return entradas_posibles

    """Obtiene todas las películas disponibles que existen en la base de datos y las muestra junto a la duración de cada una"""
    def mostrar_peliculas(self):
        peliculas = self.db.consultar_peliculas()
        for i in range(0, len(peliculas) - 1):
            print("-" + str(i + 1) + "-" + peliculas[i][0] + ", duración -> " + str(peliculas[i][1]) + " minutos")

    """Recibe la entrada_selec, que corresponde a un horario de una película seleccionado en acc_compra. Muestra los asientos disponibles
    para ese horario (busca en la base de datos), es decir, los asientos que no han sido cogidos en ninguna entrada, y luego se 
    selecciona un asiento de los mostrados y se devuelve True y el asiento si todo ha ido correctamente. Se devuelve False y None
    si el usuario desea salir del menú de selección de asiento."""
    def seleccion_asiento(self, entrada_selec):
        print("Estos son todos los asientos disponibles para la película '"+ entrada_selec[2]+"' a las "+entrada_selec[1])
        print("\t---Sala " + str(entrada_selec[0]) + "---")
        asientos_dispo = self.db.asientos_disponibles(entrada_selec)
        for asiento in asientos_dispo:
            print("-> Fila "+str(asiento[1])+", Asiento "+str(asiento[0]))
        seleccionado = False
        while not seleccionado:
            sel = input("Introduzca el asiento que desees en el formato Fila/Asiento. Si desea salir, escriba EXIT\n")
            if sel.upper() == "EXIT":
                return False, None
            datos_asiento = sel.split('/')
            if len(datos_asiento) == 1:
                print("No has introducido el asiento deseado en el formato correcto")
            else:
                for asiento in asientos_dispo:
                    if int(asiento[1]) == int(datos_asiento[0]) and int(asiento[0]) == int(datos_asiento[1]):
                        return True, asiento
                print("No se ha encontrado dicha entrada, seleccione una disponible")

    """Esta función se encarga de recibir una tarjeta por input, cifrarla para el user_accedido y guardarla en la base de datos.
    Genera un nonce para cada tarjeta, recibe los datos que serán cifrados (Numtarjeta/fcaducidad/cvv) a través de la función datos_tarjeta
    , cifra los datos mediante el algoritmo AESGCM con la contraseña del usuario (hash), y por último guarda la tarjeta y un log en la
    base de datos indicando que se ha producido un proceso de cifrado. Se produce cifrado simétrico autenticado."""
    def cifrado_tarjeta(self, user_accedido):
        user = self.db.existe_user(user_accedido)
        nonce = os.urandom(12)
        datos = self.datos_tarjeta(user_accedido)
        key, salt_used = self.encriptar_clave(contrasena_sys, True)
        aes = AESGCM(key)
        tarj_cifr = aes.encrypt(nonce, datos.encode(), None)
        tarjeta = Tarjeta(user_accedido, base64.b64encode(tarj_cifr), base64.b64encode(nonce), base64.b64encode(salt_used), 30)
        self.db.anadir_tarjeta(tarjeta)
        self.db.anadir_log(["Cifrado", user[0][0], datos, base64.b64encode(tarj_cifr)])
        print("La tarjeta es válida y ha sido guardada")

    """Con la tarj_guardada que recibe, que se corresponde con una tarjeta del usuario, se obtiene el nonce de la tarjeta y, usando
    el mismo algotirmo simétrico autenticado que en el cifrado de tarjetas, se descifran los datos de la tarjeta. Se añade un log de
    descifrado, y se devuelven los datos descifrados para compararlos"""
    def descifrar_tarj(self, tarj_guardada):
        user = self.db.existe_user(tarj_guardada[0])
        nonce = base64.b64decode(tarj_guardada[2])
        cyphertext = base64.b64decode(tarj_guardada[1])
        key, salt = self.encriptar_clave(contrasena_sys, False, base64.b64decode(tarj_guardada[3]))
        aes = AESGCM(key)
        desc = aes.decrypt(nonce, cyphertext, None)
        self.db.anadir_log(["Descifrado", user[0][0], desc.decode(), base64.b64encode(cyphertext)])
        return desc.decode()

    """Función que va a obtener los datos de la tarjeta y lo que devuelve son esos datos recibidos por input juntos"""
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

    """Se encarga de validar el número de la tarjeta introducido en input. Tiene que tener longitud de 16 dígitos, y ser numérico"""
    def validar_num_tarj(self, num_tarj):
        if len(num_tarj)!=16:
            print("El código introducido no tiene formato correcto")
            return False
        for num in num_tarj:
            if ord(num)<48 or ord(num)>57:
                print("El código introducido no tiene formato correcto")
                return False
        return True

    """Se encarga de validar la fecha de caducidad de la tarjeta introducida en un input. Tiene que tener longitud = 7, tener una /, y antes 
    de la barra tiene que haber 2 dígitos que representan al mes (entre 01 y 12) y después 4 dígitos representando el año (desde 2023 hasta 2031)"""
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

    """Se encarga de validar el cvv de la tarjeta introducida por parámetro. Tiene que tener longitud = 3, y sus dígitos tienen que ser números."""
    def validar_cvv_tarj(self, cvv_tarj):
        if len(cvv_tarj) != 3:
            print("El código introducido no tiene formato correcto")
            return False
        for num in cvv_tarj:
            if ord(num) < 48 or ord(num) > 57:
                print("El código introducido no tiene formato correcto")
                return False
        return True

    """Primero muestra las tarjetas que posee el user_accedido. Si el user_accedido no tiene tarjetas registradas, no se hará nada.
     Si no, luego, recibe la tarjeta seleccionada (orden), descifra esa tarjeta para coger su cvv, y si el cvv introducido corresponde 
     con el cvv de la tarjeta se devuelve la tarjeta seleccionada. Si se escribe exit, devuelve False"""
    def validar_tarjeta(self, user_accedido):
        tarjetas = self.mostrar_tarjetas(user_accedido)
        if len(tarjetas) > 0:
            seleccion = False
            while not seleccion:
                num = input("Seleccione la tarjeta que desea utilizar escribiendo el orden en el que aparece\n")
                if num.upper() == "EXIT":
                    return False
                try:
                    id = int(num)
                    if id > len(tarjetas) or id < 1:
                        print(
                            "Has seleccionado un numero fuera del rango de tus tarjetas, por favor, introdúzcalo correctamente")
                    else:
                        desc = self.descifrar_tarj(tarjetas[id-1])
                        cvv = desc[25:]
                        cvv_inp = input("Introduzca el cvv de la tarjeta correspondiente\n")
                        if cvv == cvv_inp:
                            return tarjetas[id-1]
                        else:
                            print("El cvv introducido no corresponde con el de la tarjeta")
                except ValueError:
                    print("No has introducido un valor correcto")

    """Esta función borra una tarjeta entre todas las tarjetas del usuario. La tarjeta a borrar se especifica a través de un input"""
    def borrar_tarjeta(self, tarjetas):
        selec = input(
            "¿Que tarjeta desea eliminar? Indique el número en el que aparece la tarjeta a borrar. Si desea salir, escriba EXIT\n")
        if selec.upper() == "EXIT":
            return "EXIT"
        try:
            id = int(selec)
            if id > len(tarjetas) or id < 1:
                print(
                    "Has seleccionado un numero fuera del rango de tus tarjetas, por favor, introdúzcalo correctamente")
            else:
                self.db.borrar_tarjeta(tarjetas[id - 1])
                return True
        except ValueError:
            print("No has introducido un valor correcto")

    """Metodo que permite actualizar el salt y el hash de la contraseña de un usuario. 
    También actualiza el cifrado de las tarjetas cuando cambiar_tarjetas=True"""
    def rotacion_claves(self, username, cambiar_tarjetas=False):
        global contrasena_sys
        contrasena_h, salt_new = self.encriptar_clave(contrasena_sys)
        print(contrasena_h)
        self.db.actualizar_contrasena(username, base64.b64encode(contrasena_h), base64.b64encode(salt_new))
        if cambiar_tarjetas:
            tarjetas_usuario=self.db.select_tarjetas(username)
            if len(tarjetas_usuario) > 0:
                for tarjeta in tarjetas_usuario:
                    saldo=tarjeta[4]
                    nonce = base64.b64decode(tarjeta[2])
                    datos_desc_tarjeta=self.descifrar_tarj(tarjeta)
                    """Se vuelve a generar un nuevo hash de la contraseña con un nuevo salt"""
                    key, salt_used = self.encriptar_clave(contrasena_sys)
                    aes = AESGCM(key)
                    tarj_cifr = aes.encrypt(nonce, datos_desc_tarjeta.encode(), None)
                    """Se borra el regitro actual de la tarjeta de la base de datos y se añade uno nuevo actualizado con el nuevo salt y el nuevo cifrado de la tarjeta"""
                    self.db.borrar_tarjeta(tarjeta)
                    tarjeta_actualizada = Tarjeta(username, base64.b64encode(tarj_cifr), base64.b64encode(nonce),
                                      base64.b64encode(salt_used), saldo)
                    self.db.anadir_tarjeta(tarjeta_actualizada)

    """Muestra las tarjetas una a una del usuario de las tarjetas registradas en la base de datos. Aparecerán en orden de como están
    registradas, cada una se descifrará, y se mostrarán los últimos 4 dígitos del número de la tarjeta además de la fecha de caducidad."""
    def mostrar_tarjetas(self, user_accedido):
        tarjetas = self.db.select_tarjetas(user_accedido)
        if len(tarjetas) == 0:
            print("No hay tarjetas guardadas")
        else:
            print("Tus tarjetas son las siguientes:")
            for i in range(0, len(tarjetas)):
                desc = self.descifrar_tarj(tarjetas[i])
                digits = desc[12:16]
                fecha_cad = desc[17:24]
                print("|" + str(
                    i + 1) + "| ->Tarjeta terminada en ************" + digits + ", con fecha de caducidad en " + fecha_cad)
        return tarjetas

    """Selecciona las entradas que ha comprado user_accedido, y las muestra, imprimiendo en la terminal los datos de la entrada
    y cuantas entradas ha comprado el usuario en total"""
    def mostrar_entradas(self, user_accedido):
        entradas = self.db.entradas_compradas(user_accedido)
        print(user_accedido+", ha comprado un total de "+str(len(entradas))+" entradas. Tus entradas son las siguientes:")
        for i in range(0, len(entradas)):
            print("|"+str(i+1)+"| -> Pelicula: "+entradas[i][0]+", Hora: "+entradas[i][1]+", Sala: "+str(entradas[i][2])+", Fila: "+str(entradas[i][3])+", Asiento: "+str(entradas[i][4]))

if __name__ == "__main__":
    term_1 = Terminal()
    term_1.sys_inicio()



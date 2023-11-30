import base64, json
import sqlite3, random, os
from cinema_structure.Película import Pelicula
from cinema_structure.Sala import Sala
from cinema_structure.Fila import Fila
from cinema_structure.Asiento import Asiento
from cinema_structure.Horario_Peli import Horario_Peli
import datetime
from users_data.Tarjeta import Tarjeta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

class Database:

    def __init__(self):
        self.base = sqlite3.connect("BaseDatos.db")
        self.puntero = self.base.cursor()
        self.contrasena_sys = "Sistema!01!Key"
        self.generar_base()

    """Método para la generación de la db. Contiene creación de tablas y generación de elementos como películas, horario, salas, filas y asientos."""
    def generar_base(self):
        #Para poder inicializar la base de datos desde 0
        self.cerrar_base()
        os.remove("BaseDatos.db")
        self.base = sqlite3.connect("BaseDatos.db")
        self.puntero = self.base.cursor()

        # Borrar claves asimétricas que había porque los users ya no están
        ficheros_asim_keys = os.listdir("claves_privadas/")
        for archivo in ficheros_asim_keys:
            ruta_archivo = os.path.join("claves_privadas/", archivo)
            os.remove(ruta_archivo)

        creacion_base_entradas = "CREATE TABLE ENTRADAS (ID BLOB, Pelicula VARCHAR2 NOT NULL, Hora CHAR(5) NOT NULL, Sala INT(1) NOT NULL, Fila INT(2) NOT NULL, Asiento INT(3) NOT NULL, Cliente VARCHAR2 NOT NULL, PRIMARY KEY(ID), FOREIGN KEY(Pelicula) REFERENCES CARTELERA(Pelicula)," \
                                 "FOREIGN KEY(Asiento) REFERENCES ASIENTOS(Asiento), FOREIGN KEY(Fila) REFERENCES FILAS(Fila), FOREIGN KEY(Sala) REFERENCES SALAS(Sala))  "
        creacion_base_tarjetas = "CREATE TABLE TARJETAS (Propietario VARCHAR2 NOT NULL, Cifrado BLOB, Nonce_tarjeta BLOB NOT NULL, Salt_used BLOB NOT NULL," \
                                 " Saldo INT(3) NOT NULL, PRIMARY KEY(Cifrado), FOREIGN KEY (Propietario) REFERENCES USERS_REGISTERED(Username))"
        creacion_base_users_registered = "CREATE TABLE USERS_REGISTERED (Username VARCHAR2, Hash_contraseña BLOB NOT NULL, Salt BLOB NOT NULL, Rol VARCHAR2 NOT NULL, Saldo INT(3) NOT NULL," \
                                 " PRIMARY KEY(Username))"
        creacion_base_log_cif ="CREATE TABLE LOG_CIFRADO_SIM (ID INTEGER, Tipo VARCHAR2 NOT NULL, Hora CHAR(5) NOT NULL, Fecha CHAR(10) NOT NULL," \
                                 " Usuario VARCHAR2 NOT NULL, Data VARCHAR2 NOT NULL, Cypher BLOB NOT NULL, Key_used BLOB NOT NULL, PRIMARY KEY(ID))"
        creacion_base_log_firma = "CREATE TABLE LOG_FIRMA (ID INTEGER, Tipo VARCHAR2 NOT NULL, Hora CHAR(5) NOT NULL, Fecha CHAR(10) NOT NULL, " \
                                  "Data VARCHAR2 NOT NULL, Firma BLOB NOT NULL, Ku_used BLOB, Kv_used VARCHAR2, User VARCHAR2 NOT NULL, Estado_verificación VARCHAR2, PRIMARY KEY(ID))"
        creacion_base_horario = "CREATE TABLE HORARIO (Sala INT(2), Hora CHAR(2) NOT NULL, Pelicula VARCHAR2, PRIMARY KEY(" \
                                "Sala, Hora, Pelicula), FOREIGN KEY (Pelicula) REFERENCES CARTELERA(Pelicula), FOREIGN KEY(Sala) REFERENCES SALAS(Sala))"
        creacion_base_peliculas = "CREATE TABLE CARTELERA (Pelicula VARCHAR2, Duracion INT(3) NOT NULL, " \
                                  "Descripción VARCHAR2, PRIMARY KEY(Pelicula))"
        creacion_base_salas = "CREATE TABLE SALAS (Sala INT(1), Num_Filas INT(2) NOT NULL, Asientos_Fila INT(3) NOT NULL, PRIMARY KEY(Sala))"
        creacion_base_filas = "CREATE TABLE FILAS (Fila INT(2), Sala INT(1), Num_Asientos INT(3) NOT NULL, PRIMARY KEY(Fila, Sala)," \
                              " FOREIGN KEY(SALA) REFERENCES SALAS(Sala))"
        creacion_base_asientos = "CREATE TABLE ASIENTOS (Asiento INT(3), Fila INT(2), Sala INT(1), PRIMARY KEY(" \
                                 "Asiento, Fila, Sala), FOREIGN KEY(Fila) REFERENCES FILAS(Asiento), FOREIGN KEY(Sala) REFERENCES SALAS(ID))"
        creacion_base_claves_asimetricas = "CREATE TABLE ASYMETHRIC_KEYS (Usuario VARCHAR2, CERTIFICATE BLOB, PRIVATE_KEY_ROUTE VARCHAR2 NOT NULL, " \
                                           "PRIMARY KEY(Usuario), FOREIGN KEY (Usuario) REFERENCES USERS_REGISTERED(Username))"
        creacion_base_peticiones = "CREATE TABLE PETICIONES(Id INT(3), Tipo VARCHAR2 NOT NULL, Entrada BLOB, Username VARCHAR2 NOT NULL, FIRMA BLOB NOT NULL, PRIMARY KEY(Id), FOREIGN KEY(Username) REFERENCES USERS_REGISTERED(Username))"
        creacion_base_peticiones_terminadas = "CREATE TABLE PETICIONES_CONFIRMADAS(Id INT(3), Tipo VARCHAR2 NOT NULL, Entrada BLOB, Username VARCHAR2 NOT NULL, FIRMA BLOB,  Estado VARCHAR2 NOT NULL, Firmante VARCHAR2, PRIMARY KEY(Id), FOREIGN KEY(Username) REFERENCES USERS_REGISTERED(Username)) "
        creacion_base_cargos = "CREATE TABLE CARGOS(Tarjeta BLOB, Entrada BLOB, PRIMARY KEY(Entrada))"
        creacion_base_csr = "CREATE TABLE CSR(CSR BLOB, PRIMARY KEY(CSR))"

        self.puntero.execute(creacion_base_users_registered)
        self.puntero.execute(creacion_base_tarjetas)
        self.puntero.execute(creacion_base_log_cif)
        self.puntero.execute(creacion_base_log_firma)
        self.puntero.execute(creacion_base_peliculas)
        self.puntero.execute(creacion_base_salas)
        self.puntero.execute(creacion_base_filas)
        self.puntero.execute(creacion_base_asientos)
        self.puntero.execute(creacion_base_horario)
        self.puntero.execute(creacion_base_entradas)
        self.puntero.execute(creacion_base_claves_asimetricas)
        self.puntero.execute(creacion_base_peticiones)
        self.puntero.execute(creacion_base_peticiones_terminadas)
        self.puntero.execute(creacion_base_cargos)
        self.puntero.execute(creacion_base_csr)

        self.generar_asientos()
        self.generar_cartelera()
        self.generar_horario()

        self.crear_asimkeys_sys()

        self.base.commit()

    """Métodos para añadir elementos a la base de datos en su respectiva tabla, con el formato de la tabla"""
    def anadir_entrada(self, entrada):
        query = "INSERT INTO ENTRADAS (Id, Pelicula, Hora, Sala, Fila, Asiento, Cliente) VALUES (?,?,?,?,?,?,?)"
        self.puntero.execute(query, (entrada.id, entrada.pelicula, entrada.hora, entrada.sala, entrada.fila, entrada.asiento, entrada.cliente))
        self.base.commit()

    def anadir_tarjeta(self, tarjeta):
        query = "INSERT INTO TARJETAS (Propietario, Cifrado, Nonce_tarjeta, Salt_used, Saldo) VALUES (?,?,?,?,?)"
        self.puntero.execute(query, (tarjeta.propietario, tarjeta.cifrado, tarjeta.nonce_tarj, tarjeta.salt_used, tarjeta.saldo))
        self.base.commit()

    def anadir_user_registered(self, user):
        query = "INSERT INTO USERS_REGISTERED (Username, Hash_contraseña, Salt, Rol, Saldo) VALUES (?,?,?,?,?)"
        self.puntero.execute(query, (user.username, user.hash, user.salt, user.role, user.saldo_cuenta))
        self.base.commit()

    def anadir_log(self, datos):
        id = self.numero_logs() + 1
        hora_str, fecha_str = self.hora_fecha_actual()
        query = "INSERT INTO LOG_CIFRADO_SIM (ID, Tipo, Hora, Fecha, Usuario, Data, Cypher, Key_used) VALUES (?,?,?,?,?,?,?,?)"
        self.puntero.execute(query, (id, datos[0], hora_str, fecha_str, datos[1], datos[2], datos[3], datos[4]))
        self.base.commit()

    def anadir_horario(self, h_pelicula):
        query = "INSERT INTO HORARIO (Sala, Hora, Pelicula) VALUES (?,?,?)"
        self.puntero.execute(query, (h_pelicula.sala, h_pelicula.hora, h_pelicula.pelicula))
        self.base.commit()

    def anadir_pelicula(self, pelicula):
        query = "INSERT INTO CARTELERA (Pelicula, Duracion, Descripción) VALUES (?,?,?)"
        self.puntero.execute(query, (pelicula.nombre, pelicula.duracion, pelicula.descripcion))
        self.base.commit()

    def anadir_sala(self, sala):
        query = "INSERT INTO SALAS (Sala, Num_filas, Asientos_Fila) VALUES (?,?,?)"
        self.puntero.execute(query, (sala.numero, sala.num_filas, sala.asientos_filas))
        self.base.commit()

    def anadir_fila(self, fila):
        query = "INSERT INTO FILAS (Fila, Sala, Num_asientos) VALUES (?,?,?)"
        self.puntero.execute(query, (fila.orden, fila.sala, fila.num_asientos))
        self.base.commit()

    def anadir_asiento(self, asiento):
        query = "INSERT INTO ASIENTOS (Asiento, Fila, Sala) VALUES (?,?,?)"
        self.puntero.execute(query, (asiento.numero, asiento.fila, asiento.sala))
        self.base.commit()

    def anadir_claves_asim(self, datos):
        query = "INSERT INTO ASYMETHRIC_KEYS (Usuario, CERTIFICATE, PRIVATE_KEY_ROUTE) VALUES (?,?,?)"
        self.puntero.execute(query, (datos[0], datos[1], datos[2]))
        self.base.commit()

    def anadir_log_firma(self, datos):
        num = self.numero_logs_firma() + 1
        hora, fecha = self.hora_fecha_actual()
        query = "INSERT INTO LOG_FIRMA (ID , Tipo , Hora , Fecha , Data , Firma , Ku_used , Kv_used , User , Estado_verificación) VALUES (?,?,?,?,?,?,?,?,?,?)"
        self.puntero.execute(query, (num, datos[0], hora, fecha, datos[1], datos[2], datos[3], datos[4], datos[5], datos[6]))
        self.base.commit()


    def anadir_peticion(self, peticion):
        query = "INSERT INTO PETICIONES(Id, Tipo, Entrada, Username, FIRMA) VALUES (?,?,?,?,?)"
        self.puntero.execute(query, (peticion[0], peticion[1], peticion[2], peticion[3], peticion[4]))
        self.base.commit()

    def anadir_peticion_confirmada(self, peticion):
        query = "INSERT INTO PETICIONES_CONFIRMADAS(Id, Tipo, Entrada, Username, FIRMA, Estado, Firmante) VALUES (?,?,?,?,?,?,?)"
        self.puntero.execute(query, (
        peticion[0], peticion[1], peticion[2], peticion[3], peticion[4], peticion[5], peticion[6]))
        self.base.commit()

    def anadir_cargo(self, cargo):
        query = "INSERT INTO CARGOS(Tarjeta, Entrada) VALUES (?,?)"
        self.puntero.execute(query, (cargo[0], cargo[1]))
        self.base.commit()

    def anadir_csr(self, csr):
        query = "INSERT INTO CSR(CSR) VALUES (?)"
        self.puntero.execute(query, (csr,))
        self.base.commit()

    """Método para la generación de las películas disponibles para ver"""
    def generar_cartelera(self):
        descripcion = ""
        self.anadir_pelicula(Pelicula("Abre jaime", 185, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Barbie y la manifestacion femenina", 114, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Piratas del Pacifico 2", 159, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Rush", 123, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Ocho apellidos alemanes", 107, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Mason", 140, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Fernando Alonso: la 33", 133, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Natillas con chorizo", 102, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("AFTER: una noche con Chucho Perez en Monaco", 120, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("El retorno de los minions", 132, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Alcasec para el mundo", 101, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("El rey tiburon", 200, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Bancan shatten", 134, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("La Ramona Pechugona", 106, descripcion))
        descripcion = ""
        self.anadir_pelicula(Pelicula("Titi me pregunto", 113, descripcion))

    """Método para generar las salas y la estructura de cada una (filas y asientos). El número de filas y asientos será aleatorio
    para cada sala entre ciertos valores"""
    def generar_asientos(self):
        for i in range(0,9):
            filas = random.randint(6,15)
            asientos = random.randint(15,20)
            self.anadir_sala(Sala(i+1, filas, asientos))
            for j in range(0, filas):
                self.anadir_fila(Fila(i+1, j+1, asientos))
                for k in range(0, asientos):
                    self.anadir_asiento(Asiento(k+1, j+1, i+1))

    """Método para generar el horario disponible de cada sala y peli, seleccionando las horas mediante una hora de inicio y
    la duración de la película que va a estar en dicha hora (y una hora de descanso)"""
    def generar_horario(self):
        horas_comienzo = ["10:45", "11:00", "11:15", "11:30"]
        hora_fin = 23
        horas_descanso = 1
        peliculas = self.consultar_peliculas()
        for i in range(0, 9):
            start_h = random.randint(0, len(horas_comienzo) - 1)
            hora_str = horas_comienzo[start_h]
            noche = False
            while not noche:
                num_pelicula = random.randint(1, 15)
                pelicula_select = peliculas[num_pelicula-1]
                self.anadir_horario(Horario_Peli(i+1, hora_str, pelicula_select[0]))
                hora_str = self.sumar_hora(pelicula_select[1], hora_str, horas_descanso)
                if int(hora_str[:2]) >= hora_fin:
                    noche = True

    def sumar_hora(self, duracion, hora_actual, hora_descanso):
        hora_act = int(hora_actual[:2])
        minuto_act = int(hora_actual[3:])
        minuto_act += duracion
        if minuto_act >= 60:
            hora_act += minuto_act // 60
            minuto_act = minuto_act % 60
        hora_act += hora_descanso
        if minuto_act < 10:
            minuto_act = "0" + str(minuto_act)
        hora_str = str(hora_act) + ":" + str(minuto_act)
        return hora_str

    """------------------CONSULTAS------------------"""

    def consultar_peticiones(self):
        query = "SELECT * FROM PETICIONES"
        self.puntero.execute(query)
        pets_u = self.puntero.fetchall()
        return pets_u

    def consultar_peticiones_conf(self):
        query = "SELECT * FROM PETICIONES_CONFIRMADAS"
        self.puntero.execute(query)
        pets_c = self.puntero.fetchall()
        return pets_c

    def consultar_peticiones_user(self, user):
        query = "SELECT * FROM PETICIONES WHERE Username = ?"
        self.puntero.execute(query, (user, ))
        pets = self.puntero.fetchall()
        return pets

    def consultar_peticiones_conf_user(self, user):
        query = "SELECT * FROM PETICIONES_CONFIRMADAS  WHERE Username = ?"
        self.puntero.execute(query, (user, ))
        pets_c = self.puntero.fetchall()
        return pets_c

    def consultar_users(self):
        query = "SELECT * FROM USERS_REGISTERED"
        self.puntero.execute(query)
        users = self.puntero.fetchall()
        return users

    """Consultas todas las películas disponibles"""
    def consultar_peliculas(self):
        query = "SELECT * FROM CARTELERA"
        self.puntero.execute(query)
        peliculas = self.puntero.fetchall()
        return peliculas

    """Consulta que devuelve un usuario y sus datos si este está registrado en la base de datos"""
    def existe_user(self, username):
        query = "SELECT * FROM USERS_REGISTERED WHERE Username = ?"
        self.puntero.execute(query, (username,))
        user = self.puntero.fetchall()
        return user

    """Consulta que devuelve el número de logs que hay en la base de datos"""
    def numero_logs(self):
        query = "SELECT * FROM LOG_CIFRADO_SIM"
        self.puntero.execute(query)
        logs = self.puntero.fetchall()
        return len(logs)

    def numero_logs_firma(self):
        query = "SELECT * FROM LOG_FIRMA"
        self.puntero.execute(query)
        logs_firma = self.puntero.fetchall()
        return len(logs_firma)

    """Consulta que devuelve las tarjetas que tiene un usuario"""
    def select_tarjetas(self, username):
        query = "SELECT * FROM TARJETAS WHERE Propietario = ?"
        self.puntero.execute(query, (username,))
        tarjetas = self.puntero.fetchall()
        return tarjetas

    """Consulta que devuelve los horarios disponibles para una película en concreto"""
    def horarios_peli(self, pelicula):
        query = "SELECT * FROM HORARIO WHERE Pelicula = ?"
        self.puntero.execute(query, (pelicula[0],))
        horarios_peli_selec = self.puntero.fetchall()
        return horarios_peli_selec

    """Consulta que devuelve las entradas compradas por un cliente"""
    def entradas_compradas(self, user_accedido):
        query = "SELECT * FROM ENTRADAS WHERE Cliente = ?"
        self.puntero.execute(query, (user_accedido,))
        entradas = self.puntero.fetchall()
        return entradas

    """Devuelve las claves asimétricas (pública y privada) de un usuario"""
    def consultar_claves_asim(self, user_accedido):
        query = "SELECT * FROM ASYMETHRIC_KEYS WHERE Usuario = ?"
        self.puntero.execute(query, (user_accedido,))
        asim_keys = self.puntero.fetchall()
        return asim_keys

    def num_sala(self, salaNum):
        query = "SELECT * FROM SALAS WHERE Sala = ?"
        self.puntero.execute(query, (salaNum,))
        sala = self.puntero.fetchall()
        return sala

    """Consulta que devuelve las tarjetas que tiene un usuario"""
    def select_cargo(self, entrada):
        query = "SELECT * FROM CARGOS WHERE Entrada = ?"
        self.puntero.execute(query, (entrada,))
        cargo = self.puntero.fetchall()
        return cargo

    """Consulta que devuelve las tarjetas que tiene un usuario"""
    def get_tarjeta(self, tarjeta):
        query = "SELECT * FROM TARJETAS WHERE Cifrado = ?"
        self.puntero.execute(query, (tarjeta,))
        tarj = self.puntero.fetchall()
        return tarj

    """Consulta que devuelve las entradas en orden según la película, y después según la hora"""
    def consultar_entradas(self):
        query = "SELECT * FROM ENTRADAS ORDER BY Pelicula, Hora"
        self.puntero.execute(query)
        entradas = self.puntero.fetchall()
        return entradas

    def consultar_csr(self):
        query = "SELECT * FROM CSR"
        self.puntero.execute(query)
        lista_csr = self.puntero.fetchall()
        return lista_csr

    """Consulta que devuelve los asientos disponibles para un horario de una película en concreto. entrada_selec es tipo Horario_Peli.
    Los asientos disponibles serán los asientos de una sala que no tengan entradas asignadas."""
    def asientos_disponibles(self, entrada_selec):
        query = "SELECT * FROM ENTRADAS WHERE Sala = '"+str(entrada_selec[0])+"' AND Hora = '"+entrada_selec[1]+"' AND Pelicula = '"+entrada_selec[2]+"'"
        self.puntero.execute(query)
        entradas = self.puntero.fetchall()
        query = "SELECT * FROM ASIENTOS WHERE Sala = '"+str(entrada_selec[0])+"'"
        self.puntero.execute(query)
        asientos = self.puntero.fetchall()
        query = "SELECT * FROM PETICIONES"
        self.puntero.execute(query)
        pets = self.puntero.fetchall()
        query = "SELECT * FROM PETICIONES_CONFIRMADAS"
        self.puntero.execute(query)
        pets_c = self.puntero.fetchall()
        disponibilidad = []
        for asiento in asientos:
            asiento_aparece = False
            for entrada in entradas:
                if asiento[0] == entrada[4] and asiento[1] == entrada[3]:
                    asiento_aparece = True
                    disponibilidad.append([asiento[0], asiento[1], "O"])
            for peticion in pets:
                if peticion[1] == "Compra":
                    entrada = json.loads(base64.b64decode(peticion[2]).decode('utf-8'))
                    if entrada["sala"] == entrada_selec[0] and entrada["hora"] == entrada_selec[1] and entrada["pelicula"] == entrada_selec[2] and asiento[0] == entrada["asiento"] and entrada["fila"] == asiento[1]:
                        asiento_aparece = True
                        disponibilidad.append([asiento[0], asiento[1], "O"])
            for peticion_c in pets_c:
                if peticion_c[1] == "Compra":
                    entrada = json.loads(base64.b64decode(peticion_c[2]).decode('utf-8'))
                    if entrada["sala"] == entrada_selec[0] and entrada["hora"] == entrada_selec[1] and entrada[
                        "pelicula"] == entrada_selec[2] and asiento[0] == entrada["asiento"] and entrada["fila"] == asiento[
                        1]:
                        asiento_aparece = True
                        disponibilidad.append([asiento[0], asiento[1], "O"])
            if not asiento_aparece:
                    disponibilidad.append([asiento[0], asiento[1], "-"])
        return disponibilidad

    """Método que devuelve la fecha y hora actual en el formato deseado"""
    def hora_fecha_actual(self):
        t = datetime.datetime.now()
        if len(str(t.hour)) == 1:
            if len(str(t.minute)) == 1:
                hora_str = "0"+str(t.hour)+":0"+str(t.minute)
            else:
                hora_str = "0"+str(t.hour)+":"+str(t.minute)
        else:
            if len(str(t.minute)) == 1:
                hora_str = str(t.hour)+":0"+str(t.minute)
            else:
                hora_str = str(t.hour)+":"+str(t.minute)
        if len(str(t.day)) == 1:
            if len(str(t.month)) == 1:
                fecha_str = "0"+str(t.day)+"-0"+str(t.month)+"-0"+str(t.year)
            else:
                fecha_str = "0"+str(t.day)+"-"+str(t.month)+"-0"+str(t.year)
        else:
            if len(str(t.month)) == 1:
                fecha_str = str(t.day)+":0"+str(t.month)+":"+str(t.year)
            else:
                fecha_str = str(t.day)+"-"+str(t.month)+"-"+str(t.year)
        return hora_str, fecha_str

    """Actualización del saldo por saldo_nuevo en una tarjeta en concreto"""
    def actualizar_saldo(self, tarjeta, saldo_nuevo):
        query = "UPDATE TARJETAS SET Saldo = ? WHERE Cifrado = ?"
        self.puntero.execute(query, (saldo_nuevo, tarjeta))
        self.base.commit()

    """Borrado de tarjeta en concreto introducida por parámetro"""
    def borrar_tarjeta(self, tarjeta):
        query = "DELETE FROM TARJETAS WHERE Cifrado = ?"
        self.puntero.execute(query, (tarjeta[1],))
        self.base.commit()

    def borrar_user(self, user):
        query = "DELETE FROM USERS_REGISTERED WHERE Username = ?"
        self.puntero.execute(query, (user[0],))
        self.base.commit()

    def borrar_peticion(self, peticionID):
        query = "DELETE FROM PETICIONES WHERE Id = ?"
        self.puntero.execute(query, (peticionID,))
        self.base.commit()

    def borrar_peticion_conf(self, peticionID):
        query = "DELETE FROM PETICIONES_CONFIRMADAS WHERE Id = ?"
        self.puntero.execute(query, (peticionID,))
        self.base.commit()

    def borrar_entrada(self, entradaID):
        query = "DELETE FROM ENTRADAS WHERE Id = ?"
        self.puntero.execute(query, (entradaID,))
        self.base.commit()

    def borrar_cargo(self, entradaID):
        query = "DELETE FROM CARGOS WHERE Entrada = ?"
        self.puntero.execute(query, (entradaID,))
        self.base.commit()

    def borrar_asym_keys(self, username):
        query = "DELETE FROM ASYMETHRIC_KEYS WHERE Usuario = ?"
        self.puntero.execute(query, (username,))
        self.base.commit()

    def borrar_csr(self, csr):
        query = "DELETE FROM CSR WHERE CSR = ?"
        self.puntero.execute(query, (csr,))
        self.base.commit()

    """Función para cuando se haga la rotación de claves"""
    def actualizar_contrasena(self, user, hash_nuevo, salt_nuevo):
        query = "UPDATE USERS_REGISTERED SET Hash_contraseña = ?, Salt = ? WHERE Username = ?"
        self.puntero.execute(query, (hash_nuevo, salt_nuevo, user))
        self.base.commit()

    def actualizar_rol_user(self, user, nuevo_rol):
        query = "UPDATE USERS_REGISTERED SET Rol = ? WHERE Username = ?"
        self.puntero.execute(query, (nuevo_rol, user))
        self.base.commit()

    def actualizar_saldo_user(self, username, nuevo_saldo):
        query = "UPDATE USERS_REGISTERED SET Saldo = ? WHERE Username = ?"
        self.puntero.execute(query, (nuevo_saldo, username))
        self.base.commit()

    def actualizar_cert(self, cert, user):
        query = "UPDATE ASYMETHRIC_KEYS SET CERTIFICATE = ? WHERE Usuario = ?"
        self.puntero.execute(query, (cert, user))
        self.base.commit()

    """Aquí vamos a crear las claves asimétricas del sistema, para poder firmar desde el programa. Se hace aquí porque
    la base de datos tiene un atributo accesible que es la contraseña utilizada en el sistema, y además se genera junto con la
    base de datos inicialmente. También crearemos un certificado autofirmado"""
    def crear_asimkeys_sys(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        ruta_pem = "claves_privadas/Sistema.pem"
        cifrador = serialization.BestAvailableEncryption(self.contrasena_sys.encode())
        pem_k = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8,
                                        encryption_algorithm=cifrador)
        with open(ruta_pem, "wb") as archivo:
            archivo.write(pem_k)
        cert = self.certificado_propio("Sistema", private_key)
        datos = ["Sistema", cert, ruta_pem]
        self.anadir_claves_asim(datos)

    def certificado_propio(self, user_accedido, kv):
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, user_accedido)])
        cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
            kv.public_key()).serial_number(
            x509.random_serial_number()).not_valid_before(
            datetime.datetime.now()).not_valid_after(
            datetime.datetime.now() + datetime.timedelta(days=30)).sign(kv, hashes.SHA256())
        cert_codificado = cert.public_bytes(serialization.Encoding.PEM)
        return cert_codificado

    """Cerrar conexión con la base"""
    def cerrar_base(self):
        self.base.close()

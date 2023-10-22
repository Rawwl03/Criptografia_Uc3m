import sqlite3, random
from cinema_structure.Película import Pelicula
from cinema_structure.Sala import Sala
from cinema_structure.Fila import Fila
from cinema_structure.Asiento import Asiento
from cinema_structure.Horario_Peli import Horario_Peli
from datetime import datetime
from users_data.Tarjeta import Tarjeta

class Database:

    def __init__(self):
        self.base = sqlite3.connect("BaseDatos.db")
        self.puntero = self.base.cursor()
        #self.generar_base()

    def generar_base(self):

        creacion_base_entradas = "CREATE TABLE ENTRADAS (Pelicula VARCHAR2, Hora CHAR(5), Sala INT(1), Fila INT(2), Asiento INT(3), Cliente VARCHAR2 NOT NULL, PRIMARY KEY(Pelicula, Hora, Sala, Fila, Asiento), FOREIGN KEY(Pelicula) REFERENCES CARTELERA(Pelicula)," \
                                 "FOREIGN KEY(Asiento) REFERENCES ASIENTOS(Asiento), FOREIGN KEY(Fila) REFERENCES FILAS(Fila), FOREIGN KEY(Sala) REFERENCES SALAS(Sala))  "
        creacion_base_tarjetas = "CREATE TABLE TARJETAS (Propietario VARCHAR2 NOT NULL, Cifrado BLOB, Nonce_tarjeta BLOB NOT NULL," \
                                 " Saldo INT(3) NOT NULL, PRIMARY KEY(Cifrado), FOREIGN KEY (Propietario) REFERENCES USERS_REGISTERED(Username))"
        creacion_base_users_registered = "CREATE TABLE USERS_REGISTERED (Username VARCHAR2, Hash_contraseña BLOB NOT NULL, Salt BLOB NOT NULL," \
                                 " PRIMARY KEY(Username))"
        creacion_base_log ="CREATE TABLE LOG_CIFRADO_SIM (ID INTEGER, Tipo VARCHAR2 NOT NULL, Hora CHAR(5) NOT NULL, Fecha CHAR(10) NOT NULL," \
                                 " Usuario VARCHAR2 NOT NULL, Data VARCHAR2 NOT NULL, Cypher BLOB NOT NULL, FOREIGN KEY (Usuario) REFERENCES USERS_REGISTERED(Username), PRIMARY KEY(ID))"
        creacion_base_horario = "CREATE TABLE HORARIO (Sala INT(2), Hora CHAR(2) NOT NULL, Pelicula VARCHAR2, PRIMARY KEY(" \
                                "Sala, Hora, Pelicula), FOREIGN KEY (Pelicula) REFERENCES CARTELERA(Pelicula), FOREIGN KEY(Sala) REFERENCES SALAS(Sala))"
        creacion_base_peliculas = "CREATE TABLE CARTELERA (Pelicula VARCHAR2, Duracion INT(3) NOT NULL, " \
                                  "Descripción VARCHAR2, PRIMARY KEY(Pelicula))"
        creacion_base_salas = "CREATE TABLE SALAS (Sala INT(1), Num_Filas INT(2), PRIMARY KEY(Sala))"
        creacion_base_filas = "CREATE TABLE FILAS (Fila INT(2), Sala INT(1), Num_Asientos INT(3) NOT NULL, PRIMARY KEY(Fila, Sala)," \
                              " FOREIGN KEY(SALA) REFERENCES SALAS(Sala))"
        creacion_base_asientos = "CREATE TABLE ASIENTOS (Asiento INT(3), Fila INT(2), Sala INT(1), PRIMARY KEY(" \
                                 "Asiento, Fila, Sala), FOREIGN KEY(Fila) REFERENCES FILAS(Asiento), FOREIGN KEY(Sala) REFERENCES SALAS(ID))"

        self.puntero.execute(creacion_base_users_registered)
        self.puntero.execute(creacion_base_tarjetas)
        self.puntero.execute(creacion_base_log)
        self.puntero.execute(creacion_base_peliculas)
        self.puntero.execute(creacion_base_salas)
        self.puntero.execute(creacion_base_filas)
        self.puntero.execute(creacion_base_asientos)
        self.puntero.execute(creacion_base_horario)
        self.puntero.execute(creacion_base_entradas)

        self.generar_asientos()
        self.generar_cartelera()
        self.generar_horario()

        self.base.commit()

    def anadir_entrada(self, entrada):
        query = "INSERT INTO ENTRADAS (Pelicula, Hora, Sala, Fila, Asiento, Cliente) VALUES (?,?,?,?,?,?)"
        self.puntero.execute(query, (entrada.pelicula, entrada.hora, entrada.sala, entrada.fila, entrada.asiento, entrada.cliente))
        self.base.commit()

    def anadir_tarjeta(self, tarjeta):
        query = "INSERT INTO TARJETAS (Propietario, Cifrado, Nonce_tarjeta, Saldo) VALUES (?,?,?,?)"
        self.puntero.execute(query, (tarjeta.propietario, tarjeta.cifrado, tarjeta.nonce_tarj, tarjeta.saldo))
        self.base.commit()

    def anadir_user_registered(self, user):
        query = "INSERT INTO USERS_REGISTERED (Username, Hash_contraseña, Salt) VALUES (?,?,?)"
        self.puntero.execute(query, (user.username, user.hash, user.salt))
        self.base.commit()

    def anadir_log(self, datos):
        id = self.numero_logs() + 1
        hora_str, fecha_str = self.hora_fecha_actual()
        query = "INSERT INTO LOG_CIFRADO_SIM (ID, Tipo, Hora, Fecha, Usuario, Data, Cypher) VALUES (?,?,?,?,?,?,?)"
        self.puntero.execute(query, (id, datos[0], hora_str, fecha_str, datos[1], datos[2], datos[3]))
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
        query = "INSERT INTO SALAS (Sala, Num_filas) VALUES (?,?)"
        self.puntero.execute(query, (sala.numero, sala.num_filas))
        self.base.commit()

    def anadir_fila(self, fila):
        query = "INSERT INTO FILAS (Fila, Sala, Num_asientos) VALUES (?,?,?)"
        self.puntero.execute(query, (fila.orden, fila.sala, fila.num_asientos))
        self.base.commit()

    def anadir_asiento(self, asiento):
        query = "INSERT INTO ASIENTOS (Asiento, Fila, Sala) VALUES (?,?,?)"
        self.puntero.execute(query, (asiento.numero, asiento.fila, asiento.sala))
        self.base.commit()

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


    def generar_asientos(self):
        for i in range(0,9):
            filas = random.randint(6,15)
            self.anadir_sala(Sala(i+1, filas))
            asientos = random.randint(15,20)
            for j in range(0, filas):
                self.anadir_fila(Fila(i+1, j+1, asientos))
                for k in range(0, asientos):
                    self.anadir_asiento(Asiento(k+1, j+1, i+1))

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

    def consultar_peliculas(self):
        query = "SELECT * FROM CARTELERA"
        self.puntero.execute(query)
        peliculas = self.puntero.fetchall()
        return peliculas

    def existe_user(self, username):
        query = "SELECT * FROM USERS_REGISTERED WHERE Username = '"+username+"'"
        self.puntero.execute(query)
        user = self.puntero.fetchall()
        return user

    def select_tarjetas(self, username):
        query = "SELECT * FROM TARJETAS WHERE Propietario = '"+username+"'"
        self.puntero.execute(query)
        tarjetas = self.puntero.fetchall()
        return tarjetas

    def horarios_peli(self, pelicula):
        query = "SELECT * FROM HORARIO WHERE Pelicula = '"+pelicula[0]+"'"
        self.puntero.execute(query)
        horarios_peli_selec = self.puntero.fetchall()
        return horarios_peli_selec

    def asientos_disponibles(self, entrada_selec):
        asientos_dispo = []
        query = "SELECT * FROM ENTRADAS WHERE Sala = '"+str(entrada_selec[0])+"' AND Hora = '"+entrada_selec[1]+"' AND Pelicula = '"+entrada_selec[2]+"'"
        self.puntero.execute(query)
        entradas = self.puntero.fetchall()
        query = "SELECT * FROM ASIENTOS WHERE Sala = '"+str(entrada_selec[0])+"'"
        self.puntero.execute(query)
        asientos = self.puntero.fetchall()
        for asiento in asientos:
            asiento_aparece = False
            for entrada in entradas:
                if asiento[0] == entrada[4] and asiento[1] == entrada[3]:
                    asiento_aparece = True
            if not asiento_aparece:
                asientos_dispo.append(asiento)
        return asientos_dispo

    def actualizar_saldo(self, tarjeta, saldo_nuevo):
        query = "UPDATE TARJETAS SET Saldo = ? WHERE Cifrado = ?"
        self.puntero.execute(query, (saldo_nuevo, tarjeta))
        self.base.commit()

    def borrar_tarjeta(self, tarjeta):
        query = "DELETE FROM TARJETAS WHERE Cifrado = ?"
        self.puntero.execute(query, (tarjeta[1],))
        self.base.commit()

    def hora_fecha_actual(self):
        t = datetime.now()
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

    def numero_logs(self):
        query = "SELECT * FROM LOG_CIFRADO_SIM"
        self.puntero.execute(query)
        logs = self.puntero.fetchall()
        return len(logs)



    """Para cuando se haga la rotación de claves"""
    def actualizar_contrasena(self, user, hash_nuevo, salt_nuevo):
        query = "UPDATE USERS_REGISTERED SET Hash_contraseña = ? AND Salt = ? WHERE Username = ?"
        self.puntero.execute(query, (hash_nuevo, salt_nuevo, user[0]))
        self.base.commit()

    def actualizar_tarjeta(self, tarjeta, cifrado_nuevo, nonce_nuevo):
        query = "DELETE FROM TARJETAS WHERE Cifrado = ?"
        self.puntero.execute(query, (tarjeta[1]))
        tarjeta_nueva = Tarjeta(tarjeta[0], cifrado_nuevo, nonce_nuevo, tarjeta[3])
        self.anadir_tarjeta(tarjeta_nueva)

    def cerrar_base(self):
        self.base.close()

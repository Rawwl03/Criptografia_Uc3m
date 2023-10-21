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
        creacion_base_tarjetas = "CREATE TABLE TARJETAS (Propietario VARCHAR2 NOT NULL, Cifrado VARCHAR2, Nonce_tarjeta VARCHAR2 NOT NULL," \
                                 " Saldo INT(3) NOT NULL, PRIMARY KEY(Cifrado), FOREIGN KEY (Propietario) REFERENCES USERS_REGISTERED(Username))"
        creacion_base_users_registered = "CREATE TABLE USERS_REGISTERED (Username VARCHAR2, Hash_contraseña VARCHAR2 NOT NULL, Salt VARCHAR2 NOT NULL," \
                                 " PRIMARY KEY(Username))"
        creacion_base_log ="CREATE TABLE LOG_CIFRADO_SIM (Tipo VARCHAR2 NOT NULL, Hora CHAR(5) NOT NULL, Fecha CHAR(10) NOT NULL," \
                                 " Usuario VARCHAR2 NOT NULL, Data VARCHAR2 NOT NULL, Result VARCHAR2 NOT NULL, FOREIGN KEY (Usuario) REFERENCES USERS_REGISTERED(Username))"
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
        query = "INSERT INTO ENTRADAS (Pelicula, Hora, Sala, Fila, Asiento, Cliente) VALUES ('"+entrada[0]+"', '"+entrada[1]+"', '"+entrada[2]+"', '"+entrada[3]+"', '"+entrada[4]+"', '"+entrada[5]+"')"
        self.puntero.execute(query)
        self.base.commit()

    def anadir_tarjeta(self, tarjeta):
        query = "INSERT INTO TARJETAS (Propietario, Cifrado, Nonce_tarjeta, Saldo) VALUES ('"+tarjeta.propietario+"', '"+tarjeta.cifrado+"', '"+tarjeta.nonce_tarj+"', "+str(tarjeta.saldo)+")"
        self.puntero.execute(query)
        self.base.commit()

    def anadir_user_registered(self, user):
        query = "INSERT INTO USERS_REGISTERED (Username, Hash_contraseña, Salt) VALUES ('"+user.username+"', '"+user.hash+"', '"+user.salt+"')"
        self.puntero.execute(query)
        self.base.commit()

    def anadir_log(self, datos):
        t = datetime.now()
        hora_str = str(t.hour) +":"+str(t.minute)
        fecha_str = str(t.day) +"/"+str(t.month)+"/"+str(t.year)
        query = "INSERT INTO LOG_CIFRADO_SIM (Tipo, Hora, Fecha, Usuario, Data, Result) VALUES ('"+datos[0]+"', '"+hora_str+"', '"+fecha_str+"', '"+datos[1]+"', '"+datos[2]+"', '"+datos[3]+"')"
        self.puntero.execute(query)
        self.base.commit()

    def anadir_horario(self, h_pelicula):
        query = "INSERT INTO HORARIO (Sala, Hora, Pelicula) VALUES ("+str(h_pelicula.sala)+", '"+h_pelicula.hora+"', '"+h_pelicula.pelicula+"')"
        self.puntero.execute(query)
        self.base.commit()

    def anadir_pelicula(self, pelicula):
        query = "INSERT INTO CARTELERA (Pelicula, Duracion, Descripción) VALUES ('"+pelicula.nombre+"', "+str(pelicula.duracion)+", '"+pelicula.descripcion+"')"
        self.puntero.execute(query)
        self.base.commit()

    def anadir_sala(self, sala):
        query = "INSERT INTO SALAS (Sala, Num_filas) VALUES ("+str(sala.numero)+", "+str(sala.num_filas)+")"
        self.puntero.execute(query)
        self.base.commit()

    def anadir_fila(self, fila):
        query = "INSERT INTO FILAS (Fila, Sala, Num_asientos) VALUES ("+str(fila.orden)+", "+str(fila.sala)+", "+str(fila.num_asientos)+")"
        self.puntero.execute(query)
        self.base.commit()

    def anadir_asiento(self, asiento):
        query = "INSERT INTO ASIENTOS (Asiento, Fila, Sala) VALUES ("+str(asiento.numero)+", "+str(asiento.fila)+", "+str(asiento.sala)+")"
        self.puntero.execute(query)
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
        query = "SELECT * FROM (ASIENTOS MINUS (SELECT Asiento, Fila, Sala FROM (ENTRADA JOIN ASIENTOS USING(Sala, Fila, Asiento)" \
                "WHERE Sala = '"+str(entrada_selec[0])+"' AND Pelicula = '"+entrada_selec[2]+"' AND Hora = '"+entrada_selec[1]+"')))"
        self.puntero.execute(query)
        asientos = self.puntero.fetchall()
        return asientos

    def actualizar_saldo(self, tarjeta, saldo_nuevo):
        query = "UPDATE TARJETAS SET Saldo = "+str(saldo_nuevo)+"WHERE Cifrado = '"+tarjeta.cifrado+"'"
        self.puntero.execute(query)
        self.base.commit()



    """Para cuando se haga la rotación de claves"""
    def actualizar_contrasena(self, user, hash_nuevo, salt_nuevo):
        query = "UPDATE USERS_REGISTERED SET Hash_contraseña = '"+hash_nuevo+"' AND Salt = '"+salt_nuevo+"' WHERE Username = '"+user[0]+"'"
        self.puntero.execute(query)
        self.base.commit()

    def actualizar_tarjeta(self, tarjeta, cifrado_nuevo, nonce_nuevo):
        query = "DELETE FROM TARJETAS WHERE Cifrado = '"+tarjeta[1]
        self.puntero.execute(query)
        tarjeta_nueva = Tarjeta(tarjeta[0], cifrado_nuevo, nonce_nuevo, tarjeta[3])
        self.anadir_tarjeta(tarjeta_nueva)

    def cerrar_base(self):
        self.base.close()
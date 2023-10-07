import random
from Película import Pelicula
from Sala import Sala
from Fila import Fila
from Asiento import Asiento
from Json_horario import Json_horario

class Cine:

    def __init__(self):
        self.salas = []
        self.peliculas_disponibles = self.cartelera()
        self.horario = Json_horario()
        self.generacion_cine()

    def generacion_cine(self):
        for i in range(0,9):
            self.salas.append(Sala(i+1))
            filas = random.randint(6,15)
            asientos = random.randint(15,20)
            for j in range(0, filas-1):
                self.salas[i].filas.append(Fila(j+1))
                for k in range(0, asientos-1):
                    self.salas[i].filas[j].asientos.append(Asiento((k+1)*(j+1)))
        self.cargar_horario()

    def cartelera(self):
        peliculas = []
        descripcion = ""
        peliculas.append(Pelicula("Abre jaime", 185, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Barbie y la manifestacion femenina", 114, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Piratas del Pacifico 2", 159, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Rush", 123, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Ocho apellidos alemanes", 107, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Mason", 140, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Fernando Alonso: la 33", 133, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Natillas con chorizo", 102, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("AFTER: una noche con Chucho Perez en Monaco", 120, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("El retorno de los minions", 132, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Alcasec para el mundo", 101, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("El rey tiburon", 200, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Bancan shatten", 134, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("La Ramona Pechugona", 106, descripcion))
        descripcion = ""
        peliculas.append(Pelicula("Titi me pregunto", 113, descripcion))
        return peliculas

    def sumar_hora(self, duracion, hora_actual, hora_descanso):
        hora_act = int(hora_actual[:2])
        minuto_act = int(hora_actual[3:])
        minuto_act += duracion
        if minuto_act >= 60:
            hora_act += minuto_act//60
            minuto_act = minuto_act % 60
        hora_act += hora_descanso
        if minuto_act<10:
            minuto_act = "0"+str(minuto_act)
        hora_str = str(hora_act)+":"+str(minuto_act)
        return hora_str

    def cargar_horario(self):
        for i in range(0, len(self.salas)):
            for j in range(0, len(self.horario._data_list[i])):
                self.salas[i].peliculas_dia[self.horario._data_list[i][j][0]] = self.horario._data_list[i][j][1]

    """Método para generar el horario por primera vez o hacer que cambie"""
    def generar_horario(self):
        horas_comienzo = ["10:45", "11:00", "11:15", "11:30"]
        hora_fin = 23
        horas_descanso = 1
        horario = [[], [], [], [], [], [], [], [], []]
        for i in range(0, self.num_salas):
            start_h = random.randint(0,len(horas_comienzo)-1)
            hora_str = horas_comienzo[start_h]
            noche = False
            while not noche:
                num_pelicula = random.randint(0, len(self.peliculas_disponibles)-1)
                pelicula = self.peliculas_disponibles[num_pelicula]
                self.salas[i].peliculas_dia[hora_str] = pelicula.nombre
                horario[i].append((hora_str, pelicula.nombre))
                hora_str = self.sumar_hora(pelicula.duracion, hora_str, horas_descanso)
                if int(hora_str[:2]) >= hora_fin:
                    noche = True
        self.horario._data_list = horario
        self.horario.actualizar_json()

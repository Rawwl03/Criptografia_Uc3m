import os, base64, time, cv2, face_recognition, json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidKey, InvalidSignature

class Entrada:

    def __init__(self, pelicula, hora, sala, fila, asiento, cliente):
        self.pelicula = pelicula
        self.hora = hora
        self.sala = sala
        self.fila = fila
        self.asiento = asiento
        self.cliente = cliente
        self.id = self.__str__()

    def __str__(self):
        return base64.b64encode(json.dumps(self.__dict__).encode('utf-8'))


def acceso_biom():
    # Cargar la imagen de la cara que quieres reconocer
    imagen_conocida = face_recognition.load_image_file("accesoBiom.jpg")
    codificacion_conocida_rawwl = face_recognition.face_encodings(imagen_conocida)[0]
    codificacion_conocida_mario = face_recognition.face_encodings(imagen_conocida)[1]

    # Iniciar la cámara
    cap = cv2.VideoCapture(0)
    inicio = time.time()
    while True:
        # Capturar un fotograma
        ret, frame = cap.read()
        # Encontrar todas las caras en el fotograma
        ubicaciones = face_recognition.face_locations(frame)
        codificaciones = face_recognition.face_encodings(frame, ubicaciones)
        # Dibujar cuadros alrededor de las caras en el fotograma
        for ubicacion in ubicaciones:
            top, right, bottom, left = ubicacion
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        # Comparar con las caras conocidas
        for codificacion in codificaciones:
            coincidencias = face_recognition.compare_faces([codificacion_conocida_rawwl, codificacion_conocida_mario],
                                                           codificacion)
            if True in coincidencias:
                print("Acceso al sistema permitido")
                cap.release()
                cv2.destroyAllWindows()
                return codificacion
        # Mostrar el fotograma
        cv2.imshow('Frame', frame)
        lap = time.time()
        if lap - inicio > 10:
            print("Acceso al sistema denegado")
            cap.release()
            cv2.destroyAllWindows()
            return False
        # Salir del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Acceso al sistema denegado")
            cap.release()
            cv2.destroyAllWindows()
            return False
        time.sleep(0.5)

def firmar_datos(datos, kv):
        firma = kv.sign(datos.encode('utf-8'), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        return firma

def verificacion_firma(datos, firma, ku):
        try:
            ku.verify(firma, datos.encode('utf-8'), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            return True
        except InvalidSignature:
            return False


def generar_asimethric_keys():
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        return private_key, public_key


if __name__=="__main__":
    a = None
    b = [1]
    c = a+str(b[0])
    print(c)

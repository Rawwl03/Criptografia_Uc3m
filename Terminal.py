import hashlib
from json_users import Json_users
from User import User


class Terminal:
    def __init__(self):
        self.database = Json_users()

    def sys(self):
        accedido = False
        while not accedido:
            print("Seleccione una opción para acceder al sistema")
            acceso = input("Registro || Acceder\n")
            if acceso.lower() == "registro":
                self.registro()
                print("Registro realizado con éxito\n")
            elif acceso.lower() == "acceder":
                user_accedido = self.acceder()
                if user_accedido:
                    accedido = True
                    print("Bienvenido, " + user_accedido)
            else:
                print("Tienes que registrarte o acceder con una cuenta")

    def acceder(self) -> str:
        i = 0
        while i < 3:
            username = input("Introduce tu usuario. Si quiere salir escriba EXIT\n")
            if username.upper() == "EXIT":
                return None
            existe, id = self.database.buscar_user(username)
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
                    contraseña_h = str(hashlib.sha256((input("Introduce la contraseña\n")).encode()).hexdigest())
                    validada = self.database.contr_check(id-1, contraseña_h)
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
        existe, id = self.database.buscar_user(username)
        if existe:
            print("Este nombre de usuario ya ha sido registrado, introduzca otro")
        else:
            registro_correcto = False
            while not registro_correcto:
                c_validada = False
                while not c_validada:
                    contraseña_h = input("Introduzca una contraseña para tu cuenta. La contraseña deberá tener entre 8 y 15 caracteres y al menos un número y una letra mayúscula. Si desea salir, escriba EXIT\n")
                    if contraseña_h.upper() == "EXIT":
                        return -1
                    if self.aprobación_clave(contraseña_h):
                        c_validada = True
                contraseña_h = str(hashlib.sha256(contraseña_h.encode()).hexdigest())
                contraseña_h2 = str(hashlib.sha256((input("La clave introducida es válida. Repita la contraseña de nuevo\n")).encode()).hexdigest())
                if contraseña_h == contraseña_h2:
                    registro_correcto = True
                else:
                    print("Las contraseñas no son iguales, escríbalas correctamente otra vez")
            new_user = User(username, contraseña_h, len(self.database._data_list) + 1)
            self.database.registrar_user(new_user)
            return 0

    def aprobación_clave(self, contraseña:str):
        if len(contraseña)<8 or len(contraseña)>15:
            return False
        contador_mayus = 0
        contador_nums = 0
        for letra in contraseña:
            if ord(letra)>47 and ord(letra)<58:
                contador_nums += 1
            elif ord(letra)>64 and ord(letra)<91:
                contador_mayus += 1
        if contador_nums > 0 and contador_mayus > 0:
            return True
        return False



if __name__ == "__main__":
    term_1 = Terminal()
    term_1.sys()



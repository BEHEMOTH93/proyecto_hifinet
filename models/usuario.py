from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario  # Flask-Login obliga a que este atributo se llame 'id'
        self.nombre = nombre
        self.email = email
        self.password = password
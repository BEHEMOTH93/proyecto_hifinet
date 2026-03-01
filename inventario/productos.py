# Se crea la clase Producto para encapsular los atributos de los equipos de Hifinet.
# Permite instanciar objetos individuales en memoria.
# ==============================================================================
class Producto:
    def __init__(self, id, nombre, descripcion, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.precio = precio
from .productos import Producto
from .bd import get_db_connection, init_db
# La clase Inventario maneja la lógica de negocio y utiliza un Diccionario 
# (self.productos_dict) para búsquedas de complejidad O(1) en memoria.
# ==============================================================================
class Inventario:
    def __init__(self):
        init_db()
        self.productos_dict = {}

    def cargar_desde_db(self):
        with get_db_connection() as conn:
            filas = conn.execute("SELECT * FROM productos").fetchall()
            self.productos_dict.clear()
            for f in filas:
                self.productos_dict[f['id']] = Producto(f['id'], f['nombre'], f['descripcion'], f['cantidad'], f['precio'])

    def añadir(self, nombre, desc, cant, pre):
        with get_db_connection() as conn:
            conn.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio) VALUES (?, ?, ?, ?)", 
                         (nombre, desc, cant, pre))
            conn.commit()
        self.cargar_desde_db()

    def eliminar(self, id_prod):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM productos WHERE id = ?", (id_prod,))
            conn.commit()
        self.cargar_desde_db()

    def actualizar(self, id_prod, cant, pre):
        with get_db_connection() as conn:
            conn.execute("UPDATE productos SET cantidad = ?, precio = ? WHERE id = ?", (cant, pre, id_prod))
            conn.commit()
        self.cargar_desde_db()

    def buscar_por_nombre(self, termino):
        self.cargar_desde_db()
        resultados = []
        for prod in self.productos_dict.values():
            if termino.lower() in prod.nombre.lower():
                resultados.append(prod)
        return resultados
import sqlite3
from pathlib import Path
# Se usa pathlib para crear la carpeta 'data' dinámicamente y almacenar 'inventario.db'.
# sqlite3.Row permite acceder a los datos como diccionarios.
# ==============================================================================
db_path = Path(__file__).parent / "data" / "inventario.db"

def get_db_connection():
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS productos 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         nombre TEXT, descripcion TEXT, cantidad INTEGER, precio REAL)''')
        # Requisito de la rúbrica: tabla de clientes o extras
        conn.execute('''CREATE TABLE IF NOT EXISTS clientes 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, servicio TEXT)''')
        conn.commit()
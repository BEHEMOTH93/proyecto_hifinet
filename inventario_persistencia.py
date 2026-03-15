import sqlite3
from Conexion.conexion import obtener_conexion

def migrar():
    try:
        # Conectar al SQLite viejo
        sqlite_conn = sqlite3.connect('instance/productos.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # OJO: Verifica si tu tabla se llama 'producto' o 'productos' en SQLite
        sqlite_cursor.execute("SELECT nombre, descripcion, cantidad, precio FROM producto")
        filas = sqlite_cursor.fetchall()

        # Conectar al MySQL nuevo
        mysql_conn = obtener_conexion()
        if mysql_conn and filas:
            mysql_cursor = mysql_conn.cursor()
            sql = "INSERT INTO productos (nombre, descripcion, cantidad, precio) VALUES (%s, %s, %s, %s)"
            mysql_cursor.executemany(sql, filas)
            mysql_conn.commit()
            print(f"¡Éxito! Se migraron {len(filas)} productos.")
            mysql_conn.close()
        sqlite_conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    migrar()
import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            port=3307,
            password='Rafa691993.', 
            database='hifinet_db'
        )
        if conexion.is_connected():
            return conexion
            
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None
import os
import json
import csv
from conexion.conexion import obtener_conexion

class ProductoService:
    
    @staticmethod
    def guardar_archivos(nombre, precio, stock):
        ruta_base = "inventario/data"
        os.makedirs(ruta_base, exist_ok=True)
        
        # Guardar TXT
        with open(f"{ruta_base}/datos.txt", "a", encoding="utf-8") as f:
            f.write(f"{nombre},{precio},{stock}\n")
            
        # Guardar CSV
        with open(f"{ruta_base}/datos.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([nombre, precio, stock])
            
        # Guardar JSON
        ruta_json = f"{ruta_base}/datos.json"
        datos = []
        if os.path.exists(ruta_json):
            try:
                with open(ruta_json, "r", encoding="utf-8") as f:
                    datos = json.load(f)
            except: datos = []
        datos.append({"nombre": nombre, "precio": float(precio), "stock": int(stock)})
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)

    @staticmethod
    def listar_todos():
        conexion = obtener_conexion()
        productos = []
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM productos")
            productos = cursor.fetchall()
            cursor.close()
            conexion.close()
        return productos

    @staticmethod
    def crear(nombre, precio, stock):
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            # IMPORTANTE: Asegúrate que tu tabla tenga estas columnas: nombre, precio, stock
            cursor.execute("INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)", (nombre, precio, stock))
            conexion.commit()
            cursor.close()
            conexion.close()
            # Después de MySQL, guardamos en los archivos
            ProductoService.guardar_archivos(nombre, precio, stock)

    @staticmethod
    def eliminar(id_prod):
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            # Ajustado a 'id' si así se llama en tu DB, o cámbialo por 'id_producto'
            cursor.execute("DELETE FROM productos WHERE id = %s", (id_prod,))
            conexion.commit()
            cursor.close()
            conexion.close()
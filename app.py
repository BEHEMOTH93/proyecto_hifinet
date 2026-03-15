import os
import json
import csv
from flask import Flask, render_template, url_for, request, redirect, flash

# Importamos la conexión a MySQL y eliminamos SQLAlchemy
from form import ProductoForm
from Conexion.conexion import obtener_conexion 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_hifinet_2026'


# FUNCIONES CREADAS PARA GUARDAR ARCHIVOS
def guardar_txt(texto):
    with open("inventario/data/datos.txt", "a", encoding="utf-8") as f:
        f.write(texto + "\n")

def guardar_json(dic):
    ruta = "inventario/data/datos.json"
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except:
        datos = []
    datos.append(dic)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

def guardar_csv(dic):
    with open("inventario/data/datos.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([dic['nombre'], dic['descripcion'], dic['cantidad'], dic['precio']])
# =======================================================

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    form = ProductoForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        cantidad = form.cantidad.data
        precio = form.precio.data
        
        # INSERTAR EN MYSQL
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            sql = "INSERT INTO productos (nombre, descripcion, cantidad, precio) VALUES (%s, %s, %s, %s)"
            valores = (nombre, descripcion, cantidad, precio)
            cursor.execute(sql, valores)
            conexion.commit() 
            cursor.close()
            conexion.close()

        # Guardar en archivos 
        dic = {
            'nombre': nombre,
            'descripcion': descripcion,
            'cantidad': cantidad,
            'precio': precio
        }
        guardar_txt(f"{nombre},{descripcion},{cantidad},{precio}")
        guardar_json(dic)
        guardar_csv(dic)

        flash('Equipo añadido exitosamente a MySQL y archivos.')
        return redirect(url_for('datos'))
        
    return render_template('producto_form.html', form=form)

@app.route('/datos')
def datos():
    form = ProductoForm() 
    
    datos_txt = []
    datos_csv = []
    datos_json = []

    try:
        with open("inventario/data/datos.txt", encoding="utf-8") as f:
            for linea in f:
                datos_txt.append(linea.strip().split(","))
    except:
        pass

    try:
        with open("inventario/data/datos.json", encoding="utf-8") as f:
            datos_json = json.load(f)
    except:
        pass

    try:
        with open("inventario/data/datos.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            for fila in reader:
                datos_csv.append(fila)
    except:
        pass

    # CONSULTAR EN MYSQL 
    productos_mysql = []
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True) # Devuelve datos como diccionarios
        cursor.execute("SELECT * FROM productos")
        productos_mysql = cursor.fetchall()
        cursor.close()
        conexion.close()

    # Le pasamos productos_mysql a la variable que HTML ya usaba (productos_sql)
    return render_template("datos.html", datos_txt=datos_txt, datos_json=datos_json, datos_csv=datos_csv, productos_sql=productos_mysql, form=form)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    # ELIMINAR EN MYSQL
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()

    flash('Equipo eliminado de la base de datos MySQL.')
    return redirect(url_for('datos'))

@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    cant = int(request.form['nueva_cantidad'])
    pre = float(request.form['nuevo_precio'])
    
    # ACTUALIZAR EN MYSQL
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        sql = "UPDATE productos SET cantidad = %s, precio = %s WHERE id = %s"
        cursor.execute(sql, (cant, pre, id))
        conexion.commit()
        cursor.close()
        conexion.close()

    flash('Inventario actualizado en MySQL.')
    return redirect(url_for('datos'))

@app.route('/buscar', methods=['GET'])
def buscar():
    form = ProductoForm()
    query = request.args.get('query', '')
    resultados = []

    # BUSCAR EN MYSQL
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        if query:
            # Busca si el nombre contiene el texto ingresado
            sql = "SELECT * FROM productos WHERE nombre LIKE %s"
            cursor.execute(sql, (f"%{query}%",))
        else:
            cursor.execute("SELECT * FROM productos")
        
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()

    return render_template('datos.html', productos=resultados, busqueda=query, form=form)

if __name__ == '__main__':
    app.run(debug=True)
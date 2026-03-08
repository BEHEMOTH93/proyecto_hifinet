import os
import json
import csv
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

from form import ProductoForm
from inventario.bd import init_db
from inventario.inventario import Inventario

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_hifinet_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.String(200))
    cantidad = db.Column(db.Integer)
    precio = db.Column(db.Float)

# =======================================================
# FUNCIONES CREADAS POR EL PROFESOR PARA GUARDAR ARCHIVOS
# =======================================================
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

init_db()
inventario = Inventario()
inventario.cargar_desde_db()

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
        
        inventario.añadir(nombre, descripcion, cantidad, precio)

        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            cantidad=cantidad,
            precio=precio
        )
        db.session.add(nuevo_producto)
        db.session.commit()

        dic = {
            'nombre': nombre,
            'descripcion': descripcion,
            'cantidad': cantidad,
            'precio': precio
        }
        
        guardar_txt(f"{nombre},{descripcion},{cantidad},{precio}")
        guardar_json(dic)
        guardar_csv(dic)

        flash('Equipo añadido exitosamente al inventario.')
        return redirect(url_for('datos'))
        
    return render_template('producto_form.html', form=form)

@app.route('/datos')
def datos():
    form = ProductoForm() # <-- Aquí cargamos el formulario para mostrarlo en línea
    
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

    productos_sql = Producto.query.all()

    return render_template("datos.html", datos_txt=datos_txt, datos_json=datos_json, datos_csv=datos_csv, productos_sql=productos_sql, form=form)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    inventario.eliminar(id)
    flash('Equipo eliminado del inventario.')
    return redirect(url_for('datos'))

@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    cant = int(request.form['nueva_cantidad'])
    pre = float(request.form['nuevo_precio'])
    inventario.actualizar(id, cant, pre)
    flash('Inventario actualizado correctamente.')
    return redirect(url_for('datos'))

@app.route('/buscar', methods=['GET'])
def buscar():
    form = ProductoForm()
    query = request.args.get('query', '')
    if query:
        resultados = inventario.buscar_por_nombre(query)
    else:
        inventario.cargar_desde_db()
        resultados = inventario.productos_dict.values()
    return render_template('datos.html', productos=resultados, busqueda=query, form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
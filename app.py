from flask import Flask, render_template, url_for, request, redirect, flash
from form import ProductoForm
from inventario.bd import init_db
from inventario.inventario import Inventario
import json
import csv

app = Flask(__name__)
# Clave obligatoria para que funcionen los formularios Flask-WTF
app.config['SECRET_KEY'] = 'clave_secreta_hifinet_2026'

init_db()
inventario = Inventario()
inventario.cargar_desde_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ProductoForm()
    # Si el formulario es válido al presionar el botón guardar:
    if form.validate_on_submit():
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        cantidad = form.cantidad.data
        precio = form.precio.data
        inventario.añadir(nombre, descripcion, cantidad, precio)
        ruta_txt = "inventario/data/datos.txt"
        ruta_json = "inventario/data/datos.json"
        ruta_csv = "inventario/data/datos.csv"

        #TXT
        with open(ruta_txt, "a") as f:
            f.write(f"{nombre},{descripcion},{cantidad},{precio}\n")
        
        #JSON
        nuevo = {
            "nombre": nombre,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "precio": precio
        }
        try:
            with open(ruta_json, "r") as f:
                datos = json.load(f)
        except:
            datos = []
        
        datos.append(nuevo)

        with open(ruta_json, "w") as f:
            json.dump(datos, f, indent=4)
        
        #CSV
        with open(ruta_csv, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([nombre, descripcion, cantidad, precio])
        flash('Equipo añadido exitosamente al inventario.')
        return redirect(url_for('index'))
        
    inventario.cargar_desde_db()
    return render_template('index.html', productos=inventario.productos_dict.values(), form=form)

@app.route('/datos')
def datos():
    datos_txt = []
    datos_csv = []
    datos_json = []

    #TXT
    try:
        with open("inventario/data/datos.txt") as f:
            for linea in f:
                datos_txt.append(linea.strip().split(","))
    except:
        pass

    #JSON
    try:
        with open("inventario/data/datos.json") as f:
            datos_json = json.load(f)
    except:
        pass

    #CSV
    try:
        with open("inventario/data/datos.csv") as f:
            reader = csv.reader(f)
            for fila in reader:
                datos_csv.append(fila)
    except:
        pass

    return render_template("datos.html", datos_txt=datos_txt, datos_json=datos_json, datos_csv=datos_csv)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    inventario.eliminar(id)
    flash('Equipo eliminado del inventario.')
    return redirect(url_for('index'))

@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    cant = int(request.form['nueva_cantidad'])
    pre = float(request.form['nuevo_precio'])
    inventario.actualizar(id, cant, pre)
    flash('Inventario actualizado correctamente.')
    return redirect(url_for('index'))

@app.route('/buscar', methods=['GET'])
def buscar():
    form = ProductoForm()
    query = request.args.get('query', '')
    if query:
        resultados = inventario.buscar_por_nombre(query)
    else:
        inventario.cargar_desde_db()
        resultados = inventario.productos_dict.values()
    return render_template('index.html', productos=resultados, busqueda=query, form=form)

if __name__ == '__main__':
    app.run(debug=True)
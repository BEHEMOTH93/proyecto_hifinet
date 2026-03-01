from flask import Flask, render_template, url_for, request, redirect, flash
from form import ProductoForm
from inventario.bd import init_db
from inventario.inventario import Inventario

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
        inventario.añadir(form.nombre.data, form.descripcion.data, form.cantidad.data, form.precio.data)
        flash('Equipo añadido exitosamente al inventario.')
        return redirect(url_for('index'))
        
    inventario.cargar_desde_db()
    return render_template('index.html', productos=inventario.productos_dict.values(), form=form)

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
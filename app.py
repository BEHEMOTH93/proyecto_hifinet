import os
import json
import csv
from flask import Flask, render_template, url_for, request, redirect, flash

# --- IMPORTACIONES PARA EL LOGIN ---
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario 

from form import ProductoForm
from Conexion.conexion import obtener_conexion 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_hifinet_2026'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Por favor, inicia sesión para acceder."

@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_usuario, nombre, email, password FROM usuarios WHERE id_usuario = %s", (user_id,))
        data = cursor.fetchone()
        cursor.close()
        conexion.close()
        if data:
            return Usuario(data[0], data[1], data[2], data[3])
    return None

# --- FUNCIONES DE GUARDADO ---
def guardar_txt(texto):
    os.makedirs("inventario/data", exist_ok=True)
    with open("inventario/data/datos.txt", "a", encoding="utf-8") as f:
        f.write(texto + "\n")

def guardar_json(dic):
    ruta = "inventario/data/datos.json"
    os.makedirs("inventario/data", exist_ok=True)
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except:
        datos = []
    datos.append(dic)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

def guardar_csv(dic):
    os.makedirs("inventario/data", exist_ok=True)
    with open("inventario/data/datos.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([dic['nombre'], dic['descripcion'], dic['cantidad'], dic['precio']])

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_usuario, nombre, email, password FROM usuarios WHERE email = %s", (email,))
            data = cursor.fetchone()
            cursor.close()
            conexion.close()
            if data and check_password_hash(data[3], password):
                user = Usuario(data[0], data[1], data[2], data[3])
                login_user(user)
                flash(f'¡Hola, {user.nombre}!')
                return redirect(url_for('index'))
            else:
                flash('Email o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']
        if password != confirm:
            flash('Las contraseñas no coinciden.')
            return render_template('registro.html')
        
        pass_hash = generate_password_hash(password)
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", (nombre, email, pass_hash))
                conexion.commit()
                flash('Registro exitoso. Ya puedes entrar.')
                return redirect(url_for('login'))
            except:
                flash('El correo ya existe.')
            finally:
                cursor.close()
                conexion.close()
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/datos')
@login_required
def datos():
    form = ProductoForm()
    datos_txt, datos_json, datos_csv = [], [], []
    
    # Lectura de archivos locales
    try:
        if os.path.exists("inventario/data/datos.txt"):
            with open("inventario/data/datos.txt", encoding="utf-8") as f:
                for linea in f: datos_txt.append(linea.strip().split(","))
        if os.path.exists("inventario/data/datos.json"):
            with open("inventario/data/datos.json", encoding="utf-8") as f:
                datos_json = json.load(f)
        if os.path.exists("inventario/data/datos.csv"):
            with open("inventario/data/datos.csv", encoding="utf-8") as f:
                reader = csv.reader(f)
                for fila in reader: datos_csv.append(fila)
    except: pass

    # Lectura de MySQL
    productos_mysql = []
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos_mysql = cursor.fetchall()
        cursor.close()
        conexion.close()
        
    return render_template("datos.html", 
                           datos_txt=datos_txt, 
                           datos_json=datos_json, 
                           datos_csv=datos_csv, 
                           productos_sql=productos_mysql, 
                           form=form)

# ESTA ES LA RUTA QUE FALTABA O TENÍA OTRO NOMBRE:
@app.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    form = ProductoForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        desc = form.descripcion.data
        cant = form.cantidad.data
        prec = form.precio.data
        
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio) VALUES (%s, %s, %s, %s)", (nombre, desc, cant, prec))
            conexion.commit()
            cursor.close()
            conexion.close()
        
        dic = {'nombre': nombre, 'descripcion': desc, 'cantidad': cant, 'precio': prec}
        guardar_txt(f"{nombre},{desc},{cant},{prec}")
        guardar_json(dic)
        guardar_csv(dic)
        
        flash('Equipo añadido correctamente.')
        return redirect(url_for('datos'))
    return render_template('producto_form.html', form=form)

@app.route('/buscar', methods=['GET'])
@login_required
def buscar():
    form = ProductoForm()
    query = request.args.get('query', '')
    resultados = []
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE nombre LIKE %s", (f"%{query}%",))
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
    return render_template('datos.html', productos_sql=resultados, busqueda=query, form=form)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
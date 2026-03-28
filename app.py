import os
import sys

# --- SOLUCIÓN PARA RENDER: Fuerza a Python a encontrar tus carpetas ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Tus importaciones de carpetas (Ahora Render las encontrará)
from models.usuario import Usuario 
from conexion.conexion import obtener_conexion 
from inventario.inventario import Inventario 
from services.producto_service import ProductoService # Para los archivos

# PDF (Semana 15)
from fpdf import FPDF

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hifinet_2026_secreta'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_usuario, nombre, email, password FROM usuarios WHERE id_usuario = %s", (user_id,))
        data = cursor.fetchone()
        cursor.close()
        conexion.close()
        if data: return Usuario(data[0], data[1], data[2], data[3])
    return None

# --- RUTAS PRINCIPALES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# --- AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
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
                return redirect(url_for('index'))
            flash('Login incorrecto')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        pass_hash = generate_password_hash(password)
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", 
                               (nombre, email, pass_hash))
                conexion.commit()
                flash('Registro exitoso. Ya puedes iniciar sesión.')
                return redirect(url_for('login'))
            except:
                flash('El correo ya existe.')
            finally:
                cursor.close()
                conexion.close()
    return render_template('registro.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- GESTIÓN DE PRODUCTOS (CRUD) ---

@app.route('/datos')
@login_required
def listar_productos():
    conexion = obtener_conexion()
    productos_db = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos_db = cursor.fetchall()
        cursor.close()
        conexion.close()
    return render_template('datos.html', productos=productos_db)

@app.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    if request.method == 'POST':
        nombre = request.form.get('txt_nombre') or request.form.get('nombre')
        precio = request.form.get('txt_precio') or request.form.get('precio')
        stock = request.form.get('txt_stock') or request.form.get('stock')
        desc = request.form.get('txt_descripcion') or "Sin descripción"
        
        conexion = obtener_conexion()
        if conexion and nombre:
            cursor = conexion.cursor()
            sql = "INSERT INTO productos (nombre, descripcion, cantidad, precio) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nombre, desc, stock, precio))
            conexion.commit()
            cursor.close()
            conexion.close()
            ProductoService.guardar_archivos(nombre, precio, stock)
            flash('Equipo guardado con éxito en DB y Archivos.')
            return redirect(url_for('listar_productos'))
    return render_template('producto_form.html')

@app.route('/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()
        flash('Equipo eliminado correctamente.')
    return redirect(url_for('listar_productos'))

# --- REQUISITO SEMANA 15: REPORTE PDF PROFESIONAL + AUDITORÍA ---

@app.route('/reporte_pdf')
@login_required
def reporte_pdf():
    conexion = obtener_conexion()
    productos = []
    ahora_dt = datetime.now()
    nombre_archivo_pdf = f"reporte_hifinet_{ahora_dt.strftime('%Y%m%d_%H%M%S')}.pdf"
    
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        
        try:
            sql_log = "INSERT INTO historial_descargas (id_usuario, nombre_usuario, fecha_hora, archivo_nombre) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_log, (current_user.id, current_user.nombre, ahora_dt, nombre_archivo_pdf))
            conexion.commit()
        except Exception as e:
            print(f"Error en auditoría: {e}")
        finally:
            cursor.close()
            conexion.close()

    pdf = FPDF()
    pdf.add_page()
    
    try:
        pdf.image('static/imagen.jpg.jpeg', 10, 8, 33)
    except: pass

    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(80); pdf.cell(30, 10, "HIFINET S.A.", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 10); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Generado por: {current_user.nombre}", ln=True, align='R')
    pdf.cell(0, 5, f"Fecha: {ahora_dt.strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='R')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "REPORTE DE INVENTARIO DE EQUIPOS", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(0, 51, 102); pdf.set_text_color(255, 255, 255)
    pdf.cell(15, 10, 'ID', 1, 0, 'C', True)
    pdf.cell(75, 10, 'Producto', 1, 0, 'C', True)
    pdf.cell(45, 10, 'Descripción', 1, 0, 'C', True)
    pdf.cell(25, 10, 'Precio', 1, 0, 'C', True)
    pdf.cell(25, 10, 'Cant.', 1, 1, 'C', True)

    pdf.set_font("Arial", '', 10); pdf.set_text_color(0, 0, 0)
    for p in productos:
        id_p = p.get('id') or p.get('id_producto') or '0'
        pdf.cell(15, 10, str(id_p), 1)
        pdf.cell(75, 10, str(p.get('nombre', 'N/A'))[:35], 1)
        pdf.cell(45, 10, str(p.get('descripcion', 'S/D'))[:25], 1)
        pdf.cell(25, 10, f"${p.get('precio', 0.0)}", 1)
        pdf.cell(25, 10, str(p.get('cantidad') or p.get('stock') or '0'), 1); pdf.ln()

    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Hifinet S.A. - Documento Interno de Control de Inventarios", 0, 0, 'C')

    pdf.output(nombre_archivo_pdf)
    return send_file(nombre_archivo_pdf, as_attachment=True)

if __name__ == '__main__':
    # Puerto dinámico para Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
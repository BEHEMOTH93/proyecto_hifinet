# Importamos Flask para crear la app y render_template para leer archivos HTML
from flask import Flask, render_template
import os  # IMPORTANTE: Esta librería permite leer el puerto que Render nos asigna

# Inicializamos la aplicación
app = Flask(__name__)

# Definimos la ruta principal (Inicio)
@app.route('/')
def index():
    # render_template busca el archivo en la carpeta 'templates'
    return render_template('index.html')

# Ruta para la información de la empresa
@app.route('/nosotros')
def about():
    return render_template('about.html')

# Ruta personalizada para tu proyecto Hifinet
@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

# CONFIGURACIÓN PARA DESPLIEGUE:
if __name__ == '__main__':
    # Render asigna un puerto dinámico; si no existe (local), usa el 5000
    port = int(os.environ.get('PORT', 5000))
    # host='0.0.0.0' permite que el servidor sea accesible desde internet
    app.run(host='0.0.0.0', port=port, debug=True)
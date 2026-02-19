# Importamos Flask para crear la app y render_template para leer archivos HTML
from flask import Flask, render_template

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

# Arranca el servidor en modo desarrollo (se actualiza solo al guardar)
if __name__ == '__main__':
    app.run(debug=True)
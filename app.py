from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Bienvenido a Hifinet - Internet de Fibra Optica</h1>"

@app.route('/cliente/<nombre>')
def cliente(nombre):
    return f"<h1>Hola {nombre}, tu servicio de Hifinet esta ACTIVO.</h1>"

if __name__ == '__main__':
    app.run(debug=True)
    
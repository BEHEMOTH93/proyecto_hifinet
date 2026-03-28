from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Equipo', validators=[DataRequired()])
    precio = FloatField('Precio $', validators=[DataRequired()])
    stock = IntegerField('Stock (Cantidad)', validators=[DataRequired()])
    submit = SubmitField('Guardar Registro')
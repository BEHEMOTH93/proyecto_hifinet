from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired

# Se implementan formularios WTF para validación del lado del servidor y
# protección nativa contra vulnerabilidades CSRF.
# ==============================================================================
class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Equipo', validators=[DataRequired()])
    descripcion = StringField('Descripción', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    precio = FloatField('Precio $', validators=[DataRequired()])
    submit = SubmitField('Guardar Registro')
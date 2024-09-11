from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField, FileField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange
from flask_wtf.file import FileAllowed, FileRequired

class LoginForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    precio = IntegerField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=1)])
    imagen = FileField('Imagen', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Añadir Producto')

class TarjetaForm(FlaskForm):
    numero_tarjeta = StringField('Número de Tarjeta', validators=[DataRequired()])
    vencimiento_tarjeta = DateField('Fecha de Vencimiento', format='%Y-%m-%d', validators=[DataRequired()])
    numero_seguridad_tarjeta = IntegerField('Código de Seguridad', validators=[DataRequired(), NumberRange(min=100, max=999)])
    submit = SubmitField('Guardar Tarjeta')
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField, FileField
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
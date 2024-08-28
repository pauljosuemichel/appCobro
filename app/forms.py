from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    name = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
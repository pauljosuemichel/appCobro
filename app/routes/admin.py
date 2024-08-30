from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from app import bcrypt, db
from app.models import Usuario, Carrito
from app.forms import LoginForm, RegisterForm

admin_bp = Blueprint('admin', __name__, url_prefix='/pages')

@admin_bp.route('/')
def panel():
    return render_template('base.html')
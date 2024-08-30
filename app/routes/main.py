from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from app import bcrypt, db
from app.models import Usuario, Carrito
from app.forms import LoginForm, RegisterForm

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("main.home"))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = Usuario.query.filter_by(name=form.name.data).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("main.home"))
        else:
            flash("Invalid email and/or password.", "danger")
            print("----Error en el logueo------")
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)

@main_bp.route('/logout')
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("main.login"))

@main_bp.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("main.home"))
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Usuario(name=form.name.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("admin/register.html", form=form)

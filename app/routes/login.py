from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, current_user
from flask_dance.contrib.google import google
from app import bcrypt, db
from app.models import Usuario
from app.forms import LoginForm, RegisterForm
import os

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=["GET", "POST"])
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

@login_bp.route('/logout')
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("main.home"))

@login_bp.route('/register', methods=["GET", "POST"])
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


@login_bp.route('/google-login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))

    resp = google.get('/oauth2/v2/userinfo')
    assert resp.ok, resp.text
    user_info = resp.json()

    # Busca un usuario existente con el email o crea uno nuevo
    email = user_info['email']
    user = Usuario.query.filter_by(email=email).first()

    if user is None:
        user = Usuario(username=user_info['name'], email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('profile'))
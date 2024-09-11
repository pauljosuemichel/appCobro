from flask import Flask
from flask_dance.contrib.google import make_google_blueprint
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import click

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    """Configuracion"""
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # Directorio donde se guardarán las imágenes
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Tamaño máximo del archivo (16 MB en este caso)
    
    """Inicializacion"""
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    """Blueprints"""
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp as admin_blueprint
    from app.routes.login import login_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(login_bp)

    # Crear el blueprint de Google OAuth
    google_bp = make_google_blueprint(
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        redirect_to='login.google_login'
    )
    app.register_blueprint(google_bp, url_prefix='/auth')
    
    """Obtener usuario actual para cada solicitud"""
    from app.models import Usuario
    login_manager.login_view = "login.login"
    login_manager.login_message_category = "danger"
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))


    """Formatos de Jinja2 personalizados"""
    @app.template_filter('price_format')
    def price_format(value):
        try:
            return '{:,.0f}'.format(int(value)).replace(',', '.')
        except (ValueError, TypeError):
            return value 



    @app.cli.command("create_user")
    @click.argument("name")
    @click.argument("password")
    def create_user(name, password):
        hashed_pw = bcrypt.generate_password_hash(password)
        new_user = Usuario(name=name, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        click.echo(f"User {name} created successfully")

    @app.cli.command("remove_user")
    @click.argument("name")
    def remove_user(name):
        user = Usuario.query.filter_by(name=name).first()
        db.session.delete(user)
        db.session.commit()
        click.echo(f"User {name} removed successfully")

    @app.cli.command("make_admin")
    @click.argument("name")
    def make_admin(name):
        user = Usuario.query.filter_by(name=name).first()
        user.is_admin = True
        db.session.commit()
        click.echo(f"User {name} is admin now")

    @app.cli.command("list_users")
    def list_users():
        users = Usuario.query.all()
        for user in users:
            click.echo(f"{user}: {"admin" if user.is_admin else "guest"}, {user.plata}")

    @app.cli.command("agregar_plata")
    @click.argument("name")
    @click.argument("cant")
    def agregar_plata(name, cant):
        user = Usuario.query.filter_by(name=name).first()
        user.plata += int(cant)
        db.session.commit()
        click.echo(f"User {name} added ${cant}")
    
    return app
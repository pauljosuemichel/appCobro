from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import click

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://uxfgd9irlopbqktk:U14V1O97n3nyjyHjrNPV@bufynsvxpltldv46gzcr-mysql.services.clever-cloud.com:3306/bufynsvxpltldv46gzcr'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)


    """Blueprints"""
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp as admin_blueprint
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_blueprint)
    
    """Obtener usuario actual para cada solicitud"""
    from app.models import Usuario
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "danger"
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

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
    def create_user(name):
        user = Usuario.query.filter_by(name).first()
        db.session.delete(user)
        db.session.commit
        click.echo(f"User {name} removed successfully")
    
    return app
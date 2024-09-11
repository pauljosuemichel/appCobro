from datetime import datetime
from . import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    numero_tarjeta = db.Column(db.Integer)
    vencimiento_tarjeta = db.Column(db.DateTime)
    numero_seguridad_tarjeta = db.Column(db.Integer)

    plata = db.Column(db.Integer, default=100000)

    carritos = db.relationship('Carrito', backref='usuario', lazy='dynamic')

    def __repr__(self):
        return f"<Usuario {self.name}>"

# Tabla de asociacion para la relacion muchos a muchos entre Carrito y Producto
class CarritoProducto(db.Model):
    __tablename__ = 'carrito_producto'
    carrito_id = db.Column(db.Integer, db.ForeignKey('carrito.id'), primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), primary_key=True)
    cantidad = db.Column(db.Integer, default=1)


class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    fecha = db.Column(db.DateTime, nullable=False)
    comprado = db.Column(db.Boolean, default=False)

    productos = db.relationship('Producto', secondary='carrito_producto', back_populates='carritos', overlaps="carrito_productos")

    def __repr__(self):
        return f"<Carrito {self.id}>"

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(120), nullable=False)

    descuento = db.Column(db.Float, default=0.0)
    proveedor = db.Column(db.String(100))

    carritos = db.relationship('Carrito', secondary='carrito_producto', back_populates='productos', overlaps="carrito_productos")

    def __repr__(self):
        return f"<Producto {self.nombre}>"



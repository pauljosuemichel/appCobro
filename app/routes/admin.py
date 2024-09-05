import os
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from app import bcrypt, db
from app.models import Usuario, Carrito, Producto
from app.forms import LoginForm, RegisterForm, ProductoForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def panel():
    return render_template('base.html')

@admin_bp.route('/registrarUsuario')
def register():
    return render_template('base.html')

@admin_bp.route('/crearProducto', methods=['GET', 'POST'])
def crearProducto():
    nombre_productos = Producto.query.with_entities(Producto.nombre).all()
    nombre_productos = [name for (name,) in nombre_productos]
    form = ProductoForm()

    if form.validate_on_submit():

        imagen = form.imagen.data
        filename = secure_filename(imagen.filename)
        rutaImagen = os.path.join('app', 'static', 'uploads', filename)
        imagen.save(rutaImagen)

        producto = Producto(
            nombre=form.nombre.data,
            precio=form.precio.data,
            stock=form.stock.data,
            imagen=filename
        )
        db.session.add(producto)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.panel'))
    return render_template('admin/añadirProducto.html', form=form, nombre_productos=nombre_productos)

@admin_bp.route('/eliminarProducto/<id>', methods=['POST'])
def eliminarProducto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Product has been deleted.', 'success')

    #Aca hay que devolver algo
    return render_template('admin/añadirProducto.html')
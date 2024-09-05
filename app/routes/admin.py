import os
from flask import Blueprint, flash, redirect, render_template, url_for, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps

from app import db
from app.models import Producto
from app.forms import ProductoForm

admin_bp = Blueprint('admin', __name__)

#Decorador personalizado para rutas con privilegios de administrador
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Error 403 Forbidden si el usuario no es administrador
        return func(*args, **kwargs)
    return decorated_view


@admin_bp.route('/crearProducto', methods=['GET', 'POST'])
@login_required
@admin_required
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
@login_required
@admin_required
def eliminarProducto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Product has been deleted.', 'success')

    #Aca hay que devolver algo
    return render_template('admin/añadirProducto.html')
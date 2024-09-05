from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime, timezone
from app import bcrypt, db
from app.models import Usuario, Carrito, Producto, CarritoProducto
from app.forms import LoginForm, RegisterForm

main_bp = Blueprint('main', __name__, template_folder='templates')


@main_bp.route('/')
def home():
    productos = Producto.query.all()
    return render_template('home.html', productos=productos)

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
    return redirect(url_for("main.home"))

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


@main_bp.route('/carrito')
@login_required
def carrito():
    carrito = Carrito.query.filter_by(usuario_id=current_user.id, comprado=False).first()

    if not carrito:
        return render_template('carrito.html', items=[])
    
    # Recuperar todos los productos en el carrito
    productos = (
        db.session.query(Producto, CarritoProducto)
        .join(CarritoProducto, Producto.id == CarritoProducto.producto_id)
        .filter(CarritoProducto.carrito_id == carrito.id)
        .all()
    )

    # Crear una lista de diccionarios para los datos del carrito
    items = []
    for producto, carrito_producto in productos:
        items.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'cantidad': carrito_producto.cantidad,
            'total': producto.precio * carrito_producto.cantidad
        })

    return render_template('carrito.html', items=items)

@main_bp.route('/modificarCarrito/<int:product_id>/<action>', methods=['POST'])
@login_required
def modificarCarrito(product_id, action):
    carrito = Carrito.query.filter_by(usuario_id=current_user.id, comprado=False).first()

    if carrito:
        carrito_producto = CarritoProducto.query.filter_by(carrito_id=carrito.id, producto_id=product_id).first()

        if carrito_producto:
            if action == 'increase':
                carrito_producto.cantidad += 1
            elif action == 'decrease':
                if carrito_producto.cantidad > 1:
                    carrito_producto.cantidad -= 1
                else:
                    db.session.delete(carrito_producto)  # Eliminar el producto si la cantidad es 0
            elif action == 'remove':
                db.session.delete(carrito_producto)
    
            db.session.commit()
            flash('Carrito actualizado.', 'success')
        else:
            flash('Producto no encontrado en el carrito.', 'danger')
    else:
        flash('No hay carrito activo.', 'danger')

    return redirect(url_for('main.carrito'))

@main_bp.route('/agregarCarrito/<int:product_id>', methods=['POST'])
@login_required
def agregarCarrito(product_id):
    producto = Producto.query.get_or_404(product_id)
    carrito = Carrito.query.filter_by(usuario_id=current_user.id, comprado=False).first()

    if not carrito:
        # Crear un nuevo carrito para el usuario si no tiene uno
        carrito = Carrito(usuario_id=current_user.id, fecha=datetime.now(timezone.utc), comprado=False)
        db.session.add(carrito)
        db.session.commit()

    # Verificar si el producto ya está en el carrito
    carrito_producto = CarritoProducto.query.filter_by(carrito_id=carrito.id, producto_id=producto.id).first()

    if carrito_producto:
        # Si el producto ya está en el carrito, incrementa la cantidad
        carrito_producto.cantidad += 1
    else:
        # Si el producto no está en el carrito, lo añadimos con cantidad 1
        carrito_producto = CarritoProducto(carrito_id=carrito.id, producto_id=producto.id, cantidad=1)
        db.session.add(carrito_producto)

    db.session.commit()

    return jsonify({'status': 'success', 'message': f'{producto.nombre} ha sido añadido al carrito.'})

@main_bp.route('/comprar/<int:cart_id>', methods=['POST'])
@login_required
def compra(cart_id):
    #Mucho codigo ...
    return render_template("carrito.html", carritos=carritos)

@main_bp.route('/contacto')
def contacto():
    #Mucho codigo ...
    return render_template("contacto.html")
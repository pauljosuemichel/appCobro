from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app import db
from app.models import Carrito, Producto, CarritoProducto, Transaccion
from app.forms import TarjetaForm
import mercadopago
import os


main_bp = Blueprint('main', __name__, template_folder='templates')

# Configura tu ACCESS_TOKEN
mp = mercadopago.SDK(os.getenv('MERCADO_PAGO_TOKEN'))


@main_bp.route('/')
def home():
    productos = Producto.query.all()
    return render_template('home.html', productos=productos)


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

    return render_template('carrito.html', items=items, carrito_id=carrito.id)

@main_bp.route('/tusCompras')
@login_required
def tusCompras():
    carritos = Carrito.query.filter_by(usuario_id=current_user.id, comprado=True)

    if not carritos:
        return render_template('carrito.html', items=[])
    
    
    carritosProductos = []
    # Recuperar todos los productos en el carrito
    for carrito in carritos:
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
        carritosProductos.append(items)

    return render_template('tusCompras.html', carritosProductos=carritosProductos)

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


@main_bp.route('/comprar/<int:carrito_id>', methods=['GET'])
@login_required
def compra(carrito_id):
    # Obtener el carrito por su ID
    carrito = Carrito.query.get_or_404(carrito_id)

    # Verificar si el carrito pertenece al usuario actual y si no está ya comprado
    if carrito.usuario_id != current_user.id or carrito.comprado:
        flash('Acción no permitida o el carrito ya ha sido comprado.', 'danger')
        return redirect(url_for('main.carrito'))
    
    # Verificar si el usuario tiene los datos de la tarjeta completos
    if not current_user.numero_tarjeta or not current_user.vencimiento_tarjeta or not current_user.numero_seguridad_tarjeta:
        flash('Por favor, complete los datos de su tarjeta para realizar la compra.', 'warning')
        return redirect(url_for('main.completar_datos_tarjeta'))

    # Verificar si la tarjeta está vencida
    if current_user.vencimiento_tarjeta < datetime.now():
        flash('La tarjeta está vencida. Actualice los datos de pago.', 'danger')
        return redirect(url_for('main.carrito'))
    
    # Calcular el total de la compra
    carrito_productos = CarritoProducto.query.filter_by(carrito_id=carrito_id).all()
    total_compra = 0
    for item in carrito_productos:
        # Obtener el producto correspondiente
        producto = Producto.query.get(item.producto_id)

        # Verificar si hay suficiente stock
        if producto.stock >= item.cantidad:
            # Restar la cantidad del stock del producto
            producto.stock -= item.cantidad
            # Calcular el subtotal del producto
            subtotal = producto.precio * item.cantidad
            total_compra += subtotal
        else:
            flash(f"No hay suficiente stock para {producto.nombre}.", 'danger')
            return redirect(url_for('main.carrito'))

    # Verificar si el usuario tiene saldo suficiente en la tarjeta
    if current_user.plata < total_compra:
        flash('No tiene suficiente saldo en la tarjeta.', 'danger')
        return redirect(url_for('main.carrito'))

    # Restar el total de la compra del saldo de la tarjeta
    current_user.plata -= total_compra

    # Marcar el carrito como comprado
    carrito.comprado = True

    # Confirmar los cambios en la base de datos
    db.session.commit()

    # Redirigir a la página de comprobante de transacción
    return redirect(url_for('main.comprobante_transaccion', carrito_id=carrito_id, costo=total_compra))

@main_bp.route('/comprobante/<int:carrito_id>/<int:costo>', methods=['GET'])
@login_required
def comprobante_transaccion(carrito_id, costo):
    return render_template('comprobante_transaccion.html',costo=costo)

@main_bp.route('/completar_tarjeta', methods=['GET', 'POST'])
@login_required
def completar_datos_tarjeta():
    form = TarjetaForm()

    if form.validate_on_submit():
        # Guardar los datos de la tarjeta en el usuario actual
        current_user.numero_tarjeta = form.numero_tarjeta.data
        current_user.vencimiento_tarjeta = form.vencimiento_tarjeta.data
        current_user.numero_seguridad_tarjeta = form.numero_seguridad_tarjeta.data

        # Confirmar los cambios en la base de datos
        db.session.commit()

        flash('Datos de la tarjeta guardados correctamente.', 'success')
        return redirect(url_for('main.carrito'))

    return render_template('completar_datos_tarjeta.html', form=form)

@main_bp.route('/contacto')
def contacto():
    #Mucho codigo ...
    return render_template("contacto.html")


@main_bp.route('/checkout/<int:carrito_id>', methods=['GET'])
def checkout(carrito_id):
    carrito = Carrito.query.get_or_404(carrito_id)
    if carrito.comprado:
        return "Carrito ya comprado", 400

    items = []
    total_amount = 0

    for producto in carrito.productos:
        items.append({
            "title": producto.nombre,
            "quantity": 1,
            "unit_price": producto.precio,
            "currency_id": "ARS"
        })
        total_amount += producto.precio

    preference_data = {
        "items": items,
        "back_urls": {
            "success": url_for('main.success', _external=True),
            "failure": url_for('main.failure', _external=True),
            "pending": url_for('main.pending', _external=True)
        },
        "auto_return": "approved",
        "notification_url": url_for('main.notifications', _external=True)
    }

    preference_response = mp.preference().create(preference_data)
    # preference_id = preference_response['response']['id']
    init_point = preference_response['response']['init_point']

    # Guarda la transacción pendiente en la base de datos
    transaccion = Transaccion(carrito_id=carrito_id, monto=total_amount, estado="pendiente")
    db.session.add(transaccion)
    db.session.commit()

    return redirect(init_point)

@main_bp.route('/success')
def success():
    return "Compra realizada con éxito!"

@main_bp.route('/failure')
def failure():
    return "La compra falló."

@main_bp.route('/pending')
def pending():
    return "La compra está pendiente."

@main_bp.route('/notifications', methods=['POST'])
def notifications():
    data = request.json
    # Aquí procesas la notificación recibida
    # Extrae los datos relevantes del webhook de Mercado Pago
    transaction_id = data.get('id')
    estado = data.get('status')

    transaccion = Transaccion.query.filter_by(id=transaction_id).first()
    if transaccion:
        transaccion.estado = estado
        db.session.commit()

    return jsonify({'status': 'ok'}), 200
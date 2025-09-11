from datetime import date
from flask import Flask, render_template, session, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
import pymysql
import bcrypt
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secretkey'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'restaurante_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mysql = MySQL()
mysql.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    text = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[4], password):  # user[4] es la columna 'contraseña'
            session['loggedin'] = True
            session['id'] = user[0]      # id_usuario
            session['nombre'] = user[1]  # nombre
            session['rol'] = user[5]     # id_rol

            # Redirige según el rol
            if user[5] == 1:  # Administrador
                return redirect('/dashboard_admin')
            elif user[5] == 2:  # Cocinero
                return render_template('dashboardAdmin.html', text="Bienvenido Cocinero")
            elif user[5] == 3:  # Cliente
                return redirect('/dashboard_cliente')
            else:
                return redirect('/dashboard_cliente')
        else:
            text = "Correo o contraseña incorrectos."

    return render_template('login.html', text=text)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    text = ''
    if request.method == 'POST':
        nombre = request.form['fullname']
        email = request.form['email']
        telefono = request.form['phone']
        password = request.form['password']

        hashed = generate_password_hash(password)

        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nombre, correo, telefono, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s)",
            (nombre, email, telefono, hashed, 3))
        conn.commit()
        cur.close()
        return redirect('/login')

    return render_template('register.html', text=text)

@app.route('/dashboard_cliente')
def dashboard_cliente():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM productos WHERE disponible = 1")
    productos = cur.fetchall()
    cur.close()
    return render_template('dashboardClientes.html', productos=productos)

# Construccion de Menu + Carrito

@app.route('/menu')
def menu():
    if 'loggedin' not in session:
        return redirect('/login')

    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    carrito_items = []
    total_carrito = 0.0
    try:
        cur.execute("SELECT * FROM productos WHERE disponible = 1")
        productos = cur.fetchall()

        carrito_ids = session.get('carrito', [])
        for pid in carrito_ids:
            cur.execute(
                "SELECT id_producto, nombre_producto AS nombre, precio, imagen FROM productos WHERE id_producto = %s",
                (pid,)
            )
            p = cur.fetchone()
            if p:
                carrito_items.append(p)
                total_carrito += float(p['precio'])
    finally:
        cur.close()
        conn.close()

    return render_template('menu.html', productos=productos, carrito_items=carrito_items, total_carrito=total_carrito)


@app.route('/carrito')
def ver_carrito():
    if 'loggedin' not in session:
        return redirect('/login')

    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    carrito_items = []
    total_carrito = 0.0
    try:
        carrito_ids = session.get('carrito', [])
        for pid in carrito_ids:
            cur.execute(
                "SELECT id_producto, nombre_producto AS nombre, precio, imagen FROM productos WHERE id_producto = %s",
                (pid,)
            )
            p = cur.fetchone()
            if p:
                carrito_items.append(p)
                total_carrito += float(p['precio'])
    finally:
        cur.close()
        conn.close()

    return render_template('carrito.html', carrito_items=carrito_items, total_carrito=total_carrito)


@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    if 'loggedin' not in session:
        return redirect('/login')

    pid = request.form.get('producto_id')
    if not pid:
        flash("Producto no válido.", "error")
        return redirect(url_for('menu'))

    carrito = session.get('carrito', [])
    carrito.append(int(pid))
    session['carrito'] = carrito

    flash("Producto agregado al carrito.", "success")
    return redirect(url_for('menu'))


@app.route('/quitar_carrito', methods=['POST'])
def quitar_carrito():
    if 'loggedin' not in session:
        return redirect('/login')

    pid = int(request.form.get('producto_id'))
    carrito = session.get('carrito', [])
    if pid in carrito:
        carrito.remove(pid)
    session['carrito'] = carrito
    return redirect(url_for('menu'))



# Mostrar mesas disponibles
@app.route('/mesas')
def mesas():
    if 'loggedin' in session:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM mesas WHERE disponible = TRUE")
        mesas_disponibles = cur.fetchall()
        cur.close()
        return render_template('mesas.html', mesas=mesas_disponibles)
    return render_template('login.html', text='Por favor inicia sesión primero.')

# Reservar mesa seleccionada
@app.route('/reservar_mesa', methods=['POST'])
def reservar_mesa():
    if 'loggedin' in session:
        mesa_id = request.form['mesa_id']
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("UPDATE mesas SET disponible = FALSE WHERE id_mesa = %s", (mesa_id,))
        conn.commit()
        cur.close()
        return render_template('dashboardClientes.html', text='Mesa reservada exitosamente.')
    return render_template('login.html', text='Por favor inicia sesión primero.')

# PANEL CRUD ADMIN
@app.route('/admin/crud')
def admin_crud():
    if 'loggedin' in session and session['rol'] == 1:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM categorias")
        categorias = cur.fetchall()
        cur.execute("SELECT p.*, c.nombre_categoria FROM productos p JOIN categorias c ON p.id_categoria = c.id_categoria")
        productos = cur.fetchall()
        cur.close()
        return render_template('editar_producto.html', categorias=categorias, productos=productos)
    return redirect('/login')

@app.route('/admin/categorias', methods=['POST'])
def registrar_categoria():
    nombre = request.form['nombre_categoria']
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO categorias (nombre_categoria) VALUES (%s)", (nombre,))
    conn.commit()
    cur.close()
    return redirect('/admin/crud')

@app.route('/admin/productos', methods=['POST'])
def registrar_producto():
    nombre = request.form['nombre_producto']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    id_categoria = request.form['id_categoria']
    disponible = 1 if 'disponible' in request.form else 0

    imagen = request.files['imagen']
    nombre_imagen = secure_filename(imagen.filename)
    ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)
    imagen.save(ruta_imagen)

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO productos (nombre_producto, descripcion, precio, imagen, id_categoria, disponible) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre, descripcion, precio, nombre_imagen, id_categoria, disponible))
    conn.commit()
    cur.close()
    return redirect('/admin/crud')

@app.route('/admin/eliminar_producto/<int:id_producto>')
def eliminar_producto(id_producto):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
    conn.commit()
    cur.close()
    return redirect('/admin/crud')

@app.route('/admin/editar_producto/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        nombre = request.form['nombre_producto']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        id_categoria = request.form['id_categoria']
        disponible = 1 if 'disponible' in request.form else 0

        imagen = request.files['imagen']
        if imagen:
            nombre_imagen = secure_filename(imagen.filename)
            ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)
            imagen.save(ruta_imagen)
            cur.execute("UPDATE productos SET nombre_producto=%s, descripcion=%s, precio=%s, imagen=%s, id_categoria=%s, disponible=%s WHERE id_producto=%s",
                        (nombre, descripcion, precio, nombre_imagen, id_categoria, disponible, id_producto))
        else:
            cur.execute("UPDATE productos SET nombre_producto=%s, descripcion=%s, precio=%s, id_categoria=%s, disponible=%s WHERE id_producto=%s",
                        (nombre, descripcion, precio, id_categoria, disponible, id_producto))

        conn.commit()
        cur.close()
        return redirect('/admin/crud')
    else:
        cur.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
        producto = cur.fetchone()
        cur.execute("SELECT * FROM categorias")
        categorias = cur.fetchall()
        cur.close()
        return render_template('editar_producto.html', producto=producto, categorias=categorias)


@app.route('/dashboard_admin')
def dashboard_admin():
    if 'loggedin' not in session or session['rol'] != 1:
        return redirect('/login')
    return render_template('dashboardAdmin.html')

@app.route('/admin/empleados')
def empleados():
    # Establece una conexión con la base de datos MySQL
    conn = mysql.connect()
    # Crea un cursor para ejecutar consultas SQL
    cur = conn.cursor()
    
    # Ejecuta una consulta SQL para obtener los empleados y su rol
    cur.execute("""
       SELECT 
        u.id_usuario,      -- 0
        u.nombre,          -- 1
        u.correo,          -- 2
        r.nombre_rol,      -- 3
        e.cargo            -- 4
    FROM usuarios u
    JOIN roles r ON u.id_rol = r.id_rol
    JOIN empleados e ON u.id_usuario = e.id_usuario  
    """)
    
    # Obtiene todos los resultados de la consulta
    empleados = cur.fetchall()
    # Cierra la conexión a la base de datos
    conn.close()
    
    # Renderiza la plantilla 'empleados.html' y le pasa la lista de empleados
    return render_template('empleados.html', empleados=empleados)

@app.route('/logout_empleado')
def logout_empleado():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('nombre', None)
    session.pop('rol', None)
    return render_template('empleado.html')

# Vista para agregar un nuevo empleado
@app.route('/add_empleado', methods=['GET', 'POST'])
def add_empleado():
    mensaje = ''  # Variable para mensajes de error o éxito
    if request.method == 'POST':
        # Obtiene los datos del formulario enviados por el administrador
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        nombre_rol = request.form['rol']  # Ejemplo: 'Empleado' o 'Administrador'
        contrasena_prov = request.form['contrasena']
        cargo = request.form['cargo']  # Ejemplo: 'Cajero', 'Mesero', etc.
        fecha_contratacion = date.today()  # Fecha actual

        # Encripta la contraseña provisional antes de guardarla
        hash_contrasena = generate_password_hash(contrasena_prov)

        # Conexión a la base de datos
        conn = mysql.connect()
        cur = conn.cursor()

        try:
            # Busca el id del rol en la tabla roles según el nombre seleccionado
            cur.execute("SELECT id_rol FROM roles WHERE nombre_rol = %s", (nombre_rol,))
            resultado = cur.fetchone()

            id_rol = resultado[0]  # Extrae el id_rol del resultado

            # Inserta el nuevo usuario en la tabla usuarios
            cur.execute("""
                INSERT INTO usuarios (nombre, correo, telefono, contraseña, id_rol)r
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, correo, telefono, hash_contrasena, id_rol))
            id_usuario = cur.lastrowid  # Obtiene el id generado automáticamente

            # Inserta el nuevo empleado en la tabla empleados con su cargo y fecha de contratación
            cur.execute("""
                INSERT INTO empleados (id_usuario, cargo, fecha_contratacion)
                VALUES (%s, %s, %s)
            """, (id_usuario, cargo, fecha_contratacion))

            conn.commit()  # Confimar los cambios en la base de datos
            return redirect(url_for('empleados'))  # Redirige a la vista de empleados
        except Exception as e:
            conn.rollback()  # Revierte los cambios si ocurre un error
            mensaje = f"Error al registrar empleado: {str(e)}"
        finally:
            conn.close()  # Cierra la conexión a la base de datos

        # Si hubo un error, vuelve a mostrar el formulario con el mensaje
        return render_template('addEmp.html', mensaje=mensaje)
    
    # Si la petición es GET, muestra el formulario vacío
    return render_template('addEmp.html')

@app.route('/pedidos_entrantes')
def pedidos_entrantes():
    conn = mysql.connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.id_pedido,  
               u.nombre, 
               p.total, 
               p.fecha_pedido
        FROM pedidos p
        JOIN usuarios u ON p.id_cliente = u.id_usuario
        WHERE p.estado = 'Pendiente'
        ORDER BY p.fecha_pedido ASC """)
    resultados = cur.fetchall()

    pedidos = []
    for fila in resultados:
        pedidos.append({
            'id': fila[0],
            'cliente': fila[1],
            'total': f"${fila[2]:,.2f}",  # <- Aquí se da formato con 2 decimales
            'hora': fila[3].strftime('%Y-%m-%d %H:%M:%S') if fila[3] else ''
        })

    conn.close()
    return render_template('pedidos_entrantes.html', pedidos=pedidos)

# Vista para ver los detalles de un pedido
@app.route('/pedido/<int:id_pedido>')
def ver_pedido(id_pedido):
    conn = mysql.connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        p.id_pedido,        # 0
        p.fecha_pedido,     # 1
        p.total,            # 2
        c.nombre,           # 3
        c.telefono          # 4
    FROM pedidos p
    JOIN usuarios c ON p.id_cliente = c.id_usuario
    WHERE p.id_pedido = %s
""", (id_pedido,))
    pedido = cur.fetchone()

    # Convierte el total a float si existe pedido
    if pedido:
        pedido = list(pedido)
        pedido[2] = float(pedido[2])  

    cur.execute("""
        SELECT pr.nombre_producto, dp.cantidad, dp.precio_unitario
        FROM detalle_pedidos dp
        JOIN productos pr ON dp.id_producto = pr.id_producto
        WHERE dp.id_pedido = %s
    """, (id_pedido,))
    productos = cur.fetchall()

    conn.close()

    if not pedido:
        return "Pedido no encontrado", 404

    return render_template('detalle_pedido.html', pedido=pedido, productos=productos)


if __name__ == '__main__':
    app.run(debug=True)
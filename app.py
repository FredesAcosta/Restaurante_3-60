import os
from pydoc import text
from utils import manejar_error_db, enviar_codigo_sms
from datetime import date, datetime, timedelta
import random
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flaskext.mysql import MySQL
import pymysql
import bcrypt
from werkzeug.utils import secure_filename
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
        SELECT id_banner AS id, imagen, cupon
        FROM banners
        ORDER BY fecha DESC
    """)
    banners = cur.fetchall()

    return render_template("index.html", banners=banners)




@app.route('/login', methods=['GET', 'POST'])
def login():
    text = ''
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            logger.debug(f"Intento de login para email: {email}")

            conn = mysql.connect()
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
            user = cur.fetchone()
            logger.debug(f"Usuario encontrado: {user is not None}")

            if user and bcrypt.checkpw(password.encode('utf-8'), user['contraseña'].encode('utf-8')):
                session['loggedin'] = True
                session['id'] = user['id_usuario']
                session['nombre'] = user['nombre']
                session['rol'] = user['id_rol']
                logger.info(f"Login exitoso para usuario: {user['nombre']}, rol: {user['id_rol']}")

                if user['id_rol'] == 1:
                    return redirect('/dashboard_admin')
                elif user['id_rol'] == 2:
                    return render_template('empleados.html', text="Bienvenido")
                else:
                    return redirect('/dashboard_cliente')
            else:
                logger.warning(f"Login fallido para email: {email}")
                text = 'Correo o contraseña incorrecta'
    except Exception as e:
        logger.error(f"Error en login: {e}")
        try:
            mensaje = manejar_error_db(e, conn)
        except Exception as inner_e:
            logger.error(f"Error en manejar_error_db: {inner_e}")
            mensaje = f"Error inesperado: {str(e)}"
        flash(mensaje, "danger")

    return render_template('login.html', text=text)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['fullname']
        correo = request.form['email']
        telefono = request.form['phone']
        clave = request.form['password']
        hashed = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        logger.debug(f"Registro de usuario: {nombre}, email: {correo}")

        conn = mysql.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO usuarios (nombre, correo, telefono, contraseña, id_rol)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, correo, telefono, hashed, 3))
            conn.commit()
            logger.info(f"Usuario registrado exitosamente: {nombre}")
            flash("Usuario registrado correctamente.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Error al registrar usuario {nombre}: {e}")
            mensaje = manejar_error_db(e, conn)
            flash(mensaje, 'danger')
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')

@app.route('/dashboard_cliente')
def dashboard_cliente():
    if 'loggedin' not in session:
        return redirect('/login')
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM productos WHERE disponible = 1")
    productos = cur.fetchall()
    cur.close()
    return render_template('dashboardClientes.html', productos=productos, nombre=session.get('nombre', 'Usuario'))

# ---------------- Recuperación por SMS (Twilio) ----------------
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """
    Formulario donde el usuario ingresa su teléfono para recibir un código SMS
    """
    if request.method == 'POST':
        telefono = request.form['telefono'].strip()
        logger.debug(f"Solicitud de recuperación para teléfono: {telefono}")

        # Normalizamos: quitamos +57 si el usuario lo pone
        telefono_normalizado = telefono.replace("+57", "").strip()
        logger.debug(f"Teléfono normalizado: {telefono_normalizado}")

        # Verificamos si el teléfono existe en la tabla usuarios
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cur.execute("SELECT * FROM usuarios WHERE telefono = %s", (telefono_normalizado,))
            user = cur.fetchone()
            logger.debug(f"Usuario encontrado para teléfono: {user is not None}")
        finally:
            cur.close()
            conn.close()

        if not user:
            logger.warning(f"Teléfono no registrado: {telefono_normalizado}")
            flash("El número no está registrado.", "danger")
            return render_template('forgot_password.html')

        # Generar código de 6 dígitos + expiración
        codigo = str(random.randint(100000, 999999))
        expiracion = datetime.now() + timedelta(minutes=10)
        logger.debug(f"Código generado: {codigo}, expiración: {expiracion}")

        conn = mysql.connect()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO password_resets (telefono, codigo, expiracion) VALUES (%s, %s, %s)",
                        (telefono_normalizado, codigo, expiracion))
            conn.commit()
            logger.info(f"Código insertado en DB para teléfono: {telefono_normalizado}")
        finally:
            cur.close()
            conn.close()

        # Enviar SMS vía Twilio
        if not enviar_codigo_sms(telefono_normalizado, codigo):
            logger.error(f"Error al enviar SMS a {telefono_normalizado}")
            flash("No se pudo enviar el SMS. Verifica el número de teléfono.", "danger")
        else:
            logger.info(f"SMS enviado exitosamente a {telefono_normalizado}")
            flash("Código enviado con éxito.", "success")
        return redirect(url_for('verify_code'))

    return render_template('forgot_password.html')


@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    """
    Formulario donde el usuario ingresa el teléfono y el código recibido por SMS.
    Si es válido, guarda telefono en session para permitir reset de contraseña.
    """
    if request.method == 'POST':
        telefono = request.form['telefono'].strip()
        telefono_normalizado = telefono.replace("+57", "").strip()
        codigo = request.form['codigo'].strip()
        logger.debug(f"Verificación de código para teléfono: {telefono_normalizado}, código: {codigo}")

        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cur.execute("SELECT * FROM password_resets WHERE telefono=%s AND codigo=%s ORDER BY id DESC LIMIT 1",
                        (telefono_normalizado, codigo))
            registro = cur.fetchone()
            logger.debug(f"Registro encontrado: {registro is not None}")
        finally:
            cur.close()
            conn.close()

        if registro and datetime.now() < registro['expiracion']:
            logger.info(f"Código válido para teléfono: {telefono_normalizado}")
            session['reset_telefono'] = telefono_normalizado
            return redirect(url_for('reset_password'))
        else:
            logger.warning(f"Código inválido o expirado para teléfono: {telefono_normalizado}")
            flash("Código inválido o expirado.", "danger")

    return render_template('verify_code.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """
    Formulario para establecer la nueva contraseña una vez verificado el código SMS.
    """
    if 'reset_telefono' not in session:
        logger.warning("Acceso a reset_password sin sesión de reset")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        nueva_pass = request.form['password']
        confirm = request.form.get('confirm_password')
        logger.debug(f"Intento de reset para teléfono: {session['reset_telefono']}")
        if nueva_pass != confirm:
            logger.warning("Contraseñas no coinciden en reset")
            flash("Las contraseñas no coinciden.", "danger")
            return render_template('reset_password.html')

        hashed = bcrypt.hashpw(nueva_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = mysql.connect()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE usuarios SET contraseña=%s WHERE telefono=%s",
                        (hashed, session['reset_telefono']))
            conn.commit()
            logger.info(f"Contraseña actualizada para teléfono: {session['reset_telefono']}")
            # opcional: borrar tokens antiguos del mismo telefono
            cur.execute("DELETE FROM password_resets WHERE telefono=%s", (session['reset_telefono'],))
            conn.commit()
            logger.debug(f"Tokens antiguos borrados para teléfono: {session['reset_telefono']}")
        finally:
            cur.close()
            conn.close()

        session.pop('reset_telefono', None)
        flash("Contraseña actualizada correctamente.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html')

# Mostrar menu disponible
@app.route('/menu')
def menu():
    if 'loggedin' not in session:
        return redirect('/login')

    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM productos WHERE disponible = 1")
    productos = cur.fetchall()

    # Construir carrito
    carrito_ids = session.get('carrito', [])
    carrito_items = []
    total_carrito = 0.0
    for pid in carrito_ids:
        cur.execute(
            "SELECT id_producto, nombre_producto AS nombre, precio, imagen "
            "FROM productos WHERE id_producto = %s", (pid,)
        )
        p = cur.fetchone()
        if p:
            carrito_items.append(p)
            total_carrito += float(p['precio'])
    cur.close()

    return render_template('menu.html',
        productos=productos,
        carrito_items=carrito_items,
        total_carrito=total_carrito
    )

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
    flash("Debes iniciar sesión", "error")
    return redirect('/login')


@app.route('/admin/categorias', methods=['POST'])
def registrar_categoria():
    nombre = request.form['nombre_categoria']
    conn = mysql.connect()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO categorias (nombre_categoria) VALUES (%s)", (nombre,))
        conn.commit()
        flash("Categoría agregada correctamente.", "success")
    except Exception as e:
        flash(manejar_error_db(e, conn), "error")

    finally:
        cur.close()
        conn.close()

    return redirect('/admin/crud')

@app.route('/admin/productos', methods=['POST'])
def registrar_producto():
    nombre = request.form['nombre_producto']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    id_categoria = request.form['id_categoria']
    disponible = 1 if 'disponible' in request.form else 0

    imagen = request.files['imagen']

    # Imagen obligatoria
    if not imagen or imagen.filename.strip() == "":
        flash("Debe subir una imagen para registrar el producto.", "error")
        return redirect('/admin/crud')

    # Si hay imagen válida, la guardamos
    nombre_imagen = secure_filename(imagen.filename)
    ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)

    conn = mysql.connect()
    cur = conn.cursor()
    try:
        imagen.save(ruta_imagen)

        cur.execute("""
            INSERT INTO productos (nombre_producto, descripcion, precio, imagen, id_categoria, disponible)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, precio, nombre_imagen, id_categoria, disponible))
        
        conn.commit()
        flash("Producto registrado correctamente.", "success")

    except Exception as e:
        flash(manejar_error_db(e, conn), "error")

    finally:
        cur.close()
        conn.close()

    return redirect('/admin/crud')

@app.route('/admin/eliminar_producto/<int:id_producto>')
def eliminar_producto(id_producto):
    conn = mysql.connect()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        conn.commit()
        flash("Producto eliminado correctamente.", "success")
    except Exception as e:
        flash(manejar_error_db(e, conn), "error")
    finally:
        cur.close()
        conn.close()

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
    if 'loggedin' in session and session['rol'] == 1:
        return render_template('dashboardAdmin.html', nombre=session.get('nombre', 'Administrador'))
    return redirect('/login')

@app.route('/admin/estadisticas', methods=['GET', 'POST'])
def admin_estadisticas():
    if 'loggedin' not in session or session['rol'] != 1:
        return redirect('/login')
    fecha_inicio = request.form.get('fecha_inicio') if request.method == 'POST' else None
    fecha_fin = request.form.get('fecha_fin') if request.method == 'POST' else None
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    # Top productos
    if fecha_inicio and fecha_fin:
        query_top = """
        SELECT p.nombre_producto, SUM(dp.cantidad) as total_vendidos
        FROM detalle_pedidos dp
        JOIN productos p ON dp.id_producto = p.id_producto
        JOIN pedidos pe ON dp.id_pedido = pe.id_pedido
        WHERE pe.fecha_pedido BETWEEN %s AND %s
        GROUP BY p.id_producto
        ORDER BY total_vendidos DESC
        LIMIT 5
        """
        cur.execute(query_top, (fecha_inicio, fecha_fin))
    else:
        query_top = """
        SELECT p.nombre_producto, SUM(dp.cantidad) as total_vendidos
        FROM detalle_pedidos dp
        JOIN productos p ON dp.id_producto = p.id_producto
        GROUP BY p.id_producto
        ORDER BY total_vendidos DESC
        LIMIT 5
        """
        cur.execute(query_top)
    top_productos = cur.fetchall()
    # Pedidos por día
    if fecha_inicio and fecha_fin:
        query_dia = """
        SELECT DATE(fecha_pedido) as fecha, COUNT(*) as total_pedidos
        FROM pedidos
        WHERE fecha_pedido BETWEEN %s AND %s
        GROUP BY DATE(fecha_pedido)
        ORDER BY fecha
        """
        cur.execute(query_dia, (fecha_inicio, fecha_fin))
    else:
        query_dia = """
        SELECT DATE(fecha_pedido) as fecha, COUNT(*) as total_pedidos
        FROM pedidos
        GROUP BY DATE(fecha_pedido)
        ORDER BY fecha
        """
        cur.execute(query_dia)
    pedidos_por_dia = cur.fetchall()
    # Pedidos por estado
    if fecha_inicio and fecha_fin:
        query_estado = """
        SELECT estado, COUNT(*) as total
        FROM pedidos
        WHERE fecha_pedido BETWEEN %s AND %s
        GROUP BY estado
        """
        cur.execute(query_estado, (fecha_inicio, fecha_fin))
    else:
        query_estado = """
        SELECT estado, COUNT(*) as total
        FROM pedidos
        GROUP BY estado
        """
        cur.execute(query_estado)
    pedidos_por_estado = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_reportes.html', nombre=session.get('nombre', 'Administrador'), top_productos=top_productos, pedidos_por_dia=pedidos_por_dia, pedidos_por_estado=pedidos_por_estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

@app.route('/admin/empleados')
def admin_empleados():
    # protección: solo admin
    if 'loggedin' not in session or session.get('rol') != 1:
        flash("Acceso no autorizado.", "error")
        return redirect(url_for('login'))

    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute("""
            SELECT 
                u.id_usuario,
                u.nombre,
                u.correo,
                r.nombre_rol,
                e.cargo
            FROM usuarios u
            JOIN roles r ON u.id_rol = r.id_rol
            JOIN empleados e ON u.id_usuario = e.id_usuario
        """)
        empleados = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    return render_template('empleados.html', empleados=empleados)


@app.route('/logout_empleado')
def logout_empleado():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('nombre', None)
    session.pop('rol', None)
    return render_template('empleado.html')

@app.route('/add_empleado', methods=['GET', 'POST'])
def add_empleado():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        telefono = request.form.get('telefono', '').strip()
        nombre_rol = request.form.get('rol', '').strip()
        contrasena_prov = request.form.get('contrasena', '').strip()
        cargo = request.form.get('cargo', '').strip()
        fecha_contratacion = date.today()

        if not (nombre and correo and contrasena_prov and nombre_rol and cargo):
            flash("Complete todos los campos.", "error")
            return redirect(url_for('admin_empleados'))

        hash_contrasena = bcrypt.hashpw(contrasena_prov.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = mysql.connect()
        cur = conn.cursor()
        try:
            # obtener ID del rol
            cur.execute("SELECT id_rol FROM roles WHERE nombre_rol = %s", (nombre_rol,))
            id_rol_result = cur.fetchone()
            if not id_rol_result:
                flash("Rol no válido.", "error")
                return redirect(url_for('admin_empleados'))

            # id_rol_result puede ser tupla o dict según cursor; manejamos tupla
            id_rol = id_rol_result[0] if isinstance(id_rol_result, (list, tuple)) else id_rol_result.get('id_rol')

            # insertar usuario
            cur.execute("""
                INSERT INTO usuarios (nombre, correo, telefono, contraseña, id_rol)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, correo, telefono, hash_contrasena, id_rol))
            id_usuario = cur.lastrowid

            # insertar en empleados
            cur.execute("""
                INSERT INTO empleados (id_usuario, cargo, fecha_contratacion)
                VALUES (%s, %s, %s)
            """, (id_usuario, cargo, fecha_contratacion))

            conn.commit()
            flash("Empleado agregado correctamente.", "success")
        except Exception as e:
            # manejar_error_db necesita conn válido — si falla, intenta pasar None con control
            try:
                mensaje = manejar_error_db(e, conn)
            except Exception:
                mensaje = f"Error inesperado: {e}"
            flash(mensaje, "error")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('admin_empleados'))

    # Si alguien accede por GET a /add_empleado, redirige al listado admin
    return redirect(url_for('admin_empleados'))

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
# =======================================|
#    Cargar de banners                   |
# =======================================|
@app.route('/admin/banners')
def admin_banners():
    if 'loggedin' not in session or session['rol'] != 1:
        return redirect('/login')

    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT * FROM banners ORDER BY fecha DESC")
    banners = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin_banners.html', banners=banners)

@app.route('/admin/banners/subir', methods=['POST'])
def subir_banner():
    if 'loggedin' not in session or session['rol'] != 1:
        return redirect('/login')

    titulo = request.form.get('titulo', '').strip()
    imagen = request.files.get('imagen')

    # Validación
    if not imagen or imagen.filename.strip() == "":
        flash("Debes seleccionar una imagen.", "danger")
        return redirect('/admin/banners')

    try:
        # Guardar imagen en /static/uploads
        nombre_imagen = secure_filename(imagen.filename)
        ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)
        imagen.save(ruta_imagen)

        # Guardar en DB
        conn = mysql.connect()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO banners (titulo, imagen)
            VALUES (%s, %s)
        """, (titulo, nombre_imagen))

        conn.commit()

        flash("Banner subido correctamente.", "success")
    except Exception as e:
        flash(manejar_error_db(e, conn), "danger")
    finally:
        cur.close()
        conn.close()

    return redirect('/admin/banners')

@app.route('/admin/banners/eliminar/<int:id_banner>')
def eliminar_banner(id_banner):
    if 'loggedin' not in session or session['rol'] != 1:
        return redirect('/login')

    conn = mysql.connect()
    cur = conn.cursor()

    try:
        # Obtener nombre de la imagen antes de borrarla
        cur.execute("SELECT imagen FROM banners WHERE id_banner = %s", (id_banner,))
        banner = cur.fetchone()

        if banner:
            # borrar archivo físico
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], banner[0])
            if os.path.exists(ruta):
                os.remove(ruta)

        cur.execute("DELETE FROM banners WHERE id_banner = %s", (id_banner,))
        conn.commit()

        flash("Banner eliminado.", "success")

    except Exception as e:
        flash(manejar_error_db(e, conn), "danger")
    finally:
        cur.close()
        conn.close()

    return redirect('/admin/banners')

if __name__ == '__main__':
    app.run(debug=True)
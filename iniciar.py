from flask import Flask, redirect, render_template, request, session,  url_for
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import pymysql
import bcrypt

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secretkey'

# Configuración de la base de datos

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'restaurante_db'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# Ruta principal (home)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    text = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        # phone = request.form['phone']
        password = request.form['password']

        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()

        if user:
            hashed_password = user['contraseña']
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                session['loggedin'] = True
                session['id'] = user['id_usuario']
                session['nombre'] = user['nombre']
                session['rol'] = user['id_rol']
                text = f"Bienvenido {user['nombre']}!"
                return render_template('dashboardClientes.html', text=text)
            else:
                text = 'Contraseña incorrecta'
        else:
            text = 'Correo no registrado'
    elif request.method == 'POST':
        text = "Por favor completa el formulario"

    return render_template('login.html', text=text)

@app.route('/eliminar_cuenta', methods=['POST'])
def eliminar_cuenta():
    if 'loggedin' in session:
        id_usuario = session['id']
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
        cur.close()
        session.clear()
        return render_template('index.html', text='Tu cuenta ha sido eliminada exitosamente.')
    return render_template('login.html', text='No has iniciado sesión.')

@app.route('/dashboard_cliente')
def dashboard_cliente():
    if 'loggedin' in session:
        return render_template('dashboardClientes.html')
    return render_template('login.html', text='Por favor inicia sesión primero.')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('nombre', None)
    session.pop('rol', None)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    text = ''
    if request.method == 'POST' and 'fullname' in request.form and 'email' in request.form and 'phone' in request.form and 'password' in request.form:
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()

        if user:
            text = "El correo ya está registrado"
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cur.execute("INSERT INTO usuarios (nombre, correo, telefono, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s)", 
                        (fullname, email, phone, hashed_password.decode('utf-8'), 3))
            conn.commit()
            text = "Cuenta creada exitosamente!"

        cur.close()
    elif request.method == 'POST':
        text = "Por favor completa el formulario"

    return render_template('register.html', text=text)


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

# Vista de empleados
@app.route('/empleados')
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
            if not resultado:
                # Si el rol no existe, muestra un mensaje de error
                mensaje = f"Error: El rol '{nombre_rol}' no existe."
                return render_template('addEmp.html', mensaje=mensaje)

            id_rol = resultado[0]  # Extrae el id_rol del resultado

            # Inserta el nuevo usuario en la tabla usuarios
            cur.execute("""
                INSERT INTO usuarios (nombre, correo, telefono, contraseña, id_rol)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, correo, telefono, hash_contrasena, id_rol))
            id_usuario = cur.lastrowid  # Obtiene el id generado automáticamente

            # Inserta el nuevo empleado en la tabla empleados con su cargo y fecha de contratación
            cur.execute("""
                INSERT INTO empleados (id_usuario, cargo, fecha_contratacion)
                VALUES (%s, %s, %s)
            """, (id_usuario, cargo, fecha_contratacion))

            conn.commit()  # Guarda los cambios en la base de datos
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

# Vista de pedidos entrantes
@app.route('/pedidos_entrantes')
def pedidos_entrantes():
    conn = mysql.connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.id_pedido, 
               p.tipo_pedido, 
               u.nombre, 
               p.total, a
               p.fecha_pedido
        FROM pedidos p
        JOIN usuarios u ON p.id_cliente = u.id_usuario
        WHERE p.estado = 'Pendiente'
        ORDER BY p.fecha_pedido ASC""")
    resultados = cur.fetchall()

    pedidos = []
    for fila in resultados:
        pedidos.append({
            'id': fila[0],
            'tipo': fila[1],
            'cliente': fila[2],
            'total': f"${fila[3]:,.2f}",  # <- Aquí se da formato con 2 decimales
            'hora': fila[4].strftime('%Y-%m-%d %H:%M:%S') if fila[4] else ''
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
            p.id_pedido,
            p.fecha_pedido,
            p.tipo_pedido,
            p.total,
            c.nombre,
            c.telefono
        FROM pedidos p
        JOIN usuarios c ON p.id_cliente = c.id_usuario
        WHERE p.id_pedido = %s
    """, (id_pedido,))
    pedido = cur.fetchone()

    cur.execute("""
        SELECT pr.nombre_producto, dp.cantidad, dp.precio_unitario
        FROM detalle_pedidos dp
        JOIN productos pr ON dp.id_producto = pr.id_producto
        WHERE dp.id_pedido = %s
    """, (id_pedido,))
    productos = cur.fetchall()

    conn.close()
    return render_template('detalle_pedido.html', pedido=pedido, productos=productos)


# Ejecuta la app en modo debug
if __name__ == '__main__':
    app.run(debug=True)

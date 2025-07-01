from modulos.app_flask import app
from flask import render_template, request, session
from modulos.db import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import bcrypt

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
    return render_template('login.html', text='Por favor inicia sesión.')

# Vista de empleados
@app.route('/empleados')
def empleados():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT  id_usuario, nombre_usuario, correo, rol FROM usuarios")
    empleados = cur.fetchall()
    conn.close()
    return render_template('empleados.html', empleados=empleados)

# Vista para agregar un nuevo empleado
@app.route('/add_empleado', methods=['GET', 'POST'])
def add_empleado():
    mensaje = ''
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        rol = request.form['rol']
        contrasena_prov = request.form['contrasena']

        # Encriptar la contraseña
        hash_contrasena = generate_password_hash(contrasena_prov)

        conn = mysql.connect()
        cur = conn.cursor()
        # Insertar en la tabla usuarios
        cur.execute("INSERT INTO usuarios (nombre_usuario, correo, contraseña, rol) VALUES (%s, %s, %s, %s)",
                    (nombre, correo, hash_contrasena, rol))
        conn.commit()
        conn.close()
        mensaje = f"¡Bienvenido {nombre}! Usuario creado correctamente."
        return render_template('addEmp.html', mensaje=mensaje)
    
    # Este return es para GET
    return render_template('addEmp.html')

# Ejecuta la app en modo debug
if __name__ == '__main__':
    app.run(debug=True)

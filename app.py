from flask import Flask, render_template, session, request
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

mysql =MySQL()

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secretkey'

# Configuración de la base de datos
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'restaurante_db'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

# Ruta principal (home)
@app.route('/')
def home():
    return render_template('/index.html')

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    text = ''
    # Si se envió el formulario con usuario y contraseña
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # Consulta para verificar usuario y contraseña
        cur.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        user = cur.fetchone()

        if user:
            # Si existe el usuario, se inicia sesión
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            return render_template('index.html', msg=text)
        else:
            text = 'Incorrect username/password!'

    elif request.method == 'POST':
        text = "Fill in the forms"

    return render_template('login.html', msg=text)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return render_template('index.html')

# Ruta de registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    text = ''
    # Si se envió el formulario con los datos requeridos
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        conn = mysql.connect()  # Conectamos a la base de datos
        cur = conn.cursor(pymysql.cursors.DictCursor)

        # Verificamos si el correo ya está registrado
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()

        if user:
            text = "El correo ya está registrado"
        else:
            # Insertamos el nuevo usuario con rol 3 (Cliente)
            cur.execute("INSERT INTO usuarios (nombre, correo, telefono, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s)", 
                        (username, email, phone, password, 3))
            conn.commit()
            text = "Cuenta creada exitosamente!"

    elif request.method == 'POST':
        text = "Por favor completa el formulario"

    return render_template('register.html', text=text)


#@app.route('/categorias', methods=['GET', 'POST'])
"""def categorias():
    text = ''
    if request.method == 'POST' and 'category' in request.form:
        categoria_nombre = request.form['category']

        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        # Buscar si ya existe
        cur.execute("SELECT * FROM categoria WHERE nombre_categoria = %s", (categoria_nombre,))
        categoria_existente = cur.fetchone()

        if categoria_existente:
            text = "La categoría ya existe."
        else:
            cur.execute("INSERT INTO categoria (nombre_categoria) VALUES (%s)", (categoria_nombre,))
            conn.commit()
            text = "Categoría creada exitosamente."
    elif request.method == 'POST':
        text = "Debes llenar el formulario."
        
    return render_template('categorias.html', text=text)"""

@app.route('/empleados')
def empleados():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT  id_usuario, nombre_usuario, correo, rol FROM usuarios")
    empleados = cur.fetchall()
    conn.close()
    return render_template('/empleados.html', empleados=empleados)

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
        return render_template('/addEmp.html', mensaje=mensaje)
    
    # Este return es para GET
    return render_template('/addEmp.html')

# Ejecuta la app en modo debug
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, session, request
from flaskext.mysql import MySQL
import pymysql

# Configuración de la conexión MySQL
mysql = MySQL()

# Inicialización de la app Flask
app = Flask(__name__, template_folder='templates')
app.secret_key = 'secretkey'  # Clave secreta para sesiones

# Configuración de la base de datos
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'restaurante_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

# Ruta principal (home)
@app.route('/')
def home():
    return render_template('index.html')

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
            text = f'Welcome {user["username"]}!'
            return render_template('index.html', text=text)
        else:
            text = 'Incorrect username/password!'

    elif request.method == 'POST':
        text = "Fill in the forms"

    return render_template('login.html', text=text)

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
        password = request.form['password']

        conn = mysql.connect()  # Conexión a la base de datos
        cur = conn.cursor(pymysql.cursors.DictCursor)  # Cursor que retorna diccionarios
        # Consulta para verificar si ya existe el usuario o correo
        cur.execute("SELECT * FROM clientes WHERE nombre = %s OR correo = %s", (username, email,))
        accounts = cur.fetchone()

        if accounts:
            text = "Account already exists"
        else:
            # Inserta el nuevo usuario en la tabla accounts
            cur.execute("INSERT INTO accounts VALUES(NULL, %s, %s, %s)", (username, email, password,))
            conn.commit()
            text = "Account successfully created!"
    # elif request.method=='POST':
    #     text = "Fill in the forms"
    return render_template('register.html', text=text)

# Ruta para agregar productos
@app.route('/producto', methods=['GET', 'POST'])
def producto():
    text = ''
    # Si se envió el formulario con los datos requeridos
    if request.method == 'POST' and 'name_product' in request.form and 'description' in request.form and 'precio' in request.form and 'cantidad' in request.form:
        name_product = request.form['name_product']
        description = request.form['description']
        precio = request.form['precio']
        cantidad = request.form['cantidad']

        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # Consulta para verificar si ya existe el producto
        cur.execute("SELECT * FROM productos WHERE nombre_producto = %s", (name_product,))
        products = cur.fetchone()
        if products:
            text = "Product already exists"
        else:
            # Inserta el nuevo producto en la tabla productos
            cur.execute("INSERT INTO productos VALUES(NULL, %s, %s, %s, 1, NULL, %s)", (name_product, description, precio, cantidad,))
        conn.commit()
        text = "Product successfully created!"
    return render_template('producto.html', text=text)

# Ejecuta la app en modo debug
if __name__ == '__main__':
    app.run(debug=True)
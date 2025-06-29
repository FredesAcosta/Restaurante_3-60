from flask import Flask, render_template,session,request
from flaskext.mysql import MySQL
import pymysql
import bcrypt

<<<<<<< Updated upstream
mysql = MySQL()# Configure MySQL connection
=======
mysql = MySQL()
>>>>>>> Stashed changes

app = Flask(__name__,template_folder='templates')
app.secret_key = 'secretkey'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'restaurante_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

<<<<<<< Updated upstream
@app.route('/login', methods=['GET','POST'])
=======
@app.route('/login', methods=['GET', 'POST'])
>>>>>>> Stashed changes
def login():
    text = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
<<<<<<< Updated upstream
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        user = cur.fetchone()

        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            text = f'Welcome {user["username"]}!'
            return render_template('index.html', text=text)
        else:
            text = 'Incorrect username/password!'
=======

        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        # Buscar el usuario solo por el correo
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()

        if user:
            # Comparar contraseñas con bcrypt
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
>>>>>>> Stashed changes

    elif request.method == 'POST':
        text = "Fill in the forms"

    return render_template('login.html', text=text)

@app.route('/eliminar_cuenta', methods=['POST'])
def eliminar_cuenta():
    print("Se recibió solicitud para eliminar cuenta.")  
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
        return render_template('dashboard_cliente.html')
    return render_template('login.html', text='Por favor inicia sesión primero.')

@app.route('/logout')
def logout():
<<<<<<< Updated upstream
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('index.html')
=======
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return render_template('index.html')
>>>>>>> Stashed changes

@app.route('/register', methods=['GET','POST'])
def register():
    text = ''
<<<<<<< Updated upstream
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form['username']
=======
    if request.method == 'POST' and 'fullname' in request.form and 'email' in request.form and 'phone' in request.form and 'password' in request.form:
        fullname = request.form['fullname']
>>>>>>> Stashed changes
        email = request.form['email']
        password = request.form['password']

<<<<<<< Updated upstream
        conn = mysql.connect()#conectamos a la base de datos
        cur = conn.cursor(pymysql.cursors.DictCursor)#instanciamos el cursor para que nos retorne un diccionario
        cur.execute(" SELECT * FROM clientes WHERE nombre = %s OR correo = %s",(username,email,))#aqui se ejecuta la consulta
        accounts = cur.fetchone()

        if accounts:
            text = "Account already exists" 
        else:
            #insercicion de datos
            cur.execute("INSERT INTO accounts VALUES(NULL, %s, %s, %s)", (username, email, password,))
            conn.commit()
            text = "Account successfully created!"    
    # elif request.method=='POST':
    #     text = "Fill in the forms"
    return render_template('register.html',text=text)

@app.route('/producto', methods=['GET','POST'])
def producto():
    text = ''
    if request.method == 'POST' and 'name_product' in request.form and 'description' in request.form and 'precio' in request.form and 'cantidad' in request.form:
        name_product = request.form['name_product']
        description = request.form['description']
        precio = request.form['precio']
        cantidad = request.form['cantidad']

        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM productos WHERE nombre_producto = %s", (name_product,))
        products = cur.fetchone()
        if products:
            text = "Product already exists"
        else:
            # Insert data into the database
            cur.execute("INSERT INTO productos VALUES(NULL, %s, %s, %s, 1, NULL, %s)", (name_product, description, precio, cantidad,))
        conn.commit()
        text = "Product successfully created!"
    return render_template('producto.html', text=text)
=======
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()

        if user:
            text = "El correo ya está registrado"
        else:
            # Encriptar contraseña antes de guardarla
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cur.execute("INSERT INTO usuarios (nombre, correo, telefono, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s)", 
                        (fullname, email, phone, hashed_password.decode('utf-8'), 3))
            conn.commit()
            text = "Cuenta creada exitosamente!"

        cur.close()
    elif request.method == 'POST':
        text = "Por favor completa el formulario"

    return render_template('register.html', text=text)
>>>>>>> Stashed changes

if __name__ == '__main__':
    app.run(debug=True)

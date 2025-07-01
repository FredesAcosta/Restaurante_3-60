from flask import Flask, render_template, session, request
from flaskext.mysql import MySQL
import pymysql
import bcrypt

mysql = MySQL()  # Configurar conexión MySQL

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secretkey'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'restaurante_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    text = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
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
        return render_template('dashboardClienteS.html', text='Mesa reservada exitosamente.')
    return render_template('login.html', text='Por favor inicia sesión.')


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, session, request, redirect, url_for, flash
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
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['contrasena'].encode('utf-8')):
            session['loggedin'] = True
            session['id'] = user['id_usuario']
            session['nombre'] = user['nombre']
            session['rol'] = user['id_rol']

            if user['id_rol'] == 1:
                return redirect('/dashboard_admin')
            elif user['id_rol'] == 2:
                return render_template('dashboardEmpleado.html', text="Bienvenido")
            else:
                return redirect('/dashboard_cliente')
        else:
            text = 'Correo o contraseña incorrecta'

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

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nombre, correo, telefono, contrasena, id_rol) VALUES (%s, %s, %s, %s, %s)",
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
    if 'loggedin' in session and session['rol'] == 1:
        return render_template('dashboardAdmin.html')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
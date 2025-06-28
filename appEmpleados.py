from app import app, render_template, mysql, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/empleados')
def empleados():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM empleados")
    empleados = cur.fetchall()
    conn.close()
    return render_template('empleados.html', empleados=empleados)
# appEmpleados.py

from app import app, render_template, mysql, request, session, redirect, url_for

@app.route('/agregarEmpleado', methods=['GET', 'POST'])
def agregar_empleado():
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
        # Insertar en la tabla empleados
        cur.execute("INSERT INTO empleados (nombre_usuario, correo, contraseña, rol) VALUES (%s, %s, %s, %s)",
                    (nombre, correo, hash_contrasena, rol))
        conn.commit()
        conn.close()
        mensaje = f"¡Bienvenido {nombre}! Usuario creado correctamente."
        return render_template('agregarEmpleado.html', mensaje=mensaje)
from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import mysql

auth_bp = Blueprint("auth", __name__, url_prefix="/")

@auth_bp.route("/")
def home():
    return render_template("auth/index.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    text = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[4], password):
            session["loggedin"] = True
            session["id"] = user[0]
            session["nombre"] = user[1]
            session["rol"] = user[5]

            if user[5] == 1:
                return redirect("/admin/dashboard")
            elif user[5] == 2:
                return redirect("/cocinero/pedidos")
            elif user[5] == 3:
                return redirect("/cliente/dashboard")
        else:
            text = "Correo o contraseña incorrectos."

    return render_template("auth/login.html", text=text)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["fullname"]
        email = request.form["email"]
        telefono = request.form["phone"]
        password = request.form["password"]

        hashed = generate_password_hash(password)

        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (nombre, correo, telefono, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s)",
            (nombre, email, telefono, hashed, 3),
        )
        conn.commit()
        cur.close()
        return redirect("/login")

    return render_template("auth/register.html")

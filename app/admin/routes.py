from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from ..extensions import mysql
import os
import pymysql

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
def dashboard_admin():
    if "loggedin" not in session or session["rol"] != 1:
        return redirect("/login")
    return render_template("admin/dashboardAdmin.html")

@admin_bp.route("/crud")
def admin_crud():
    if "loggedin" in session and session["rol"] == 1:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM categorias")
        categorias = cur.fetchall()
        cur.execute("SELECT p.*, c.nombre_categoria FROM productos p JOIN categorias c ON p.id_categoria = c.id_categoria")
        productos = cur.fetchall()
        cur.close()
        return render_template("admin/editar_producto.html", categorias=categorias, productos=productos)
    return redirect("/login")

# Aquí moverías las demás rutas de productos, empleados, etc.

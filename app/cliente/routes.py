from flask import Blueprint, render_template, session, redirect, request, url_for, flash
from ..extensions import mysql
import pymysql

cliente_bp = Blueprint("cliente", __name__, url_prefix="/cliente")

@cliente_bp.route("/dashboard")
def dashboard_cliente():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM productos WHERE disponible = 1")
    productos = cur.fetchall()
    cur.close()
    return render_template("cliente/dashboardClientes.html", productos=productos)

@cliente_bp.route("/menu")
def menu():
    if "loggedin" not in session:
        return redirect("/login")

    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    carrito_items = []
    total_carrito = 0.0
    try:
        cur.execute("SELECT * FROM productos WHERE disponible = 1")
        productos = cur.fetchall()

        carrito_ids = session.get("carrito", [])
        for pid in carrito_ids:
            cur.execute("SELECT id_producto, nombre_producto AS nombre, precio, imagen FROM productos WHERE id_producto = %s", (pid,))
            p = cur.fetchone()
            if p:
                carrito_items.append(p)
                total_carrito += float(p["precio"])
    finally:
        cur.close()
        conn.close()

    return render_template("cliente/menu.html", productos=productos, carrito_items=carrito_items, total_carrito=total_carrito)

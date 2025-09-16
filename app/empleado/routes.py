from flask import Blueprint, render_template
from ..extensions import mysql

empleado_bp = Blueprint("empleado", __name__, url_prefix="/empleado")

@empleado_bp.route("/pedidos")
def pedidos_entrantes():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id_pedido, u.nombre, p.total, p.fecha_pedido
        FROM pedidos p
        JOIN usuarios u ON p.id_cliente = u.id_usuario
        WHERE p.estado = 'Pendiente'
        ORDER BY p.fecha_pedido ASC
    """)
    resultados = cur.fetchall()
    conn.close()

    pedidos = []
    for fila in resultados:
        pedidos.append({
            "id": fila[0],
            "cliente": fila[1],
            "total": f"${fila[2]:,.2f}",
            "hora": fila[3].strftime("%Y-%m-%d %H:%M:%S") if fila[3] else ""
        })

    return render_template("empleado/pedidos_entrantes.html", pedidos=pedidos)

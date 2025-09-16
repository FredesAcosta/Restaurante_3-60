import os
from flask import Flask
from .extensions import mysql
from werkzeug.utils import secure_filename

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Configuración
    app.secret_key = "secretkey"
    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = ''
    app.config['MYSQL_DATABASE_DB'] = 'restaurante_db'
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    app.config['UPLOAD_FOLDER'] = os.path.join("static", "uploads")
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inicializar extensiones
    mysql.init_app(app)

    # Registrar blueprints
    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .cliente.routes import cliente_bp
    from .empleado.routes import empleado_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(empleado_bp)

    return app

Restaurante 360

Sistema web de gestión de pedidos para restaurante
Flask · MySQL · HTML · CSS · Arquitectura MVC

Descripción

Restaurante 360 es una aplicación web diseñada para gestionar pedidos, menú, usuarios y administración interna de un restaurante.
Permite a clientes realizar pedidos en línea, seleccionar mesas, gestionar su perfil y visualizar productos en un menú dinámico.
Incluye un panel administrativo con CRUD de productos y categorías.

Tecnologías

Backend: Python (Flask)

Frontend: HTML, CSS, Bootstrap

Base de datos: MySQL / MariaDB

Herramientas: XAMPP, VS Code, Postman, GitHub

Funcionalidades
Cliente

Registro y login.

Visualizar menú.

Carrito de compras con persistencia por sesión.

Realizar pedidos (domicilio, mesa, para llevar).

Seleccionar mesas disponibles.

Gestionar perfil y eliminar cuenta.

Administrador

CRUD de productos.

CRUD de categorías.

Gestión de disponibilidad del menú.

Vista general de pedidos.

Estructura del Proyecto
Restaurante360/
│
├── app.py
├── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── registro.html
│   ├── menu.html
│   ├── carrito.html
│   ├── cliente/
│   │   └── mesas.html
│   └── admin/
│       ├── productos.html
│       └── categorias.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
└── database/
    └── restaurante360.sql

Instalación
1. Clonar el repositorio
git clone https://github.com/usuario/Restaurante360.git
cd Restaurante360

2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate   # Windows

3. Instalar dependencias
pip install -r requirements.txt

4. Configurar la base de datos

Importar el archivo:

database/restaurante360.sql


Configurar app.py:

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'restaurante_db'

5. Ejecutar el servidor
python app.py


Aplicación disponible en
http://localhost:5000

Autenticación

Login y registro con validación

Manejo de sesiones

Control de permisos (cliente / administrador)

Mantenimiento del proyecto

Código organizado en MVC simplificado

Archivos HTML con Jinja2

Reutilización de componentes

Base de datos relacional normalizada

Licencia

Proyecto académico de uso libre.

👤 Autor

Brandon Florez Cruz
Fredes Acosta
Tecnólogo en Análisis y Desarrollo de Software – SENA

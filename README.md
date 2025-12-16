Restaurante 360

Sistema de información web desarrollado para la gestión integral de un restaurante, que permite administrar pedidos a domicilio o en mesa, productos, usuarios, reservas, brindando soporte tanto a clientes como a empleados y administradores.

Descripción General

Restaurante 360 es una aplicación web diseñada para optimizar los procesos operativos de un restaurante, facilitando la toma de pedidos, el control del menú, la administración de clientes y empleados, y el seguimiento de ventas.
El sistema está orientado a entornos académicos y reales, aplicando buenas prácticas de desarrollo de software, bases de datos relacionales y visualización de datos.

Objetivo del Proyecto

Desarrollar un sistema de información que permita:

Automatizar el proceso de pedidos del restaurante.

Gestionar productos, categorías e inventario.

Administrar usuarios con diferentes roles.

Registrar pagos, reservas y comentarios.

Centralizar la información en una base de datos confiable.

Facilitar el análisis de datos mediante herramientas de visualización.

Arquitectura del Sistema

El sistema sigue una arquitectura cliente-servidor con un enfoque MVC simplificado:

Modelo: Base de datos relacional en MySQL / MariaDB.

Vista: Interfaces web desarrolladas en HTML y CSS.

Controlador: Aplicación backend desarrollada con Flask (Python).

Tecnologías Utilizadas

Lenguaje Backend: Python 3

Framework Web: Flask

Base de Datos: MySQL / MariaDB (XAMPP)

Frontend: HTML5, CSS3

Control de Versiones: Git y GitHub

Entorno Local: XAMPP

Visualización de Datos: Power BI

Sistema Operativo: Windows

Estructura del Proyecto
Restaurante360/
│
├── app.py
├── database/
│   ├── restaurante_db.sql
│   ├── restaurante360_estructura.sql
│   ├── restaurante_db_inserts_prueba.sql
│   └── vistas_restaurante360.sql
│
├── templates/
│   ├── login.html
│   ├── registro.html
│   ├── menu.html
│   ├── dashboard_cliente.html
│   └── dashboard_admin.html
│
├── static/
│   ├── css/
│   └── img/
│
├── tests/
│   └── test_integracion.py
│
└── README.md

Roles del Sistema

El sistema maneja tres roles principales:

Administrador: Gestión total del sistema (productos, usuarios, reportes).

Empleado: Gestión operativa de pedidos y atención.

Cliente: Realiza pedidos, reservas y comentarios.

Base de Datos

La base de datos restaurante_db contiene las siguientes tablas principales:

clientes

empleados

roles

usuarios

categorias

productos

pedidos

detalle_pedidos

pagos

reservas

comentarios

inventario

historial_actividad

Además, incluye vistas para facilitar el análisis de información, como:

vista_pedidos_cliente

vista_ventas_diarias

⚙️ Configuración Local
1️⃣ Clonar el repositorio
git clone https://github.com/usuario/restaurante360.git

2️⃣ Configurar XAMPP

Iniciar Apache y MySQL

Puerto configurado: 3307

3️⃣ Crear la base de datos
CREATE DATABASE restaurante_db;

4️⃣ Importar estructura y datos
mysql -h localhost -P 3307 -u root -p restaurante_db < restaurante360_estructura.sql
mysql -h localhost -P 3307 -u root -p restaurante_db < restaurante_db_inserts_prueba.sql

5️⃣ Ejecutar la aplicación
python app.py

Pruebas

El sistema cuenta con pruebas de integración que validan:

Flujo completo de pedidos

Validación de datos inválidos

Integridad del proceso de compra

Ejecutar pruebas:

pytest

📊 Análisis de Datos

Los datos del sistema pueden ser exportados a Power BI, permitiendo:

Análisis de ventas diarias

Comportamiento de clientes

Productos más vendidos

Seguimiento de ingresos

Documentación

El proyecto cuenta con:

Manual Técnico

Diccionario de Datos

Diagramas UML (Casos de Uso, Clases, Secuencia)

Scripts SQL (estructura, vistas e inserts)

README del proyecto

🎓 Contexto Académico

Este proyecto fue desarrollado como parte de un entregable académico del SENA, aplicando los conocimientos adquiridos en:

Análisis y Desarrollo de Software

Bases de Datos

Programación Backend

Documentación Técnica

Inteligencia de Negocios

Autores

Proyecto: Restaurante 360
Autor: Brandon Cruz y Fredes Acosota
Programa: Análisis y Desarrollo de Software
Institución: SENA

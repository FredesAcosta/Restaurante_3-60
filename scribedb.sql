Create database restaurant_db
USE restaurant_db;

-- 1. Tabla de Roles
CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) UNIQUE
);

-- 2. Tabla de Usuarios (centralizada)
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    telefono VARCHAR(15) NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    id_rol INT NOT NULL,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- 3. Tabla de Empleados (solo información adicional si lo deseas)
CREATE TABLE empleados (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    cargo ENUM('Cocinero', 'Cajero', 'Repartidor', 'Mesero', 'Administrador') NOT NULL,
    fecha_contratacion DATE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- 4. Tabla de Categorías
CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(100) UNIQUE
);

-- 5. Tabla de Productos
CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(100),
    descripcion TEXT,
    precio DECIMAL(10,2),
    imagen VARCHAR(255),
    id_categoria INT,
    disponible BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);

-- 6. Tabla de Pedidos
CREATE TABLE pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('Pendiente', 'Preparando', 'En camino', 'Entregado', 'Cancelado') DEFAULT 'Pendiente',
    total DECIMAL(10,2),
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario)
);

-- 7. Detalle de Pedidos
CREATE TABLE detalle_pedidos (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT,
    id_producto INT,
    cantidad INT,
    precio_unitario DECIMAL(10,2),
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- 8. Tabla de Pagos
CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT,
    metodo_pago ENUM('Efectivo', 'Tarjeta', 'Transferencia', 'Pago móvil'),
    estado_pago ENUM('Pendiente', 'Pagado', 'Rechazado') DEFAULT 'Pendiente',
    fecha_pago DATETIME,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
);

-- 9. Tabla de Comentarios
CREATE TABLE comentarios (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    id_producto INT,
    comentario TEXT,
    calificacion INT CHECK(calificacion BETWEEN 1 AND 5),
    fecha_comentario DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- 10. Tabla de Reservas
CREATE TABLE reservas (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    fecha_reserva DATE,
    hora TIME,
    cantidad_personas INT,
    estado ENUM('Pendiente', 'Confirmada', 'Cancelada'),
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario)
);

-- 11. Historial de actividad
CREATE TABLE historial_actividad (
    id_actividad INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    accion TEXT,
    fecha_actividad DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
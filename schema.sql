-- Sistema de Gestión de Inventario
-- Equipo: Brandon Alan CM

CREATE DATABASE IF NOT EXISTS inventario_db;
USE inventario_db;

-- Tabla principal de productos
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    cantidad INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 5,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de movimientos de inventario (entradas y salidas)
CREATE TABLE IF NOT EXISTS movimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    tipo ENUM('entrada', 'salida') NOT NULL,
    cantidad INT NOT NULL,
    motivo VARCHAR(200),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

-- Tabla de alertas de reposicion generadas automaticamente
CREATE TABLE IF NOT EXISTS alertas_reposicion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    stock_actual INT NOT NULL,
    stock_minimo INT NOT NULL,
    mensaje VARCHAR(300),
    resuelta BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

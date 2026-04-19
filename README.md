# Sistema de Gestión de Inventario — TechNova Solutions
**Equipo:** Brandon Alan CM  
**Dominio:** 3 — Gestión de Inventario

---

## Descripción

Sistema backend para controlar el inventario de productos: registrar entradas y salidas de stock, consultar niveles actuales y recibir alertas automáticas cuando un producto cae por debajo del stock mínimo.

---

## Estructura del proyecto

```
equipo-brandon-alan-cm/
├── app.py              # Aplicación Flask principal
├── requirements.txt    # Dependencias Python
├── Dockerfile          # Configuración del contenedor
├── schema.sql          # Script SQL para crear la base de datos
├── evidencias/         # Capturas de pantalla de la entrega
└── README.md
```

---

## Base de datos (RDS MySQL)

3 tablas con relaciones:

| Tabla | Descripción |
|-------|-------------|
| `productos` | Catálogo de productos con precio, cantidad y stock mínimo |
| `movimientos` | Historial de entradas y salidas (FK → productos) |
| `alertas_reposicion` | Alertas generadas automáticamente cuando el stock baja (FK → productos) |

### Crear la base de datos

```bash
mysql -h <RDS_ENDPOINT> -u admin -p < schema.sql
```

---

## Rutas HTTP

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Interfaz HTML principal |
| POST | `/productos` | Registrar nuevo producto |
| POST | `/movimientos` | Registrar entrada o salida de inventario |
| GET | `/stock` | Consultar stock actual de todos los productos |
| GET | `/alertas` | Ver alertas de reposición activas |
| GET | `/productos/<id>` | Detalle de un producto con sus movimientos |

---

## Correr con Docker en EC2

### 1. Construir la imagen

```bash
docker build -t inventario-app .
```

### 2. Correr el contenedor

```bash
docker run -d \
  -p 5000:5000 \
  -e DB_HOST=<RDS_ENDPOINT> \
  -e DB_USER=admin \
  -e DB_PASSWORD=<TU_PASSWORD> \
  -e DB_NAME=inventario_db \
  -e DB_PORT=3306 \
  --name inventario \
  inventario-app
```

### 3. Acceder desde el navegador

```
http://<IP_PUBLICA_EC2>:5000
```

---

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DB_HOST` | Endpoint del RDS |
| `DB_USER` | Usuario de la base de datos |
| `DB_PASSWORD` | Contraseña de la base de datos |
| `DB_NAME` | Nombre de la base de datos (default: `inventario_db`) |
| `DB_PORT` | Puerto MySQL (default: `3306`) |

---

## Tarea pesada

Al registrar una **salida** que deja el stock por debajo del mínimo, el sistema genera automáticamente una alerta de reposición. Este proceso incluye un `time.sleep(5)` que simula el análisis y notificación costosa.

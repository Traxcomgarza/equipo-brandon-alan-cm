"""
Sistema de Gestión de Inventario - TechNova Solutions
Equipo: Brandon Alan CM
Dominio 3: Control de stock, movimientos y alertas de reposición
"""

import os
import time
import mysql.connector
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv

# Cargar variables del archivo .env si existe
load_dotenv()

app = Flask(__name__)

# ─────────────────────────────────────────────
# Configuración de conexión a RDS desde variables de entorno
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST"),
    "user":     os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
    "port":     int(os.environ.get("DB_PORT", 3306)),
}


def get_connection():
    """Crea y retorna una conexión a la base de datos."""
    return mysql.connector.connect(**DB_CONFIG)


# ─────────────────────────────────────────────
# Estilos y nav compartidos entre páginas
# ─────────────────────────────────────────────
BASE_STYLES = """
<style>
    body { font-family: Arial, sans-serif; max-width: 960px; margin: 40px auto; padding: 0 20px; background: #f5f5f5; }
    h1 { color: #2c3e50; }
    h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 6px; }
    table { width: 100%; border-collapse: collapse; background: white; margin-bottom: 30px; }
    th { background: #3498db; color: white; padding: 10px; text-align: left; }
    td { padding: 8px 10px; border-bottom: 1px solid #ddd; }
    tr:hover { background: #ecf0f1; }
    .bajo { background: #ffe0e0 !important; }
    form { background: white; padding: 20px; margin-bottom: 30px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
    input, select { padding: 8px; margin: 4px 0 10px 0; width: 100%; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
    button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
    button:hover { background: #2980b9; }
    nav { margin-bottom: 16px; }
    nav a { margin-right: 16px; color: #3498db; text-decoration: none; font-weight: bold; }
    nav a:hover { text-decoration: underline; }
    .badge-alerta { background: #e74c3c; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
    .badge-ok { background: #27ae60; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
    .msg { font-weight: bold; margin-bottom: 10px; min-height: 20px; }
    .msg.ok { color: #27ae60; }
    .msg.err { color: #e74c3c; }
</style>
"""

BASE_NAV = """
<h1>&#128230; Sistema de Inventario &#8212; TechNova Solutions</h1>
<nav>
    <a href="/">&#127968; Inicio</a>
    <a href="/stock-page">&#128202; Stock Actual</a>
    <a href="/alertas-page">&#128680; Alertas</a>
</nav>
<hr>
"""

# ─────────────────────────────────────────────
# Plantilla HTML — Página principal
# ─────────────────────────────────────────────
HTML_INDEX = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Inventario TechNova</title>
    {styles}
</head>
<body>
    {nav}

    <h2>Registrar Producto</h2>
    <form id="formProducto">
        <input type="text"   id="nombre"    placeholder="Nombre del producto" required>
        <input type="text"   id="categoria" placeholder="Categoria" required>
        <input type="number" id="precio"    placeholder="Precio" step="0.01" min="0" required>
        <input type="number" id="cantidad"  placeholder="Cantidad inicial" min="0" required>
        <input type="number" id="stock_min" placeholder="Stock minimo" min="0" required>
        <button type="submit">Agregar Producto</button>
    </form>
    <div id="msg_producto" class="msg"></div>

    <h2>Registrar Movimiento</h2>
    <form id="formMovimiento">
        <select id="mov_producto_id" required>
            <option value="">-- Selecciona un producto --</option>
        </select>
        <select id="mov_tipo">
            <option value="entrada">Entrada</option>
            <option value="salida">Salida</option>
        </select>
        <input type="number" id="mov_cantidad" placeholder="Cantidad" min="1" required>
        <input type="text"   id="mov_motivo"   placeholder="Motivo (opcional)">
        <button type="submit">Registrar Movimiento</button>
    </form>
    <div id="msg_movimiento" class="msg"></div>

    <h2>Productos Registrados</h2>
    <table>
        <thead>
            <tr><th>ID</th><th>Nombre</th><th>Categoria</th><th>Precio</th><th>Cantidad</th><th>Stock Min.</th><th>Estado</th></tr>
        </thead>
        <tbody id="tablaProductos"></tbody>
    </table>

    <script>
        async function cargarProductos() {
            const res = await fetch('/stock');
            const data = await res.json();

            // Actualizar tabla
            const tbody = document.getElementById('tablaProductos');
            tbody.innerHTML = '';
            data.forEach(p => {
                const bajo = p.cantidad <= p.stock_minimo;
                tbody.innerHTML += '<tr class="' + (bajo ? 'bajo' : '') + '">' +
                    '<td>' + p.id + '</td>' +
                    '<td>' + p.nombre + '</td>' +
                    '<td>' + p.categoria + '</td>' +
                    '<td>$' + parseFloat(p.precio).toFixed(2) + '</td>' +
                    '<td>' + p.cantidad + '</td>' +
                    '<td>' + p.stock_minimo + '</td>' +
                    '<td>' + (bajo
                        ? '<span class="badge-alerta">Bajo minimo</span>'
                        : '<span class="badge-ok">OK</span>') + '</td>' +
                    '</tr>';
            });

            // Actualizar dropdown con productos existentes
            const select = document.getElementById('mov_producto_id');
            const valorActual = select.value;
            select.innerHTML = '<option value="">-- Selecciona un producto --</option>';
            data.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = '[' + p.id + '] ' + p.nombre + ' (stock: ' + p.cantidad + ')';
                select.appendChild(opt);
            });
            if (valorActual) select.value = valorActual;
        }

        document.getElementById('formProducto').addEventListener('submit', async (e) => {
            e.preventDefault();
            const msgDiv = document.getElementById('msg_producto');
            const body = {
                nombre:       document.getElementById('nombre').value,
                categoria:    document.getElementById('categoria').value,
                precio:       parseFloat(document.getElementById('precio').value),
                cantidad:     parseInt(document.getElementById('cantidad').value),
                stock_minimo: parseInt(document.getElementById('stock_min').value),
            };
            const res = await fetch('/productos', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
            const data = await res.json();
            msgDiv.className = 'msg ' + (res.ok ? 'ok' : 'err');
            msgDiv.textContent = data.mensaje || data.error;
            if (res.ok) {
                document.getElementById('formProducto').reset();
                cargarProductos();
            }
        });

        document.getElementById('formMovimiento').addEventListener('submit', async (e) => {
            e.preventDefault();
            const msgDiv = document.getElementById('msg_movimiento');
            msgDiv.className = 'msg';
            msgDiv.textContent = 'Procesando movimiento...';
            const body = {
                producto_id: parseInt(document.getElementById('mov_producto_id').value),
                tipo:        document.getElementById('mov_tipo').value,
                cantidad:    parseInt(document.getElementById('mov_cantidad').value),
                motivo:      document.getElementById('mov_motivo').value,
            };
            const res = await fetch('/movimientos', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
            const data = await res.json();
            msgDiv.className = 'msg ' + (res.ok ? 'ok' : 'err');
            msgDiv.textContent = data.mensaje || data.error;
            if (res.ok) {
                document.getElementById('formMovimiento').reset();
                cargarProductos();
            }
        });

        cargarProductos();
    </script>
</body>
</html>
"""

# ─────────────────────────────────────────────
# Plantilla HTML — Página Stock Actual
# ─────────────────────────────────────────────
HTML_STOCK_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Stock Actual - TechNova</title>
    {styles}
</head>
<body>
    {nav}
    <h2>Stock Actual</h2>
    <p id="resumen" style="color:#555;"></p>
    <table>
        <thead>
            <tr><th>ID</th><th>Nombre</th><th>Categoria</th><th>Precio</th><th>Cantidad</th><th>Stock Min.</th><th>Estado</th></tr>
        </thead>
        <tbody id="tablaStock"></tbody>
    </table>
    <script>
        async function cargarStock() {
            const res = await fetch('/stock');
            const data = await res.json();
            const tbody = document.getElementById('tablaStock');
            tbody.innerHTML = '';
            let bajos = 0;
            data.forEach(p => {
                const bajo = p.cantidad <= p.stock_minimo;
                if (bajo) bajos++;
                tbody.innerHTML += '<tr class="' + (bajo ? 'bajo' : '') + '">' +
                    '<td>' + p.id + '</td>' +
                    '<td>' + p.nombre + '</td>' +
                    '<td>' + p.categoria + '</td>' +
                    '<td>$' + parseFloat(p.precio).toFixed(2) + '</td>' +
                    '<td>' + p.cantidad + '</td>' +
                    '<td>' + p.stock_minimo + '</td>' +
                    '<td>' + (bajo
                        ? '<span class="badge-alerta">Bajo minimo</span>'
                        : '<span class="badge-ok">Normal</span>') + '</td>' +
                    '</tr>';
            });
            document.getElementById('resumen').textContent =
                'Total: ' + data.length + ' productos — ' + bajos + ' con stock bajo minimo';
        }
        cargarStock();
    </script>
</body>
</html>
"""

# ─────────────────────────────────────────────
# Plantilla HTML — Página Alertas
# ─────────────────────────────────────────────
HTML_ALERTAS_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Alertas - TechNova</title>
    {styles}
    <style>
        .btn-resolver { background: #27ae60; padding: 4px 10px; font-size: 12px; width: auto; }
        .btn-resolver:hover { background: #219a52; }
    </style>
</head>
<body>
    {nav}
    <h2>Alertas de Reposicion</h2>
    <p id="resumen_alertas" style="color:#555;"></p>
    <table>
        <thead>
            <tr><th>#</th><th>Producto</th><th>Categoria</th><th>Stock Actual</th><th>Stock Min.</th><th>Mensaje</th><th>Fecha</th><th>Accion</th></tr>
        </thead>
        <tbody id="tablaAlertas"></tbody>
    </table>
    <script>
        async function cargarAlertas() {
            const res = await fetch('/alertas');
            const data = await res.json();
            const tbody = document.getElementById('tablaAlertas');
            tbody.innerHTML = '';
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#27ae60;padding:20px;">No hay alertas activas</td></tr>';
            }
            data.forEach(a => {
                tbody.innerHTML +=
                    '<tr>' +
                    '<td>' + a.alerta_id + '</td>' +
                    '<td>' + a.producto + '</td>' +
                    '<td>' + a.categoria + '</td>' +
                    '<td><strong style="color:#e74c3c">' + a.stock_actual + '</strong></td>' +
                    '<td>' + a.stock_minimo + '</td>' +
                    '<td style="font-size:13px">' + a.mensaje + '</td>' +
                    '<td style="font-size:12px">' + a.creado_en + '</td>' +
                    '<td><button class="btn-resolver" onclick="resolver(' + a.alerta_id + ')">Resolver</button></td>' +
                    '</tr>';
            });
            document.getElementById('resumen_alertas').textContent =
                data.length + ' alerta(s) activa(s)';
        }

        async function resolver(id) {
            const res = await fetch('/alertas/' + id + '/resolver', { method: 'POST' });
            const data = await res.json();
            if (res.ok) cargarAlertas();
            else alert(data.error);
        }

        cargarAlertas();
    </script>
</body>
</html>
"""


# ─────────────────────────────────────────────
# RUTA 1: Interfaz HTML principal
# ─────────────────────────────────────────────
def render_page(template):
    """Inyecta estilos y nav en la plantilla sin usar .format() para evitar
    conflictos con las llaves {} del CSS y JavaScript."""
    html = template.replace("{styles}", BASE_STYLES).replace("{nav}", BASE_NAV)
    return Response(html, mimetype="text/html")


@app.route("/")
def index():
    """Retorna la interfaz HTML del sistema de inventario."""
    return render_page(HTML_INDEX)


# ─────────────────────────────────────────────
# RUTA 1b: Página de Stock Actual
# ─────────────────────────────────────────────
@app.route("/stock-page")
def stock_page():
    """Página HTML dedicada para visualizar el stock actual."""
    return render_page(HTML_STOCK_PAGE)


# ─────────────────────────────────────────────
# RUTA 1c: Página de Alertas
# ─────────────────────────────────────────────
@app.route("/alertas-page")
def alertas_page():
    """Página HTML dedicada para visualizar y gestionar alertas."""
    return render_page(HTML_ALERTAS_PAGE)


# ─────────────────────────────────────────────
# RUTA 2: Registrar un nuevo producto (POST)
# ─────────────────────────────────────────────
@app.route("/productos", methods=["POST"])
def registrar_producto():
    """
    Recibe JSON con: nombre, categoria, precio, cantidad, stock_minimo
    Inserta el producto en la base de datos.
    """
    conn = None
    cursor = None
    try:
        data = request.get_json()

        # Validar campos requeridos
        campos = ["nombre", "categoria", "precio", "cantidad", "stock_minimo"]
        for campo in campos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Inserción con parámetros (nunca concatenación de strings)
        sql = """
            INSERT INTO productos (nombre, categoria, precio, cantidad, stock_minimo)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data["nombre"],
            data["categoria"],
            data["precio"],
            data["cantidad"],
            data["stock_minimo"],
        ))
        conn.commit()

        return jsonify({"mensaje": "Producto registrado correctamente", "id": cursor.lastrowid}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Cierre apropiado de conexiones
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ─────────────────────────────────────────────
# RUTA 3: Registrar movimiento de inventario (POST)
# ─────────────────────────────────────────────
@app.route("/movimientos", methods=["POST"])
def registrar_movimiento():
    """
    Recibe JSON con: producto_id, tipo (entrada/salida), cantidad, motivo
    Actualiza el stock del producto y genera alerta si queda bajo mínimo.
    La generación de alerta incluye time.sleep(5) simulando proceso costoso.
    """
    conn = None
    cursor = None
    try:
        data = request.get_json()

        campos = ["producto_id", "tipo", "cantidad"]
        for campo in campos:
            if campo not in data:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400

        if data["tipo"] not in ("entrada", "salida"):
            return jsonify({"error": "tipo debe ser 'entrada' o 'salida'"}), 400

        if data["cantidad"] <= 0:
            return jsonify({"error": "La cantidad debe ser mayor a 0"}), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener producto actual con parámetros
        cursor.execute("SELECT * FROM productos WHERE id = %s", (data["producto_id"],))
        producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        # Calcular nuevo stock según tipo de movimiento
        if data["tipo"] == "entrada":
            nuevo_stock = producto["cantidad"] + data["cantidad"]
        else:
            # Validar que haya suficiente stock para la salida
            if data["cantidad"] > producto["cantidad"]:
                return jsonify({"error": "Stock insuficiente para registrar la salida"}), 400
            nuevo_stock = producto["cantidad"] - data["cantidad"]

        # Actualizar cantidad en productos
        cursor.execute(
            "UPDATE productos SET cantidad = %s WHERE id = %s",
            (nuevo_stock, data["producto_id"])
        )

        # Insertar registro en movimientos
        cursor.execute(
            """INSERT INTO movimientos (producto_id, tipo, cantidad, motivo)
               VALUES (%s, %s, %s, %s)""",
            (data["producto_id"], data["tipo"], data["cantidad"], data.get("motivo", ""))
        )
        conn.commit()

        alerta_generada = False

        # ── TAREA PESADA ──────────────────────────────────────────────
        # Si es una salida y el stock queda por debajo del mínimo,
        # se genera una alerta de reposición.
        # time.sleep(5) simula el proceso costoso de análisis y notificación.
        # ─────────────────────────────────────────────────────────────
        if data["tipo"] == "salida" and nuevo_stock < producto["stock_minimo"]:
            time.sleep(5)  # Simula proceso costoso de generación de alerta

            mensaje_alerta = (
                f"ALERTA: '{producto['nombre']}' tiene stock {nuevo_stock} "
                f"por debajo del minimo de {producto['stock_minimo']} unidades. "
                f"Se requiere reposicion urgente."
            )

            cursor.execute(
                """INSERT INTO alertas_reposicion (producto_id, stock_actual, stock_minimo, mensaje)
                   VALUES (%s, %s, %s, %s)""",
                (data["producto_id"], nuevo_stock, producto["stock_minimo"], mensaje_alerta)
            )
            conn.commit()
            alerta_generada = True

        respuesta = {
            "mensaje": f"Movimiento registrado. Stock actual: {nuevo_stock}",
            "stock_actual": nuevo_stock,
            "alerta_generada": alerta_generada,
        }
        return jsonify(respuesta), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ─────────────────────────────────────────────
# RUTA 4: Consultar stock actual de todos los productos (GET)
# ─────────────────────────────────────────────
@app.route("/stock", methods=["GET"])
def consultar_stock():
    """Retorna la lista de todos los productos con su stock actual."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, nombre, categoria, precio, cantidad, stock_minimo FROM productos ORDER BY nombre")
        productos = cursor.fetchall()

        return jsonify(productos), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ─────────────────────────────────────────────
# RUTA 5: Ver alertas de reposición activas (GET)
# ─────────────────────────────────────────────
@app.route("/alertas", methods=["GET"])
def ver_alertas():
    """
    Retorna las alertas de reposición no resueltas,
    junto con la información del producto relacionado.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # JOIN entre alertas y productos para mostrar info completa
        sql = """
            SELECT
                a.id AS alerta_id,
                p.nombre AS producto,
                p.categoria,
                a.stock_actual,
                a.stock_minimo,
                a.mensaje,
                a.resuelta,
                a.creado_en
            FROM alertas_reposicion a
            JOIN productos p ON a.producto_id = p.id
            WHERE a.resuelta = FALSE
            ORDER BY a.creado_en DESC
        """
        cursor.execute(sql)
        alertas = cursor.fetchall()

        # Convertir timestamps a string para serialización JSON
        for alerta in alertas:
            if alerta.get("creado_en"):
                alerta["creado_en"] = str(alerta["creado_en"])

        return jsonify(alertas), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ─────────────────────────────────────────────
# RUTA 6: Marcar alerta como resuelta (POST)
# ─────────────────────────────────────────────
@app.route("/alertas/<int:alerta_id>/resolver", methods=["POST"])
def resolver_alerta(alerta_id):
    """Marca una alerta de reposición como resuelta."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE alertas_reposicion SET resuelta = TRUE WHERE id = %s", (alerta_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Alerta no encontrada"}), 404

        return jsonify({"mensaje": "Alerta marcada como resuelta"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ─────────────────────────────────────────────
# RUTA 7: Detalle de un producto por ID (GET)
# ─────────────────────────────────────────────
@app.route("/productos/<int:producto_id>", methods=["GET"])
def detalle_producto(producto_id):
    """Retorna el detalle de un producto específico junto con sus últimos movimientos."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener producto por ID con parámetro
        cursor.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
        producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        # Obtener los últimos 10 movimientos del producto
        cursor.execute(
            """SELECT tipo, cantidad, motivo, creado_en
               FROM movimientos WHERE producto_id = %s
               ORDER BY creado_en DESC LIMIT 10""",
            (producto_id,)
        )
        movimientos = cursor.fetchall()

        # Convertir timestamps
        if producto.get("creado_en"):
            producto["creado_en"] = str(producto["creado_en"])
        for m in movimientos:
            if m.get("creado_en"):
                m["creado_en"] = str(m["creado_en"])

        return jsonify({"producto": producto, "movimientos": movimientos}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ─────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

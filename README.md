# Sistema de Inventario
**Equipo:** Brandon Alan Carrion Morales 
**Dominio:** Sistema de Inventario 
**Fecha:** 18 Abril 2026

---

## ¿Qué problema resuelve?
Permite que la empresa tenga control de sus productos, asi mismo les permite ver
si tienen escases de algun producto

---

## Estructura de la Base de Datos

| Tabla | Descripcion | Relacion |
|-------|-------------|----------|
| productos | Guarda los productos con su nombre, categoria, precio y cantidad disponible | Tabla principal |
| movimientos | Registra cada vez que entra o sale mercancia | Se conecta con productos |
| alertas_reposicion| Guarda las alertas cuando un producto se queda sin stock suficiente | Se conecta con productos|

---

## Rutas de la API

| Metodo | Ruta | Que hace |
|--------|------|----------|
| GET | / | Pagina principal con formularios y lista de productos |
| GET | /stock-page | Pagina con el stock actual de todos los productos |
| GET | /alertas-page | Pagina con las alertas de reposicion activas |
| GET | /stock | Retorna los productos en formato JSON |
| GET | /alertas | Retorna las alertas activas en formato JSON |
| GET | /productos/<id>| Muestra el detalle de un producto especifico |
| POST | /productos| Agrega un nuevo producto |
| POST | /movimientos | Registra una entrada o salida de inventario |
| POST | /alertas/<id>/resolver | Marca una alerta como resuelta |


---

## ¿Cuál es la tarea pesada y por qué bloquea el sistema?
Cuando se registra una salida de inventario y el stock queda por debajo del minimo, el sistema genera una alerta automatica. En ese momento se ejecuta un timesleep que simula el tiempo que tomaria un proceso real, como generar un reporte. El problema es que mientras esos 5 segundos pasan, el servidor no puede atender a nadie mas. Si varios usuarios usan el sistema al mismo tiempo y varios activan esta alerta, tendrian que esperar en fila. En un sistema real esto se resolveria procesando esa tarea en segundo plano.
---

## Cómo levantar el proyecto


```bash
# 1. Clonar el repositorio
git clone [URL_DEL_REPO]

# 2. Crear las tablas en RDS
mysql -h ENDPOINT_RDS -u admin -p < schema.sql

# 3. Construir la imagen Docker
docker build -t inventario-app .

# 4. Correr el contenedor
docker run -d -p 5000:5000 \
  --env-file .env \
  --name inventario \
  inventario-app

# 5. Abrir en el navegador
http://IP_EC2:5000
```

---

## Decisiones técnicas
Use flask porque es sencillo y rapido de configurar,l a base de datos esta en RDS de AWS para que los datos no se pierdan si el contenedor se reinicia, las contrasenas y datos de conexion nunca estan escritos en el codigo, siempre vienen de un archivo de variables de entorno.
---

## Estructura del repositorio

```
equipo-[nombre]/
├── app.py
├── requirements.txt
├── Dockerfile
├── schema.sql
├── evidencias/
│   ├── 01_rds_tablas.png
│   ├── 02_docker_build.png
│   ├── 03_contenedor_corriendo.png
│   ├── 04_interfaz_navegador.png
│   ├── 05_registro_exitoso.png
│   ├── 06_consulta_datos.png
│   └── 07_tarea_pesada.png
└── README.md
```

---

## Checklist de Autoevaluación

**ESTRUCTURA**
- [✓] El repositorio tiene exactamente la estructura pedida
- [✓] Todos los archivos tienen el nombre correcto
- [✓] Las evidencias tienen nombres descriptivos (no foto1.png)

**BASE DE DATOS**
- [✓] El archivo schema.sql existe y crea todas las tablas
- [✓] Hay mínimo 3 tablas con relaciones entre ellas
- [✓] La captura 01 muestra las tablas creadas en RDS

**APLICACIÓN**
- [✓] Hay mínimo 5 rutas HTTP funcionales
- [✓] Hay al menos una ruta GET que retorna datos de la BD
- [✓] La interfaz HTML abre correctamente en el navegador
- [✓] El time.sleep() de la tarea pesada está presente y es de 5+ segundos

**CONTENEDOR**
- [✓] El Dockerfile existe y hace docker build sin errores
- [✓] El contenedor corre con docker run usando variables de entorno
- [✓] Ninguna credencial está escrita directamente en app.py
- [✓] La aplicación es accesible desde el navegador con la IP de la EC2

**CALIDAD DE CÓDIGO**
- [✓] Todas las rutas tienen manejo de errores con try/except
- [✓] Todas las conexiones a BD se cierran en bloque finally
- [✓] Las consultas SQL usan %s, no concatenación de strings
- [✓] El código tiene comentarios explicando la lógica

**README**
- [✓] Describe el problema que resuelve
- [✓] Tiene la tabla de rutas completa
- [✓] Explica la tarea pesada con sus palabras
- [✓] Tiene los comandos para levantar el proyecto

**PUNTOS EXTRA (si aplica)**
- [ ] Servicio A no tiene time.sleep()
- [ ] Servicio B no tiene rutas HTML
- [ ] B usa nombre de contenedor como hostname, no IP
- [ ] B no tiene puerto expuesto en docker-compose.yml
- [ ] Hay dos capturas JSON diferentes (B encendido vs apagado)

---

## Rúbrica de Evaluación

| Criterio | Puntos | Qué se verifica |
|----------|--------|-----------------|
| Base de datos en RDS con 3+ tablas y relaciones | 15 | schema.sql funcional, captura de tablas creadas |
| Aplicación con 5+ rutas funcionales | 20 | Demo en vivo, GET y POST funcionando |
| Interfaz HTML accesible desde navegador | 10 | Captura con IP pública de EC2 |
| Tarea pesada presente y demostrable | 10 | time.sleep() en código, captura de logs o tiempo |
| Dockerfile correcto y contenedor corriendo | 20 | docker build y docker ps sin errores |
| Credenciales en variables de entorno | 10 | No hay strings de contraseñas en app.py |
| Calidad del código (errores, cierre BD, SQL seguro) | 10 | Revisión del código fuente |
| README completo y redactado con sus palabras | 5 | No copiado, tiene todos los apartados |
| **Puntos extra — Microservicios** | **+10** | Los 4 criterios cumplidos con evidencia |

**Total base: 100 puntos + 10 puntos extra posibles**

---

## Fecha de Entrega

El repositorio debe estar **público y completo** antes de la clase de presentación. Durante la sesión, cada persona tendrá **10 minutos**:

- **7 minutos** — demo en vivo con el sistema corriendo en su EC2
- **3 minutos** — preguntas técnicas del profesor

Las preguntas pueden ser sobre cualquier línea de su código. Debes poder responder — si solo uno sabe cómo funciona el sistema, el equipo pierde puntos en la presentación.

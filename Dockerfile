# Imagen base oficial de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias primero (aprovecha cache de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY app.py .

# Las credenciales de BD se pasan como variables de entorno al correr el contenedor
# Nunca se escriben en el código ni en la imagen
ENV DB_HOST=""
ENV DB_USER=""
ENV DB_PASSWORD=""
ENV DB_NAME="inventario_db"
ENV DB_PORT="3306"

# Exponer el puerto de Flask
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "app.py"]

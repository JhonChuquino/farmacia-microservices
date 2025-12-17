# Imagen base ligera con Python 3.11
FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements.txt primero para instalar dependencias
COPY requirements.txt .

# Instalar dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Variables de entorno por defecto (pueden ser sobrescritas por docker-compose)
ENV MONGO_URL=mongodb://mongo:27017/pharma_store_db
ENV JWT_SECRET=supersecretkey

# Comando de inicio
CMD ["python", "app.py"]

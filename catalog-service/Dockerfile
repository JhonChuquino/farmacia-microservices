# Imagen base ligera con Python 3.11
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del microservicio
COPY . .

ENV MONGO_URL=mongodb://mongo:27017/pharma_store_db
ENV API_KEY=nube
ENV JWT_SECRET=supersecretkey

CMD sh -c "python seed.py && python app.py"


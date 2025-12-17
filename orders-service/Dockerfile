FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MONGO_URL=mongodb://mongo:27017/pharma_store_db
ENV API_KEY=nube
ENV JWT_SECRET=supersecretkey

CMD ["python", "app.py"]

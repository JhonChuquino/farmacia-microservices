from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")

client = MongoClient(MONGO_URL)
db = client.get_database()
products = db.products

data = [
    {
        "sku": "MED-001",
        "name": "Paracetamol 500mg",
        "price": 5.00,
        "category": "Analgesico"
    },
    {
        "sku": "MED-002",
        "name": "Ibuprofeno 400mg",
        "price": 7.50,
        "category": "Antiinflamatorio"
    }
]

if products.count_documents({}) == 0:
    products.insert_many(data)
    print("Catalogo: datos iniciales insertados")
else:
    print("Catalogo: datos ya existen, seed omitido")

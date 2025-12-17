from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")

client = MongoClient(MONGO_URL)
db = client.get_database()
users = db.get_collection("users")

data = [
    {
        "username": "admin",
        "password": generate_password_hash("admin123"),
        "role": "ADMIN"
    },
    {
        "username": "farmaceutico",
        "password": generate_password_hash("farm123"),
        "role": "FARMACEUTICO"
    },
    {
        "username": "cajero",
        "password": generate_password_hash("cajero123"),
        "role": "CAJERO"
    },
    {
        "username": "almacen",
        "password": generate_password_hash("almacen123"),
        "role": "ALMACEN"
    }
]

if users.count_documents({}) == 0:
    users.insert_many(data)
    print("Usuarios iniciales insertados correctamente")
else:
    print("Usuarios ya existen, seed omitido")

from flask import Flask, jsonify, request
from pymongo import MongoClient
import os
import jwt
from functools import wraps

app = Flask(__name__)

# 🔐 Secret key para JWT
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")

# 🔗 Conexión a MongoDB
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client.get_database()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"service": "Catalog Service active 🚀"})

# Middleware: validar JWT y rol
def token_required(roles=[]):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = None
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ")[1]
            if not token:
                return jsonify({"message": "Token is missing"}), 401
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                if roles and data["role"] not in roles:
                    return jsonify({"message": "Unauthorized role"}), 403
            except Exception as e:
                return jsonify({"message": str(e)}), 401
            return f(*args, **kwargs)
        return wrapper
    return decorator

# 🧾 Listar catálogo con información del lote más próximo a vencer
@app.route("/catalog", methods=["GET"])
@token_required(roles=["ADMIN", "FARMACEUTICO"])
def get_catalog():
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "inventory",
                    "localField": "sku",
                    "foreignField": "sku",
                    "as": "inventory"
                }
            },
            {
                "$unwind": {
                    "path": "$inventory",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$sort": {
                    "inventory.expiry_date": 1
                }
            },
            {
                "$group": {
                    "_id": "$sku",
                    "sku": {"$first": "$sku"},
                    "name": {"$first": "$name"},
                    "category": {"$first": "$category"},
                    "unit_price": {"$first": "$unit_price"},
                    "available_quantity": {"$sum": "$inventory.quantity"},
                    "next_batch": {"$first": "$inventory.batch"},
                    "expiry_date": {"$first": "$inventory.expiry_date"}
                }
            },
            {
                "$project": {
                    "_id": 0
                }
            }
        ]


        products = list(db.products.aggregate(pipeline))
        for p in products:
            p.pop("_id", None)  # eliminar ObjectId

        if not products:
            return jsonify([{"message": "No products found"}]), 200

        return jsonify(products), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

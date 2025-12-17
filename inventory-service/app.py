from flask import Flask, jsonify, request
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
import jwt
from functools import wraps
from flask import request, jsonify


app = Flask(__name__)


# 🔐 Secret key para JWT
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")

# 🔗 Conexión a MongoDB
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client.get_database()


@app.route("/", methods=["GET"])
def home():
    return jsonify({"service": "Inventory Service active 🧾"})


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

# Listar todo el inventario
@app.route("/inventory", methods=["GET"])
@token_required(roles=["ADMIN","FARMACEUTICO"])
def list_inventory():
    inventory = list(db.inventory.find({}, {"_id": 0}))
    if not inventory:
        return jsonify([{"message": "Inventory is empty"}]), 200
    return jsonify(inventory), 200

# Buscar por SKU
@app.route("/inventory/<sku>", methods=["GET"])
@token_required(roles=["ADMIN","FARMACEUTICO"])
def search_by_sku(sku):
    batches = list(db.inventory.find({"sku": sku}, {"_id": 0}).sort("expiry_date", 1))
    if not batches:
        return jsonify({"message": f"No inventory found for SKU {sku}"}), 404
    return jsonify(batches), 200

# Productos próximos a vencer
@app.route("/inventory/expiring", methods=["GET"])
@token_required(roles=["ADMIN", "FARMACEUTICO"])
def expiring_soon():
    days = int(request.args.get("days", 15))
    today = datetime.utcnow()
    limit_date = today + timedelta(days=days)

    cursor = db.inventory.find(
        {"expiry_date": {"$lte": limit_date}}
    ).sort("expiry_date", 1)

    response = []

    for item in cursor:
        expiry = item["expiry_date"]
        days_remaining = (expiry - today).days

        response.append({
            "sku": item.get("sku"),
            "batch": item.get("batch"),
            "quantity": item.get("quantity"),
            "expiry_date": expiry.strftime("%Y-%m-%d"),
            "days_remaining": days_remaining,
            "priority": (
                "🔴 Alta" if days_remaining <= 7 else
                "🟡 Media" if days_remaining <= 30 else
                "🟢 Baja"
            )
        })


    if not response:
        return jsonify([{"message": f"No products expiring in the next {days} days"}]), 200

    return jsonify(response), 200

# Registrar nuevo lote
@app.route("/inventory", methods=["POST"])
@token_required(roles=["ADMIN"])
def add_batch():
    data = request.get_json()
    if not data or not all(k in data for k in ("sku", "batch", "quantity", "expiry_date")):
        return jsonify({"error": "Missing required fields"}), 400
    
    db.inventory.insert_one({
        "sku": data["sku"],
        "batch": data["batch"],
        "quantity": data["quantity"],
        "entry_date": datetime.utcnow(),
        "expiry_date": datetime.strptime(data["expiry_date"], "%Y-%m-%d")

    })
    return jsonify({"message": "Batch added successfully"}), 201



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

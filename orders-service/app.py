from flask import Flask, jsonify, request
from pymongo import MongoClient
import os
import jwt
import requests
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

# 🔐 Secret key para JWT
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")

# 🔗 Conexión a MongoDB
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client.get_database()

# Variables de entorno para otros servicios
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory-service:5000/inventory")
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog-service:5000/catalog")

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


@app.route("/", methods=["GET"])
def home():
    return jsonify({"service": "Orders Service active 🧾"})


# 🧾 Crear orden
@app.route("/orders", methods=["POST"])
@token_required(roles=["ADMIN", "CAJERO"])
def create_order():
    data = request.get_json()

    # 🔐 Token y headers
    token = request.headers.get("Authorization").split(" ")[1]
    headers = {"Authorization": f"Bearer {token}"}

    # 📦 Obtener producto desde Catalog
    catalog_response = requests.get(CATALOG_URL, headers=headers)
    products = catalog_response.json()

    product = next((p for p in products if p["sku"] == data["sku"]), None)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404

    unit_price = product.get("unit_price", 0)

    # 🔄 Descontar stock via Inventory Service
    inventory_payload = {
        "sku": data["sku"],
        "quantity": data["quantity"]
    }

    inventory_response = requests.post(
        f"{INVENTORY_URL}/decrease",
        json=inventory_payload,
        headers=headers
    )

    if inventory_response.status_code != 200:
        return jsonify({"error": "Stock insuficiente"}), 400

    # 🧾 Crear orden
    order = {
        "order_number": f"ORD-{int(datetime.utcnow().timestamp())}",
        "sku": data["sku"],
        "product_name": product["name"],
        "quantity": data["quantity"],
        "price": unit_price,
        "unit_price": unit_price,
        "total": unit_price * data["quantity"],
        "date": datetime.utcnow().isoformat(),
        "status": "COMPLETADA"
    }

    db.orders.insert_one(order)
    return jsonify(order), 201



# Listar órdenes
@app.route("/orders", methods=["GET"])
@token_required(roles=["ADMIN", "CAJERO"])
def list_orders():
    orders = list(db.orders.find({}, {"_id": 0}))

    flattened = []

    for order in orders:
        for item in order.get("items", []):
            flattened.append({
                "order_number": order.get("order_number"),
                "product_name": item.get("product_name", "N/A"),
                "sku": item.get("sku"),
                "quantity": item.get("quantity", 0),
                "price": item.get("price", 0),
                "unit_price": item.get("price", 0),
                "total": item.get("price", 0) * item.get("quantity", 0),
                "date": order.get("created_at"),
                "status": order.get("status")
            })

    if not flattened:
        return jsonify([]), 200

    return jsonify(flattened), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

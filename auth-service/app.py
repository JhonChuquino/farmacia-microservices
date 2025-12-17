from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)

# 🔐 Secret key para JWT
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")

# 🔗 Conexión a MongoDB
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client.get_database()
users_collection = db.get_collection("users")

print("MongoDB collections:", db.list_collection_names())

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
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token"}), 401
            return f(*args, **kwargs)
        return wrapper
    return decorator

# 🔑 Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    print("Login request data:", data) 
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Username and password required"}), 400

    user = users_collection.find_one({"username": data["username"]})
    if not user or not check_password_hash(user.get("password"), data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token = jwt.encode({
        "username": data["username"],
        "role": user.get("role", "USER"),
        "exp": datetime.utcnow() + timedelta(hours=2)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})

# 🏠 Ruta de prueba protegida
@app.route("/protected", methods=["GET"])
@token_required(roles=["ADMIN", "FARMACEUTICO", "CAJERO"])
def protected():
    return jsonify({"message": "Access granted"}), 200

# 📌 Registrar usuarios (solo ADMIN puede)
@app.route("/register", methods=["POST"])
@token_required(roles=["ADMIN"])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ("username", "password", "role")):
        return jsonify({"message": "Missing required fields"}), 400

    if users_collection.find_one({"username": data["username"]}):
        return jsonify({"message": "User already exists"}), 400

    users_collection.insert_one({
        "username": data["username"],
        "password": generate_password_hash(data["password"], method="scrypt"),
        "role": data["role"]
    })
    return jsonify({"message": "User registered successfully"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

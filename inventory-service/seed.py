from pymongo import MongoClient
import os
from datetime import datetime

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")

client = MongoClient(MONGO_URL)
db = client.get_database()
inventory = db.inventory

data = [
    {
        "sku": "MED-001",
        "batch": "LOT-001",
        "quantity": 100,
        "entry_date": datetime(2025, 12, 1),
        "expiry_date": datetime(2026, 1, 15)
    },
    {
        "sku": "MED-002",
        "batch": "LOT-002",
        "quantity": 50,
        "entry_date": datetime(2025, 12, 1),
        "expiry_date": datetime(2026, 2, 1)
    },
    {
        "sku": "MED-003",
        "batch": "LOT-003",
        "quantity": 50,
        "entry_date": datetime(2025, 12, 1),
        "expiry_date": datetime(2026, 1, 1)
    }
]

for item in data:
    exists = inventory.count_documents({
        "sku": item["sku"],
        "batch": item["batch"],
        "expiry_date": item["expiry_date"]
    })
    

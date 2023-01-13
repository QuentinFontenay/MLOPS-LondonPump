from pymongo import mongo_client
import pymongo
from .config import settings

print(f'Connecting to MongoDB {settings.DATABASE_URL}')
client = mongo_client.MongoClient(
    settings.DATABASE_URL, serverSelectionTimeoutMS=5000)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect to the MongoDB server.")

db = client[settings.MONGO_INITDB_DATABASE]
User = db.users
Predictions = db.predictions
Stations = db.stations

User.create_index([("username", pymongo.ASCENDING)], unique=True)

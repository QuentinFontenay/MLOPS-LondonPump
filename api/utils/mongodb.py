from pymongo import mongo_client
import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

connexion_url = f"mongodb://{os.getenv('MONGO_LONDON_FIRE_USER')}:{os.getenv('MONGO_LONDON_FIRE_PASSWORD')}@{os.getenv('MONGO_INITDB_HOST')}/{os.getenv('MONGO_INITDB_DATABASE')}?authSource={os.getenv('MONGO_INITDB_DATABASE')}"
print(f'Connecting to MongoDB {connexion_url}')
client = mongo_client.MongoClient(connexion_url, serverSelectionTimeoutMS=5000)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect to the MongoDB server.")

db = client[os.getenv('MONGO_INITDB_DATABASE')]
User = db.users
Predictions = db.predictions
Stations = db.stations
RiskStations = db.riskStations
User.create_index([("username", pymongo.ASCENDING)], unique=True)

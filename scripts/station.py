from pymongo import mongo_client
import os
import sys
import argparse
import csv
from dotenv import load_dotenv

load_dotenv()

def connect_to_mongo():
    client = mongo_client.MongoClient(
        os.environ.get('DATABASE_URL'), serverSelectionTimeoutMS=5000)

    try:
        conn = client.server_info()
        print(f'Connected to MongoDB {conn.get("version")}')
    except Exception:
        print("Unable to connect to the MongoDB server.")

    db = client[os.environ.get('MONGO_INITDB_DATABASE')]
    stations = db.stations

    return stations

argParser = argparse.ArgumentParser()
argParser.add_argument("-f", "--file", help="file with stations")

args = argParser.parse_args()

if args.file != None:
    stations = connect_to_mongo()
    result = stations.delete_many({})
    print("Deleted %s stations" % result.deleted_count)
    with open(args.file, 'r') as file:
        csvreader = csv.reader(file)
        for index, row in enumerate(csvreader):
            if index != 0:
                object = { "code": row[0], "name": row[1], "latitude": float(row[2]), "longitude": float(row[3]) }
                stations.insert_one(object)
                print("Inserted station= %s" % row[0])
else:
    print("Please provide a file with stations")
    sys.exit(2)
